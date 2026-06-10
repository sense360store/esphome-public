#!/usr/bin/env python3
"""STABLE-RELEASE-MATRIX-ALL-YAML-001: classify every product YAML.

Read-only enumerator that classifies every YAML under ``products/`` into
exactly one of the six release classes used by the canonical all-YAML
release matrix documented in
``docs/all-yaml-release-matrix.md``:

  * ``stable-release``          — release-eligible on the ``stable`` channel
  * ``preview-release``         — release-eligible on the ``preview`` channel
  * ``manual-candidate-only``   — tracked in
                                  ``config/manual-firmware-artifacts.json``
                                  for the workflow_dispatch-only manual lane
  * ``compile-only``            — CI validation skeleton under
                                  ``products/compile-only/``
  * ``blocked``                 — catalog ``status: blocked``
  * ``not-a-product-entrypoint``— WebFlash wrapper, legacy-compatible YAML,
                                  helper, or anything that is not a standalone
                                  release entry point

Release-eligibility is driven **exclusively** by
``config/webflash-builds.json``. The catalog
(``config/product-catalog.json``), the manual lane
(``config/manual-firmware-artifacts.json``), and the compile-only registry
(``config/compile-only-targets.json``) are the lifecycle / non-release
sources of truth.

The script is read-only:

  * it never publishes a GitHub Release;
  * it never writes ``firmware/sources.json`` or ``manifest.json``;
  * it never commits a ``.bin`` / checksum / build-info file;
  * it never flips ``webflash_build_matrix`` or adds an ``artifact_name``;
  * it never edits any YAML under ``products/`` or
    ``products/webflash/`` or any ``config/*.json``;
  * it never invents a YAML/product combo that does not exist on disk
    and in the source-of-truth files;
  * it refuses any FanRelay / FanPWM / FanDAC token in the release matrix
    (the same guardrail enforced by
    ``scripts/plan_room_release_notes.py`` and
    ``scripts/list_release_targets.py``).

Usage::

    python3 scripts/classify_all_yaml_release_matrix.py
    python3 scripts/classify_all_yaml_release_matrix.py --json
    python3 scripts/classify_all_yaml_release_matrix.py \\
        --class stable-release
    python3 scripts/classify_all_yaml_release_matrix.py \\
        --release-selectable
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCTS_DIR = REPO_ROOT / "products"
WEBFLASH_DIR = PRODUCTS_DIR / "webflash"
COMPILE_ONLY_DIR = PRODUCTS_DIR / "compile-only"

DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
DEFAULT_MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
DEFAULT_COMPILE_PATH = REPO_ROOT / "config" / "compile-only-targets.json"

CLASS_STABLE = "stable-release"
CLASS_PREVIEW = "preview-release"
# TRIAC-COMMISSIONING-001: the experimental self-build mains channel
# (config/release-channel-policy.json experimental_lane). Release-selectable on
# the 'experimental' build channel, but NEVER stable / recommended / default /
# buyable / kit-exposed.
CLASS_EXPERIMENTAL = "experimental-release"
CLASS_MANUAL = "manual-candidate-only"
CLASS_COMPILE_ONLY = "compile-only"
CLASS_BLOCKED = "blocked"
CLASS_NOT_ENTRYPOINT = "not-a-product-entrypoint"

ALL_CLASSES = (
    CLASS_STABLE,
    CLASS_PREVIEW,
    CLASS_EXPERIMENTAL,
    CLASS_MANUAL,
    CLASS_COMPILE_ONLY,
    CLASS_BLOCKED,
    CLASS_NOT_ENTRYPOINT,
)

RELEASE_SELECTABLE_CLASSES = (CLASS_STABLE, CLASS_PREVIEW, CLASS_EXPERIMENTAL)

# Fan family tokens that are manual-candidate-only and must never appear
# in the release matrix (mirrors plan_room_release_notes.py and
# list_release_targets.py).
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC")


class ClassifyError(Exception):
    """Raised when the all-YAML release matrix cannot be classified safely."""


def _load_json(path: Path, label: str) -> Dict[str, Any]:
    if not path.is_file():
        raise ClassifyError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ClassifyError(f"{label} is not valid JSON: {exc}")


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _enumerate_yaml(products_dir: Path) -> List[str]:
    out: List[str] = []
    for path in sorted(products_dir.rglob("*.yaml")):
        out.append(_rel(path))
    return out


def _index_catalog(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for entry in catalog.get("products", []) or []:
        if not isinstance(entry, dict):
            continue
        py = entry.get("product_yaml")
        if isinstance(py, str) and py:
            index[py] = entry
    return index


def _index_wrappers(catalog: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for entry in catalog.get("products", []) or []:
        if not isinstance(entry, dict):
            continue
        wrapper = entry.get("webflash_wrapper")
        if isinstance(wrapper, str) and wrapper:
            index[wrapper] = entry
    return index


def _index_builds(builds_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index the WebFlash release matrix.

    ``config/webflash-builds.json`` keys each entry by the WebFlash
    wrapper YAML (``products/webflash/<stem>.yaml``) and by the
    ``config_string``. Index by both so a lookup from the canonical
    product YAML (via its catalog ``config_string``) and from the
    wrapper YAML both resolve.
    """
    index: Dict[str, Dict[str, Any]] = {}
    for entry in builds_doc.get("builds", []) or []:
        if not isinstance(entry, dict):
            continue
        py = entry.get("product_yaml")
        cs = entry.get("config_string")
        if isinstance(py, str) and py:
            index[py] = entry
        if isinstance(cs, str) and cs:
            index.setdefault(f"config_string:{cs}", entry)
    return index


