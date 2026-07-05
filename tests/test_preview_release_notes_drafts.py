#!/usr/bin/env python3
"""Regression guard for the preview WebFlash release-note DRAFTS (dry-run).

RELEASE-PREVIEW-RELEASE-NOTES-DRYRUN-001.

Locks the invariants of the dry-run release-note drafts authored for the three
metadata-ready preview WebFlash build rows added by
``RELEASE-PREVIEW-WEBFLASH-BUILD-ROWS-001`` (``Ceiling-POE-AirIQ-RoomIQ``,
``Ceiling-POE-RoomIQ``, ``Ceiling-POE-RoomIQ-LED``).

For every preview WebFlash build row this guard asserts release-note coverage:

  * the three metadata-ready (``release_state: metadata-ready-unpublished``)
    preview rows each have a committed draft under
    ``docs/release-notes/preview/<config-string>.md``;
  * the already-published VentIQ LED preview row
    (``Ceiling-POE-VentIQ-RoomIQ-LED``) is covered by its recorded published
    release proof (``docs/webflash-release-proof.md``, archived under
    DOCS-DISPOSITION-001 with its content recoverable via the
    ``docs/archive-index.md`` row) and is NOT re-drafted here, and the
    stable Bathroom baseline (``Ceiling-POE-VentIQ-RoomIQ``) is not drafted
    as a preview either.

For each of the three drafts it asserts (task item 3 / 6):

  * the draft passes the WebFlash release-body contract
    (``scripts/validate-webflash-release-notes.py``) on the ``preview`` channel
    — the four required H2 sections are present and non-empty;
  * the draft clearly says PREVIEW firmware, not stable, not recommended, not a
    customer default, not hardware verified, not buyable as a public shop
    product, firmware-build proof only citing hosted compile run ``26821900127``,
    with no hardware / bench / compliance / commercial-availability proof
    claimed, and points normal customers to the stable Bathroom PoE release;
  * the draft carries NO stable / recommended / default language for the build
    itself (every "recommended" / "default" mention is negated, no affirmative
    stable/recommended/default claim appears, and the draft's own artifact is
    the ``-preview.bin`` — the only ``-stable.bin`` it names is the Bathroom
    cross-reference).

And for the three metadata-ready build rows it re-asserts the
compile-evidence reference, the hidden / not-buyable commercial posture, the
preview warning copy, and the absence of stable promotion — plus the hard
guardrails (no ``manifest.json`` / ``firmware/sources.json`` / ``.bin`` /
Release / tag produced; no TRIAC or fan draft; launch SKU unchanged).

Uses Python's stdlib unittest (matching the no-pytest convention the other
validators in this repo use). Run with::

    python3 tests/test_preview_release_notes_drafts.py
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
SHOP_PATH = REPO_ROOT / "config" / "shop-commercial-source-of-truth.json"
DRAFT_DIR = REPO_ROOT / "docs" / "release-notes" / "preview"
# docs/webflash-release-proof.md was archived under DOCS-DISPOSITION-001;
# the published LED preview coverage is checked against its archive row.
ARCHIVE_INDEX = REPO_ROOT / "docs" / "archive-index.md"
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"
SHARED_PREVIEW_NOTES = "v1.0.0-preview.md"

COMPILE_RUN_ID = 26821900127

# The three rows this dry-run drafted, by config string. The committed drafts
# are HISTORICAL dry-run records of the v1.0.0-preview cut.
# STABLE-PROMOTION-RECONCILE-001: two of the three have since been promoted to
# the stable channel (Ceiling-POE-RoomIQ v1.0.5 on 2026-06-08,
# Ceiling-POE-AirIQ-RoomIQ v1.0.6 on 2026-06-09, owner-waiver promotions), so
# only the LED room bundle is still metadata-ready on the preview channel.
DRAFTED_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
    "Ceiling-POE-RoomIQ-LED",
)
# The LED room bundle is the only PREVIEW-channel metadata-ready row (these
# configs are pinned to the preview-channel contract below). The FanTRIAC
# experimental self-build mains build (TRIAC-COMMISSIONING-001) is also
# metadata-ready, but on the EXPERIMENTAL channel, so it is tracked separately.
STILL_METADATA_READY_CONFIGS = ("Ceiling-POE-RoomIQ-LED",)
EXPERIMENTAL_METADATA_READY_CONFIGS = ("Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",)
PROMOTED_CONFIGS = (
    "Ceiling-POE-AirIQ-RoomIQ",
    "Ceiling-POE-RoomIQ",
)
# The preview artifact each draft named at drafting time (historical, static).
DRAFTED_ARTIFACTS = {
    cs: f"Sense360-{cs}-v1.0.0-preview.bin" for cs in DRAFTED_CONFIGS
}
STABLE_CONFIG = "Ceiling-POE-VentIQ-RoomIQ"
PUBLISHED_LED_PREVIEW_CONFIG = "Ceiling-POE-VentIQ-RoomIQ-LED"
# The stable Bathroom artifact the drafts cross-referenced at drafting time
# (historical text pin; the live ledger artifact has since been bumped).
STABLE_BATHROOM_ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.0-stable.bin"
LAUNCH_SKU = "S360-KIT-BATH-P"

FAN_DRIVER_TOKENS = ("FanRelay", "FanPWM", "FanDAC", "FanTRIAC")

# Warning-copy phrases every draft must clearly state (task item 3), matched
# case-insensitively against the whitespace-normalised body.
REQUIRED_PHRASES = (
    "preview firmware",
    "not stable",
    "not recommended",
    "not a customer default",
    "not hardware verified",
    "not buyable as a public shop product",
    "firmware-build proof only",
    str(COMPILE_RUN_ID),
    "no hardware, bench, compliance, or commercial-availability proof",
    "stable bathroom poe release",
)

# Affirmative claims that would mark the preview build stable / recommended /
# default; none may appear in a preview draft (task item 6).
FORBIDDEN_AFFIRMATIVE = (
    "is stable",
    "now stable",
    "marked stable",
    "promoted to stable",
    "is recommended",
    "is the default",
    "is a default",
    "is default",
    "customer-ready",
    "production-ready",
)


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_webflash_release_notes_for_drafts", VALIDATOR_PATH
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_VALIDATOR = _load_validator()


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _normalise(text: str) -> str:
    """Lowercase, drop Markdown blockquote markers / backticks, collapse runs of
    whitespace (incl. newlines) to single spaces so wrapped prose still matches.
    """
    lines = [re.sub(r"^\s*>\s?", "", ln) for ln in text.splitlines()]
    joined = " ".join(lines).replace("`", "")
    return re.sub(r"\s+", " ", joined).lower()


def _draft_path(config_string: str) -> Path:
    return DRAFT_DIR / f"{config_string.lower()}.md"


def _builds() -> List[Dict[str, Any]]:
    return _load_json(BUILDS_PATH)["builds"]


def _by_cs() -> Dict[str, Dict[str, Any]]:
    return {b["config_string"]: b for b in _builds()}


def _preview_rows() -> List[Dict[str, Any]]:
    return [b for b in _builds() if b.get("channel") == "preview"]


def _metadata_ready_rows() -> List[Dict[str, Any]]:
    return [
        b
        for b in _builds()
        if b.get("release_state") == "metadata-ready-unpublished"
    ]


class MetadataReadySelectionTests(unittest.TestCase):
    """The dry-run drafted the three then-metadata-ready preview rows; after
    the promotions only the LED room bundle is still metadata-ready."""

    def test_metadata_ready_rows_are_the_unpromoted_configs(self) -> None:
        # The unpromoted preview LED room bundle plus the FanTRIAC experimental
        # self-build mains build (TRIAC-COMMISSIONING-001), which is on the
        # experimental channel (its channel/warning contract is asserted
        # separately, not under the preview-channel rows above).
        got = sorted(b["config_string"] for b in _metadata_ready_rows())
        self.assertEqual(
            got,
            sorted(STILL_METADATA_READY_CONFIGS + EXPERIMENTAL_METADATA_READY_CONFIGS),
        )

    def test_metadata_ready_rows_are_non_stable_channel(self) -> None:
        # Metadata-ready rows are never stable: the LED room bundle is on the
        # preview channel; the FanTRIAC experimental self-build mains build
        # (TRIAC-COMMISSIONING-001) is on the experimental channel.
        for b in _metadata_ready_rows():
            with self.subTest(config_string=b["config_string"]):
                self.assertIn(b["channel"], ("preview", "experimental"))

    def test_promoted_rows_left_the_preview_channel(self) -> None:
        by_cs = _by_cs()
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertEqual(by_cs[cs]["channel"], "stable")
                self.assertNotIn("release_state", by_cs[cs])


class DraftFilesExistTests(unittest.TestCase):
    """Task item 2 / 6: each drafted row keeps its committed dry-run draft."""

    def test_each_drafted_row_has_a_draft(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertTrue(
                    _draft_path(cs).is_file(),
                    f"missing release-note draft for {cs}: {_draft_path(cs)}",
                )

    def test_draft_basename_follows_lowercase_config_convention(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                self.assertEqual(_draft_path(cs).name, f"{cs.lower()}.md")


class DraftStructuralContractTests(unittest.TestCase):
    """Task item 6: drafts validate against the WebFlash release-body contract."""

    def test_each_draft_passes_release_notes_validator_on_preview(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                body = _draft_path(cs).read_text(encoding="utf-8")
                errors = _VALIDATOR.validate_body(body, channel="preview")
                self.assertEqual(errors, [], f"{cs}: {errors}")

    def test_each_draft_has_the_four_required_h2_sections(self) -> None:
        required = {"Changelog", "Known Issues", "Features", "Hardware Requirements"}
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                body = _draft_path(cs).read_text(encoding="utf-8")
                sections = _VALIDATOR._parse_sections(body)
                self.assertTrue(
                    required.issubset(sections.keys()),
                    f"{cs}: missing sections {required - set(sections.keys())}",
                )


class DraftWarningCopyTests(unittest.TestCase):
    """Task item 3: every draft clearly states the preview warning copy."""

    def test_each_draft_states_every_required_phrase(self) -> None:
        for cs in DRAFTED_CONFIGS:
            norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
            for phrase in REQUIRED_PHRASES:
                with self.subTest(config_string=cs, phrase=phrase):
                    self.assertIn(
                        phrase,
                        norm,
                        f"{cs}: draft is missing required warning phrase "
                        f"{phrase!r}",
                    )

    def test_each_draft_cites_hosted_compile_run(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                self.assertIn("compile run", norm)
                self.assertIn(str(COMPILE_RUN_ID), norm)

    def test_each_draft_points_customers_to_stable_bathroom_release(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                self.assertIn("stable bathroom poe release", norm)
                self.assertIn(STABLE_BATHROOM_ARTIFACT.lower(), norm)
                self.assertIn(LAUNCH_SKU.lower(), norm)

    def test_each_draft_marks_itself_a_dry_run_draft(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                self.assertIn("dry-run draft only", norm)
                self.assertIn("not attached to any github release", norm)


class DraftNoStableRecommendedDefaultLanguageTests(unittest.TestCase):
    """Task item 6: no stable / recommended / default language for the build."""

    def test_recommended_is_always_negated(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                self.assertEqual(
                    norm.count("recommended"),
                    norm.count("not recommended"),
                    f"{cs}: every 'recommended' mention must be 'not recommended'",
                )

    def test_default_is_always_negated(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                self.assertEqual(
                    norm.count("default"),
                    norm.count("not a customer default"),
                    f"{cs}: every 'default' mention must be 'not a customer "
                    "default'",
                )

    def test_no_affirmative_stable_recommended_default_claim(self) -> None:
        for cs in DRAFTED_CONFIGS:
            norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
            for bad in FORBIDDEN_AFFIRMATIVE:
                with self.subTest(config_string=cs, phrase=bad):
                    self.assertNotIn(
                        bad,
                        norm,
                        f"{cs}: preview draft must not claim {bad!r}",
                    )

    def test_draft_self_artifact_is_preview_only(self) -> None:
        # The draft's own artifact is the -preview.bin it was drafted with
        # (historical pin — the promoted rows' live artifacts are stable now);
        # the only -stable.bin it names is the Bathroom stable cross-reference.
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                norm = _normalise(_draft_path(cs).read_text(encoding="utf-8"))
                own = DRAFTED_ARTIFACTS[cs]
                self.assertTrue(own.endswith("-preview.bin"))
                self.assertIn(own.lower(), norm)
                self.assertEqual(
                    norm.count("-stable.bin"),
                    1,
                    f"{cs}: the only -stable.bin reference must be the Bathroom "
                    "stable cross-reference",
                )
                self.assertIn(STABLE_BATHROOM_ARTIFACT.lower(), norm)


class MetadataReadyRowPostureTests(unittest.TestCase):
    """Task item 6: each drafted build row carries the compile-evidence
    reference and the hidden / not-buyable posture; the unpromoted row keeps
    the preview warning copy while the promoted rows dropped the preview-only
    fields on promotion."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_cs = _by_cs()

    def test_rows_cite_firmware_build_compile_evidence(self) -> None:
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                ev = self.by_cs[cs].get("compile_evidence")
                self.assertIsInstance(ev, dict)
                self.assertEqual(ev.get("run_id"), COMPILE_RUN_ID)
                self.assertEqual(ev.get("proof_class"), "firmware-build-only")
                self.assertEqual(ev.get("result"), "success")

    def test_rows_carry_warning_copy_matching_promotion_state(self) -> None:
        for cs in STILL_METADATA_READY_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row.get("warning_copy_key"), "preview")
                self.assertIn(
                    "PREVIEW FIRMWARE", row.get("release_note_warning", "")
                )
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertNotIn("warning_copy_key", row)
                self.assertNotIn("release_note_warning", row)

    def test_rows_are_hidden_not_buyable(self) -> None:
        # posture.stable mirrors the channel after the promotions.
        for cs in DRAFTED_CONFIGS:
            with self.subTest(config_string=cs):
                posture = self.by_cs[cs].get("commercial_posture", {})
                self.assertEqual(posture.get("visibility"), "hidden")
                self.assertFalse(posture.get("buyable"))
                self.assertFalse(posture.get("recommended"))
                self.assertFalse(posture.get("customer_default"))
                self.assertEqual(posture.get("stable"), cs in PROMOTED_CONFIGS)

    def test_rows_channels_match_promotion_state(self) -> None:
        for cs in STILL_METADATA_READY_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row["channel"], "preview")
                self.assertEqual(
                    row.get("release_state"), "metadata-ready-unpublished"
                )
                self.assertTrue(row["artifact_name"].endswith("-preview.bin"))
        for cs in PROMOTED_CONFIGS:
            with self.subTest(config_string=cs):
                row = self.by_cs[cs]
                self.assertEqual(row["channel"], "stable")
                self.assertTrue(row["artifact_name"].endswith("-stable.bin"))


