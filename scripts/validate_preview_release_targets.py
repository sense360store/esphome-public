#!/usr/bin/env python3
"""Validate the concrete preview release-target manifest.

RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001.

This script consumes ``config/preview-release-targets.json`` — the concrete,
CI-consumable preview / advanced-preview release-target manifest for every
buildable Sense360 firmware target — and asserts that it stays consistent with
the policy and the surrounding config files without ever publishing a preview
artifact, adding a ``config/webflash-builds.json`` row, flipping a
``config/product-catalog.json`` status, promoting anything to stable, or
claiming any bench / compliance / hardware / build evidence.

Cross-references enforced (metadata only):

  * every target's ``yaml_path`` exists on disk;
  * ``channel_tier`` is a known tier from ``config/release-channel-policy.json``
    and ``build_channel`` follows that policy's ``build_channel_mapping`` and is
    an ``allowed_channels`` value in ``config/webflash-compatibility.json``;
  * ``expected_artifact_name`` is exactly
    ``Sense360-{config_string}-v{version}-{build_channel}.bin``;
  * preview / advanced-preview targets carry the policy warning copy and are
    never recommended / customer-default / REQUIRED_CONFIG / customer-kit
    default, and never claim bench evidence or a verified schematic;
  * TRIAC is advanced-preview only, with the mains-risk warning, not (yet)
    WebFlash-importable, delivered on the ``advanced-manual-preview`` lane, and
    carries a build blocker (HW-005 buildability, not a preview-policy block);
  * fan-driver targets are PREVIEW release targets delivered on the
    ``manual-preview`` lane (WebFlash import gated until the WebFlash warning UX
    is ready), map to the manual lane in
    ``config/manual-firmware-artifacts.json``, and keep
    ``webflash_build_matrix=false`` in the catalog;
  * ledger-present targets (``published-stable`` / ``published-preview`` /
    ``webflash-preview-metadata-ready``) agree with ``config/webflash-builds.json``
    on channel + artifact name, and unpublished targets are absent from it and
    carry a build blocker;
  * every committed ``config/webflash-builds.json`` build is represented;
  * every non-stable row of the policy ``preview_release_matrix`` is represented
    with the same intended channel and artifact name.

This is a CI validation lane only; it builds nothing and changes nothing.

Run with::

    python3 scripts/validate_preview_release_targets.py --metadata-only

``--metadata-only`` is the default so the script is safe to run anywhere.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"

MANIFEST_ID = "RELEASE-PREVIEW-TARGETS-ALL-PRODUCTS-001"

REQUIRED_TARGET_FIELDS = (
    "target_id",
    "product",
    "family",
    "config_string",
    "yaml_path",
    "channel_tier",
    "build_channel",
    "version",
    "expected_artifact_name",
    "is_preview_target",
    "is_fan",
    "is_triac",
    "delivery_lane",
    "webflash_import_eligibility",
    "publication_status",
    "warning_copy_required",
    "warning_copy_key",
    "release_note_warning",
    "stable_blocker",
    "build_blocker",
    "recommended",
    "customer_default",
    "required_config",
    "customer_kit_default",
    "bench_evidence_claimed",
    "schematic_status_verified_claim",
)

DELIVERY_LANES = frozenset({"webflash", "manual-preview", "advanced-manual-preview"})
FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")
PUBLISHED_STATUSES = frozenset({"published-stable", "published-preview"})

# RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001: a webflash-lane target whose reviewed
# config/webflash-builds.json row exists but whose firmware artifact is not yet
# published (no binary / GitHub Release / tag / manifest.json) is recorded as
# "webflash-preview-metadata-ready". Like the "published-*" statuses, the build
# ledger row must exist and agree on channel + artifact name; unlike them, no
# published/exposed artifact is claimed.
WEBFLASH_PREVIEW_METADATA_READY = "webflash-preview-metadata-ready"
LEDGER_PRESENT_STATUSES = PUBLISHED_STATUSES | frozenset(
    {WEBFLASH_PREVIEW_METADATA_READY}
)

_ARTIFACT_RE = re.compile(r"^Sense360-(.+)-v(\d+\.\d+\.\d+)-([a-z]+)\.bin$")

# Scope flags that must all be false — this manifest is metadata only.
SCOPE_MUST_BE_FALSE = (
    "publishes_artifacts",
    "touches_webflash_repo",
    "adds_webflash_builds_entries",
    "flips_product_catalog_status",
    "marks_any_product_stable",
    "claims_bench_evidence",
    "claims_compliance",
    "claims_hardware_proof",
    "claims_build_proof",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(
    manifest: Dict[str, Any],
    policy: Dict[str, Any],
    compat: Dict[str, Any],
    builds_doc: Dict[str, Any],
    catalog_doc: Dict[str, Any],
    manual_doc: Dict[str, Any],
) -> List[str]:
    """Return a list of error strings (empty == valid)."""
    errors: List[str] = []

    if manifest.get("schema_version") != 1:
        errors.append(
            f"schema_version must be 1; got {manifest.get('schema_version')!r}"
        )
    if manifest.get("id") != MANIFEST_ID:
        errors.append(f"id must be {MANIFEST_ID!r}; got {manifest.get('id')!r}")

    # Scope guardrails: metadata-only manifest.
    scope = manifest.get("scope", {})
    if not isinstance(scope, dict):
        errors.append("scope must be an object")
        scope = {}
    for flag in SCOPE_MUST_BE_FALSE:
        if scope.get(flag) is not False:
            errors.append(f"scope.{flag} must be false")

    tiers = policy.get("channel_tiers", {})
    policy_mapping = policy.get("build_channel_mapping", {})
    policy_warning = policy.get("warning_copy", {})
    allowed_channels = set(compat.get("allowed_channels", []) or [])

    # The manifest must reuse the policy's build-channel mapping and warning copy
    # verbatim so the two files can never drift.
    if manifest.get("build_channel_mapping") != policy_mapping:
        errors.append(
            "build_channel_mapping must match "
            "config/release-channel-policy.json build_channel_mapping"
        )
    if manifest.get("warning_copy") != policy_warning:
        errors.append(
            "warning_copy must match config/release-channel-policy.json warning_copy"
        )

    builds_by_cs = {
        b.get("config_string"): b
        for b in builds_doc.get("builds", []) or []
        if isinstance(b, dict) and b.get("config_string")
    }
    catalog_by_cs = {
        p.get("config_string"): p
        for p in catalog_doc.get("products", []) or []
        if isinstance(p, dict) and p.get("config_string")
    }
    manual_yamls = {
        c.get("product_yaml")
        for c in manual_doc.get("candidates", []) or []
        if isinstance(c, dict)
    }

    targets = manifest.get("targets")
    if not isinstance(targets, list) or not targets:
        errors.append("targets must be a non-empty array")
        return errors

    totals = manifest.get("totals", {})
    if isinstance(totals, dict) and totals.get("targets") not in (None, len(targets)):
        errors.append(
            f"totals.targets {totals.get('targets')!r} does not match the "
            f"number of targets ({len(targets)})"
        )

    seen_ids: Dict[str, int] = {}
    stable_count = 0

    for idx, target in enumerate(targets, start=1):
        if not isinstance(target, dict):
            errors.append(f"target #{idx}: must be a JSON object")
            continue

        terr: List[str] = []
        tid = target.get("target_id", f"#{idx}")

        for field in REQUIRED_TARGET_FIELDS:
            if field not in target:
                terr.append(f"target {tid!r}: missing required field {field!r}")

        if target.get("target_id"):
            if target["target_id"] in seen_ids:
                terr.append(
                    f"target {tid!r}: duplicate target_id (also at "
                    f"#{seen_ids[target['target_id']]})"
                )
            else:
                seen_ids[target["target_id"]] = idx

        cs = target.get("config_string", "")
        tier = target.get("channel_tier")
        build_channel = target.get("build_channel")
        version = target.get("version", "")
        lane = target.get("delivery_lane")
        elig = target.get("webflash_import_eligibility", {})
        pub = target.get("publication_status")

        yaml_path = target.get("yaml_path", "")
        if yaml_path and not (REPO_ROOT / yaml_path).is_file():
            terr.append(f"target {tid!r}: yaml_path not found: {yaml_path}")

        if tier not in tiers:
            terr.append(
                f"target {tid!r}: channel_tier {tier!r} is not a known policy tier"
            )
        else:
            expected_build_channel = policy_mapping.get(tier)
            if build_channel != expected_build_channel:
                terr.append(
                    f"target {tid!r}: build_channel {build_channel!r} must be "
                    f"{expected_build_channel!r} for tier {tier!r}"
                )
        if build_channel not in allowed_channels:
            terr.append(
                f"target {tid!r}: build_channel {build_channel!r} is not an "
                f"allowed WebFlash channel {sorted(allowed_channels)}"
            )

        # Artifact name is exactly Sense360-{cs}-v{version}-{build_channel}.bin.
        expected_artifact = f"Sense360-{cs}-v{version}-{build_channel}.bin"
        if target.get("expected_artifact_name") != expected_artifact:
            terr.append(
                f"target {tid!r}: expected_artifact_name "
                f"{target.get('expected_artifact_name')!r} must be "
                f"{expected_artifact!r}"
            )
        match = _ARTIFACT_RE.match(target.get("expected_artifact_name", ""))
        if not match:
            terr.append(
                f"target {tid!r}: expected_artifact_name does not match the "
                "Sense360-<config>-v<x.y.z>-<channel>.bin pattern"
            )
        elif match.group(1) != cs:
            terr.append(
                f"target {tid!r}: artifact config {match.group(1)!r} does not "
                f"match config_string {cs!r}"
            )

        if lane not in DELIVERY_LANES:
            terr.append(
                f"target {tid!r}: delivery_lane {lane!r} not in "
                f"{sorted(DELIVERY_LANES)}"
            )

        if not isinstance(elig, dict) or "eligible" not in elig:
            terr.append(
                f"target {tid!r}: webflash_import_eligibility must be an object "
                "with an 'eligible' boolean"
            )
            elig = {}

        # No fake evidence anywhere.
        if target.get("bench_evidence_claimed") is not False:
            terr.append(f"target {tid!r}: bench_evidence_claimed must be false")
        if target.get("schematic_status_verified_claim") is not False:
            terr.append(
                f"target {tid!r}: schematic_status_verified_claim must be false"
            )

        is_preview = target.get("is_preview_target")
        if is_preview != (tier != "stable"):
            terr.append(
                f"target {tid!r}: is_preview_target must be "
                f"{tier != 'stable'} for tier {tier!r}"
            )

        if tier == "stable":
            stable_count += 1
            if target.get("warning_copy_required") is not False:
                terr.append(
                    f"target {tid!r}: stable target must not require warning copy"
                )
        else:
            # Preview / advanced-preview invariants.
            if target.get("warning_copy_required") is not True:
                terr.append(f"target {tid!r}: preview target must require warning copy")
            key = target.get("warning_copy_key")
            if key not in policy_warning:
                terr.append(
                    f"target {tid!r}: warning_copy_key {key!r} does not resolve "
                    "in warning_copy"
                )
            elif target.get("release_note_warning") != policy_warning[key]:
                terr.append(
                    f"target {tid!r}: release_note_warning must equal the "
                    f"warning_copy[{key!r}] text"
                )
            for flag in (
                "recommended",
                "customer_default",
                "required_config",
                "customer_kit_default",
            ):
                if target.get(flag) is not False:
                    terr.append(
                        f"target {tid!r}: preview target must have {flag}=false"
                    )
            if not target.get("stable_blocker"):
                terr.append(
                    f"target {tid!r}: preview target must record a stable_blocker"
                )

        # Fan / TRIAC rules.
        tokens = cs.split("-")
        has_fan_token = any(t in tokens for t in FAN_DRIVER_TOKENS)
        if target.get("is_fan") != has_fan_token:
            terr.append(
                f"target {tid!r}: is_fan={target.get('is_fan')!r} disagrees with "
                f"config_string tokens {tokens}"
            )
        if target.get("is_triac") != ("FanTRIAC" in tokens):
            terr.append(f"target {tid!r}: is_triac disagrees with config_string tokens")

        if target.get("is_triac"):
            if tier != "advanced-preview":
                terr.append(
                    f"target {tid!r}: TRIAC must be advanced-preview, got {tier!r}"
                )
            if target.get("warning_copy_key") != "advanced-preview":
                terr.append(
                    f"target {tid!r}: TRIAC must use the advanced-preview warning"
                )
            if elig.get("exposure_class") != "acknowledgement-gated-advanced":
                terr.append(
                    f"target {tid!r}: TRIAC exposure_class must be "
                    "acknowledgement-gated-advanced"
                )
            if elig.get("eligible") is not False:
                terr.append(f"target {tid!r}: TRIAC must not be WebFlash-importable")
            if lane != "advanced-manual-preview":
                terr.append(
                    f"target {tid!r}: TRIAC delivery_lane must be "
                    "'advanced-manual-preview' (no longer 'blocked'; preview is "
                    "allowed, only the HW-005 buildability blocker stops a cut)"
                )
            if not target.get("build_blocker"):
                terr.append(f"target {tid!r}: TRIAC must record a build_blocker")
        elif target.get("is_fan"):
            # Non-TRIAC fan driver: manual-preview lane (releasable preview
            # artifact; WebFlash import gated until the WebFlash warning UX is
            # ready, so still not WebFlash-importable here).
            if lane != "manual-preview":
                terr.append(
                    f"target {tid!r}: fan-driver delivery_lane must be "
                    "'manual-preview'"
                )
            if elig.get("eligible") is not False:
                terr.append(
                    f"target {tid!r}: fan-driver target must not be "
                    "WebFlash-importable"
                )
            if yaml_path not in manual_yamls:
                terr.append(
                    f"target {tid!r}: fan-driver yaml_path {yaml_path!r} is not a "
                    "candidate in config/manual-firmware-artifacts.json"
                )
            cat = catalog_by_cs.get(cs)
            if cat is not None and cat.get("webflash_build_matrix") is not False:
                terr.append(
                    f"target {tid!r}: catalog webflash_build_matrix must stay "
                    "false for a fan-driver target"
                )

        # WebFlash lane: publication vs the build ledger.
        in_builds = cs in builds_by_cs
        if lane == "webflash":
            if has_fan_token:
                terr.append(
                    f"target {tid!r}: webflash lane target must not carry a fan "
                    "token (fan drivers use the manual-preview / "
                    "advanced-manual-preview lanes, not webflash)"
                )
            if pub in LEDGER_PRESENT_STATUSES:
                if not in_builds:
                    terr.append(
                        f"target {tid!r}: publication_status {pub!r} but "
                        "config_string is not in config/webflash-builds.json"
                    )
                else:
                    build = builds_by_cs[cs]
                    if build.get("channel") != build_channel:
                        terr.append(
                            f"target {tid!r}: webflash-builds channel "
                            f"{build.get('channel')!r} != build_channel "
                            f"{build_channel!r}"
                        )
                    if build.get("artifact_name") != target.get(
                        "expected_artifact_name"
                    ):
                        terr.append(
                            f"target {tid!r}: webflash-builds artifact_name "
                            "disagrees with expected_artifact_name"
                        )
            else:
                if in_builds:
                    terr.append(
                        f"target {tid!r}: publication_status {pub!r} but the "
                        "config_string IS already in config/webflash-builds.json"
                    )
                if not target.get("build_blocker"):
                    terr.append(
                        f"target {tid!r}: unpublished webflash target must record "
                        "a build_blocker"
                    )
        else:
            # manual-preview / advanced-manual-preview lanes are non-WebFlash
            # preview delivery lanes and must never be in the WebFlash build
            # ledger (config/webflash-builds.json stays the sole WebFlash
            # release-eligibility source of truth).
            if in_builds:
                terr.append(
                    f"target {tid!r}: delivery_lane {lane!r} but config_string is "
                    "in config/webflash-builds.json"
                )

        if terr:
            errors.extend(terr)

    if stable_count != 1:
        errors.append(
            f"exactly one stable baseline target is expected; found {stable_count}"
        )

    # Coverage: every committed build is represented.
    target_cs = {t.get("config_string") for t in targets if isinstance(t, dict)}
    for cs in builds_by_cs:
        if cs not in target_cs:
            errors.append(
                f"config/webflash-builds.json build {cs!r} is not represented in "
                "the preview-release-targets manifest"
            )

    # Coverage: every non-stable policy matrix row is represented with the same
    # intended channel and artifact name.
    target_by_cs: Dict[str, Dict[str, Any]] = {}
    for t in targets:
        if isinstance(t, dict) and t.get("config_string"):
            target_by_cs.setdefault(t["config_string"], t)
    for row in policy.get("preview_release_matrix", []) or []:
        if row.get("intended_channel") == "stable":
            continue
        rcs = row.get("config_string")
        match = target_by_cs.get(rcs)
        if match is None:
            errors.append(f"policy preview row {rcs!r} has no target in the manifest")
            continue
        if match.get("channel_tier") != row.get("intended_channel"):
            errors.append(
                f"policy preview row {rcs!r}: intended_channel "
                f"{row.get('intended_channel')!r} != manifest channel_tier "
                f"{match.get('channel_tier')!r}"
            )
        if match.get("expected_artifact_name") != row.get("expected_artifact_name"):
            errors.append(
                f"policy preview row {rcs!r}: expected_artifact_name disagrees "
                "with the manifest"
            )

    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        default=True,
        help="Validate manifest metadata and cross-references (default).",
    )
    parser.parse_args(argv)

    manifest = _load_json(MANIFEST_PATH)
    policy = _load_json(POLICY_PATH)
    compat = _load_json(COMPAT_PATH)
    builds_doc = _load_json(BUILDS_PATH)
    catalog_doc = _load_json(CATALOG_PATH)
    manual_doc = _load_json(MANUAL_PATH)

    print("🔍 Validating preview release-target manifest...\n")
    targets = manifest.get("targets", []) or []
    print(
        f"Read {len(targets)} target(s) from "
        f"{MANIFEST_PATH.relative_to(REPO_ROOT)}."
    )

    errors = validate(manifest, policy, compat, builds_doc, catalog_doc, manual_doc)
    if errors:
        print(f"\nMetadata errors ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    print("✅ Preview release-target manifest validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