def _index_manual(manual_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for entry in manual_doc.get("candidates", []) or []:
        if not isinstance(entry, dict):
            continue
        py = entry.get("product_yaml")
        if isinstance(py, str) and py:
            index[py] = entry
    return index


def _index_compile(compile_doc: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    for entry in compile_doc.get("targets", []) or []:
        if not isinstance(entry, dict):
            continue
        py = entry.get("product_yaml")
        if isinstance(py, str) and py:
            index.setdefault(py, entry)
    return index


def _assert_no_fan_in_release(
    builds_doc: Dict[str, Any], manual_idx: Dict[str, Dict[str, Any]]
) -> None:
    fan_yamls = set(manual_idx.keys())
    for entry in builds_doc.get("builds", []) or []:
        if not isinstance(entry, dict):
            continue
        config_string = str(entry.get("config_string", ""))
        product_yaml = str(entry.get("product_yaml", ""))
        for token in FAN_FAMILY_TOKENS:
            if token.lower() in config_string.lower():
                raise ClassifyError(
                    f"guardrail violation: release build {config_string!r} "
                    f"carries fan family token {token!r}; FanRelay / FanPWM / "
                    "FanDAC are manual-candidate-only and must never be "
                    "release-eligible"
                )
        if product_yaml in fan_yamls:
            raise ClassifyError(
                f"guardrail violation: release build product_yaml "
                f"{product_yaml!r} matches a manual fan candidate; fan "
                "candidates must not be a release artifact"
            )


def classify_yaml(
    yaml_path: str,
    *,
    catalog_idx: Dict[str, Dict[str, Any]],
    wrapper_idx: Dict[str, Dict[str, Any]],
    builds_idx: Dict[str, Dict[str, Any]],
    manual_idx: Dict[str, Dict[str, Any]],
    compile_idx: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Classify a single YAML path into one of ``ALL_CLASSES``.

    The decision order is deterministic and reflects the matrix contract:

      1. WebFlash wrapper under ``products/webflash/`` → not-a-product-entrypoint
         (wrappers re-include their canonical product YAML; they are not
         standalone remote-package entry points).
      2. Compile-only skeleton under ``products/compile-only/`` →
         compile-only.
      3. Helper YAML directly under ``products/`` with no catalog row →
         not-a-product-entrypoint.
      4. In ``config/webflash-builds.json`` (the release-matrix source of
         truth) → stable-release or preview-release per ``channel``.
      5. In ``config/manual-firmware-artifacts.json`` candidates →
         manual-candidate-only.
      6. Catalog ``status: blocked`` → blocked.
      7. Catalog ``status: legacy-compatible`` → not-a-product-entrypoint.
      8. Catalog ``status: hardware-pending`` (no manual / no blocked
         classification) → blocked (no release path exists; not the same
         as the explicit catalog ``blocked`` status).
      9. Default → not-a-product-entrypoint.
    """
    record: Dict[str, Any] = {
        "yaml_path": yaml_path,
        "release_class": CLASS_NOT_ENTRYPOINT,
        "config_string": None,
        "catalog_status": None,
        "hardware_status": None,
        "channel": None,
        "version": None,
        "artifact_name": None,
        "webflash_wrapper": None,
        "webflash_build_matrix": False,
        "is_release_selectable": False,
        "is_webflash_wrapper": False,
        "is_compile_only_skeleton": False,
        "is_manual_candidate": False,
        "compile_validation_status": None,
        "notes_reference": None,
    }

    catalog_entry = catalog_idx.get(yaml_path)
    wrapper_parent = wrapper_idx.get(yaml_path)
    builds_entry = builds_idx.get(yaml_path)
    manual_entry = manual_idx.get(yaml_path)
    compile_entry = compile_idx.get(yaml_path)

    # The release matrix (``config/webflash-builds.json``) keys each entry
    # by the WebFlash wrapper YAML, not by the canonical product YAML.
    # When classifying the canonical YAML, fall through to the
    # catalog's ``config_string`` to find its release-matrix row.
    if builds_entry is None and catalog_entry is not None:
        config_string = catalog_entry.get("config_string")
        if isinstance(config_string, str) and config_string:
            builds_entry = builds_idx.get(f"config_string:{config_string}")

    if catalog_entry:
        record["config_string"] = catalog_entry.get("config_string")
        record["catalog_status"] = catalog_entry.get("status")
        record["hardware_status"] = catalog_entry.get("hardware_status")
        record["webflash_wrapper"] = catalog_entry.get("webflash_wrapper")
        record["webflash_build_matrix"] = bool(
            catalog_entry.get("webflash_build_matrix", False)
        )
        record["artifact_name"] = catalog_entry.get("artifact_name")
        record["version"] = catalog_entry.get("version")
        record["channel"] = catalog_entry.get("channel")

    if compile_entry:
        record["compile_validation_status"] = compile_entry.get(
            "compile_validation_status"
        )

    # 1. WebFlash wrapper — not a standalone entry point.
    if yaml_path.startswith("products/webflash/"):
        record["is_webflash_wrapper"] = True
        record["release_class"] = CLASS_NOT_ENTRYPOINT
        if wrapper_parent:
            record["config_string"] = wrapper_parent.get("config_string")
            record["catalog_status"] = wrapper_parent.get("status")
            record["notes_reference"] = wrapper_parent.get("product_yaml")
        return record

    # 2. Compile-only skeleton.
    if yaml_path.startswith("products/compile-only/"):
        record["is_compile_only_skeleton"] = True
        record["release_class"] = CLASS_COMPILE_ONLY
        return record

    # 3. Helper YAML under products/ with no catalog row (e.g. secrets.yaml).
    if catalog_entry is None:
        record["release_class"] = CLASS_NOT_ENTRYPOINT
        return record

    # 4. Release-eligible per config/webflash-builds.json.
    if builds_entry:
        channel = str(builds_entry.get("channel", "")).strip().lower()
        record["channel"] = builds_entry.get("channel")
        record["version"] = builds_entry.get("version")
        record["artifact_name"] = builds_entry.get("artifact_name")
        record["config_string"] = builds_entry.get(
            "config_string", record["config_string"]
        )
        if channel == "stable":
            record["release_class"] = CLASS_STABLE
            record["is_release_selectable"] = True
        elif channel == "preview":
            record["release_class"] = CLASS_PREVIEW
            record["is_release_selectable"] = True
        elif channel == "experimental":
            # TRIAC-COMMISSIONING-001 experimental self-build mains lane.
            # Release-selectable (the matrix builds it on an experimental tag)
            # but never stable / recommended / default / buyable / kit-exposed.
            record["release_class"] = CLASS_EXPERIMENTAL
            record["is_release_selectable"] = True
        else:
            raise ClassifyError(
                f"unknown channel {channel!r} in config/webflash-builds.json "
                f"for {yaml_path}"
            )
        return record

    # 5. Manual-candidate-only per config/manual-firmware-artifacts.json.
    if manual_entry is not None:
        record["is_manual_candidate"] = True
        record["release_class"] = CLASS_MANUAL
        return record

    # 6. Catalog explicit ``blocked`` status.
    status = (catalog_entry.get("status") or "").strip()
    if status == "blocked":
        record["release_class"] = CLASS_BLOCKED
        return record

    # 7. Legacy-compatible / pre-WebFlash YAMLs are not release products.
    if status == "legacy-compatible":
        record["release_class"] = CLASS_NOT_ENTRYPOINT
        return record

    # 8. Hardware-pending in the catalog but not in the manual lane and not
    #    explicitly ``blocked``: still has no release path. Classify as
    #    ``blocked`` so it cannot leak into release-selection.
    if status == "hardware-pending":
        record["release_class"] = CLASS_BLOCKED
        return record

    # 9. Default.
    record["release_class"] = CLASS_NOT_ENTRYPOINT
    return record


def classify(
    *,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    builds_path: Path = DEFAULT_BUILDS_PATH,
    manual_path: Path = DEFAULT_MANUAL_PATH,
    compile_path: Path = DEFAULT_COMPILE_PATH,
    products_dir: Path = PRODUCTS_DIR,
) -> Dict[str, Any]:
    """Classify every YAML under ``products_dir`` and return a structured plan."""
    catalog = _load_json(catalog_path, "config/product-catalog.json")
    builds_doc = _load_json(builds_path, "config/webflash-builds.json")
    manual_doc = _load_json(manual_path, "config/manual-firmware-artifacts.json")
    compile_doc = _load_json(compile_path, "config/compile-only-targets.json")

    catalog_idx = _index_catalog(catalog)
    wrapper_idx = _index_wrappers(catalog)
    builds_idx = _index_builds(builds_doc)
    manual_idx = _index_manual(manual_doc)
    compile_idx = _index_compile(compile_doc)

    _assert_no_fan_in_release(builds_doc, manual_idx)

    if not products_dir.is_dir():
        raise ClassifyError(f"products directory not found: {products_dir}")

    yaml_paths = _enumerate_yaml(products_dir)
    records = [
        classify_yaml(
            p,
            catalog_idx=catalog_idx,
            wrapper_idx=wrapper_idx,
            builds_idx=builds_idx,
            manual_idx=manual_idx,
            compile_idx=compile_idx,
        )
        for p in yaml_paths
    ]

    counts: Dict[str, int] = {c: 0 for c in ALL_CLASSES}
    for r in records:
        counts[r["release_class"]] += 1

    selectable = [r for r in records if r["is_release_selectable"]]
    selectable_stable = [r for r in selectable if r["release_class"] == CLASS_STABLE]
    selectable_preview = [r for r in selectable if r["release_class"] == CLASS_PREVIEW]
    selectable_experimental = [
        r for r in selectable if r["release_class"] == CLASS_EXPERIMENTAL
    ]

    return {
        "yaml_total": len(records),
        "counts": counts,
        "records": records,
        "release_selectable": [r["config_string"] for r in selectable],
        "stable_targets": [r["config_string"] for r in selectable_stable],
        "preview_targets": [r["config_string"] for r in selectable_preview],
        "experimental_targets": [r["config_string"] for r in selectable_experimental],
    }


def filter_records(
    plan: Dict[str, Any],
    *,
    release_class: Optional[str] = None,
    release_selectable: bool = False,
) -> List[Dict[str, Any]]:
    records: Iterable[Dict[str, Any]] = plan["records"]
    if release_class is not None:
        records = (r for r in records if r["release_class"] == release_class)
    if release_selectable:
        records = (r for r in records if r["is_release_selectable"])
    return list(records)


def _render_table(records: List[Dict[str, Any]]) -> str:
    headers = (
        "yaml_path",
        "release_class",
        "channel",
        "catalog_status",
        "config_string",
    )
    rows = [headers]
    for r in records:
        rows.append(
            (
                r["yaml_path"],
                r["release_class"],
                str(r["channel"] or "-"),
                str(r["catalog_status"] or "-"),
                str(r["config_string"] or "-"),
            )
        )
    widths = [max(len(str(row[i])) for row in rows) for i in range(len(headers))]
    lines: List[str] = []
    for i, row in enumerate(rows):
        lines.append(
            "  ".join(str(cell).ljust(widths[j]) for j, cell in enumerate(row))
        )
        if i == 0:
            lines.append("  ".join("-" * widths[j] for j in range(len(headers))))
    return "\n".join(lines)


def _render_summary(plan: Dict[str, Any]) -> str:
    counts = plan["counts"]
    lines = [
        f"all-yaml release matrix — {plan['yaml_total']} product YAMLs",
        "",
    ]
    for cls in ALL_CLASSES:
        lines.append(f"  {cls:24s} {counts.get(cls, 0)}")
    lines.append("")
    lines.append(
        "release-selectable (config/webflash-builds.json): "
        + ", ".join(plan["release_selectable"]) if plan["release_selectable"] else
        "release-selectable (config/webflash-builds.json): (none)"
    )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Classify every YAML under products/ into the all-YAML release "
            "matrix (STABLE-RELEASE-MATRIX-ALL-YAML-001). Read-only: "
            "creates no GitHub Release, builds no firmware, never writes "
            "firmware/sources.json or manifest.json."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the full classification as JSON.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print only the per-class counts.",
    )
    parser.add_argument(
        "--class",
        dest="release_class",
        choices=ALL_CLASSES,
        default=None,
        help="Restrict output to a single release class.",
    )
    parser.add_argument(
        "--release-selectable",
        action="store_true",
        help=(
            "Restrict output to release-selectable YAMLs "
            "(stable-release or preview-release)."
        ),
    )
    parser.add_argument(
        "--products",
        type=Path,
        default=PRODUCTS_DIR,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--builds",
        type=Path,
        default=DEFAULT_BUILDS_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--manual",
        type=Path,
        default=DEFAULT_MANUAL_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--compile-targets",
        dest="compile_targets",
        type=Path,
        default=DEFAULT_COMPILE_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        plan = classify(
            catalog_path=args.catalog,
            builds_path=args.builds,
            manual_path=args.manual,
            compile_path=args.compile_targets,
            products_dir=args.products,
        )
    except ClassifyError as exc:
        print(f"classify-all-yaml-release-matrix: {exc}", file=sys.stderr)
        return 2

    if args.json:
        records = filter_records(
            plan,
            release_class=args.release_class,
            release_selectable=args.release_selectable,
        )
        out = {
            "yaml_total": plan["yaml_total"],
            "counts": plan["counts"],
            "release_selectable": plan["release_selectable"],
            "stable_targets": plan["stable_targets"],
            "preview_targets": plan["preview_targets"],
            "records": records,
        }
        print(json.dumps(out, indent=2))
        return 0

    if args.summary:
        print(_render_summary(plan))
        return 0

    records = filter_records(
        plan,
        release_class=args.release_class,
        release_selectable=args.release_selectable,
    )
    if not records:
        print("(no YAMLs match the requested filter)")
        return 0
    print(_render_table(records))
    print()
    print(_render_summary(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