class EveryPreviewRowHasCoverageTests(unittest.TestCase):
    """Task item 6: EVERY preview WebFlash build row has release-note coverage —
    either a dry-run draft (metadata-ready) or a recorded published release."""

    def test_every_preview_row_is_covered(self) -> None:
        for row in _preview_rows():
            cs = row["config_string"]
            with self.subTest(config_string=cs):
                if row.get("release_state") == "metadata-ready-unpublished":
                    self.assertTrue(
                        _draft_path(cs).is_file(),
                        f"{cs}: metadata-ready preview row has no draft",
                    )
                elif cs == PUBLISHED_LED_PREVIEW_CONFIG:
                    # Covered by its recorded published release proof; not
                    # re-drafted here (task item 5). The proof doc was
                    # archived under DOCS-DISPOSITION-001; the coverage
                    # record is now its docs/archive-index.md row, which
                    # must keep recording the exact original path.
                    archive_index = ARCHIVE_INDEX.read_text(encoding="utf-8")
                    self.assertIn(
                        "docs/webflash-release-proof.md",
                        archive_index,
                        "the archived published-release proof must be "
                        "recorded in docs/archive-index.md",
                    )
                else:
                    self.fail(
                        f"unexpected preview row without coverage policy: {cs}"
                    )


class PublishedAndStableNotDraftedTests(unittest.TestCase):
    """Task items 4 / 5: stable Bathroom + published LED preview not re-drafted."""

    def test_stable_baseline_has_no_preview_draft(self) -> None:
        self.assertFalse(
            _draft_path(STABLE_CONFIG).is_file(),
            "the stable Bathroom baseline must not be drafted as a preview",
        )

    def test_published_led_preview_has_no_preview_draft(self) -> None:
        self.assertFalse(
            _draft_path(PUBLISHED_LED_PREVIEW_CONFIG).is_file(),
            "the published VentIQ LED preview must not be re-drafted here",
        )


