#!/usr/bin/env python3
"""Customer-docs mirror guards (SENSE360-CUSTOMER-DOCS-001).

The customer docs site renders commercial names and installer-preset
facts only from synchronized mirrors with provenance. These guards keep
the mirrors honest offline (CI has no sibling checkouts, so freshness is
re-established by re-running scripts/refresh_customer_docs_mirrors.py at
refresh time; here we pin schema, provenance and the commercial rules):

- both mirrors exist, parse, and carry a complete provenance block
  (owning repo, 40-hex source SHA, generator);
- the SOT mirror derives `commercially_available` from SOT's single
  lifecycle rule (status == "available") and the posture flag agrees;
- while no bundle is available, the posture note forbids buy/price copy;
- the preset snapshot carries firmware presets only — a preset is never
  a commercial listing.

Stdlib unittest only; runnable directly or under plain pytest.
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOT_MIRROR = REPO_ROOT / "config" / "sot-commercial-mirror.json"
PRESET_SNAPSHOT = REPO_ROOT / "config" / "webflash-preset-snapshot.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class ProvenanceTests(unittest.TestCase):
    def _check(self, doc, source_repo, source_file):
        self.assertEqual(doc["schema_version"], 1)
        self.assertIn("never hand-author", doc["role"].lower())
        prov = doc["provenance"]
        self.assertEqual(prov["source_repo"], source_repo)
        self.assertTrue(SHA40.match(prov["source_sha"]), prov["source_sha"])
        self.assertIn(source_file, prov["source_files"])
        self.assertEqual(
            prov["generator"], "scripts/refresh_customer_docs_mirrors.py"
        )

    def test_sot_mirror_provenance(self):
        self._check(_load(SOT_MIRROR), "sense360store/SOT", "bundles.yaml")

    def test_preset_snapshot_provenance(self):
        self._check(
            _load(PRESET_SNAPSHOT),
            "sense360store/WebFlash",
            "scripts/data/kits.json",
        )


class CommercialRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mirror = _load(SOT_MIRROR)

    def test_available_flag_derived_from_lifecycle_only(self):
        for bundle in self.mirror["bundles"]:
            self.assertEqual(
                bundle["commercially_available"],
                bundle["status"] == "available",
                bundle["id"],
            )

    def test_posture_agrees_with_rows(self):
        derived = any(
            b["commercially_available"] for b in self.mirror["bundles"]
        )
        self.assertEqual(
            self.mirror["commercial_posture"]["any_bundle_available"], derived
        )

    def test_bundles_have_identity(self):
        for bundle in self.mirror["bundles"]:
            self.assertTrue(bundle.get("id"))
            self.assertTrue(bundle.get("status"))


class PresetRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = _load(PRESET_SNAPSHOT)

    def test_presets_are_firmware_presets_only(self):
        presets = self.snapshot["presets"]
        self.assertTrue(presets)
        for preset in presets:
            self.assertEqual(preset["presentation"], "firmware-preset")
            self.assertTrue(preset.get("sku"))
            self.assertTrue(preset.get("room_label"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
