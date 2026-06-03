#!/usr/bin/env python3
"""Validate and plan the manual-preview fan publish workflow.

RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001 (tag confirm-gate added by
RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001).

This helper is intentionally metadata-only unless called by the GitHub Actions
workflow to print a matrix, release body, validate an output directory, or
validate the release tag. It reads the non-WebFlash fan ledger in
``config/preview-fan-triac-build-rows.json`` plus
``config/manual-firmware-artifacts.json`` and never reads
``config/webflash-builds.json`` as a matrix source.

Release-tag confirm-gate (``--validate-release-tag`` / enforced in every mode):
the fan artifacts publish to the shared ``v1.0.0-preview`` preview release by
default (RELEASE-PREVIEW-FAN-SHARED-TAG-001), and that default is frictionless.
Targeting any other tag requires ``--confirm-tag-override true`` so an accidental
dispatch to the wrong tag fails fast. This does not reintroduce a dedicated fan
tag — the shared release stays the intended vehicle.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "config" / "preview-fan-triac-build-rows.json"
MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
WEBFLASH_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"

DEFAULT_VERSION = "1.0.0"
DEFAULT_CHANNEL = "preview"
ALL_TARGETS = "all-manual-preview-fans"
# RELEASE-PREVIEW-FAN-SHARED-TAG-001: the manual-preview fan artifacts are
# published to the shared v1.0.0-preview preview release — the single preview
# release for every preview artifact (room-bundle + LED + fan). There is no
# dedicated v1.0.0-manual-preview-fans vehicle.
EXPECTED_RELEASE_TAG = "v1.0.0-preview"

WORKFLOW_ID = "RELEASE-PREVIEW-FAN-PUBLISH-WORKFLOW-001"
RUN_ID = "RELEASE-PREVIEW-FAN-PUBLISH-RUN-001"
PLAN_ID = "RELEASE-PREVIEW-FAN-PUBLISH-PLAN-001"
TAG_GUARD_ID = "RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001"

# The shared preview release tag is the frictionless default (per
# RELEASE-PREVIEW-FAN-SHARED-TAG-001). Targeting any OTHER tag is allowed only
# with an explicit confirmation, so an accidental dispatch to the wrong tag (a
# typo, the stable release, or a stray new release) fails fast instead of
# creating / overwriting the wrong release (TAG_GUARD_ID).
SHARED_PREVIEW_RELEASE_TAG = EXPECTED_RELEASE_TAG

FAN_CONFIGS = (
    "Ceiling-POE-VentIQ-FanRelay-RoomIQ",
    "Ceiling-POE-FanPWM",
    "Ceiling-POE-FanDAC",
)
TRIAC_CONFIG = "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ"
FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

POSTURE_FALSE_FIELDS = (
    "buyable",
    "recommended",
    "customer_default",
    "stable",
    "release_one_required_config",
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_truthy(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "on"}


def _validate_release_tag(
    release_tag: str, *, confirm_override: bool = False
) -> List[str]:
    """Confirm-gate any release tag other than the shared preview release.

    RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001 (complements
    RELEASE-PREVIEW-FAN-SHARED-TAG-001). The fan artifacts publish to the shared
    ``v1.0.0-preview`` preview release by default, and that default is
    frictionless. Targeting any OTHER tag is allowed only with ``confirm_override``
    so an accidental dispatch to the wrong tag (a typo, the stable release, or a
    stray new release) fails fast instead of creating / overwriting the wrong
    release. This does not reintroduce a dedicated fan tag — the shared release
    stays the intended vehicle.

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
            f"the manual-preview fan artifacts to a different release tag "
            f"({TAG_GUARD_ID})"
        )
    return errors


def _artifact_name(config_string: str, version: str, channel: str) -> str:
    return f"Sense360-{config_string}-v{version}-{channel}.bin"


