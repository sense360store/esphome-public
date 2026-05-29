#!/usr/bin/env python3
"""Read-only product-catalog cross-file consistency validator (PRODUCT-003).

This validator does not mutate any file and does not generate scaffold YAMLs.
It cross-checks ``config/product-catalog.json`` against:

  - ``config/webflash-builds.json``        (WebFlash build matrix)
  - ``config/webflash-compatibility.json`` (WebFlash naming contract snapshot)
  - ``config/hardware-catalog.json``       (Canonical SKU table)
  - ``scripts/product_name_mapper.py``     (Artifact name mapper)
  - product YAML paths under ``products/``
  - WebFlash wrapper YAML paths under ``products/webflash/``

Cross-cutting checks (every entry):

  - ``product_yaml`` is a non-empty string and the file exists.
  - ``status`` is one of the catalog's declared lifecycle statuses.
  - ``webflash_build_matrix`` is a boolean.
  - At least one of ``config_string`` / ``legacy_config_id`` is present.
  - ``product_yaml`` is unique across the catalog.
  - ``config_string`` is unique where present.
  - ``legacy_config_id`` is unique where present.

Production entries (``status: production``) additionally require:

  - ``config_string``, ``version``, ``channel``, ``artifact_name``,
    ``webflash_wrapper``, ``hardware_status``, ``hardware`` (non-empty map),
    ``modules`` (non-empty map), with ``webflash_build_matrix: true``.
  - Appears in ``config/webflash-builds.json`` by ``config_string``.
  - ``artifact_name`` equals
    ``generate_webflash_filename(basename(product_yaml, .yaml), version, channel)``
    from ``scripts/product_name_mapper.py``.
  - ``webflash_wrapper`` file exists.
  - Basename of ``webflash_wrapper`` (without ``.yaml``) equals
    ``config_string`` lower-cased.
  - Every SKU in ``hardware`` is present in ``config/hardware-catalog.json``.

Preview entries (``status: preview``) additionally require:

  - ``config_string``, ``product_yaml``, ``hardware_status``.
  - If ``webflash_build_matrix: true`` then ``webflash_wrapper`` is set and exists.
  - ``channel`` (where present) is not ``stable``.
  - ``config_string`` is not in ``release_one_required_configs``.

Blocked entries (``status: blocked``) additionally require:

  - ``blocker``, ``reason`` non-empty.
  - ``webflash_build_matrix: false``.
  - No ``artifact_name``.
  - Not present in ``config/webflash-builds.json``.

Legacy-compatible entries (``status: legacy-compatible``) additionally require:

  - ``webflash_build_matrix: false``.
  - No ``artifact_name``.
  - No ``webflash_wrapper``.
  - No ``config_string`` (the WebFlash ``config_string`` namespace is
    reserved for WebFlash-shippable entries; legacy-compatible entries use
    ``legacy_config_id`` instead).
  - Not present in ``config/webflash-builds.json``.

Cross-cutting forbidden-token guard (PRODUCT-STALE-001):

  - No catalog entry's ``config_string`` may contain any token from
    ``config/webflash-compatibility.json`` ``forbidden_tokens``. This
    mirrors the existing build-matrix-level guard in
    ``tests/validate_webflash_builds.py`` at the catalog layer so a
    stale alias (e.g. ``Bathroom``, ``Comfort``, ``Presence``) cannot
    leak into any catalog row, even one with
    ``webflash_build_matrix: false``.

The validator is read-only. The intended use is:

  python3 scripts/validate_product_catalog_consistency.py

which prints a summary and exits non-zero on any error. It also supports
a checklist mode for diagnosing what would be needed to safely add (or
finish adding) a product:

  python3 scripts/validate_product_catalog_consistency.py \
      --checklist Ceiling-POE-VentIQ-RoomIQ
  python3 scripts/validate_product_catalog_consistency.py \
      --product products/sense360-ceiling-poe-ventiq-roomiq.yaml
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
COMPAT_PATH = REPO_ROOT / "config" / "webflash-compatibility.json"
HARDWARE_PATH = REPO_ROOT / "config" / "hardware-catalog.json"

# Reuse the canonical mapper so this validator agrees with the build job.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from product_name_mapper import generate_webflash_filename  # noqa: E402

EXPECTED_LIFECYCLE_STATUSES = (
    "production",
    "preview",
    "compile-only",
    "hardware-pending",
    "blocked",
    "legacy-compatible",
    "deprecated",
    "removed",
)

WEBFLASH_ELIGIBLE_STATUSES = frozenset({"production", "preview"})

PRODUCTION_REQUIRED_STRING_FIELDS = (
    "config_string",
    "product_yaml",
    "webflash_wrapper",
    "artifact_name",
    "version",
    "channel",
    "hardware_status",
)

PRODUCTION_REQUIRED_MAP_FIELDS = (
    "hardware",
    "modules",
)

PREVIEW_REQUIRED_STRING_FIELDS = (
    "config_string",
    "product_yaml",
    "hardware_status",
)

BLOCKED_REQUIRED_STRING_FIELDS = (
    "blocker",
    "reason",
)


class ProductCatalogConsistencyValidator:
    """Cross-file consistency validator for the product catalog.

    Read-only. Does not mutate any catalog, build matrix, wrapper, or
    product YAML.
    """

    def __init__(self, repo_root: Path = REPO_ROOT) -> None:
        self.repo_root = Path(repo_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self._loaded = False
        self.catalog: Dict[str, Any] = {}
        self.builds_doc: Dict[str, Any] = {}
        self.compat: Dict[str, Any] = {}
        self.hardware_doc: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_json(self, abs_path: Path, label: str) -> Optional[Any]:
        if not abs_path.is_file():
            self.errors.append(f"{label}: file does not exist ({abs_path})")
            return None
        try:
            return json.loads(abs_path.read_text())
        except json.JSONDecodeError as exc:
            self.errors.append(f"{label}: JSON parse error - {exc}")
            return None

    def load(self) -> bool:
        catalog = self._load_json(CATALOG_PATH, "config/product-catalog.json")
        builds = self._load_json(BUILDS_PATH, "config/webflash-builds.json")
        compat = self._load_json(COMPAT_PATH, "config/webflash-compatibility.json")
        hw = self._load_json(HARDWARE_PATH, "config/hardware-catalog.json")
        if catalog is None or builds is None or compat is None or hw is None:
            return False
        self.catalog = catalog if isinstance(catalog, dict) else {}
        self.builds_doc = builds if isinstance(builds, dict) else {}
        self.compat = compat if isinstance(compat, dict) else {}
        self.hardware_doc = hw if isinstance(hw, dict) else {}
        self._loaded = True
        return True

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def _products(self) -> List[Dict[str, Any]]:
        products = self.catalog.get("products", [])
        return [p for p in products if isinstance(p, dict)]

    def _build_config_strings(self) -> set:
        builds = self.builds_doc.get("builds", [])
        return {
            b.get("config_string")
            for b in builds
            if isinstance(b, dict) and b.get("config_string")
        }

    def _hardware_skus(self) -> set:
        items = self.hardware_doc.get("items", [])
        return {i.get("sku") for i in items if isinstance(i, dict) and i.get("sku")}

    def _release_one_required(self) -> set:
        return set(self.compat.get("release_one_required_configs", []))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _err(self, entry_label: str, msg: str) -> None:
        self.errors.append(f"{entry_label}: {msg}")

    def _warn(self, entry_label: str, msg: str) -> None:
        self.warnings.append(f"{entry_label}: {msg}")

    @staticmethod
    def _entry_label(entry: Dict[str, Any], idx: int) -> str:
        if entry.get("config_string"):
            return f"entry[{idx}] config_string={entry['config_string']!r}"
        if entry.get("legacy_config_id"):
            return f"entry[{idx}] legacy_config_id={entry['legacy_config_id']!r}"
        if entry.get("product_yaml"):
            return f"entry[{idx}] product_yaml={entry['product_yaml']!r}"
        return f"entry[{idx}]"

    @staticmethod
    def _wrapper_basename_stem(rel: str) -> str:
        return Path(rel).stem

    @staticmethod
    def _product_key_from_yaml(rel: str) -> str:
        """Reproduce the build-time product key the workflow passes to the mapper.

        The release workflow derives ``matrix.product`` from
        ``basename(product_yaml, .yaml)``. We use the same derivation so the
        catalog's declared ``artifact_name`` is checked against the same value
        CI will produce.
        """
        return Path(rel).stem

    # ------------------------------------------------------------------
    # Per-entry validation
    # ------------------------------------------------------------------

    def _validate_common(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        status = entry.get("status")
        if status not in EXPECTED_LIFECYCLE_STATUSES:
            self._err(
                label,
                f"status {status!r} is not one of "
                f"{list(EXPECTED_LIFECYCLE_STATUSES)}",
            )

        wbm = entry.get("webflash_build_matrix")
        if not isinstance(wbm, bool):
            self._err(
                label,
                "webflash_build_matrix must be a boolean "
                f"(got {type(wbm).__name__})",
            )

        rel = entry.get("product_yaml")
        if status == "removed":
            # A ``removed`` tombstone must NOT carry a ``product_yaml`` that
            # still resolves to an active YAML file (PRODUCT-DEP-001,
            # "Required metadata for removal"). Absence is the expected shape;
            # if a path is present it must not resolve (e.g. a retained
            # legacy-compatible archival relationship would be a different
            # status, not ``removed``).
            if isinstance(rel, str) and rel and (self.repo_root / rel).is_file():
                self._err(
                    label,
                    "removed tombstone must not have a product_yaml that "
                    f"resolves to an active YAML file: {rel}",
                )
        elif not isinstance(rel, str) or rel == "":
            self._err(label, "product_yaml must be a non-empty string")
        elif not (self.repo_root / rel).is_file():
            self._err(label, f"product_yaml file does not exist: {rel}")

        has_cs = "config_string" in entry and entry["config_string"] not in (None, "")
        has_legacy = "legacy_config_id" in entry and entry["legacy_config_id"] not in (
            None,
            "",
        )
        if not (has_cs or has_legacy):
            self._err(
                label,
                "entry must have at least one of 'config_string' or "
                "'legacy_config_id'",
            )

    def _validate_uniqueness(self) -> None:
        seen_paths: Dict[str, int] = {}
        seen_config_strings: Dict[str, int] = {}
        seen_legacy_ids: Dict[str, int] = {}
        config_strings_set: set = set()

        for idx, entry in enumerate(self._products()):
            label = self._entry_label(entry, idx)
            rel = entry.get("product_yaml")
            if isinstance(rel, str) and rel:
                if rel in seen_paths:
                    self._err(
                        label,
                        f"duplicate product_yaml {rel!r} "
                        f"(also at entry[{seen_paths[rel]}])",
                    )
                else:
                    seen_paths[rel] = idx

            cs = entry.get("config_string")
            if isinstance(cs, str) and cs:
                if cs in seen_config_strings:
                    self._err(
                        label,
                        f"duplicate config_string {cs!r} "
                        f"(also at entry[{seen_config_strings[cs]}])",
                    )
                else:
                    seen_config_strings[cs] = idx
                    config_strings_set.add(cs)

            legacy = entry.get("legacy_config_id")
            if isinstance(legacy, str) and legacy:
                if legacy in seen_legacy_ids:
                    self._err(
                        label,
                        f"duplicate legacy_config_id {legacy!r} "
                        f"(also at entry[{seen_legacy_ids[legacy]}])",
                    )
                else:
                    seen_legacy_ids[legacy] = idx

        for idx, entry in enumerate(self._products()):
            label = self._entry_label(entry, idx)
            legacy = entry.get("legacy_config_id")
            if isinstance(legacy, str) and legacy in config_strings_set:
                self._err(
                    label,
                    f"legacy_config_id {legacy!r} collides with a "
                    "WebFlash config_string; the two namespaces must stay "
                    "disjoint",
                )

    def _validate_production(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        for field in PRODUCTION_REQUIRED_STRING_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or value == "":
                self._err(
                    label,
                    f"production entry missing required string field " f"{field!r}",
                )

        for field in PRODUCTION_REQUIRED_MAP_FIELDS:
            value = entry.get(field)
            if not isinstance(value, dict) or len(value) == 0:
                self._err(
                    label,
                    f"production entry missing required non-empty map field "
                    f"{field!r}",
                )

        if entry.get("webflash_build_matrix") is not True:
            self._err(
                label,
                "production entry must have webflash_build_matrix=true",
            )

        cs = entry.get("config_string")
        if isinstance(cs, str) and cs:
            if cs not in self._build_config_strings():
                self._err(
                    label,
                    f"production entry config_string {cs!r} is not present "
                    "in config/webflash-builds.json",
                )

        wrapper = entry.get("webflash_wrapper")
        if isinstance(wrapper, str) and wrapper:
            if not (self.repo_root / wrapper).is_file():
                self._err(
                    label,
                    f"webflash_wrapper file does not exist: {wrapper}",
                )
            if isinstance(cs, str) and cs:
                expected_stem = cs.lower()
                actual_stem = self._wrapper_basename_stem(wrapper)
                if actual_stem != expected_stem:
                    self._err(
                        label,
                        f"webflash_wrapper basename {actual_stem!r} does not "
                        f"match lowercased config_string {expected_stem!r}",
                    )

        rel = entry.get("product_yaml")
        version = entry.get("version")
        channel = entry.get("channel")
        artifact = entry.get("artifact_name")
        if (
            isinstance(rel, str)
            and isinstance(version, str)
            and isinstance(channel, str)
            and isinstance(artifact, str)
        ):
            product_key = self._product_key_from_yaml(rel)
            produced = generate_webflash_filename(product_key, version, channel)
            if produced != artifact:
                self._err(
                    label,
                    f"artifact_name {artifact!r} does not match mapper "
                    f"output {produced!r} for product key {product_key!r} "
                    f"v{version} {channel}",
                )

        hardware = entry.get("hardware")
        if isinstance(hardware, dict):
            known = self._hardware_skus()
            for slot, sku in hardware.items():
                if not isinstance(sku, str) or not sku:
                    self._err(
                        label,
                        f"hardware slot {slot!r} has invalid SKU {sku!r}",
                    )
                elif sku not in known:
                    self._err(
                        label,
                        f"hardware slot {slot!r} SKU {sku!r} is not in "
                        "config/hardware-catalog.json",
                    )

    def _validate_preview(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        for field in PREVIEW_REQUIRED_STRING_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or value == "":
                self._err(
                    label,
                    f"preview entry missing required string field {field!r}",
                )

        if entry.get("webflash_build_matrix") is True:
            wrapper = entry.get("webflash_wrapper")
            if not isinstance(wrapper, str) or wrapper == "":
                self._err(
                    label,
                    "preview entry with webflash_build_matrix=true must "
                    "have a webflash_wrapper",
                )
            elif not (self.repo_root / wrapper).is_file():
                self._err(
                    label,
                    f"preview entry webflash_wrapper file does not exist: "
                    f"{wrapper}",
                )

        channel = entry.get("channel")
        if isinstance(channel, str) and channel == "stable":
            self._err(
                label,
                "preview entry must not use channel 'stable'; promote to "
                "production first",
            )

        cs = entry.get("config_string")
        if isinstance(cs, str) and cs and cs in self._release_one_required():
            self._err(
                label,
                f"preview entry config_string {cs!r} is in "
                "release_one_required_configs; only production entries may "
                "claim a Release-One required slot",
            )

    def _validate_blocked(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        for field in BLOCKED_REQUIRED_STRING_FIELDS:
            value = entry.get(field)
            if not isinstance(value, str) or value == "":
                self._err(
                    label,
                    f"blocked entry missing required string field {field!r}",
                )

        if entry.get("webflash_build_matrix") is not False:
            self._err(
                label,
                "blocked entry must have webflash_build_matrix=false",
            )

        if "artifact_name" in entry:
            self._err(
                label,
                "blocked entry must not have artifact_name",
            )

        cs = entry.get("config_string")
        if isinstance(cs, str) and cs and cs in self._build_config_strings():
            self._err(
                label,
                f"blocked entry config_string {cs!r} appears in "
                "config/webflash-builds.json",
            )

    def _validate_legacy_compatible(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        if entry.get("webflash_build_matrix") is not False:
            self._err(
                label,
                "legacy-compatible entry must have webflash_build_matrix=false",
            )

        if "artifact_name" in entry:
            self._err(
                label,
                "legacy-compatible entry must not have artifact_name",
            )

        if "webflash_wrapper" in entry:
            self._err(
                label,
                "legacy-compatible entry must not have webflash_wrapper",
            )

        if "config_string" in entry:
            self._err(
                label,
                "legacy-compatible entry must not have config_string "
                "(use legacy_config_id; the WebFlash config_string "
                "namespace is reserved for WebFlash-shippable entries)",
            )

        cs = entry.get("config_string")
        if isinstance(cs, str) and cs and cs in self._build_config_strings():
            self._err(
                label,
                f"legacy-compatible entry config_string {cs!r} appears in "
                "config/webflash-builds.json",
            )

    def _validate_forbidden_tokens(
        self,
        entry: Dict[str, Any],
        label: str,
    ) -> None:
        """Reject any catalog entry whose ``config_string`` contains a token
        from ``config/webflash-compatibility.json`` ``forbidden_tokens``.

        Mirrors the existing build-matrix-level guard at the catalog layer so
        a stale alias cannot leak into any catalog row, regardless of
        ``webflash_build_matrix`` value. PRODUCT-STALE-001.
        """
        cs = entry.get("config_string")
        if not isinstance(cs, str) or not cs:
            return
        forbidden = self.compat.get("forbidden_tokens", [])
        if not isinstance(forbidden, list):
            return
        forbidden_set = {t for t in forbidden if isinstance(t, str)}
        if not forbidden_set:
            return
        for token in cs.split("-"):
            if token in forbidden_set:
                self._err(
                    label,
                    f"config_string {cs!r} contains forbidden token "
                    f"{token!r} (see config/webflash-compatibility.json "
                    "forbidden_tokens and docs/webflash-contract.md)",
                )

    # ------------------------------------------------------------------
    # Driver
    # ------------------------------------------------------------------

    def validate_all(self) -> Tuple[int, int]:
        if not self._loaded and not self.load():
            return 0, 0

        self._validate_uniqueness()

        products = self._products()
        for idx, entry in enumerate(products):
            label = self._entry_label(entry, idx)
            self._validate_common(entry, label)
            self._validate_forbidden_tokens(entry, label)
            status = entry.get("status")
            if status == "production":
                self._validate_production(entry, label)
            elif status == "preview":
                self._validate_preview(entry, label)
            elif status == "blocked":
                self._validate_blocked(entry, label)
            elif status == "legacy-compatible":
                self._validate_legacy_compatible(entry, label)

        return len(products), len(self.errors)

    def print_summary(self, total: int) -> None:
        print("\n" + "=" * 70)
        print(
            f"Product catalog consistency: {total} entries checked, "
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)"
        )
        print("=" * 70)
        if self.errors:
            print(f"\nErrors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  ❌ {e}")
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  ⚠️  {w}")
        if not self.errors and not self.warnings:
            print("\n✅ Product catalog is internally consistent.")

    # ------------------------------------------------------------------
    # Checklist mode
    # ------------------------------------------------------------------

    def find_entry(
        self,
        identifier: str,
    ) -> Optional[Dict[str, Any]]:
        """Resolve a catalog entry by config_string or legacy_config_id."""
        for entry in self._products():
            if entry.get("config_string") == identifier:
                return entry
            if entry.get("legacy_config_id") == identifier:
                return entry
        return None

    def find_entry_by_product_yaml(
        self,
        rel_path: str,
    ) -> Optional[Dict[str, Any]]:
        for entry in self._products():
            if entry.get("product_yaml") == rel_path:
                return entry
        return None

    def checklist(
        self,
        identifier: Optional[str] = None,
        product_yaml: Optional[str] = None,
    ) -> List[Tuple[bool, str]]:
        """Return ordered (ok, description) checklist items for an entry.

        ``identifier`` is matched against ``config_string`` first, then
        ``legacy_config_id``. ``product_yaml`` is matched against
        ``product_yaml``. If the entry is not found, every item is unchecked
        with an explanation describing the expected shape.
        """
        if not self._loaded:
            self.load()

        entry: Optional[Dict[str, Any]] = None
        if product_yaml is not None:
            entry = self.find_entry_by_product_yaml(product_yaml)
        elif identifier is not None:
            entry = self.find_entry(identifier)

        items: List[Tuple[bool, str]] = []

        if entry is None:
            ident_repr = identifier or product_yaml or "<unspecified>"
            items.append((False, f"catalog entry exists for {ident_repr!r}"))
            items.append((False, "product YAML exists (path: <set in catalog entry>)"))
            items.append(
                (False, "WebFlash wrapper exists (path: <set if WebFlash-shippable>)")
            )
            items.append((False, "WebFlash wrapper basename matches config string"))
            items.append((False, "webflash-builds entry exists if production"))
            items.append((False, "artifact mapper agrees with declared artifact_name"))
            items.append((False, "hardware SKUs declared (production only)"))
            items.append(
                (False, "blocked modules declared (production only, where applicable)")
            )
            return items

        status = entry.get("status")
        items.append(
            (
                True,
                f"catalog entry exists (status={status!r})",
            )
        )

        rel = entry.get("product_yaml")
        if isinstance(rel, str) and rel and (self.repo_root / rel).is_file():
            items.append((True, f"product YAML exists ({rel})"))
        else:
            items.append(
                (
                    False,
                    f"product YAML exists (catalog: {rel!r})",
                )
            )

        wrapper = entry.get("webflash_wrapper")
        wrapper_required = (
            status in WEBFLASH_ELIGIBLE_STATUSES
            and entry.get("webflash_build_matrix") is True
        )
        if wrapper_required:
            if (
                isinstance(wrapper, str)
                and wrapper
                and (self.repo_root / wrapper).is_file()
            ):
                items.append((True, f"WebFlash wrapper exists ({wrapper})"))
            else:
                items.append(
                    (
                        False,
                        f"WebFlash wrapper exists (catalog: {wrapper!r})",
                    )
                )
            cs = entry.get("config_string")
            if (
                isinstance(wrapper, str)
                and wrapper
                and isinstance(cs, str)
                and cs
                and self._wrapper_basename_stem(wrapper) == cs.lower()
            ):
                items.append(
                    (
                        True,
                        "WebFlash wrapper basename matches config string",
                    )
                )
            else:
                items.append(
                    (
                        False,
                        "WebFlash wrapper basename matches config string",
                    )
                )
        else:
            items.append(
                (
                    True,
                    "WebFlash wrapper not required (not WebFlash-shippable)",
                )
            )
            items.append(
                (
                    True,
                    "WebFlash wrapper basename check skipped",
                )
            )

        cs = entry.get("config_string")
        in_builds = isinstance(cs, str) and cs and cs in self._build_config_strings()
        if status == "production":
            items.append(
                (
                    bool(in_builds),
                    f"webflash-builds entry exists (config_string={cs!r})",
                )
            )
        elif status == "blocked":
            items.append(
                (
                    not in_builds,
                    f"webflash-builds entry absent (blocked, config_string={cs!r})",
                )
            )
        else:
            items.append(
                (
                    True,
                    f"webflash-builds entry rule N/A for status={status!r}",
                )
            )

        if status == "production":
            rel = entry.get("product_yaml")
            version = entry.get("version")
            channel = entry.get("channel")
            artifact = entry.get("artifact_name")
            mapper_ok = False
            mapper_detail = ""
            if (
                isinstance(rel, str)
                and isinstance(version, str)
                and isinstance(channel, str)
                and isinstance(artifact, str)
            ):
                produced = generate_webflash_filename(
                    self._product_key_from_yaml(rel), version, channel
                )
                mapper_ok = produced == artifact
                mapper_detail = f"mapper={produced!r}, catalog={artifact!r}"
            else:
                mapper_detail = "missing product_yaml/version/channel/artifact_name"
            items.append(
                (
                    mapper_ok,
                    f"artifact mapper agrees with declared artifact_name "
                    f"({mapper_detail})",
                )
            )
        else:
            items.append(
                (
                    True,
                    "artifact mapper check N/A (only required for production)",
                )
            )

        if status == "production":
            hardware = entry.get("hardware")
            if isinstance(hardware, dict) and hardware:
                known = self._hardware_skus()
                unknown = [
                    sku
                    for sku in hardware.values()
                    if not isinstance(sku, str) or sku not in known
                ]
                if not unknown:
                    skus = ", ".join(sorted(set(hardware.values())))
                    items.append((True, f"hardware SKUs declared ({skus})"))
                else:
                    items.append(
                        (
                            False,
                            f"hardware SKUs declared (unknown: {unknown})",
                        )
                    )
            else:
                items.append((False, "hardware SKUs declared"))

            blocked = entry.get("blocked_modules", [])
            if isinstance(blocked, list) and blocked:
                items.append(
                    (
                        True,
                        f"blocked modules declared ({', '.join(blocked)})",
                    )
                )
            else:
                items.append(
                    (
                        True,
                        "blocked modules declared (none — optional)",
                    )
                )
        else:
            items.append(
                (
                    True,
                    "hardware SKUs check N/A (only required for production)",
                )
            )
            items.append(
                (
                    True,
                    "blocked modules check N/A (only meaningful for production)",
                )
            )

        return items

    @staticmethod
    def format_checklist(
        identifier: str,
        items: List[Tuple[bool, str]],
    ) -> str:
        lines = [f"Product add checklist for {identifier!r}:"]
        for ok, desc in items:
            mark = "[x]" if ok else "[ ]"
            lines.append(f"  {mark} {desc}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "PRODUCT-003 read-only product-catalog consistency validator. "
            "Cross-checks config/product-catalog.json against the WebFlash "
            "build matrix, the WebFlash compatibility snapshot, the hardware "
            "catalog, the artifact mapper, and the product / wrapper YAML "
            "paths. Use --checklist or --product to print an add-product "
            "checklist for one entry instead of validating the whole catalog."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--checklist",
        metavar="CONFIG_STRING_OR_LEGACY_ID",
        help=(
            "Print an add-product checklist for the given config_string or "
            "legacy_config_id. Read-only."
        ),
    )
    group.add_argument(
        "--product",
        metavar="PATH",
        help=(
            "Print an add-product checklist for the catalog entry whose "
            "product_yaml matches the given repo-relative path. Read-only."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    validator = ProductCatalogConsistencyValidator()
    if not validator.load():
        for e in validator.errors:
            print(f"  ❌ {e}", file=sys.stderr)
        return 1

    if args.checklist is not None:
        items = validator.checklist(identifier=args.checklist)
        print(validator.format_checklist(args.checklist, items))
        return 0

    if args.product is not None:
        items = validator.checklist(product_yaml=args.product)
        print(validator.format_checklist(args.product, items))
        return 0

    print("🔍 Validating product catalog cross-file consistency...\n")
    total, _failed = validator.validate_all()
    validator.print_summary(total)
    return 1 if validator.errors else 0


if __name__ == "__main__":
    sys.exit(main())
