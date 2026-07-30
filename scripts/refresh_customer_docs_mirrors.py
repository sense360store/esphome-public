#!/usr/bin/env python3
"""Regenerate the customer-docs data mirrors (SENSE360-CUSTOMER-DOCS-001).

The customer docs site renders commercial names and installer preset facts
only from synchronized mirrors with provenance — never from hand-authored
copy (the programme's documentation-authority rules). This script reads
LOCAL checkouts of the owning repositories and regenerates:

  config/sot-commercial-mirror.json      from  sense360store/SOT bundles.yaml
  config/webflash-preset-snapshot.json   from  sense360store/WebFlash
                                               scripts/data/kits.json

Both mirrors are synchronized evidence, NEVER authority:

  - Commercial names, status, visibility and buyability are owned by SOT.
    SOT's validator defines status == "available" as the only commercial
    state meaning "a customer can buy this"; the mirror derives
    `commercially_available` from that single rule and fails loudly on a
    contradictory explicit flag rather than inventing a second model.
  - Installer preset identity (which room presets exist, their labels and
    component lists) is owned by WebFlash. The snapshot lets docs name
    presets that actually exist; it never adds or reorders presets.
  - Never hand-edit either mirror. Refresh from clean checkouts at merged
    main commits and commit the diff with the source SHAs recorded here.

Usage:
    python3 scripts/refresh_customer_docs_mirrors.py \
        --sot-path /path/to/SOT --webflash-path /path/to/WebFlash
    ... --check   # regenerate in memory, exit non-zero on drift

Normal CI does not run --check (CI has no sibling checkouts);
tests/test_customer_docs_mirrors.py guards schema, provenance and the
no-commercial-claim rules offline instead. Requires PyYAML for the SOT
side only.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_MIRROR_PATH = REPO_ROOT / "config" / "sot-commercial-mirror.json"
PRESET_SNAPSHOT_PATH = REPO_ROOT / "config" / "webflash-preset-snapshot.json"

# SOT's lifecycle rule (SOT scripts/validate.py): the one commercial state.
COMMERCIAL_STATUSES = {"available"}

BUNDLE_FIELDS = (
    "id",
    "name",
    "status",
    "visibility",
    "tier",
    "physical_bundle_sku",
    "recommended_rooms",
    "webflash_config",
)

PRESET_FIELDS = (
    "sku",
    "display_name",
    "room_label",
    "recommended_rooms",
    "description",
    "presentation",
    "commercial_bundle_id",
    "recommended",
    "components",
)


def _git_sha(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _git_commit_date(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "show", "-s", "--format=%cs", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def build_sot_mirror(sot_path: Path) -> dict:
    import yaml

    doc = yaml.safe_load((sot_path / "bundles.yaml").read_text(encoding="utf-8"))
    rows = []
    for bundle in doc.get("bundles") or []:
        status = bundle.get("status")
        derived = status in COMMERCIAL_STATUSES
        explicit = bundle.get("buyable")
        if explicit is not None and bool(explicit) != derived:
            raise SystemExit(
                f"refresh: bundle {bundle.get('id')!r} explicit buyable="
                f"{explicit!r} contradicts SOT lifecycle status {status!r}"
            )
        row = {k: bundle.get(k) for k in BUNDLE_FIELDS if bundle.get(k) is not None}
        row["commercially_available"] = derived
        rows.append(row)
    return {
        "schema_version": 1,
        "role": (
            "Synchronized SOT commercial-surface MIRROR for the customer docs "
            "site (SENSE360-CUSTOMER-DOCS-001). Not commercial authority: "
            "bundle names, contents, lifecycle status, visibility and "
            "buyability are owned by sense360store/SOT (bundles.yaml). "
            "Refresh with scripts/refresh_customer_docs_mirrors.py; never "
            "hand-author it as independent truth."
        ),
        "provenance": {
            "source_repo": "sense360store/SOT",
            "source_sha": _git_sha(sot_path),
            "source_commit_date": _git_commit_date(sot_path),
            "source_files": ["bundles.yaml"],
            "generator": "scripts/refresh_customer_docs_mirrors.py",
        },
        "commercial_posture": {
            "any_bundle_available": any(r["commercially_available"] for r in rows),
            "note": (
                "Derived from SOT lifecycle status alone (status == "
                "'available'). While false, customer docs must not render "
                "buy/price/shop copy for any bundle."
            ),
        },
        "bundles": rows,
    }


def build_preset_snapshot(webflash_path: Path) -> dict:
    kits_doc = json.loads(
        (webflash_path / "scripts" / "data" / "kits.json").read_text(encoding="utf-8")
    )
    rows = []
    for kit in kits_doc.get("kits") or []:
        rows.append({k: kit.get(k) for k in PRESET_FIELDS if kit.get(k) is not None})
    return {
        "schema_version": 1,
        "role": (
            "Synchronized WebFlash installer-preset SNAPSHOT for the customer "
            "docs site (SENSE360-CUSTOMER-DOCS-001). Not preset authority: "
            "room presets are owned by sense360store/WebFlash "
            "(scripts/data/kits.json); a preset is an installer firmware "
            "preset, never a commercial listing. Docs may name only presets "
            "present here. Refresh with "
            "scripts/refresh_customer_docs_mirrors.py; never hand-author."
        ),
        "provenance": {
            "source_repo": "sense360store/WebFlash",
            "source_sha": _git_sha(webflash_path),
            "source_commit_date": _git_commit_date(webflash_path),
            "source_files": ["scripts/data/kits.json"],
            "generator": "scripts/refresh_customer_docs_mirrors.py",
        },
        "presets": rows,
    }


def _dump(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sot-path", type=Path, required=True)
    parser.add_argument("--webflash-path", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    outputs = {
        SOT_MIRROR_PATH: _dump(build_sot_mirror(args.sot_path)),
        PRESET_SNAPSHOT_PATH: _dump(build_preset_snapshot(args.webflash_path)),
    }
    drift = []
    for path, text in outputs.items():
        if args.check:
            current = path.read_text(encoding="utf-8") if path.is_file() else ""
            if current != text:
                drift.append(str(path.relative_to(REPO_ROOT)))
        else:
            path.write_text(text, encoding="utf-8")
            print(f"wrote {path.relative_to(REPO_ROOT)}")
    if drift:
        print("stale mirrors: " + ", ".join(drift), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
