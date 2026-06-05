#!/usr/bin/env python3
"""Validate the fan-control / TRIAC preview build-row ledger.

RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001.

This script consumes ``config/preview-fan-triac-build-rows.json`` — the
concrete build-row ledger for the four buildable fan-control and TRIAC
PREVIEW / advanced-preview release targets delivered on the NON-WebFlash
preview lanes (``manual-preview`` for FanRelay / FanPWM / FanDAC,
``advanced-manual-preview`` for FanTRIAC) — and asserts that it stays
consistent with the canonical sources without ever publishing a preview
artifact, adding a ``config/webflash-builds.json`` row, flipping a
``config/product-catalog.json`` status, promoting anything to stable, or
claiming any bench / compliance / hardware proof. FanTRIAC carries
firmware-build compile proof only (TRIAC-UNBLOCK-BUILD-001 cleared its HW-005
buildability blocker); no row claims bench / compliance / hardware proof.

Cross-references enforced (metadata only):

  * exactly the four expected config strings are present (no extras / dups);
  * every row's ``product_yaml`` and ``release_note_draft`` exist on disk;
  * every row agrees with its ``config/preview-release-targets.json`` target
    (by ``preview_release_target_id``) on config string, channel tier, build
    channel, version, delivery lane, warning-copy key, stable blocker, build
    blocker, expected artifact name, and the never-recommended / never-default
    / never-required posture;
  * every row's ``release_note_warning`` equals the policy ``warning_copy`` text
    for its key, and the artifact name is exactly
    ``Sense360-{config_string}-v{version}-{build_channel}.bin``;
  * no row's config string appears in ``config/webflash-builds.json`` (the fan /
    TRIAC tokens stay off the WebFlash build matrix);
  * every row's ``commercial_posture`` is hidden / not buyable / not
    recommended / not customer-default / not stable / not required-config;
  * FanRelay / FanPWM / FanDAC (manual-preview) reference a real candidate in
    ``config/manual-firmware-artifacts.json`` whose ``product_yaml`` matches,
    carry no build blocker, are buildable now, and cite firmware-build compile
    evidence (run ``26821900127``);
  * FanTRIAC (advanced-manual-preview) has its HW-005 build blocker cleared
    (TRIAC-UNBLOCK-BUILD-001; build_blocker null), is buildable now, carries a
    firmware-build compile_evidence object (result success), keeps COMPLIANCE-001
    in its stable_blocker, and uses the ``acknowledgement-gated-advanced``
    exposure class;
  * every manual-firmware-artifacts candidate is represented here as a
    manual-preview row.

This is a CI validation lane only; it builds nothing and changes nothing.

Run with::

    python3 scripts/validate_preview_fan_triac_build_rows.py --metadata-only

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
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
TARGETS_PATH = REPO_ROOT / "config" / "preview-release-targets.json"
POLICY_PATH = REPO_ROOT / "config" / "release-channel-policy.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"

LEDGER_ID = "RELEASE-PREVIEW-FAN-TRIAC-BUILD-ROWS-001"
COMPILE_RUN_ID = 26821900127

EXPECTED_CONFIGS = frozenset(
    {
        "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
        "Ceiling-POE-FanPWM",
        "Ceiling-POE-FanDAC",
        "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
    }
)
SIMPLE_INSTALL_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
SIMPLE_INSTALL_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
LAUNCH_SKU = "S360-KIT-BATH-P"

FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

REQUIRED_ROW_FIELDS = (
    "config_string",
    "family",
    "sku",
    "preview_release_target_id",
    "manual_lane_candidate_id",
    "product_yaml",
    "channel_tier",
    "build_channel",
    "version",
    "delivery_lane",
    "expected_preview_artifact_name",
    "webflash_importable",
    "webflash_exposure_class",
    "warning_copy_key",
    "release_note_warning",
    "release_note_draft",
    "stable_blocker",
    "build_blocker",
    "buildable_now",
    "compile_evidence",
    "commercial_posture",
    "consuming_bundles",
)

SCOPE_MUST_BE_FALSE = (
    "publishes_artifacts",
    "creates_github_release",
    "creates_tag",
    "commits_bin",
    "touches_webflash_repo",
    "writes_firmware_sources_or_manifest",
    "adds_webflash_builds_entries",
    "flips_product_catalog_status",
    "marks_any_product_stable",
    "marks_any_product_recommended_or_default",
    "exposes_candidate_bundles_buyable",
    "changes_simple_install",
    "changes_launch_sku",
    "claims_hardware_proof",
    "claims_bench_evidence",
    "claims_compliance",
    "claims_triac_safety_or_compliance_proof",
)

POSTURE_MUST_BE_FALSE = (
    "buyable",
    "recommended",
    "customer_default",
    "stable",
    "release_one_required_config",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(
    ledger: Dict[str, Any],
    targets_doc: Dict[str, Any],
    policy: Dict[str, Any],
    builds_doc: Dict[str, Any],
    manual_doc: Dict[str, Any],
) -> List[str]:
    """Return a list of error strings (empty == valid)."""
    errors: List[str] = []

    if ledger.get("schema_version") != 1:
        errors.append(
            f"schema_version must be 1; got {ledger.get('schema_version')!r}"
        )
    if ledger.get("id") != LEDGER_ID:
        errors.append(f"id must be {LEDGER_ID!r}; got {ledger.get('id')!r}")

    # Scope guardrails: build-row metadata only.
    scope = ledger.get("scope", {})
    if not isinstance(scope, dict):
        errors.append("scope must be an object")
        scope = {}
    for flag in SCOPE_MUST_BE_FALSE:
        if scope.get(flag) is not False:
            errors.append(f"scope.{flag} must be false")

    # Simple install is the stable Bathroom PoE build, unchanged.
    simple = ledger.get("simple_install", {})
    if simple.get("config_string") != SIMPLE_INSTALL_CONFIG:
        errors.append("simple_install.config_string must be the stable Bathroom config")
    if simple.get("artifact_name") != SIMPLE_INSTALL_ARTIFACT:
        errors.append("simple_install.artifact_name must be the stable Bathroom artifact")
    if simple.get("launch_sku") != LAUNCH_SKU:
        errors.append(f"simple_install.launch_sku must be {LAUNCH_SKU!r}")
    if simple.get("channel") != "stable":
        errors.append("simple_install.channel must be 'stable'")

    targets_by_id = {
        t.get("target_id"): t
        for t in targets_doc.get("targets", []) or []
        if isinstance(t, dict) and t.get("target_id")
    }
    warning_copy = policy.get("warning_copy", {})
    builds_cs = {
        b.get("config_string")
        for b in builds_doc.get("builds", []) or []
        if isinstance(b, dict)
    }
    manual_by_id = {
        c.get("id"): c
        for c in manual_doc.get("candidates", []) or []
        if isinstance(c, dict) and c.get("id")
    }

    rows = ledger.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows must be a non-empty array")
        return errors

    totals = ledger.get("totals", {})
    if isinstance(totals, dict) and totals.get("rows") not in (None, len(rows)):
        errors.append(
            f"totals.rows {totals.get('rows')!r} does not match the number of "
            f"rows ({len(rows)})"
        )

    seen_cs: Dict[str, int] = {}
    referenced_candidates: set[str] = set()

    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            errors.append(f"row #{idx}: must be a JSON object")
            continue
        rid = row.get("config_string", f"#{idx}")
        rerr: List[str] = []

        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                rerr.append(f"row {rid!r}: missing required field {field!r}")

        cs = row.get("config_string", "")
        if cs not in EXPECTED_CONFIGS:
            rerr.append(f"row {rid!r}: unexpected config_string {cs!r}")
        if cs in seen_cs:
            rerr.append(f"row {rid!r}: duplicate config_string (also at #{seen_cs[cs]})")
        else:
            seen_cs[cs] = idx

        version = row.get("version", "")
        build_channel = row.get("build_channel")
        lane = row.get("delivery_lane")
        key = row.get("warning_copy_key")
        tokens = cs.split("-")
        is_triac = "FanTRIAC" in tokens

        # product_yaml + release_note_draft exist on disk.
        py = row.get("product_yaml", "")
        if py and not (REPO_ROOT / py).is_file():
            rerr.append(f"row {rid!r}: product_yaml not found: {py}")
        draft = row.get("release_note_draft", "")
        if draft and not (REPO_ROOT / draft).is_file():
            rerr.append(f"row {rid!r}: release_note_draft not found: {draft}")

        # Artifact name shape.
        expected_artifact = f"Sense360-{cs}-v{version}-{build_channel}.bin"
        if row.get("expected_preview_artifact_name") != expected_artifact:
            rerr.append(
                f"row {rid!r}: expected_preview_artifact_name "
                f"{row.get('expected_preview_artifact_name')!r} must be "
                f"{expected_artifact!r}"
            )
        if build_channel != "preview":
            rerr.append(
                f"row {rid!r}: build_channel must be 'preview' (got {build_channel!r})"
            )

        # Warning copy matches the policy verbatim.
        if key not in warning_copy:
            rerr.append(f"row {rid!r}: warning_copy_key {key!r} not in policy warning_copy")
        elif row.get("release_note_warning") != warning_copy[key]:
            rerr.append(
                f"row {rid!r}: release_note_warning must equal policy "
                f"warning_copy[{key!r}]"
            )

        # Never WebFlash-importable; never in the WebFlash build ledger.
        if row.get("webflash_importable") is not False:
            rerr.append(f"row {rid!r}: webflash_importable must be false")
        if cs in builds_cs:
            rerr.append(
                f"row {rid!r}: config_string is in config/webflash-builds.json; "
                "fan / TRIAC tokens must stay off the WebFlash build matrix"
            )

        # Commercial posture locked.
        posture = row.get("commercial_posture", {})
        if not isinstance(posture, dict):
            rerr.append(f"row {rid!r}: commercial_posture must be an object")
            posture = {}
        if posture.get("visibility") != "hidden":
            rerr.append(f"row {rid!r}: commercial_posture.visibility must be 'hidden'")
        for flag in POSTURE_MUST_BE_FALSE:
            if posture.get(flag) is not False:
                rerr.append(f"row {rid!r}: commercial_posture.{flag} must be false")

        if row.get("consuming_bundles") not in ([], None):
            if row.get("consuming_bundles") != []:
                rerr.append(
                    f"row {rid!r}: consuming_bundles must be empty (fan / TRIAC "
                    "targets feed no room bundle)"
                )

        # Cross-check against the canonical preview-release-targets manifest.
        tid = row.get("preview_release_target_id")
        target = targets_by_id.get(tid)
        if target is None:
            rerr.append(
                f"row {rid!r}: preview_release_target_id {tid!r} not found in "
                "config/preview-release-targets.json"
            )
        else:
            for fld, lfld in (
                ("config_string", "config_string"),
                ("channel_tier", "channel_tier"),
                ("build_channel", "build_channel"),
                ("version", "version"),
                ("delivery_lane", "delivery_lane"),
                ("warning_copy_key", "warning_copy_key"),
                ("stable_blocker", "stable_blocker"),
                ("build_blocker", "build_blocker"),
            ):
                if row.get(lfld) != target.get(fld):
                    rerr.append(
                        f"row {rid!r}: {lfld} disagrees with preview-release-targets "
                        f"target {tid!r} ({row.get(lfld)!r} != {target.get(fld)!r})"
                    )
            if target.get("expected_artifact_name") != row.get(
                "expected_preview_artifact_name"
            ):
                rerr.append(
                    f"row {rid!r}: expected_preview_artifact_name disagrees with "
                    "the preview-release-targets artifact name"
                )
            for flag in (
                "recommended",
                "customer_default",
                "required_config",
                "customer_kit_default",
            ):
                if target.get(flag) is not False:
                    rerr.append(
                        f"row {rid!r}: preview-release-targets target must have "
                        f"{flag}=false"
                    )
            # Fans are preview / manual-preview WebFlash-import ELIGIBLE
            # (RELEASE-PREVIEW-FAN-WEBFLASH-ELIGIBILITY-001); TRIAC stays gated.
            # This is the import-eligibility dimension only -- the ledger row's own
            # webflash_importable stays false (no committed webflash-builds.json row;
            # checked above).
            expected_eligible = False if is_triac else True
            target_eligible = target.get("webflash_import_eligibility", {}).get(
                "eligible"
            )
            if target_eligible is not expected_eligible:
                rerr.append(
                    f"row {rid!r}: preview-release-targets target "
                    f"webflash_import_eligibility.eligible must be {expected_eligible} "
                    f"({'TRIAC stays gated' if is_triac else 'fans are preview / manual-preview WebFlash-import eligible'})"
                )

        # Lane-specific rules.
        if is_triac:
            if lane != "advanced-manual-preview":
                rerr.append(f"row {rid!r}: TRIAC delivery_lane must be advanced-manual-preview")
            if row.get("channel_tier") != "advanced-preview":
                rerr.append(f"row {rid!r}: TRIAC channel_tier must be advanced-preview")
            if key != "advanced-preview":
                rerr.append(f"row {rid!r}: TRIAC warning_copy_key must be advanced-preview")
            if row.get("webflash_exposure_class") != "acknowledgement-gated-advanced":
                rerr.append(
                    f"row {rid!r}: TRIAC webflash_exposure_class must be "
                    "acknowledgement-gated-advanced"
                )
            if row.get("manual_lane_candidate_id") is not None:
                rerr.append(
                    f"row {rid!r}: TRIAC must not be a manual-firmware-artifacts "
                    "candidate (it is delivered on the advanced-manual-preview "
                    "lane, not the manual-preview CI build lane)"
                )
            # TRIAC-UNBLOCK-BUILD-001: the HW-005 BUILDABILITY blocker is
            # resolved (SX1509-free Core respin routes TRI_GPIO1/2 direct to
            # IO14/IO13, corrected by TRIAC-PINMAP-CORRECT-001). build_blocker
            # is cleared, the target is buildable, and
            # it carries firmware-build compile evidence. Stable stays gated by
            # COMPLIANCE-001 (+ PACKAGE-TRIAC-001), recorded in stable_blocker.
            if row.get("build_blocker") is not None:
                rerr.append(
                    f"row {rid!r}: TRIAC build_blocker must be null "
                    "(HW-005 buildability resolved by TRIAC-UNBLOCK-BUILD-001)"
                )
            if row.get("buildable_now") is not True:
                rerr.append(f"row {rid!r}: TRIAC buildable_now must be true")
            ev = row.get("compile_evidence")
            if not isinstance(ev, dict):
                rerr.append(
                    f"row {rid!r}: TRIAC must carry a compile_evidence object "
                    "(buildable, compile-validated)"
                )
            else:
                if ev.get("result") != "success":
                    rerr.append(
                        f"row {rid!r}: TRIAC compile_evidence.result must be success"
                    )
                if ev.get("proof_class") != "firmware-build-only":
                    rerr.append(
                        f"row {rid!r}: TRIAC compile_evidence.proof_class must be "
                        "firmware-build-only"
                    )
            if "COMPLIANCE-001" not in str(row.get("stable_blocker") or ""):
                rerr.append(
                    f"row {rid!r}: TRIAC stable_blocker must still cite COMPLIANCE-001"
                )
        else:
            if lane != "manual-preview":
                rerr.append(f"row {rid!r}: fan-driver delivery_lane must be manual-preview")
            if row.get("channel_tier") != "preview":
                rerr.append(f"row {rid!r}: fan-driver channel_tier must be preview")
            if key != "preview":
                rerr.append(f"row {rid!r}: fan-driver warning_copy_key must be preview")
            if row.get("webflash_exposure_class") is not None:
                rerr.append(f"row {rid!r}: fan-driver webflash_exposure_class must be null")
            if row.get("build_blocker") is not None:
                rerr.append(f"row {rid!r}: fan-driver build_blocker must be null")
            if row.get("buildable_now") is not True:
                rerr.append(f"row {rid!r}: fan-driver buildable_now must be true")
            # Manual-lane candidate cross-reference.
            cand_id = row.get("manual_lane_candidate_id")
            if not cand_id:
                rerr.append(
                    f"row {rid!r}: manual-preview row must reference a "
                    "manual_lane_candidate_id"
                )
            else:
                referenced_candidates.add(cand_id)
                cand = manual_by_id.get(cand_id)
                if cand is None:
                    rerr.append(
                        f"row {rid!r}: manual_lane_candidate_id {cand_id!r} not in "
                        "config/manual-firmware-artifacts.json candidates"
                    )
                elif cand.get("product_yaml") != py:
                    rerr.append(
                        f"row {rid!r}: manual candidate {cand_id!r} product_yaml "
                        f"{cand.get('product_yaml')!r} != row product_yaml {py!r}"
                    )
            # Firmware-build compile evidence.
            ev = row.get("compile_evidence")
            if not isinstance(ev, dict):
                rerr.append(f"row {rid!r}: fan-driver must carry a compile_evidence object")
            else:
                if ev.get("run_id") != COMPILE_RUN_ID:
                    rerr.append(
                        f"row {rid!r}: compile_evidence.run_id must be {COMPILE_RUN_ID}"
                    )
                if ev.get("proof_class") != "firmware-build-only":
                    rerr.append(
                        f"row {rid!r}: compile_evidence.proof_class must be "
                        "firmware-build-only"
                    )
                if ev.get("result") != "success":
                    rerr.append(f"row {rid!r}: compile_evidence.result must be success")

        errors.extend(rerr)

    # Coverage: exactly the four expected config strings.
    missing = EXPECTED_CONFIGS - set(seen_cs)
    if missing:
        errors.append("missing build rows for: " + ", ".join(sorted(missing)))

    # Every manual-firmware-artifacts candidate is represented as a row.
    for cand_id in manual_by_id:
        if cand_id not in referenced_candidates:
            errors.append(
                f"manual-firmware-artifacts candidate {cand_id!r} is not represented "
                "as a manual-preview build row"
            )

    return errors


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        default=True,
        help="Validate ledger metadata and cross-references (default).",
    )
    parser.parse_args(argv)

    ledger = _load_json(LEDGER_PATH)
    targets_doc = _load_json(TARGETS_PATH)
    policy = _load_json(POLICY_PATH)
    builds_doc = _load_json(BUILDS_PATH)
    manual_doc = _load_json(MANUAL_PATH)

    print("🔍 Validating fan-control / TRIAC preview build-row ledger...\n")
    rows = ledger.get("rows", []) or []
    print(f"Read {len(rows)} build row(s) from {LEDGER_PATH.relative_to(REPO_ROOT)}.")

    errors = validate(ledger, targets_doc, policy, builds_doc, manual_doc)
    if errors:
        print(f"\nMetadata errors ({len(errors)}):")
        for error in errors:
            print(f"  ❌ {error}")
        return 1

    print("✅ Fan-control / TRIAC preview build-row ledger validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
