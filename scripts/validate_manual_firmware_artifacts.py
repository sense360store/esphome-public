#!/usr/bin/env python3
"""Validate the non-release manual firmware artifact lane (MANUAL-FIRMWARE-CI-ARTIFACTS-001).

This script consumes ``config/manual-firmware-artifacts.json`` — the data
source for the ``workflow_dispatch``-only
``.github/workflows/manual-firmware-artifacts.yml`` lane — and enforces the
non-release guarantees required by ``MANUAL-FIRMWARE-ARTIFACT-POLICY-001``
(PR #619). It is a metadata / policy validator and a small helper the
workflow calls to build its matrix and compute artifact names; it never
compiles, never publishes, and never writes any firmware file.

The lane it guards exists to produce **only** temporary, expiring GitHub
Actions artifacts for point-to-point operator handoff. This validator asserts
that the config can never quietly turn into a release lane:

  * ``artifact_mode`` is exactly ``manual-candidate``;
  * ``release`` is ``false``, ``webflash`` is ``false``, and
    ``release_channel`` is ``null`` (no release channel may be set);
  * artifact naming carries an explicit ``-manual-<short-sha>-nonrelease``
    marker and never a release version (``vX.Y.Z``) or channel suffix
    (``-stable`` / ``-preview``);
  * every candidate points at a top-level ``products/sense360-*.yaml``
    (never a ``products/webflash/*`` wrapper — no WebFlash wrapper is added);
  * every candidate's ``product_yaml`` exists and is registered as a
    ``compile-only`` target carrying ``compile_validation_status:
    validated-full-compile`` with ``webflash_exposure_allowed_now=false``;
  * every candidate is present in ``config/product-catalog.json``; under
    owner declaration HW-RELEASE-001 (``docs/hw-release-001.md``) the catalog
    entry may carry ``webflash_build_matrix=true`` with an ``artifact_name``
    and ``webflash_wrapper`` on a NON-STABLE channel (FanPWM / FanDAC:
    preview; FanRelay: experimental) — the manual lane itself never reuses
    the catalog release name, and a stable-channel fan entry is refused.

Modes::

    python3 scripts/validate_manual_firmware_artifacts.py --metadata-only
    python3 scripts/validate_manual_firmware_artifacts.py --print-matrix
    python3 scripts/validate_manual_firmware_artifacts.py \
        --artifact-name products/sense360-ceiling-poe-fanpwm.yaml <short_sha>

``--metadata-only`` is the default and is always run first by the other
modes, so a malformed config can never produce a matrix or a name.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
TARGETS_PATH = REPO_ROOT / "config" / "compile-only-targets.json"
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"

ARTIFACT_MODE = "manual-candidate"
MANUAL_MARKER = "manual"
NONRELEASE_SUFFIX = "nonrelease"
REQUIRED_COMPILE_STATUS = "validated-full-compile"

# A release artifact name looks like Sense360-<Product>-vX.Y.Z-<channel>.bin.
# A manual artifact name must match NONE of these patterns.
_RELEASE_VERSION_RE = re.compile(r"v\d+\.\d+\.\d+")
_RELEASE_CHANNEL_RE = re.compile(r"-(stable|preview|beta)\b")

REQUIRED_CANDIDATE_FIELDS = (
    "id",
    "family",
    "product_yaml",
    "compile_only_target_id",
)

# The three fan candidates this lane must cover (and only these).
EXPECTED_PRODUCT_YAMLS = frozenset(
    {
        "products/sense360-ceiling-poe-ventiq-fanrelay-roomiq.yaml",
        "products/sense360-ceiling-poe-fanpwm.yaml",
        "products/sense360-ceiling-poe-fandac.yaml",
    }
)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_basename(product_yaml: str, short_sha: str) -> str:
    """Return the non-release manual artifact basename for a product YAML.

    Shape: ``<product-stem>-manual-<short-sha>-nonrelease``. Carries the
    product/config name, the reviewed commit short SHA, and the
    manual / non-release marker; never a release version or channel suffix.
    """
    stem = Path(product_yaml).stem
    short_sha = (short_sha or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{4,40}", short_sha):
        raise ValueError(
            f"short_sha must be 4-40 hex chars, got {short_sha!r}"
        )
    return f"{stem}-{MANUAL_MARKER}-{short_sha}-{NONRELEASE_SUFFIX}"


def _looks_like_release_name(name: str) -> bool:
    return bool(_RELEASE_VERSION_RE.search(name) or _RELEASE_CHANNEL_RE.search(name))


def validate(
    config: Dict[str, Any],
    targets_doc: Dict[str, Any],
    catalog_doc: Dict[str, Any],
) -> List[str]:
    """Return a list of error strings (empty == valid)."""
    errors: List[str] = []

    if config.get("schema_version") != 1:
        errors.append(
            f"schema_version must be 1; got {config.get('schema_version')!r}"
        )

    if config.get("artifact_mode") != ARTIFACT_MODE:
        errors.append(
            f"artifact_mode must be {ARTIFACT_MODE!r}; got "
            f"{config.get('artifact_mode')!r}"
        )

    # The lane is non-release by construction: these three flags lock it in.
    if config.get("release") is not False:
        errors.append("release must be false (this is a non-release lane)")
    if config.get("webflash") is not False:
        errors.append("webflash must be false (no WebFlash exposure)")
    if config.get("release_channel") is not None:
        errors.append(
            "release_channel must be null; the manual lane cannot set a "
            f"release channel (got {config.get('release_channel')!r})"
        )

    naming = config.get("naming")
    if not isinstance(naming, dict):
        errors.append("naming must be an object")
        naming = {}
    if naming.get("marker") != MANUAL_MARKER:
        errors.append(f"naming.marker must be {MANUAL_MARKER!r}")
    if naming.get("nonrelease_suffix") != NONRELEASE_SUFFIX:
        errors.append(f"naming.nonrelease_suffix must be {NONRELEASE_SUFFIX!r}")

    # Cross-reference indexes.
    targets_by_id: Dict[str, Dict[str, Any]] = {
        t.get("id"): t
        for t in targets_doc.get("targets", []) or []
        if isinstance(t, dict) and t.get("id")
    }
    catalog_by_yaml: Dict[str, Dict[str, Any]] = {
        p.get("product_yaml"): p
        for p in catalog_doc.get("products", []) or []
        if isinstance(p, dict) and p.get("product_yaml")
    }

    candidates = config.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append("candidates must be a non-empty array")
        return errors

    seen_ids: set[str] = set()
    seen_yamls: set[str] = set()

    for idx, cand in enumerate(candidates, start=1):
        if not isinstance(cand, dict):
            errors.append(f"candidate #{idx}: must be a JSON object")
            continue

        for field in REQUIRED_CANDIDATE_FIELDS:
            if not cand.get(field):
                errors.append(f"candidate #{idx}: missing required field {field!r}")

        cid = cand.get("id")
        if cid:
            if cid in seen_ids:
                errors.append(f"candidate #{idx}: duplicate id {cid!r}")
            seen_ids.add(cid)

        product_yaml = cand.get("product_yaml", "")
        if product_yaml:
            seen_yamls.add(product_yaml)

            # No WebFlash wrapper: candidates point at the top-level product
            # YAML, never a products/webflash/* wrapper.
            if not product_yaml.startswith("products/sense360-"):
                errors.append(
                    f"candidate {cid!r}: product_yaml must be a top-level "
                    f"products/sense360-*.yaml, got {product_yaml!r}"
                )
            if product_yaml.startswith("products/webflash/"):
                errors.append(
                    f"candidate {cid!r}: product_yaml must not be a "
                    "products/webflash/* wrapper (no WebFlash wrapper is added)"
                )
            if not (REPO_ROOT / product_yaml).is_file():
                errors.append(
                    f"candidate {cid!r}: product_yaml not found: {product_yaml}"
                )

            # The generated artifact name must never look like a release name.
            sample = artifact_basename(product_yaml, "deadbeef")
            if _looks_like_release_name(sample):
                errors.append(
                    f"candidate {cid!r}: artifact name {sample!r} resembles a "
                    "release artifact (version / channel); manual names must not"
                )

        # Compile-only target cross-reference: must be full-compile validated
        # and not WebFlash-exposed.
        target_id = cand.get("compile_only_target_id")
        if target_id:
            target = targets_by_id.get(target_id)
            if target is None:
                errors.append(
                    f"candidate {cid!r}: compile_only_target_id {target_id!r} "
                    "not found in config/compile-only-targets.json"
                )
            else:
                if target.get("product_yaml") != product_yaml:
                    errors.append(
                        f"candidate {cid!r}: compile-only target {target_id!r} "
                        f"product_yaml {target.get('product_yaml')!r} does not "
                        f"match candidate product_yaml {product_yaml!r}"
                    )
                if target.get("compile_validation_status") != REQUIRED_COMPILE_STATUS:
                    errors.append(
                        f"candidate {cid!r}: compile-only target {target_id!r} "
                        f"must carry compile_validation_status "
                        f"{REQUIRED_COMPILE_STATUS!r}"
                    )
                if target.get("webflash_exposure_allowed_now") is not False:
                    errors.append(
                        f"candidate {cid!r}: compile-only target {target_id!r} "
                        "must have webflash_exposure_allowed_now=false"
                    )

        # Product-catalog cross-reference. HW-RELEASE-001
        # (docs/hw-release-001.md): the fan candidates are release-eligible
        # catalog entries on their non-stable channels now, so the checks
        # here are channel teeth (never stable, never production) plus the
        # unchanged rule that the manual lane never reuses the catalog
        # release artifact_name (enforced by the -manual-candidate- name
        # shape asserted elsewhere in this validator).
        if product_yaml:
            entry = catalog_by_yaml.get(product_yaml)
            if entry is None:
                errors.append(
                    f"candidate {cid!r}: product_yaml {product_yaml!r} not "
                    "found in config/product-catalog.json"
                )
            else:
                if entry.get("status") == "production":
                    errors.append(
                        f"candidate {cid!r}: catalog status must never be "
                        "'production' (fan configs are never stable)"
                    )
                if entry.get("channel") == "stable":
                    errors.append(
                        f"candidate {cid!r}: catalog channel must never be "
                        "'stable' (HW-RELEASE-001 admits fans on preview / "
                        "experimental only)"
                    )
                artifact = entry.get("artifact_name") or ""
                if artifact.endswith("-stable.bin"):
                    errors.append(
                        f"candidate {cid!r}: catalog artifact_name "
                        f"{artifact!r} must never carry the -stable channel "
                        "suffix"
                    )

    # The lane must cover exactly the three fan candidates.
    missing = EXPECTED_PRODUCT_YAMLS - seen_yamls
    if missing:
        errors.append(
            "missing expected fan candidate product_yaml(s): "
            + ", ".join(sorted(missing))
        )
    extra = seen_yamls - EXPECTED_PRODUCT_YAMLS
    if extra:
        errors.append(
            "unexpected product_yaml(s) for the manual fan lane: "
            + ", ".join(sorted(extra))
        )

    return errors


def build_matrix(config: Dict[str, Any]) -> Dict[str, Any]:
    rows = []
    for cand in config.get("candidates", []) or []:
        rows.append(
            {
                "id": cand.get("id"),
                "family": cand.get("family"),
                "product_yaml": cand.get("product_yaml"),
            }
        )
    return {"include": rows}


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--metadata-only", action="store_true", default=False)
    mode.add_argument("--print-matrix", action="store_true", default=False)
    mode.add_argument(
        "--artifact-name",
        nargs=2,
        metavar=("PRODUCT_YAML", "SHORT_SHA"),
        help="Print the non-release manual artifact basename for a product YAML.",
    )
    args = parser.parse_args(argv)

    config = _load_json(CONFIG_PATH)
    targets_doc = _load_json(TARGETS_PATH)
    catalog_doc = _load_json(CATALOG_PATH)

    errors = validate(config, targets_doc, catalog_doc)
    if errors:
        sys.stderr.write(
            f"Manual firmware artifact config validation FAILED "
            f"({len(errors)} error(s)):\n"
        )
        for err in errors:
            sys.stderr.write(f"  - {err}\n")
        return 1

    if args.print_matrix:
        print(json.dumps(build_matrix(config), separators=(",", ":")))
        return 0

    if args.artifact_name:
        product_yaml, short_sha = args.artifact_name
        print(artifact_basename(product_yaml, short_sha))
        return 0

    print(
        "OK: config/manual-firmware-artifacts.json validates "
        f"({len(config.get('candidates', []))} non-release manual candidate(s))."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
