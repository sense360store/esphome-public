#!/usr/bin/env python3
"""Customer docs site drift gates (SENSE360-CUSTOMER-DOCS-001 Phase 1).

A customer-doc factual claim that disagrees with its source catalogue
fails CI. Phase 1 pins:

- the fixed page spine: every room page carries the seven sections in
  order (What's in the box, Mount it, Flash it, Connect to Home
  Assistant, What you'll see, Tune it, Troubleshoot);
- publication state: Bathroom is the one room in the nav; the Bedroom
  and Kitchen room pages exist but stay OUT of the nav until the owner
  changes bundle visibility (unpublished rendering of OD-SOT-009 — the
  decision id appears here and in authoring comments only, never in
  rendered customer prose);
- flash instructions name only installer presets that exist in the
  WebFlash preset snapshot;
- box contents match the preset's component list (board labels);
- attachment honesty: room pages state radar attachments are not
  included (open owner decision rendered honestly);
- while the SOT mirror says no bundle is commercially available, no
  customer page carries buy/price/shop copy;
- no internal programme/tracking identifiers in rendered customer prose
  (HTML comments are authoring notes and are exempt);
- entity lists come from the generated tables (snippet includes of
  files that exist under site/generated/);
- zone-configuration guidance is linked to the sense360zones surface,
  never duplicated here.

Stdlib unittest only; runnable directly or under plain pytest.
"""

import json
import re
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DOCS = REPO_ROOT / "site" / "docs"
MKDOCS_YML = REPO_ROOT / "site" / "mkdocs.yml"
GENERATED = REPO_ROOT / "site" / "generated"
PRESET_SNAPSHOT = REPO_ROOT / "config" / "webflash-preset-snapshot.json"
SOT_MIRROR = REPO_ROOT / "config" / "sot-commercial-mirror.json"

SPINE = (
    "## What's in the box",
    "## Mount it",
    "## Flash it",
    "## Connect to Home Assistant",
    "## What you'll see",
    "## Tune it",
    "## Troubleshoot",
)

CUSTOMER_PAGES = [
    "rooms/bathroom.md",
    "rooms/bedroom.md",
    "rooms/kitchen.md",
    "zone-studio.md",
    "help/index.md",
    "advanced/index.md",
]

UNPUBLISHED_ROOMS = ("rooms/bedroom.md", "rooms/kitchen.md")

FORBIDDEN_COMMERCIAL = re.compile(
    r"buy now|add to cart|shop now|on sale|order now|price[ds]? at|£\d|\$\d",
    re.IGNORECASE,
)
# Programme/tracking identifier shapes (e.g. ABC-DEF-001, OD-SOT-004).
INTERNAL_ID = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)+-\d{3}\b")


