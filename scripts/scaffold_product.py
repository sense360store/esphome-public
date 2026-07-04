#!/usr/bin/env python3
"""PRODUCT-010: conservative product scaffold report generator.

This script is a read-only, dry-run helper for future maintainers who are
adding a new Sense360 product/config. It does NOT mutate any file:

  * It does not edit ``config/product-catalog.json``.
  * It does not edit ``config/webflash-builds.json``.
  * It does not edit ``config/webflash-compatibility.json``.
  * It does not edit ``config/hardware-catalog.json``.
  * It does not create or modify any product YAML under ``products/``.
  * It does not create or modify any WebFlash wrapper under
    ``products/webflash/``.
  * It does not edit ``scripts/product_name_mapper.py``.
  * It does not edit any package, workflow, component, header, or test.
  * It does not generate firmware, release notes, GitHub releases, or
    WebFlash imports.
  * It cannot scaffold a ``production`` entry. Production is reached via
    the promotion gates documented in
    ``docs/preview-to-stable-promotion-gates.md`` (archived under
    DOCS-DISPOSITION-001; see ``docs/archive-index.md``) — not by a
    scaffold.

What it does, on a single invocation:

  1. Parses and validates a WebFlash config string against the rules in
     ``config/webflash-compatibility.json``.
  2. Cross-references the proposed catalog entry against
     ``config/product-catalog.json`` and
     ``config/webflash-builds.json``.
  3. Validates every ``--hardware slot=SKU`` against
     ``config/hardware-catalog.json``.
  4. Derives the canonical WebFlash artifact name via
     ``scripts/product_name_mapper.py`` (read-only import) when a
     ``--product-yaml`` path is supplied.
  5. Enforces per-status lifecycle rules
     (``compile-only`` / ``hardware-pending`` / ``preview`` / ``blocked``).
  6. Rejects ``production`` / ``deprecated`` / ``removed`` /
     ``legacy-compatible`` with an explanatory message.
  7. Enforces the FanTRIAC HW-005 policy: any config string containing
     ``FanTRIAC`` is forced to ``blocked`` with ``blocker=HW-005``.
  8. Prints a Markdown scaffold report to stdout. The report contains
     example JSON snippets but the script never writes them anywhere.

Exit code: 0 on success, non-zero on any validation failure.

Usage (example):

    python3 scripts/scaffold_product.py \\
        --config-string Ceiling-POE-VentIQ-RoomIQ-LED \\
        --status compile-only \\
        --product-yaml products/sense360-ceiling-poe-ventiq-roomiq-led.yaml \\
        --hardware core=S360-100 \\
        --hardware ventiq=S360-211 \\
        --hardware roomiq=S360-200 \\
        --hardware poe=S360-410 \\
        --hardware led=S360-300

The ``--catalog`` / ``--builds`` / ``--compat`` / ``--hardware-catalog``
flags are intended for tests; they let the script run against synthetic
JSON fixtures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
DEFAULT_COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
DEFAULT_HARDWARE_PATH = REPO_ROOT / "config" / "hardware-catalog.json"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from product_name_mapper import (  # noqa: E402
    convert_product_name,
    generate_webflash_filename,
)

ALLOWED_STATUSES = ("compile-only", "hardware-pending", "preview", "blocked")
REJECTED_STATUSES = (
    "production",
    "deprecated",
    "removed",
    "legacy-compatible",
)

FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")
FANTRIAC_BLOCKER = "HW-005"

VALIDATION_COMMANDS = (
    "python3 tests/test_scaffold_product.py",
    "python3 tests/test_product_catalog.py",
    "python3 tests/test_product_catalog_consistency.py",
    "python3 tests/validate_webflash_builds.py",
    "python3 tests/test_webflash_compatibility.py",
    "python3 tests/test_webflash_artifact_naming.py",
    "python3 tests/test_validate_webflash_release_notes.py",
    "python3 tests/test_generate_webflash_release_notes.py",
    "python3 tests/test_product_substitutions.py",
    "python3 tests/test_release_one_entity_names.py",
    "python3 tests/validate_configs.py",
)

DO_NOT_CHANGE_GUARDRAILS = (
    "Release-One config string `Ceiling-POE-VentIQ-RoomIQ` and artifact "
    "`Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin` must stay "
    "unchanged.",
    "FanTRIAC stays blocked under HW-005. This scaffold must not unblock "
    "`Ceiling-POE-VentIQ-FanTRIAC-RoomIQ` or add a FanTRIAC product to "
    "the build matrix.",
    "Sense360 LED stays excluded from Release-One. The LED-bearing "
    "preview entry `Ceiling-POE-VentIQ-RoomIQ-LED` stays `status: "
    "preview`, `channel: preview`.",
    "Mains-voltage posture per COMPLIANCE-001-RESOLUTION-001 (COMPLIANCE-001 "
    "closed by market posture — never placed on the market): `S360-400` "
    "Sense360 240v PSU and `S360-320` Sense360 TRIAC remain "
    "`cataloged_unverified`; the experimental-lane preconditions gate any "
    "publish, and a market-placement act would reopen COMPLIANCE-001.",
    "No firmware build, no GitHub Release, no WebFlash import, no "
    "production promotion. Those are owned by the promotion gates in "
    "`docs/preview-to-stable-promotion-gates.md` (archived under "
    "DOCS-DISPOSITION-001; see `docs/archive-index.md`).",
)

NEXT_PR_SEQUENCE = (
    "1. Add the product YAML under `products/` and (if WebFlash-shippable) "
    "a wrapper under `products/webflash/`. Validate with "
    "`tests/validate_configs.py` and `tests/test_product_substitutions.py`.",
    "2. Add a catalog entry to `config/product-catalog.json` at the "
    "scaffolded status. Run `scripts/validate_product_catalog_consistency.py` "
    "and `tests/test_product_catalog.py`.",
    "3. For `preview` entries that will land in the build matrix: add the "
    "entry to `config/webflash-builds.json` with a non-`stable` channel and "
    "an artifact name produced by `scripts/product_name_mapper.py`. Run "
    "`tests/validate_webflash_builds.py` and "
    "`tests/test_webflash_artifact_naming.py`.",
    "4. Record a build / release proof following the archived pattern of "
    "`docs/webflash-release-proof.md` (see `docs/archive-index.md`) "
    "after the corresponding GitHub Release exists. WebFlash import is a "
    "follow-up PR in the WebFlash repo.",
    "5. Production promotion is a separate process per "
    "`docs/preview-to-stable-promotion-gates.md` (archived; see "
    "`docs/archive-index.md`). This scaffold cannot "
    "scaffold a production entry.",
)


class ScaffoldError(Exception):
    """Raised when scaffold validation cannot proceed."""


# ----------------------------------------------------------------------
# Loading
# ----------------------------------------------------------------------


def _load_json(path: Path, label: str) -> Dict[str, Any]:
    if not path.is_file():
        raise ScaffoldError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ScaffoldError(f"{label} is not valid JSON: {exc}")


def _parse_hardware_assignments(values: List[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for raw in values:
        if "=" not in raw:
            raise ScaffoldError(f"--hardware value {raw!r} must be SLOT=SKU")
        slot, sku = raw.split("=", 1)
        slot = slot.strip()
        sku = sku.strip()
        if not slot or not sku:
            raise ScaffoldError(
                f"--hardware value {raw!r} must be SLOT=SKU " "(both parts non-empty)"
            )
        if slot in out:
            raise ScaffoldError(f"--hardware slot {slot!r} declared more than once")
        out[slot] = sku
    return out


# ----------------------------------------------------------------------
# Grammar parsing
# ----------------------------------------------------------------------


def _parse_config_string(
    config_string: str, compat: Dict[str, Any]
) -> Tuple[List[str], List[str]]:
    """Return (tokens, errors).

    Tokens come back even when there are errors, so the report can show
    what the parser saw.
    """
    errors: List[str] = []
    tokens = config_string.split("-")

    if config_string == compat.get("rescue_config_string"):
        return tokens, errors

    if len(tokens) < 2:
        errors.append(
            f"config_string {config_string!r} must contain at least a "
            "mounting and a power token"
        )
        return tokens, errors

    mounting = set(compat.get("canonical_mounting", []))
    power = set(compat.get("canonical_power", []))
    modules = set(compat.get("canonical_modules", []))
    forbidden = set(compat.get("forbidden_tokens", []))

    if tokens[0] not in mounting:
        errors.append(
            f"Invalid mounting token {tokens[0]!r}; " f"allowed: {sorted(mounting)}"
        )
    if tokens[1] not in power:
        errors.append(
            f"Invalid power token {tokens[1]!r}; " f"allowed: {sorted(power)}"
        )

    for token in tokens:
        if token in forbidden:
            if token == "Fan":
                errors.append(
                    "Generic Fan token is forbidden; use FanRelay, "
                    "FanPWM, FanDAC, or FanTRIAC"
                )
            else:
                errors.append(
                    f"Forbidden legacy token {token!r}; "
                    "see docs/webflash-contract.md"
                )

    for token in tokens[2:]:
        if token in forbidden:
            continue
        if token not in modules:
            errors.append(f"Unknown module token {token!r}")

    rules = compat.get("rules", {})
    if (
        rules.get("airiq_and_ventiq_mutually_exclusive")
        and "AirIQ" in tokens
        and "VentIQ" in tokens
    ):
        errors.append("AirIQ and VentIQ are mutually exclusive")

    if (
        rules.get("fandac_conflicts_with_airiq")
        and "FanDAC" in tokens
        and "AirIQ" in tokens
    ):
        errors.append("FanDAC conflicts with AirIQ; see docs/webflash-contract.md")

    present_fans = [t for t in FAN_DRIVER_TOKENS if t in tokens]
    if len(present_fans) > 1:
        errors.append(f"more than one fan-driver token: {present_fans}")

    return tokens, errors


# ----------------------------------------------------------------------
# Markdown helpers
# ----------------------------------------------------------------------


def _ok(msg: str) -> str:
    return f"- OK: {msg}"


def _err(msg: str) -> str:
    return f"- ERROR: {msg}"


def _info(msg: str) -> str:
    return f"- {msg}"


def _section(title: str, lines: List[str]) -> str:
    body = "\n".join(lines) if lines else "(none)"
    return f"## {title}\n\n{body}\n"


def _json_block(data: Any) -> str:
    return "```json\n" + json.dumps(data, indent=2, sort_keys=False) + "\n```"


# ----------------------------------------------------------------------
# Report builder
# ----------------------------------------------------------------------


def build_report(args: argparse.Namespace) -> Tuple[str, int]:
    """Return (markdown_report, exit_code)."""

    errors: List[str] = []
    sections: List[str] = ["# Product Scaffold Report\n"]

    # ----- Status validation ------------------------------------------------
    status = args.status
    if status in REJECTED_STATUSES:
        if status == "production":
            errors.append(
                "status 'production' is not scaffoldable. Production is "
                "reached via the promotion gates in "
                "docs/preview-to-stable-promotion-gates.md (archived; see "
                "docs/archive-index.md), not by a "
                "scaffold."
            )
        else:
            errors.append(
                f"status {status!r} is a lifecycle operation, not a "
                "new-product scaffold (compile-only, hardware-pending, "
                "preview, or blocked only)"
            )
    elif status not in ALLOWED_STATUSES:
        errors.append(
            f"status {status!r} is not allowed; choose one of "
            f"{list(ALLOWED_STATUSES)}"
        )

    # ----- Load supporting data --------------------------------------------
    try:
        catalog = _load_json(Path(args.catalog), "product catalog")
        builds_doc = _load_json(Path(args.builds), "webflash builds")
        compat = _load_json(Path(args.compat), "webflash compatibility")
        hardware_doc = _load_json(Path(args.hardware_catalog), "hardware catalog")
    except ScaffoldError as exc:
        return f"# Product Scaffold Report\n\nERROR: {exc}\n", 2

    # ----- Hardware assignments parse --------------------------------------
    try:
        hardware = _parse_hardware_assignments(args.hardware or [])
    except ScaffoldError as exc:
        return f"# Product Scaffold Report\n\nERROR: {exc}\n", 2

    # ----- Input section ----------------------------------------------------
    input_lines = [
        _info(f"`config_string`: `{args.config_string}`"),
        _info(f"`status`: `{status}`"),
        _info(f"`product_yaml`: `{args.product_yaml}`"),
    ]
    if args.webflash_wrapper:
        input_lines.append(_info(f"`webflash_wrapper`: `{args.webflash_wrapper}`"))
    if args.version:
        input_lines.append(_info(f"`version`: `{args.version}`"))
    if args.channel:
        input_lines.append(_info(f"`channel`: `{args.channel}`"))
    if args.hardware_status:
        input_lines.append(_info(f"`hardware_status`: `{args.hardware_status}`"))
    if args.webflash_build_matrix:
        input_lines.append(_info("`webflash_build_matrix`: requested"))
    if args.blocker:
        input_lines.append(_info(f"`blocker`: `{args.blocker}`"))
    if args.reason:
        input_lines.append(_info(f"`reason`: `{args.reason}`"))
    if args.missing_hardware_evidence:
        input_lines.append(
            _info("`missing_hardware_evidence`: " f"`{args.missing_hardware_evidence}`")
        )
    if hardware:
        for slot, sku in hardware.items():
            input_lines.append(_info(f"hardware `{slot}` → `{sku}`"))
    sections.append(_section("Input", input_lines))

    # ----- Parsed config string --------------------------------------------
    tokens, grammar_errors = _parse_config_string(args.config_string, compat)
    parsed_lines = [_info(f"tokens: `{tokens}`")]
    sections.append(_section("Parsed config string", parsed_lines))

    grammar_lines: List[str] = []
    if grammar_errors:
        for err in grammar_errors:
            grammar_lines.append(_err(err))
            errors.append(f"grammar: {err}")
    else:
        grammar_lines.append(_ok("config string parses against compatibility rules"))
    sections.append(_section("Compatibility grammar check", grammar_lines))

    # ----- Existing repo state ---------------------------------------------
    existing_lines: List[str] = []
    catalog_products = catalog.get("products", []) or []
    duplicate_entry = next(
        (
            p
            for p in catalog_products
            if isinstance(p, dict) and p.get("config_string") == args.config_string
        ),
        None,
    )
    if duplicate_entry is not None:
        existing_lines.append(
            _err(
                f"duplicate catalog entry: {args.config_string!r} already "
                f"in config/product-catalog.json with "
                f"status={duplicate_entry.get('status')!r}"
            )
        )
        errors.append(
            f"duplicate catalog entry for config_string " f"{args.config_string!r}"
        )
    else:
        existing_lines.append(
            _ok(f"no existing catalog entry for {args.config_string!r}")
        )

    builds = builds_doc.get("builds", []) or []
    existing_build = next(
        (
            b
            for b in builds
            if isinstance(b, dict) and b.get("config_string") == args.config_string
        ),
        None,
    )
    if existing_build is not None:
        existing_lines.append(
            _err(
                f"build-matrix entry for {args.config_string!r} already "
                "exists in config/webflash-builds.json"
            )
        )
        errors.append(
            f"build-matrix entry already exists for " f"{args.config_string!r}"
        )
    else:
        existing_lines.append(
            _ok(f"no existing build-matrix entry for " f"{args.config_string!r}")
        )

    if args.product_yaml.startswith("products/webflash/"):
        existing_lines.append(
            _err(
                f"product_yaml {args.product_yaml!r} points at the "
                "WebFlash wrapper directory; wrappers belong in "
                "webflash_wrapper, not product_yaml"
            )
        )
        errors.append(
            "product_yaml points at products/webflash/; "
            "use --webflash-wrapper for the wrapper"
        )

    product_yaml_abs = REPO_ROOT / args.product_yaml
    if product_yaml_abs.is_file():
        existing_lines.append(_ok(f"product YAML exists ({args.product_yaml})"))
    else:
        existing_lines.append(
            _info(
                f"product YAML does NOT yet exist "
                f"({args.product_yaml}) — create it in a follow-up PR"
            )
        )

    if args.webflash_wrapper:
        wrapper_abs = REPO_ROOT / args.webflash_wrapper
        if wrapper_abs.is_file():
            existing_lines.append(
                _ok(f"WebFlash wrapper exists ({args.webflash_wrapper})")
            )
        else:
            existing_lines.append(
                _info(
                    f"WebFlash wrapper does NOT yet exist "
                    f"({args.webflash_wrapper}) — create it in a "
                    "follow-up PR"
                )
            )

    sections.append(_section("Existing repo state", existing_lines))

    # ----- Hardware SKU check ----------------------------------------------
    hardware_lines: List[str] = []
    known_skus = {
        item.get("sku")
        for item in hardware_doc.get("items", []) or []
        if isinstance(item, dict) and item.get("sku")
    }
    if not hardware:
        hardware_lines.append(
            _info(
                "no `--hardware slot=SKU` assignments declared "
                "(scaffold report only; required for preview promotion)"
            )
        )
    else:
        for slot, sku in hardware.items():
            if sku in known_skus:
                hardware_lines.append(_ok(f"`{slot}` → `{sku}` (catalog)"))
            else:
                hardware_lines.append(
                    _err(f"`{slot}` → `{sku}` not in " "config/hardware-catalog.json")
                )
                errors.append(
                    f"hardware slot {slot!r} SKU {sku!r} is not in "
                    "config/hardware-catalog.json"
                )
    sections.append(_section("Hardware SKU check", hardware_lines))

    # ----- FanTRIAC HW-005 policy ------------------------------------------
    has_fantriac = "FanTRIAC" in tokens
    if has_fantriac:
        if status != "blocked":
            errors.append(
                "config string contains FanTRIAC; scaffold must be "
                "`--status blocked --blocker HW-005 --reason ...` until "
                "HW-005 evidence changes"
            )
        else:
            if args.blocker != FANTRIAC_BLOCKER:
                errors.append("FanTRIAC scaffold must set --blocker HW-005")

    # ----- Per-status lifecycle rules --------------------------------------
    derived_artifact: Optional[str] = None
    mapper_display: Optional[str] = None
    if args.version and args.channel:
        product_key = Path(args.product_yaml).stem
        try:
            mapper_display = convert_product_name(product_key)
            derived_artifact = generate_webflash_filename(
                product_key, args.version, args.channel
            )
        except Exception as exc:  # pragma: no cover - mapper is pure
            errors.append(f"artifact-name derivation failed: {exc}")

    release_one_required = set(compat.get("release_one_required_configs", []))

    if status == "compile-only":
        if not args.hardware_status:
            errors.append(
                "compile-only requires --hardware-status (e.g. "
                "'pending-bringup' or 'verified-candidate')"
            )
        if args.webflash_build_matrix:
            errors.append(
                "compile-only must not request --webflash-build-matrix; "
                "compile-only is intentionally not WebFlash-shippable"
            )

    elif status == "hardware-pending":
        if not args.hardware_status:
            errors.append("hardware-pending requires --hardware-status")
        if not args.missing_hardware_evidence:
            errors.append(
                "hardware-pending requires "
                "--missing-hardware-evidence describing the open evidence"
            )
        if args.webflash_build_matrix:
            errors.append("hardware-pending must not request --webflash-build-matrix")

    elif status == "preview":
        if not args.hardware_status:
            errors.append("preview requires --hardware-status")
        if not args.channel:
            errors.append("preview requires --channel (non-stable)")
        elif args.channel == "stable":
            errors.append(
                "preview must not use --channel stable; promote to "
                "production via the promotion gates first"
            )
        else:
            allowed_channels = set(compat.get("allowed_channels", []))
            if allowed_channels and args.channel not in allowed_channels:
                errors.append(
                    f"channel {args.channel!r} is not in allowed_channels "
                    f"{sorted(allowed_channels)}"
                )
        if not args.version:
            errors.append("preview requires --version")
        if args.config_string in release_one_required:
            errors.append(
                f"preview must not claim a Release-One required config "
                f"({args.config_string!r}); only production may"
            )
        if args.webflash_build_matrix:
            if not args.webflash_wrapper:
                errors.append(
                    "preview --webflash-build-matrix requires "
                    "--webflash-wrapper (path under products/webflash/)"
                )
            else:
                wrapper_stem = Path(args.webflash_wrapper).stem
                if wrapper_stem != args.config_string.lower():
                    errors.append(
                        f"webflash_wrapper basename {wrapper_stem!r} does "
                        f"not match lowercased config_string "
                        f"{args.config_string.lower()!r}"
                    )
            if not args.version or not args.channel:
                errors.append(
                    "preview --webflash-build-matrix requires both "
                    "--version and --channel"
                )

    elif status == "blocked":
        if not args.blocker:
            errors.append("blocked requires --blocker (e.g. HW-005)")
        if not args.reason:
            errors.append("blocked requires --reason")
        if args.webflash_build_matrix:
            errors.append("blocked must not request --webflash-build-matrix")

    # ----- Proposed product-catalog entry ----------------------------------
    proposed_entry: Dict[str, Any] = {
        "config_string": args.config_string,
        "status": status,
        "product_yaml": args.product_yaml,
        "webflash_build_matrix": bool(args.webflash_build_matrix),
    }
    if args.webflash_wrapper:
        proposed_entry["webflash_wrapper"] = args.webflash_wrapper
    if args.version:
        proposed_entry["version"] = args.version
    if args.channel:
        proposed_entry["channel"] = args.channel
    if args.hardware_status:
        proposed_entry["hardware_status"] = args.hardware_status
    if derived_artifact and status == "preview" and args.webflash_build_matrix:
        proposed_entry["artifact_name"] = derived_artifact
    if hardware:
        proposed_entry["hardware"] = dict(hardware)
    if status == "blocked":
        if args.blocker:
            proposed_entry["blocker"] = args.blocker
        if args.reason:
            proposed_entry["reason"] = args.reason
    if has_fantriac:
        proposed_entry.setdefault("notes", "FanTRIAC blocked under HW-005.")

    catalog_section = [
        _info("The example below is NOT written to disk by this script."),
        _info(
            "If you decide to add this entry, hand-edit "
            "`config/product-catalog.json` in a separate PR."
        ),
        "",
        _json_block(proposed_entry),
    ]
    if mapper_display:
        catalog_section.insert(
            2,
            _info(
                "Derived WebFlash display name from "
                f"`product_name_mapper.py`: `{mapper_display}`"
            ),
        )
    if derived_artifact:
        catalog_section.insert(
            2,
            _info(
                "Derived artifact name from "
                f"`product_name_mapper.py`: `{derived_artifact}`"
            ),
        )
    sections.append(_section("Proposed product-catalog entry", catalog_section))

    # ----- Optional WebFlash build-matrix entry ----------------------------
    build_lines: List[str] = []
    if status == "preview" and args.webflash_build_matrix:
        build_entry: Dict[str, Any] = {
            "config_string": args.config_string,
            "product_yaml": args.webflash_wrapper or "",
            "artifact_name": derived_artifact or "",
            "channel": args.channel or "",
            "version": args.version or "",
            "chip_family": "ESP32-S3",
            "hardware_requirements": [],
            "features": [],
        }
        build_lines.append(
            _info("The example below is NOT written to disk by this script.")
        )
        build_lines.append(
            _info(
                "Add this to `config/webflash-builds.json` in a separate "
                "PR, then run `tests/validate_webflash_builds.py`."
            )
        )
        build_lines.append("")
        build_lines.append(_json_block(build_entry))
    else:
        build_lines.append(
            _info(
                "Recommendation: `webflash_build_matrix: false`. "
                f"Status `{status}` is not WebFlash-shippable as a "
                "build-matrix entry from this scaffold."
            )
        )
    sections.append(_section("Optional WebFlash build-matrix entry", build_lines))

    # ----- Required files ---------------------------------------------------
    required_files = [
        _info(f"Product YAML: `{args.product_yaml}` (create if missing)"),
    ]
    if status == "preview" and args.webflash_build_matrix:
        required_files.append(
            _info(
                "WebFlash wrapper: "
                f"`{args.webflash_wrapper or '<set --webflash-wrapper>'}`"
            )
        )
    elif args.webflash_wrapper:
        required_files.append(
            _info(
                f"WebFlash wrapper: `{args.webflash_wrapper}` (optional "
                "at this status)"
            )
        )
    required_files.append(
        _info("Catalog entry: hand-edit `config/product-catalog.json`")
    )
    if status == "preview" and args.webflash_build_matrix:
        required_files.append(
            _info("Build matrix entry: hand-edit " "`config/webflash-builds.json`")
        )
    sections.append(_section("Required files", required_files))

    # ----- Validation commands ---------------------------------------------
    cmd_lines = [_info(f"`{c}`") for c in VALIDATION_COMMANDS]
    sections.append(_section("Validation commands", cmd_lines))

    # ----- Human review checklist -------------------------------------------
    checklist_items: List[Tuple[bool, str]] = []
    checklist_items.append(
        (not grammar_errors, "Config string parses against compatibility rules")
    )
    checklist_items.append(
        (
            duplicate_entry is None,
            f"No existing catalog entry for {args.config_string!r}",
        )
    )
    checklist_items.append(
        (
            existing_build is None,
            f"No existing build-matrix entry for {args.config_string!r}",
        )
    )
    if hardware:
        all_known = all(sku in known_skus for sku in hardware.values())
        checklist_items.append(
            (all_known, "Every declared hardware SKU is in the catalog")
        )
    checklist_items.append(
        (
            status in ALLOWED_STATUSES,
            f"Scaffold status is one of {list(ALLOWED_STATUSES)}",
        )
    )
    checklist_items.append(
        (
            not (has_fantriac and status != "blocked"),
            "FanTRIAC stays blocked under HW-005",
        )
    )
    checklist_items.append(
        (
            args.config_string not in release_one_required or status != "preview",
            "Preview does not claim a Release-One required config",
        )
    )
    if status == "preview":
        checklist_items.append(
            (
                args.channel is not None and args.channel != "stable",
                "Preview channel is non-stable",
            )
        )
    if status == "preview" and args.webflash_build_matrix:
        checklist_items.append(
            (
                bool(args.webflash_wrapper),
                "WebFlash wrapper path supplied for preview build matrix",
            )
        )
    checklist_items.append(
        (
            True,
            "Human reviewer must independently verify "
            "`docs/product-onboarding.md` and "
            "`docs/preview-to-stable-promotion-gates.md` (both archived "
            "under DOCS-DISPOSITION-001; see `docs/archive-index.md`) "
            "before merging any follow-up PR.",
        )
    )
    checklist_lines = [
        f"- [{'x' if ok else ' '}] {desc}" for ok, desc in checklist_items
    ]
    sections.append(_section("Human review checklist", checklist_lines))

    # ----- Do-not-change guardrails ----------------------------------------
    guardrail_lines = [_info(g) for g in DO_NOT_CHANGE_GUARDRAILS]
    sections.append(_section("Do-not-change guardrails", guardrail_lines))

    # ----- Next PR sequence -------------------------------------------------
    next_lines = [_info(step) for step in NEXT_PR_SEQUENCE]
    sections.append(_section("Next PR sequence", next_lines))

    # ----- Status footer ---------------------------------------------------
    if errors:
        sections.append(
            "## Result\n\n"
            + "\n".join(_err(e) for e in errors)
            + "\n\nExit code: non-zero. Fix the errors above and re-run.\n"
        )
        return "\n".join(sections), 1
    sections.append(
        "## Result\n\n- OK: scaffold report passed every validation.\n"
        "\nExit code: 0. This report is advisory only; no file was "
        "written.\n"
    )
    return "\n".join(sections), 0


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "PRODUCT-010 conservative product scaffold report generator. "
            "Report-only: this script never writes any file. Produces a "
            "Markdown report of grammar checks, repo-state cross-checks, "
            "hardware SKU checks, proposed catalog/build snippets, and a "
            "human review checklist. Cannot scaffold production."
        )
    )
    parser.add_argument(
        "--config-string",
        required=True,
        help="WebFlash config string (e.g. Ceiling-POE-VentIQ-RoomIQ-LED).",
    )
    parser.add_argument(
        "--status",
        required=True,
        help=(
            "Target lifecycle status. Allowed: "
            f"{', '.join(ALLOWED_STATUSES)}. "
            f"Rejected: {', '.join(REJECTED_STATUSES)}."
        ),
    )
    parser.add_argument(
        "--product-yaml",
        required=True,
        help="Repo-relative path to the product YAML under products/.",
    )
    parser.add_argument(
        "--webflash-wrapper",
        default=None,
        help=(
            "Repo-relative path to the WebFlash wrapper under "
            "products/webflash/ (required for preview with "
            "--webflash-build-matrix)."
        ),
    )
    parser.add_argument(
        "--hardware",
        action="append",
        default=[],
        metavar="SLOT=SKU",
        help=(
            "Hardware slot to SKU mapping (e.g. core=S360-100). May be "
            "supplied multiple times. SKUs are validated against "
            "config/hardware-catalog.json."
        ),
    )
    parser.add_argument(
        "--hardware-status",
        default=None,
        help=(
            "Catalog hardware_status string (e.g. pending-bringup, "
            "verified-candidate, verified-led-candidate, "
            "verified-for-release-one)."
        ),
    )
    parser.add_argument(
        "--version",
        default=None,
        help="Semantic version, e.g. 1.0.0 (required for preview).",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help=(
            "Release channel (preview, beta, dev, rescue). Required for "
            "preview. Must not be stable."
        ),
    )
    parser.add_argument(
        "--webflash-build-matrix",
        action="store_true",
        help=(
            "Propose a config/webflash-builds.json entry. Only allowed "
            "for status=preview. Requires --webflash-wrapper, --version, "
            "and --channel."
        ),
    )
    parser.add_argument(
        "--blocker",
        default=None,
        help="Blocker ID (e.g. HW-005). Required for status=blocked.",
    )
    parser.add_argument(
        "--reason",
        default=None,
        help="Human-readable reason. Required for status=blocked.",
    )
    parser.add_argument(
        "--missing-hardware-evidence",
        default=None,
        help=(
            "Short text describing the missing evidence. Required for "
            "status=hardware-pending."
        ),
    )
    parser.add_argument(
        "--catalog",
        default=str(DEFAULT_CATALOG_PATH),
        help="Override path to product-catalog.json (testing).",
    )
    parser.add_argument(
        "--builds",
        default=str(DEFAULT_BUILDS_PATH),
        help="Override path to webflash-builds.json (testing).",
    )
    parser.add_argument(
        "--compat",
        default=str(DEFAULT_COMPAT_PATH),
        help="Override path to webflash-compatibility.json (testing).",
    )
    parser.add_argument(
        "--hardware-catalog",
        default=str(DEFAULT_HARDWARE_PATH),
        help="Override path to hardware-catalog.json (testing).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    report, exit_code = build_report(args)
    sys.stdout.write(report)
    if not report.endswith("\n"):
        sys.stdout.write("\n")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