def _manual_by_id(manual_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {
        c.get("id"): c
        for c in manual_doc.get("candidates", []) or []
        if isinstance(c, dict) and c.get("id")
    }


def _webflash_config_strings(builds_doc: Dict[str, Any]) -> set[str]:
    return {
        b.get("config_string")
        for b in builds_doc.get("builds", []) or []
        if isinstance(b, dict) and b.get("config_string")
    }


def _select_rows(
    ledger: Dict[str, Any],
    manual_doc: Dict[str, Any],
    builds_doc: Dict[str, Any],
    *,
    version: str = DEFAULT_VERSION,
    release_target: str = ALL_TARGETS,
) -> tuple[List[Dict[str, Any]], List[str]]:
    errors: List[str] = []

    if ledger.get("schema_version") != 1:
        errors.append("preview fan/TRIAC ledger schema_version must be 1")

    manual_by_id = _manual_by_id(manual_doc)
    webflash_configs = _webflash_config_strings(builds_doc)

    rows_by_config = {
        row.get("config_string"): row
        for row in ledger.get("rows", []) or []
        if isinstance(row, dict) and row.get("config_string")
    }

    if set(FAN_CONFIGS).difference(rows_by_config):
        missing = sorted(set(FAN_CONFIGS).difference(rows_by_config))
        errors.append("missing manual-preview fan row(s): " + ", ".join(missing))
    if TRIAC_CONFIG not in rows_by_config:
        errors.append(f"missing TRIAC row {TRIAC_CONFIG!r}; exclusion cannot be checked")

    selected_configs: Iterable[str]
    if release_target in ("", ALL_TARGETS):
        selected_configs = FAN_CONFIGS
    elif release_target in FAN_CONFIGS:
        selected_configs = (release_target,)
    elif release_target == TRIAC_CONFIG:
        errors.append(f"{TRIAC_CONFIG} is build-blocked by HW-005 and cannot be published")
        selected_configs = ()
    else:
        errors.append(
            "release_target must be all-manual-preview-fans or one of "
            + ", ".join(FAN_CONFIGS)
        )
        selected_configs = ()

    triac = rows_by_config.get(TRIAC_CONFIG)
    if triac:
        if triac.get("buildable_now") is not False:
            errors.append("TRIAC must remain buildable_now=false")
        if not triac.get("build_blocker") or "HW-005" not in triac.get("build_blocker", ""):
            errors.append("TRIAC must carry the HW-005 build blocker")
        if triac.get("compile_evidence") is not None:
            errors.append("TRIAC must not claim compile evidence")

    selected: List[Dict[str, Any]] = []
    for config_string in selected_configs:
        row = rows_by_config.get(config_string)
        if not row:
            continue

        prefix = f"{config_string}: "
        if row.get("delivery_lane") != "manual-preview":
            errors.append(prefix + "delivery_lane must be manual-preview")
        if row.get("channel_tier") != "preview":
            errors.append(prefix + "channel_tier must be preview")
        if row.get("build_channel") != DEFAULT_CHANNEL:
            errors.append(prefix + "build_channel must be preview")
        if row.get("version") != version:
            errors.append(prefix + f"version must be {version!r}")
        if row.get("buildable_now") is not True:
            errors.append(prefix + "buildable_now must be true")
        if row.get("build_blocker") is not None:
            errors.append(prefix + "build_blocker must be null")
        if row.get("webflash_importable") is not False:
            errors.append(prefix + "webflash_importable must be false")
        if config_string in webflash_configs:
            errors.append(prefix + "must not appear in config/webflash-builds.json")

        expected_artifact = _artifact_name(config_string, version, DEFAULT_CHANNEL)
        if row.get("expected_preview_artifact_name") != expected_artifact:
            errors.append(prefix + f"artifact name must be {expected_artifact!r}")

        product_yaml = row.get("product_yaml", "")
        if not product_yaml.startswith("products/sense360-"):
            errors.append(prefix + "product_yaml must be a top-level products/sense360-*.yaml")
        if product_yaml.startswith("products/webflash/"):
            errors.append(prefix + "product_yaml must not be a WebFlash wrapper")
        if product_yaml and not (REPO_ROOT / product_yaml).is_file():
            errors.append(prefix + f"product_yaml not found: {product_yaml}")

        draft = row.get("release_note_draft", "")
        if draft and not (REPO_ROOT / draft).is_file():
            errors.append(prefix + f"release_note_draft not found: {draft}")

        candidate_id = row.get("manual_lane_candidate_id")
        candidate = manual_by_id.get(candidate_id)
        if not candidate:
            errors.append(prefix + f"manual candidate {candidate_id!r} not found")
        else:
            if candidate.get("product_yaml") != product_yaml:
                errors.append(prefix + "manual candidate product_yaml mismatch")
            if candidate.get("delivery_lane") != "manual-preview":
                errors.append(prefix + "manual candidate lane must be manual-preview")
            if candidate.get("preview_release_target") is not True:
                errors.append(prefix + "manual candidate must be a preview release target")
            if candidate.get("webflash_importable") is not False:
                errors.append(prefix + "manual candidate webflash_importable must be false")

        evidence = row.get("compile_evidence")
        if not isinstance(evidence, dict):
            errors.append(prefix + "compile_evidence must be present")
        else:
            if evidence.get("result") != "success":
                errors.append(prefix + "compile_evidence.result must be success")
            if evidence.get("proof_class") != "firmware-build-only":
                errors.append(prefix + "compile_evidence.proof_class must be firmware-build-only")

        posture = row.get("commercial_posture")
        if not isinstance(posture, dict):
            errors.append(prefix + "commercial_posture must be an object")
        else:
            if posture.get("visibility") != "hidden":
                errors.append(prefix + "commercial_posture.visibility must be hidden")
            for field in POSTURE_FALSE_FIELDS:
                if posture.get(field) is not False:
                    errors.append(prefix + f"commercial_posture.{field} must be false")

        selected.append(row)

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
                "candidate_id": row["manual_lane_candidate_id"],
                "product_yaml": row["product_yaml"],
                "artifact_name": row["expected_preview_artifact_name"],
                "release_note_draft": row["release_note_draft"],
            }
        )
    return {"include": include}