def _rendered_prose(text):
    """The page text with HTML comments (authoring notes) removed."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _nav_paths(node, out):
    if isinstance(node, dict):
        for value in node.values():
            _nav_paths(value, out)
    elif isinstance(node, list):
        for item in node:
            _nav_paths(item, out)
    elif isinstance(node, str):
        out.append(node)


def nav_paths():
    config = yaml.safe_load(MKDOCS_YML.read_text(encoding="utf-8"))
    out = []
    _nav_paths(config.get("nav") or [], out)
    return out


class SpineTests(unittest.TestCase):
    def test_room_pages_carry_the_fixed_spine_in_order(self):
        for rel in ("rooms/bathroom.md", "rooms/bedroom.md", "rooms/kitchen.md"):
            with self.subTest(page=rel):
                text = (SITE_DOCS / rel).read_text(encoding="utf-8")
                positions = [text.find(h) for h in SPINE]
                self.assertNotIn(-1, positions, f"{rel}: missing spine section")
                self.assertEqual(
                    positions, sorted(positions), f"{rel}: spine out of order"
                )


class PublicationStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nav = nav_paths()

    def test_bathroom_is_in_the_nav(self):
        self.assertIn("rooms/bathroom.md", self.nav)

    def test_unpublished_rooms_stay_out_of_the_nav(self):
        for rel in UNPUBLISHED_ROOMS:
            with self.subTest(page=rel):
                self.assertTrue((SITE_DOCS / rel).is_file(), f"{rel} must exist")
                self.assertNotIn(
                    rel,
                    self.nav,
                    f"{rel} is built ready but must stay out of the nav "
                    "until the owner changes bundle visibility",
                )


class FactualClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = json.loads(PRESET_SNAPSHOT.read_text(encoding="utf-8"))
        cls.mirror = json.loads(SOT_MIRROR.read_text(encoding="utf-8"))
        cls.presets = {p["room_label"]: p for p in cls.snapshot["presets"]}

    def test_nav_room_flash_steps_name_existing_presets(self):
        # Every "Choose the **X** setup" instruction on a PUBLISHED room
        # page must name a preset that exists in the snapshot.
        for rel in nav_paths():
            if not rel.startswith("rooms/"):
                continue
            text = _rendered_prose(
                (SITE_DOCS / rel).read_text(encoding="utf-8")
            )
            for label in re.findall(r"Choose the \*\*([^*]+)\*\* setup", text):
                self.assertIn(
                    label,
                    self.presets,
                    f"{rel}: names preset {label!r} that is not in the "
                    "WebFlash preset snapshot",
                )

    def test_bathroom_box_contents_match_the_preset_components(self):
        text = (SITE_DOCS / "rooms/bathroom.md").read_text(encoding="utf-8")
        box = text.split("## What's in the box", 1)[1].split("## ", 1)[0]
        components = self.presets["Bathroom"]["components"]
        self.assertTrue(components)
        for component in components:
            self.assertIn(
                component["label"],
                box,
                f"bathroom box contents must list {component['label']} "
                "(from the preset snapshot)",
            )

    def test_room_pages_state_attachments_not_included(self):
        for rel in ("rooms/bathroom.md", "rooms/bedroom.md", "rooms/kitchen.md"):
            text = _rendered_prose(
                (SITE_DOCS / rel).read_text(encoding="utf-8")
            )
            self.assertIn(
                "not included",
                text,
                f"{rel}: radar attachments must be honestly rendered as "
                "not included while the owner decision is open",
            )

    def test_no_commercial_copy_while_nothing_is_available(self):
        if self.mirror["commercial_posture"]["any_bundle_available"]:
            self.skipTest("a bundle is commercially available per SOT")
        for rel in CUSTOMER_PAGES:
            text = _rendered_prose(
                (SITE_DOCS / rel).read_text(encoding="utf-8")
            )
            match = FORBIDDEN_COMMERCIAL.search(text)
            self.assertIsNone(
                match,
                f"{rel}: commercial copy {match.group(0)!r} while no SOT "
                "bundle is available" if match else None,
            )

    def test_no_internal_ids_in_rendered_prose(self):
        for rel in CUSTOMER_PAGES:
            text = _rendered_prose(
                (SITE_DOCS / rel).read_text(encoding="utf-8")
            )
            hits = INTERNAL_ID.findall(text)
            self.assertEqual(
                hits, [], f"{rel}: internal identifiers in customer prose"
            )

    def test_entity_lists_are_generated_includes(self):
        for rel in ("rooms/bathroom.md", "rooms/bedroom.md", "rooms/kitchen.md"):
            text = (SITE_DOCS / rel).read_text(encoding="utf-8")
            includes = re.findall(r'--8<--\s+"([^"]+)"', text)
            self.assertTrue(
                includes, f"{rel}: entity list must be a generated include"
            )
            for name in includes:
                self.assertTrue(
                    (GENERATED / name).is_file(),
                    f"{rel}: snippet {name} missing from site/generated/",
                )

    def test_home_page_channel_badges_match_the_release_matrix(self):
        # The hand-written channel badges on the home page must agree
        # with config/webflash-builds.json (found drifted once: the
        # Kitchen guide carried a stable badge after the recorded
        # preview demotion).
        builds = json.loads(
            (REPO_ROOT / "config" / "webflash-builds.json").read_text(
                encoding="utf-8"
            )
        )
        channel_by_stem = {
            b["config_string"].lower(): b["channel"]
            for b in builds["builds"]
        }
        text = (SITE_DOCS / "index.md").read_text(encoding="utf-8")
        rows = re.findall(
            r"\]\(products/([a-z0-9-]+)\.md\).*?s360-badge--(\w+)", text
        )
        self.assertTrue(rows, "home page product table rows not found")
        for stem, badge in rows:
            declared = channel_by_stem.get(stem)
            if declared is None:
                continue
            self.assertEqual(
                badge,
                declared,
                f"index.md badges {stem} as {badge!r} but the release "
                f"matrix declares {declared!r}",
            )

    def test_zone_studio_is_linked_not_duplicated(self):
        text = _rendered_prose(
            (SITE_DOCS / "zone-studio.md").read_text(encoding="utf-8")
        )
        self.assertIn("github.com/sense360store/sense360zones", text)
        # Guidance is owned by the add-on repository: this page must not
        # grow step-by-step zone-editing instructions.
        self.assertNotRegex(
            text,
            r"(?m)^\s*\d+\.\s",
            "zone-studio.md must link the owned guide, not duplicate "
            "step-by-step usage",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
