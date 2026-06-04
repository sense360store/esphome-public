#!/usr/bin/env python3
"""Validate and drive the room-bundle fan-control preview publish workflow.

ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001 (queued by ROOM-BUNDLE-FAN-PUBLISH-PLAN-001;
the eventual run is ROOM-BUNDLE-FAN-PUBLISH-RUN-001).

This is the additive sibling of ``scripts/validate_manual_preview_fan_publish.py``
(RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001). That validator is hard-scoped to the
**three single-driver** manual-preview fan rows in
``config/preview-fan-triac-build-rows.json`` and cites compile run
``26821900127``. THIS validator covers the **five full-composition room-bundle**
fan-control configs that carry hosted full ESPHome compile proof from the OTHER
compile run, ``26913592989`` (``ROOM-BUNDLE-FAN-COMPILE-RESULTS-001``):

    Ceiling-POE-VentIQ-FanPWM-RoomIQ
    Ceiling-POE-VentIQ-FanDAC-RoomIQ
    Ceiling-POE-AirIQ-FanRelay-RoomIQ
    Ceiling-POE-AirIQ-FanDAC-RoomIQ
    Ceiling-POE-AirIQ-FanPWM-RoomIQ

It reads ``config/room-bundle-fan-variants.json`` (the canonical source of truth)
plus ``config/compile-only-targets.json`` (the compile-evidence ledger) and never
reads ``config/webflash-builds.json`` as a matrix source — it only confirms the
five (and any fan token) stay OUT of that WebFlash release-eligibility ledger.

The five publish to the shared ``v1.0.0-preview`` preview release
(RELEASE-PREVIEW-FAN-SHARED-TAG-001) and reuse the tag confirm-gate
(RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001): the shared release is the
frictionless default and any OTHER tag needs ``--confirm-tag-override true`` so an
accidental dispatch to the wrong tag fails fast.

Hard invariants enforced here:
  * scope is EXACTLY the five compile-validated room-bundle fan configs;
  * each cites compile run ``26913592989`` and ``proof_scope: firmware-build-only``;
  * the two FanDAC configs carry the GP8403 IC1 ``0x58`` / IC2 ``0x5A`` requirement
    (``0x59`` forbidden — SGP41 collision) and the pending ``FANDAC-I2C-ADDR-001``
    bench verification;
  * TRIAC (``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ``) is excluded (``HW-005``);
  * nothing is stable / recommended / customer-default / buyable; and
  * no WebFlash build row is added for any of the five (fan-token guardrail).

This helper is metadata-only unless the GitHub Actions workflow calls it to print
a matrix, build a release body, validate an output directory, or validate the
release tag. It NEVER publishes firmware, creates a Release/tag, or writes
``manifest.json`` / ``firmware/sources.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
VARIANTS_PATH = REPO_ROOT / "config" / "room-bundle-fan-variants.json"
COMPILE_TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

DEFAULT_VERSION = "1.0.0"
DEFAULT_CHANNEL = "preview"
ALL_TARGETS = "all-room-bundle-fan-previews"

# RELEASE-PREVIEW-FAN-SHARED-TAG-001: every preview artifact (room-bundle + LED +
# fan) lives in the single shared v1.0.0-preview preview release. There is no
# dedicated room-bundle-fan tag.
EXPECTED_RELEASE_TAG = "v1.0.0-preview"
SHARED_PREVIEW_RELEASE_TAG = EXPECTED_RELEASE_TAG

WORKFLOW_ID = "ROOM-BUNDLE-FAN-PUBLISH-WORKFLOW-001"
RUN_ID = "ROOM-BUNDLE-FAN-PUBLISH-RUN-001"
PLAN_ID = "ROOM-BUNDLE-FAN-PUBLISH-PLAN-001"
COMPILE_RESULTS_ID = "ROOM-BUNDLE-FAN-COMPILE-RESULTS-001"
# The tag confirm-gate is shared with the single-driver manual-preview fan
# publish workflow; this workflow reuses that gate rather than inventing a new one.
TAG_GUARD_ID = "RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001"

# The compile run that validated THESE five room-bundle configs. Distinct from
# the single-driver lane's run (26821900127).
EXPECTED_COMPILE_RUN_ID = 26913592989

# The publish delivery lane (Advanced-install-only preview). The SOURCE delivery
# lane recorded per-variant is "room-bundle-preview-compile-validated".
PUBLISH_DELIVERY_LANE = "manual-preview"
SOURCE_DELIVERY_LANE = "room-bundle-preview-compile-validated"
EXPECTED_PROOF_SCOPE = "firmware-build-only"
EXPECTED_VARIANT_STATUS = "buildable-preview-compile-validated"
EXPECTED_PREVIEW_STATUS = "preview-compile-validated"
EXPECTED_COMPILE_STATUS = "validated-full-compile"
EXPECTED_CATALOG_STATUS = "hardware-pending"

# Scope: exactly these five, in the canonical order of the compile-results record.
ROOM_BUNDLE_FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanPWM-RoomIQ",
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanRelay-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanPWM-RoomIQ",
)
# The two FanDAC configs that carry the IC2 0x5A address override.
FANDAC_CONFIGS = (
    "Ceiling-POE-VentIQ-FanDAC-RoomIQ",
    "Ceiling-POE-AirIQ-FanDAC-RoomIQ",
)
# TRIAC is out of scope (HW-005, build-blocked, no compile proof, no .bin).
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

# FanDAC GP8403 I2C address policy (FANDAC-I2C-ADDR-001 stays pending).
FANDAC_IC1 = "0x58"
FANDAC_IC2 = "0x5A"
FANDAC_FORBIDDEN = "0x59"
FANDAC_BENCH_FOLLOWUP = "FANDAC-I2C-ADDR-001"

# Commercial-posture flags that must be false for every selected config — a
# preview publish must never claim stable / recommended / default / buyable / proof.
POSTURE_FALSE_FIELDS = (
    "recommended",
    "customer_default",
    "buyable",
    "bench_evidence_claimed",
    "compliance_claimed",
)

# The exact preview artifact filenames the run must produce at version 1.0.0.
EXPECTED_PREVIEW_ARTIFACTS = tuple(
    f"Sense360-{cs}-v{DEFAULT_VERSION}-{DEFAULT_CHANNEL}.bin"
    for cs in ROOM_BUNDLE_FAN_CONFIGS
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def _artifact_name(config_string: str, version: str, channel: str) -> str:
    return f"Sense360-{config_string}-v{version}-{channel}.bin"


def _validate_release_tag(
    release_tag: str, *, confirm_override: bool = False
) -> List[str]:
    """Confirm-gate any release tag other than the shared preview release.

    RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001 (shared with the single-driver
    manual-preview fan publish workflow). The room-bundle fan artifacts publish to
    the shared ``v1.0.0-preview`` preview release by default, and that default is
    frictionless. Targeting any OTHER tag is allowed only with ``confirm_override``
    so an accidental dispatch to the wrong tag (a typo, the stable release, or a
    stray new release) fails fast instead of creating / overwriting the wrong
    release.

    Returns a list of error strings (empty == the tag is allowed).
    """
    errors: List[str] = []
    tag = (release_tag or "").strip()
    if not tag:
        errors.append("release_tag must not be empty")
        return errors
    if tag == EXPECTED_RELEASE_TAG:
        return errors
    if not confirm_override:
        errors.append(
            f"release_tag {tag!r} is not the shared preview release "
            f"{EXPECTED_RELEASE_TAG!r}; set confirm_tag_override=true to publish "
            f"the room-bundle fan preview artifacts to a different release tag "
            f"({TAG_GUARD_ID})"
        )
    return errors


def _variants_by_config(variants_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        v.get("intended_firmware_config_string"): v
        for v in variants_doc.get("fan_variant_candidates", []) or []
        if isinstance(v, dict) and v.get("intended_firmware_config_string")
    }


def _compile_target_for(
    compile_doc: Dict[str, Any], config_string: str, run_id: int
) -> Optional[Dict[str, Any]]:
    """Return the compile-only target whose config_string matches AND whose
    compile evidence cites ``run_id``.

    Several config strings appear more than once in the compile-only ledger (e.g.
    a skeleton + a top-level product YAML), so matching on the run id uniquely
    pins the room-bundle target rather than relying on dict last-wins.
    """
    for target in compile_doc.get("targets", []) or []:
        if not isinstance(target, dict):
            continue
        if target.get("config_string") != config_string:
            continue
        evidence = target.get("compile_evidence")
        if isinstance(evidence, dict) and evidence.get("run_id") == run_id:
            return target
    return None


def _webflash_config_strings(builds_doc: Dict[str, Any]) -> set[str]:
    return {
        b.get("config_string")
        for b in builds_doc.get("builds", []) or []
        if isinstance(b, dict) and b.get("config_string")
    }


def _validate_fandac_requirement(
    requirement: Optional[Dict[str, Any]], prefix: str
) -> List[str]:
    """Enforce the GP8403 IC2 0x5A address policy + pending bench follow-up."""
    errors: List[str] = []
    if not isinstance(requirement, dict):
        errors.append(prefix + "FanDAC fan_dac_address_requirement must be present")
        return errors
    if requirement.get("gp8403_ic1") != FANDAC_IC1:
        errors.append(prefix + f"FanDAC GP8403 IC1 must be {FANDAC_IC1}")
    if requirement.get("gp8403_ic2") != FANDAC_IC2:
        errors.append(prefix + f"FanDAC GP8403 IC2 must be {FANDAC_IC2}")
    if requirement.get("forbidden_gp8403_address") != FANDAC_FORBIDDEN:
        errors.append(
            prefix + f"FanDAC forbidden GP8403 address must be {FANDAC_FORBIDDEN}"
        )
    if requirement.get("sgp41") != FANDAC_FORBIDDEN:
        errors.append(prefix + f"FanDAC must record the SGP41 collision at {FANDAC_FORBIDDEN}")
    if requirement.get("bench_verification_followup") != FANDAC_BENCH_FOLLOWUP:
        errors.append(
            prefix + f"FanDAC bench follow-up must be {FANDAC_BENCH_FOLLOWUP}"
        )
    if requirement.get("bench_verification_status") != "pending":
        errors.append(
            prefix + "FanDAC bench_verification_status must stay 'pending' "
            "(no hardware verification claimed)"
        )
    return errors


def _select_rows(
    variants_doc: Dict[str, Any],
    compile_doc: Dict[str, Any],
    builds_doc: Dict[str, Any],
    *,
    version: str = DEFAULT_VERSION,
    release_target: str = ALL_TARGETS,
) -> tuple[List[Dict[str, Any]], List[str]]:
    errors: List[str] = []

    if variants_doc.get("schema_version") != 2:
        errors.append("room-bundle fan variants schema_version must be 2")
    if compile_doc.get("schema_version") != 1:
        errors.append("compile-only targets schema_version must be 1")

    variants = _variants_by_config(variants_doc)
    webflash_configs = _webflash_config_strings(builds_doc)

    # The document-level compile_results.validated_config_strings must be exactly
    # the five — this validator's scope is anchored to that recorded proof.
    validated = variants_doc.get("compile_results", {}).get(
        "validated_config_strings", []
    )
    if sorted(validated) != sorted(ROOM_BUNDLE_FAN_CONFIGS):
        errors.append(
            "compile_results.validated_config_strings must be exactly the five "
            "room-bundle fan configs"
        )

    # The document-level FanDAC address policy must match the enforced constants.
    policy = variants_doc.get("fan_dac_i2c_address_policy", {})
    required = policy.get("required_addresses_with_air_quality_module", {})
    if required.get("gp8403_ic1") != FANDAC_IC1 or required.get("gp8403_ic2") != FANDAC_IC2:
        errors.append("fan_dac_i2c_address_policy IC1/IC2 must be 0x58 / 0x5A")
    if required.get("forbidden_gp8403_address") != FANDAC_FORBIDDEN:
        errors.append("fan_dac_i2c_address_policy forbidden address must be 0x59")

    # TRIAC exclusion must be real: the variant exists and is build-blocked.
    triac = variants.get(TRIAC_CONFIG)
    if not triac:
        errors.append(f"TRIAC variant {TRIAC_CONFIG!r} missing; exclusion cannot be checked")
    else:
        if triac.get("firmware_config_status") != "defined-build-blocked":
            errors.append("TRIAC must stay firmware_config_status=defined-build-blocked")
        ev = triac.get("firmware_config_evidence", {})
        if ev.get("buildable_now") is not False:
            errors.append("TRIAC must stay buildable_now=false")
        if "HW-005" not in (ev.get("build_blocker") or ""):
            errors.append("TRIAC must carry the HW-005 build blocker")

    # Selection.
    selected_configs: Iterable[str]
    if release_target in ("", ALL_TARGETS):
        selected_configs = ROOM_BUNDLE_FAN_CONFIGS
    elif release_target in ROOM_BUNDLE_FAN_CONFIGS:
        selected_configs = (release_target,)
    elif release_target == TRIAC_CONFIG:
        errors.append(
            f"{TRIAC_CONFIG} is build-blocked by HW-005 and cannot be published"
        )
        selected_configs = ()
    else:
        errors.append(
            "release_target must be all-room-bundle-fan-previews or one of "
            + ", ".join(ROOM_BUNDLE_FAN_CONFIGS)
        )
        selected_configs = ()

    selected: List[Dict[str, Any]] = []
    for config_string in selected_configs:
        prefix = f"{config_string}: "
        variant = variants.get(config_string)
        if not variant:
            errors.append(prefix + "missing room-bundle fan variant")
            continue

        if not variant.get("firmware_config_exists"):
            errors.append(prefix + "firmware_config_exists must be true")
        if variant.get("firmware_config_status") != EXPECTED_VARIANT_STATUS:
            errors.append(
                prefix + f"firmware_config_status must be {EXPECTED_VARIANT_STATUS!r}"
            )
        # The build channel posture is preview (compile-validated). The publish
        # delivery lane is manual-preview (Advanced-install-only) — encoded by the
        # workflow / PUBLISH_DELIVERY_LANE constant, not a per-variant source field.
        if variant.get("preview_status") != EXPECTED_PREVIEW_STATUS:
            errors.append(
                prefix + f"preview_status must be {EXPECTED_PREVIEW_STATUS!r} (preview channel)"
            )
        if variant.get("webflash_exposed") is not False:
            errors.append(prefix + "webflash_exposed must be false")
        if variant.get("stable_status") != "blocked":
            errors.append(prefix + "stable_status must be blocked")
        if variant.get("commercial_availability") != "waitlist-only":
            errors.append(prefix + "commercial_availability must be waitlist-only")
        for field in POSTURE_FALSE_FIELDS:
            if variant.get(field) is not False:
                errors.append(prefix + f"{field} must be false")

        evidence = variant.get("firmware_config_evidence")
        if not isinstance(evidence, dict):
            errors.append(prefix + "firmware_config_evidence must be present")
            continue

        if evidence.get("compile_validation_status") != EXPECTED_COMPILE_STATUS:
            errors.append(
                prefix + f"compile_validation_status must be {EXPECTED_COMPILE_STATUS!r}"
            )
        if evidence.get("delivery_lane") != SOURCE_DELIVERY_LANE:
            errors.append(prefix + f"delivery_lane must be {SOURCE_DELIVERY_LANE!r}")
        if evidence.get("catalog_status") != EXPECTED_CATALOG_STATUS:
            errors.append(prefix + f"catalog_status must be {EXPECTED_CATALOG_STATUS!r}")

        compile_evidence = evidence.get("compile_evidence")
        if not isinstance(compile_evidence, dict):
            errors.append(prefix + "compile_evidence must be present")
        else:
            if compile_evidence.get("run_id") != EXPECTED_COMPILE_RUN_ID:
                errors.append(
                    prefix + f"compile_evidence.run_id must be {EXPECTED_COMPILE_RUN_ID}"
                )
            if compile_evidence.get("result") != "success":
                errors.append(prefix + "compile_evidence.result must be success")
            if compile_evidence.get("proof_scope") != EXPECTED_PROOF_SCOPE:
                errors.append(
                    prefix + f"compile_evidence.proof_scope must be {EXPECTED_PROOF_SCOPE!r}"
                )

        product_yaml = evidence.get("product_yaml", "")
        bundle_yaml = evidence.get("bundle_yaml", "")
        if not product_yaml.startswith("products/sense360-"):
            errors.append(prefix + "product_yaml must be a top-level products/sense360-*.yaml")
        if product_yaml.startswith("products/webflash/"):
            errors.append(prefix + "product_yaml must not be a WebFlash wrapper")
        if product_yaml and not (REPO_ROOT / product_yaml).is_file():
            errors.append(prefix + f"product_yaml not found: {product_yaml}")
        if not bundle_yaml.startswith("products/bundles/"):
            errors.append(prefix + "bundle_yaml must be a products/bundles/*.yaml")
        if bundle_yaml and not (REPO_ROOT / bundle_yaml).is_file():
            errors.append(prefix + f"bundle_yaml not found: {bundle_yaml}")

        # Cross-check the compile-evidence ledger pins the same product YAML + run.
        target = _compile_target_for(
            compile_doc, config_string, EXPECTED_COMPILE_RUN_ID
        )
        if not target:
            errors.append(
                prefix + f"no compile-only target cites run {EXPECTED_COMPILE_RUN_ID}"
            )
        else:
            if target.get("product_yaml") != product_yaml:
                errors.append(prefix + "compile target product_yaml mismatch")
            if target.get("compile_validation_status") != EXPECTED_COMPILE_STATUS:
                errors.append(prefix + "compile target must be validated-full-compile")

        # FanDAC address policy (or absence for non-FanDAC).
        requirement = evidence.get("fan_dac_address_requirement")
        if config_string in FANDAC_CONFIGS:
            errors.extend(_validate_fandac_requirement(requirement, prefix))
        elif requirement is not None:
            errors.append(prefix + "non-FanDAC config must not carry a FanDAC address requirement")

        # Fan-token guardrail: the five never enter the WebFlash build ledger.
        if config_string in webflash_configs:
            errors.append(prefix + "must not appear in config/webflash-builds.json")

        expected_artifact = _artifact_name(config_string, version, DEFAULT_CHANNEL)
        if not expected_artifact.endswith("-preview.bin"):
            errors.append(prefix + "artifact must end with -preview.bin")

        stable_blockers = variant.get("stable_blockers") or []
        selected.append(
            {
                "config_string": config_string,
                "sku": variant.get("sku", ""),
                "room": variant.get("room", ""),
                "fan_driver": variant.get("fan_driver", ""),
                "product_yaml": product_yaml,
                "bundle_yaml": bundle_yaml,
                "compile_only_target_id": evidence.get("compile_only_target_id", ""),
                "artifact_name": expected_artifact,
                "warning_copy": variant.get("warning_copy", ""),
                "stable_blocker": stable_blockers[0] if stable_blockers else "",
                "is_fandac": config_string in FANDAC_CONFIGS,
            }
        )

    # Repo-wide fan-token guardrail (independent of selection).
    for config_string in webflash_configs:
        for token in FAN_TOKENS:
            if token.lower() in config_string.lower():
                errors.append(
                    f"config/webflash-builds.json must not contain fan token {token}: "
                    f"{config_string}"
                )

    return selected, errors


def _matrix(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    include = []
    for row in rows:
        include.append(
            {
                "config_string": row["config_string"],
                "target_id": row["compile_only_target_id"],
                "product_yaml": row["product_yaml"],
                "artifact_name": row["artifact_name"],
            }
        )
    return {"include": include}


def _release_body(rows: List[Dict[str, Any]], *, version: str, release_tag: str) -> str:
    artifact_lines = [
        f"- `{row['artifact_name']}` ({row['config_string']})" for row in rows
    ]
    changelog_lines = [
        f"- Publish room-bundle preview firmware for `{row['config_string']}` "
        f"as `{row['artifact_name']}`."
        for row in rows
    ]
    fandac_configs = [row["config_string"] for row in rows if row["is_fandac"]]
    known_issue_lines = [
        "- PREVIEW firmware only: not stable, not recommended, not a customer "
        "default, not hardware verified, and not buyable.",
        "- Hardware, bench, mains-safety, and compliance evidence remain "
        "stable-only blockers; no such proof is claimed by this release.",
    ]
    if fandac_configs:
        known_issue_lines.append(
            "- The FanDAC artifacts ("
            + ", ".join(f"`{cs}`" for cs in fandac_configs)
            + f") require the GP8403 IC2 `{FANDAC_IC2}` address override and a "
            f"matching S360-312 IC2 DIP switch (IC1 `{FANDAC_IC1}`; `{FANDAC_FORBIDDEN}` "
            "is forbidden — it collides with the air-quality SGP41 at "
            f"`{FANDAC_FORBIDDEN}`). The DIP-position to address mapping is NOT "
            f"bench verified; `{FANDAC_BENCH_FOLLOWUP}` stays pending."
        )
    known_issue_lines.extend(
        [
            f"- `{TRIAC_CONFIG}` is excluded because `HW-005` still blocks "
            "buildability.",
            "- These room-bundle fan artifacts share the `v1.0.0-preview` preview "
            "release with the room-bundle and LED preview artifacts. WebFlash "
            "import eligibility is controlled separately by WebFlash import "
            "policy; presence in this shared release does not make them WebFlash "
            "one-click imports, and no fan row is added to "
            "`config/webflash-builds.json`.",
        ]
    )
    feature_lines = [
        f"- Full-composition room-bundle preview for `{row['config_string']}` "
        f"({row['room']} bundle + {row['fan_driver']} fan driver)."
        for row in rows
    ]
    hardware_lines = [
        f"- `{row['config_string']}` uses `{row['product_yaml']}`; "
        f"stable blocker remains: {row['stable_blocker']}"
        for row in rows
    ]

    def bullets(lines: Iterable[str]) -> str:
        return "\n".join(lines)

    return "\n".join(
        [
            f"# Sense360 room-bundle fan-control preview firmware {version}",
            "",
            f"Canonical workflow: `{WORKFLOW_ID}`.",
            f"Release tag: `{release_tag}`.",
            "",
            "These full-composition Bathroom / Kitchen fan-control room-bundle "
            "preview artifacts are published to the shared `v1.0.0-preview` "
            "preview release — the single preview release that also carries the "
            "room-bundle and LED preview artifacts. Publishing here does not "
            "imply stable, recommended, default, buyable, certified, or "
            "WebFlash-importable status; WebFlash import eligibility is controlled "
            "separately by WebFlash import policy.",
            "",
            "Artifacts:",
            bullets(artifact_lines),
            "",
            "## Changelog",
            bullets(changelog_lines),
            "",
            "## Known Issues",
            bullets(known_issue_lines),
            "",
            "## Features",
            bullets(feature_lines),
            "",
            "## Hardware Requirements",
            bullets(hardware_lines),
            "",
            f"Compile evidence: hosted Compile-only Firmware Validation run "
            f"`{EXPECTED_COMPILE_RUN_ID}` ({COMPILE_RESULTS_ID}; firmware-build "
            "proof only).",
        ]
    )


def _validate_output_dir(rows: List[Dict[str, Any]], output_dir: Path) -> List[str]:
    errors: List[str] = []
    expected = {row["artifact_name"] for row in rows}
    found = {p.name for p in output_dir.glob("*.bin")} if output_dir.is_dir() else set()

    missing = expected - found
    extra = found - expected
    if missing:
        errors.append("missing expected artifact(s): " + ", ".join(sorted(missing)))
    if extra:
        errors.append("unexpected .bin artifact(s): " + ", ".join(sorted(extra)))

    for name in found:
        if "FanTRIAC" in name or "TRIAC" in name:
            errors.append(f"TRIAC artifact must not be present: {name}")
        if not name.endswith("-preview.bin"):
            errors.append(f"room-bundle preview artifact must end with -preview.bin: {name}")
        if "-stable.bin" in name:
            errors.append(f"stable artifact must not be present: {name}")

    return errors


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default=DEFAULT_VERSION)
    parser.add_argument("--release-tag", default=EXPECTED_RELEASE_TAG)
    parser.add_argument(
        "--confirm-tag-override",
        default="false",
        help=(
            "Confirm a non-shared release tag (true/false). Required to publish to "
            "any tag other than the shared preview release "
            f"({TAG_GUARD_ID})."
        ),
    )
    parser.add_argument("--release-target", default=ALL_TARGETS)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--metadata-only", action="store_true")
    mode.add_argument("--validate-release-tag", action="store_true")
    mode.add_argument("--print-matrix", action="store_true")
    mode.add_argument("--release-body", action="store_true")
    mode.add_argument("--validate-output-dir")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Tag confirm-gate is enforced in every mode; the shared preview release
    # default passes silently.
    tag_errors = _validate_release_tag(
        args.release_tag, confirm_override=_is_truthy(args.confirm_tag_override)
    )

    if args.validate_release_tag:
        if tag_errors:
            print(
                "Room-bundle fan release-tag validation FAILED:", file=sys.stderr
            )
            for error in tag_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print(f"Release tag {args.release_tag!r} accepted for the room-bundle fan publish.")
        return 0

    variants = _load_json(VARIANTS_PATH)
    compile_targets = _load_json(COMPILE_TARGETS_PATH)
    builds = _load_json(WEBFLASH_BUILDS_PATH)

    rows, errors = _select_rows(
        variants,
        compile_targets,
        builds,
        version=args.version,
        release_target=args.release_target,
    )
    errors = tag_errors + errors
    if errors:
        print("Room-bundle fan publish validation FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    if args.print_matrix:
        print(json.dumps(_matrix(rows), separators=(",", ":")))
        return 0

    if args.release_body:
        print(_release_body(rows, version=args.version, release_tag=args.release_tag))
        return 0

    if args.validate_output_dir:
        output_errors = _validate_output_dir(rows, Path(args.validate_output_dir))
        if output_errors:
            print("Room-bundle fan output validation FAILED:", file=sys.stderr)
            for error in output_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("Room-bundle fan output validation passed.")
        return 0

    print(
        "Room-bundle fan publish metadata validated "
        f"({len(rows)} target(s), version={args.version}, target={args.release_target})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