class StableBathroomCrossReferenceTests(unittest.TestCase):
    """The 'use the stable Bathroom PoE release' pointer matches the commercial
    source of truth (launch SKU unchanged)."""

    def test_launch_sku_and_artifact_match_shop_source_of_truth(self) -> None:
        # The shop artifact mirrors the LIVE stable Bathroom build (the ledger
        # version moves with release bumps; the drafts' v1.0.0 cross-reference
        # stays a historical text pin checked separately above).
        shop = _load_json(SHOP_PATH)["launch_product"]
        row = _by_cs()[STABLE_CONFIG]
        self.assertEqual(shop["shop_sku"], LAUNCH_SKU)
        self.assertEqual(shop["firmware_config"], STABLE_CONFIG)
        self.assertEqual(shop["artifact_name"], row["artifact_name"])

    def test_stable_row_still_stable_in_build_ledger(self) -> None:
        row = _by_cs()[STABLE_CONFIG]
        self.assertEqual(row["channel"], "stable")
        self.assertEqual(
            row["artifact_name"],
            f"Sense360-{STABLE_CONFIG}-v{row['version']}-stable.bin",
        )


class GuardrailTests(unittest.TestCase):
    """Hard guardrails: dry-run only — no publish side effects, no TRIAC / fan
    draft, no draft directory pollution."""

    def test_no_publish_side_effect_files_committed(self) -> None:
        self.assertFalse((REPO_ROOT / "manifest.json").exists())
        self.assertFalse((REPO_ROOT / "firmware" / "sources.json").exists())

    def test_no_bin_committed_under_release_notes(self) -> None:
        bins = list(DRAFT_DIR.rglob("*.bin")) if DRAFT_DIR.is_dir() else []
        self.assertEqual(bins, [], f"no .bin may be committed; found {bins}")

    def test_draft_directory_holds_only_the_three_drafts_and_readme(self) -> None:
        present = sorted(p.name for p in DRAFT_DIR.glob("*.md"))
        expected = sorted(
            ["README.md", SHARED_PREVIEW_NOTES]
            + [f"{cs.lower()}.md" for cs in DRAFTED_CONFIGS]
        )
        self.assertEqual(present, expected)

    def test_no_triac_or_fan_draft_present(self) -> None:
        for p in DRAFT_DIR.glob("*.md"):
            for token in FAN_DRIVER_TOKENS:
                self.assertNotIn(
                    token.lower(),
                    p.name.lower(),
                    f"no TRIAC / fan draft may be added; found {p.name}",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
