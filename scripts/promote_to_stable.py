#!/usr/bin/env python3
"""Promote a WebFlash config from preview to stable (esphome-public side).

This is the esphome-public half of the cross-repo promote-to-stable helper.
It performs the single, deterministic, auditable edit that promotes config C
to stable version V across the two esphome-public source-of-truth files,
replacing the hand edit that this is easy to get subtly wrong:

  1. ``config/product-catalog.json`` : the matching product entry becomes
       ``status=production``, ``channel=stable``, ``version=V``,
       ``artifact_name=<stable artifact>`` (and ``channel_tier=stable`` when
       that mirror field is present on the entry).
  2. ``config/webflash-builds.json`` : the matching build row becomes
       ``channel=stable``, ``version=V``, ``artifact_name=<stable artifact>``
       (and ``channel_tier=stable`` when present).

The stable ``artifact_name`` is computed with the SAME mapper the release job
and the consistency validator use
(``scripts/product_name_mapper.generate_webflash_filename``), so the promoted
catalog stays internally consistent with what CI would produce.

What this tool deliberately does NOT do:

  - It never commits, pushes, signs, tags, or merges. It only edits the two
    JSON files for a human to review.
  - It does not decide whether a promotion is justified (hardware / bench /
    owner sign-off). It only performs the mechanical edits once a human has
    decided to promote.
  - It does not scrub the human-authored prose fields (``notes``,
    ``stable_blocker``, ``commercial_posture`` flags, preview warning copy).
    Those are review surface; the tool lists the preview-only fields that a
    reviewer may want to revisit, but leaves them untouched so the diff stays
    minimal and obvious.

In ``--dry-run`` mode it writes nothing and prints exactly what it would
change. When it does write (dry-run off), it then runs the read-only
``scripts/validate_product_catalog_consistency.py`` and surfaces the result so
the operator immediately sees whether the promotion left the catalog
consistent.

Usage::

    python3 scripts/promote_to_stable.py <config_string> <version> [--dry-run]
    python3 scripts/promote_to_stable.py Ceiling-POE-AirIQ-RoomIQ 1.1.0 --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_REL = "config/product-catalog.json"
BUILDS_REL = "config/webflash-builds.json"
VALIDATOR_REL = "scripts/validate_product_catalog_consistency.py"

# Reuse the canonical artifact mapper so this tool agrees with the build job
# and scripts/validate_product_catalog_consistency.py.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from product_name_mapper import generate_webflash_filename  # noqa: E402

STABLE_CHANNEL = "stable"
PRODUCTION_STATUS = "production"

# A promotion only makes sense from these lifecycle states. ``blocked`` (e.g.
# FanTRIAC), ``removed``, ``deprecated`` and ``legacy-compatible`` are refused
# outright so the tool can never be used to flip a blocked product to stable.
PROMOTABLE_STATUSES = frozenset(
    {"preview", "hardware-pending", "compile-only", "production"}
)

# Production-required fields the consistency validator demands. Used only for an
# advisory pre-check so the operator is warned BEFORE applying if the entry is
# not actually production-ready (the authoritative gate stays the validator).
PRODUCTION_REQUIRED_STRINGS = (
    "webflash_wrapper",
    "hardware_status",
)
PRODUCTION_REQUIRED_MAPS = ("hardware", "modules")

# Preview-only fields a reviewer may want to revisit after promotion. The tool
# does NOT touch these (they are human-authored prose / posture), it only points
# them out.
PREVIEW_ONLY_REVIEW_FIELDS = (
    "webflash_exposure_class",
    "warning_copy_key",
    "release_note_warning",
    "release_state",
    "stable_blocker",
)

VERSION_RE = re.compile(r"^\d+(?:\.\d+)*$")


class PromotionError(Exception):
    """Raised for an unrecoverable refusal (bad input or unsafe state)."""


@dataclass
class FieldChange:
    field: str
    old: Any
    new: Any

    @property
    def changed(self) -> bool:
        return self.old != self.new


@dataclass
class Plan:
    config_string: str
    version: str
    artifact_name: str
    catalog_changes: List[FieldChange] = field(default_factory=list)
    builds_changes: List[FieldChange] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    review_fields: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(c.changed for c in self.catalog_changes) or any(
            c.changed for c in self.builds_changes
        )


def normalize_version(raw: str) -> str:
    """Strip an optional leading ``v`` and validate a clean numeric version.

    Refuses anything that is not a dotted run of integers (for example a
    pre-release suffix such as ``1.0.0-rc1``) so an ambiguous version can never
    be written into an artifact name.
    """
    if raw is None:
        raise PromotionError("version is required")
    candidate = raw.strip()
    if candidate[:1] in ("v", "V"):
        candidate = candidate[1:]
    if not VERSION_RE.match(candidate):
        raise PromotionError(
            f"version {raw!r} is not a clean numeric version (expected e.g. "
            "1.0.5); refusing rather than guess"
        )
    return candidate


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, obj: Dict[str, Any]) -> None:
    # esphome JSON is 2-space indented and keeps non-ASCII literally
    # (ensure_ascii=False). This round-trips byte-identical, so only the
    # intended values move in the diff.
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _find_by_config_string(
    items: List[Dict[str, Any]], config_string: str
) -> Optional[Dict[str, Any]]:
    for item in items:
        if isinstance(item, dict) and item.get("config_string") == config_string:
            return item
    return None


def _planned_field_changes(
    entry: Dict[str, Any],
    *,
    set_status: bool,
    version: str,
    artifact_name: str,
) -> List[FieldChange]:
    """Compute the (status,) channel, version, artifact_name (and channel_tier)
    changes for one entry. ``channel_tier`` is only touched when it already
    exists on the entry, because it definitionally mirrors ``channel``.
    """
    changes: List[FieldChange] = []
    if set_status:
        changes.append(FieldChange("status", entry.get("status"), PRODUCTION_STATUS))
    changes.append(FieldChange("channel", entry.get("channel"), STABLE_CHANNEL))
    changes.append(FieldChange("version", entry.get("version"), version))
    changes.append(
        FieldChange("artifact_name", entry.get("artifact_name"), artifact_name)
    )
    if "channel_tier" in entry:
        changes.append(
            FieldChange("channel_tier", entry.get("channel_tier"), STABLE_CHANNEL)
        )
    return changes


def compute_plan(
    catalog: Dict[str, Any],
    builds: Dict[str, Any],
    config_string: str,
    raw_version: str,
) -> Plan:
    """Pure planning: read the two loaded documents and return the set of edits.

    Raises :class:`PromotionError` on any refusal. Performs no I/O writes.
    """
    version = normalize_version(raw_version)

    products = [p for p in catalog.get("products", []) if isinstance(p, dict)]
    entry = _find_by_config_string(products, config_string)
    if entry is None:
        raise PromotionError(
            f"config_string {config_string!r} not found in {CATALOG_REL}; "
            "nothing to promote"
        )

    status = entry.get("status")
    if status not in PROMOTABLE_STATUSES:
        raise PromotionError(
            f"catalog entry {config_string!r} has status {status!r}, which is "
            f"not promotable (promotable: {sorted(PROMOTABLE_STATUSES)}). A "
            "blocked / removed / deprecated / legacy-compatible product can not "
            "be promoted to stable by this tool."
        )

    product_yaml = entry.get("product_yaml")
    if not isinstance(product_yaml, str) or not product_yaml:
        raise PromotionError(
            f"catalog entry {config_string!r} has no product_yaml; cannot derive "
            "the stable artifact name"
        )

    build_rows = [b for b in builds.get("builds", []) if isinstance(b, dict)]
    build_row = _find_by_config_string(build_rows, config_string)
    if build_row is None:
        raise PromotionError(
            f"config_string {config_string!r} not found in {BUILDS_REL}; the "
            "WebFlash build matrix must already carry the row that is being "
            "promoted"
        )

    product_key = Path(product_yaml).stem
    artifact_name = generate_webflash_filename(product_key, version, STABLE_CHANNEL)

    plan = Plan(
        config_string=config_string,
        version=version,
        artifact_name=artifact_name,
    )
    plan.catalog_changes = _planned_field_changes(
        entry, set_status=True, version=version, artifact_name=artifact_name
    )
    plan.builds_changes = _planned_field_changes(
        build_row, set_status=False, version=version, artifact_name=artifact_name
    )

    # Advisory pre-check: warn if the entry is not production-ready. The
    # authoritative gate stays validate_product_catalog_consistency.py, run
    # after a real apply.
    for f in PRODUCTION_REQUIRED_STRINGS:
        value = entry.get(f)
        if not isinstance(value, str) or not value:
            plan.warnings.append(
                f"catalog entry is missing production-required field {f!r}; "
                "the consistency validator will fail until it is set"
            )
    for f in PRODUCTION_REQUIRED_MAPS:
        value = entry.get(f)
        if not isinstance(value, dict) or not value:
            plan.warnings.append(
                f"catalog entry is missing production-required map {f!r}; "
                "the consistency validator will fail until it is set"
            )

    plan.review_fields = [f for f in PREVIEW_ONLY_REVIEW_FIELDS if f in entry]
    return plan


def _format_value(value: Any) -> str:
    if value is None:
        return "<absent>"
    return json.dumps(value, ensure_ascii=False)


def print_plan(plan: Plan, *, dry_run: bool) -> None:
    mode = "DRY RUN (no files written)" if dry_run else "APPLY"
    print("=" * 72)
    print(f"promote-to-stable (esphome-public) — {mode}")
    print(f"  config_string : {plan.config_string}")
    print(f"  version       : {plan.version}")
    print(f"  artifact_name : {plan.artifact_name}")
    print("=" * 72)

    def render(title: str, rel: str, changes: List[FieldChange]) -> None:
        print(f"\n{title}  ({rel})")
        any_change = False
        for change in changes:
            if change.changed:
                any_change = True
                print(
                    f"    {change.field}: {_format_value(change.old)} "
                    f"-> {_format_value(change.new)}"
                )
            else:
                print(f"    {change.field}: {_format_value(change.old)} (unchanged)")
        if not any_change:
            print("    (already at the target state — no field changes)")

    render("product-catalog entry", CATALOG_REL, plan.catalog_changes)
    render("webflash-builds row", BUILDS_REL, plan.builds_changes)

    if plan.warnings:
        print("\nWARNINGS:")
        for w in plan.warnings:
            print(f"  ! {w}")

    if plan.review_fields:
        print(
            "\nReviewer note: the following preview-only fields are LEFT "
            "UNTOUCHED and may need manual cleanup for a stable entry:"
        )
        print(f"  {', '.join(plan.review_fields)}")


def apply_plan(
    catalog: Dict[str, Any],
    builds: Dict[str, Any],
    plan: Plan,
) -> None:
    entry = _find_by_config_string(
        [p for p in catalog.get("products", []) if isinstance(p, dict)],
        plan.config_string,
    )
    build_row = _find_by_config_string(
        [b for b in builds.get("builds", []) if isinstance(b, dict)],
        plan.config_string,
    )
    assert entry is not None and build_row is not None  # guaranteed by compute_plan
    for change in plan.catalog_changes:
        entry[change.field] = change.new
    for change in plan.builds_changes:
        build_row[change.field] = change.new

    dump_json(REPO_ROOT / CATALOG_REL, catalog)
    dump_json(REPO_ROOT / BUILDS_REL, builds)


def run_validator() -> int:
    print("\n" + "-" * 72)
    print(f"Running {VALIDATOR_REL} ...")
    print("-" * 72)
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / VALIDATOR_REL)],
        cwd=str(REPO_ROOT),
    )
    return result.returncode


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Promote a WebFlash config from preview to stable in the "
            "esphome-public catalog + build matrix. Edits files only; never "
            "commits, pushes, signs, or merges."
        )
    )
    parser.add_argument("config_string", help="WebFlash config string to promote")
    parser.add_argument("version", help="target stable version, e.g. 1.0.5")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print exactly what would change without writing any file",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    catalog = load_json(REPO_ROOT / CATALOG_REL)
    builds = load_json(REPO_ROOT / BUILDS_REL)

    try:
        plan = compute_plan(catalog, builds, args.config_string, args.version)
    except PromotionError as exc:
        print(f"REFUSING TO PROCEED: {exc}", file=sys.stderr)
        return 2

    print_plan(plan, dry_run=args.dry_run)

    if args.dry_run:
        print(
            "\nDry run only. Re-run without --dry-run to write the changes, then "
            f"review the diff and {VALIDATOR_REL} output."
        )
        return 0

    if not plan.has_changes:
        print("\nNothing to write (already at the target state).")
        return 0

    apply_plan(catalog, builds, plan)
    print("\nWrote changes to:")
    print(f"  {CATALOG_REL}")
    print(f"  {BUILDS_REL}")

    rc = run_validator()
    if rc != 0:
        print(
            "\nThe consistency validator reported errors. Review the promotion, "
            "fix the entry (or revert), and re-run the validator.",
            file=sys.stderr,
        )
        return 1
    print(
        "\nDone. Review the diff and open a review-first PR. This tool did not "
        "commit, push, sign, or merge anything."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