def _release_body(rows: List[Dict[str, Any]], *, version: str, release_tag: str) -> str:
    artifact_lines = [
        f"- `{row['expected_preview_artifact_name']}` ({row['config_string']})"
        for row in rows
    ]
    changelog_lines = [
        f"- Publish manual-preview firmware for `{row['config_string']}` "
        f"as `{row['expected_preview_artifact_name']}`."
        for row in rows
    ]
    known_issue_lines = [
        "- PREVIEW firmware only: not stable, not recommended, not a customer default, "
        "not hardware verified, and not buyable.",
        "- Hardware, bench, mains-safety, and compliance evidence remain stable-only "
        "blockers; no such proof is claimed by this release.",
        f"- `{TRIAC_CONFIG}` is excluded because `HW-005` still blocks buildability.",
        "- These fan artifacts share the `v1.0.0-preview` preview release with the "
        "room-bundle preview artifacts. WebFlash import eligibility is controlled "
        "separately by WebFlash import policy; presence in this shared release does "
        "not make them WebFlash one-click imports, and no fan row is added to "
        "`config/webflash-builds.json`.",
    ]
    feature_lines = [
        f"- Manual-preview delivery lane for `{row['config_string']}`."
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
            f"# Sense360 manual-preview fan firmware {version}",
            "",
            f"Canonical workflow: `{WORKFLOW_ID}`.",
            f"Release tag: `{release_tag}`.",
            "",
            "These buildable manual-preview fan artifacts are published to the "
            "shared `v1.0.0-preview` preview release — the single preview release "
            "that also carries the room-bundle preview artifacts. Publishing here "
            "does not imply stable, recommended, default, buyable, certified, or "
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
            "Compile evidence: hosted Preview Compile Dry-Run run `26821900127` "
            "(firmware-build proof only).",
        ]
    )


def _validate_output_dir(rows: List[Dict[str, Any]], output_dir: Path) -> List[str]:
    errors: List[str] = []
    expected = {row["expected_preview_artifact_name"] for row in rows}
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
            errors.append(f"manual-preview artifact must end with -preview.bin: {name}")

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
            "any tag other than the shared preview release. "
            "RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001."
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

    # Tag confirm-gate (RELEASE-PREVIEW-FAN-PUBLISH-TAG-GUARD-001) is enforced in
    # every mode; the shared preview release default passes silently.
    tag_errors = _validate_release_tag(
        args.release_tag, confirm_override=_is_truthy(args.confirm_tag_override)
    )

    if args.validate_release_tag:
        if tag_errors:
            print(
                "Manual-preview fan release-tag validation FAILED:", file=sys.stderr
            )
            for error in tag_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print(f"Release tag {args.release_tag!r} accepted for the fan publish.")
        return 0

    ledger = _load_json(LEDGER_PATH)
    manual = _load_json(MANUAL_PATH)
    builds = _load_json(WEBFLASH_BUILDS_PATH)

    rows, errors = _select_rows(
        ledger,
        manual,
        builds,
        version=args.version,
        release_target=args.release_target,
    )
    errors = tag_errors + errors
    if errors:
        print("Manual-preview fan publish validation FAILED:", file=sys.stderr)
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
            print("Manual-preview fan output validation FAILED:", file=sys.stderr)
            for error in output_errors:
                print(f"  - {error}", file=sys.stderr)
            return 1
        print("Manual-preview fan output validation passed.")
        return 0

    print(
        "Manual-preview fan publish metadata validated "
        f"({len(rows)} target(s), version={args.version}, target={args.release_target})."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
