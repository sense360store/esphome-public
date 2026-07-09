#!/usr/bin/env python3
"""RELEASE-PRODUCT-SELECTION-001 contract tests.

Locks in the operator-facing release-target selection added to the
release-notes draft workflow so it cannot silently regress (e.g. by
quietly defaulting back to a single hardcoded product, by accepting an
off-catalog free-text value, or by letting a FanRelay / FanPWM / FanDAC
token become selectable for release).

The invariants:

  * ``release-notes-draft.yml`` exposes ``config_string`` as a
    ``type: choice`` input whose options exactly match the
    release-eligible ``config_string`` values in
    ``config/webflash-builds.json`` — no free-text default that
    silently scopes to one product.
  * Every FanRelay / FanPWM / FanDAC option a picker lists maps to a
    non-stable build row (HW-RELEASE-001: FanPWM / FanDAC on preview,
    FanRelay on experimental; fan configs are NEVER stable).
  * The release-note planner (``scripts/plan_room_release_notes.py``)
    scopes correctly by ``config_string``, accepts the release-eligible
    fan targets on their lanes, and refuses any fan-family config that
    is not release-eligible.

``firmware-build-release.yml`` no longer carries a ``workflow_dispatch``
lane (it fires only on the published ``release`` event), so its former
``release_target`` picker and ``release-dry-run`` job invariants were
removed together with that lane.

Run with::

    python3 tests/test_release_product_selection.py
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"
RELEASE_NOTES_WORKFLOW = WORKFLOWS_DIR / "release-notes-draft.yml"
BUMP_WORKFLOW = WORKFLOWS_DIR / "bump-version.yml"
CREATE_WORKFLOW = WORKFLOWS_DIR / "create-release.yml"
BUILDS_JSON = REPO_ROOT / "config" / "webflash-builds.json"

FAN_TOKENS = ("FanRelay", "FanPWM", "FanDAC")

# CI-PIPELINE-CLARITY-001 P3: config_string targets that are release-eligible
# in the single source (config/webflash-builds.json) but intentionally NOT yet
# offered by the Bump / Create pickers. This set was the tracked, documented
# gap for the experimental FanTRIAC target under P2; P3 (the FanTRIAC
# product-state change) wired FanTRIAC into the Bump / Create pickers in the
# same PR that empties this set, so Bump / Create now cover every
# release-eligible target with no carve-out. It is kept (empty) as the single
# place to re-document any future intentional picker/source divergence rather
# than silent drift.
PENDING_BUMP_CREATE_PICKER_ADDITIONS = frozenset()

# CI-PIPELINE-CLARITY-001 P4a: config_string values that were DE-LISTED from
# the release-eligible set because they were never built or served (no upstream
# binary, not in the served set). They must NOT reappear in the single source
# (config/webflash-builds.json) or in any release picker until a real build row
# is re-added deliberately. HW-RELEASE-001 (docs/hw-release-001.md, owner
# decision of record) deliberately RE-LISTED Ceiling-POE-RoomIQ-LED with a
# real preview build row, emptying this set; it stays as the single place to
# document any future de-list.
DELISTED_RELEASE_CONFIGS = frozenset()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _triggers(data: dict) -> dict:
    # PyYAML parses bare key ``on:`` as boolean True (YAML 1.1 truthy key).
    raw = data.get("on")
    if raw is None:
        raw = data.get(True)
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, list):
        return {key: None for key in raw}
    if isinstance(raw, str):
        return {raw: None}
    return {}


def _release_eligible_config_strings() -> list[str]:
    doc = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
    return [
        e["config_string"]
        for e in doc.get("builds", [])
        if isinstance(e, dict) and isinstance(e.get("config_string"), str)
    ]


def _release_channels_by_config() -> dict[str, str]:
    doc = json.loads(BUILDS_JSON.read_text(encoding="utf-8"))
    return {
        e["config_string"]: str(e.get("channel", ""))
        for e in doc.get("builds", [])
        if isinstance(e, dict) and isinstance(e.get("config_string"), str)
    }


def _picker(workflow_path: Path) -> dict:
    """Return the ``config_string`` workflow_dispatch input for a workflow."""
    data = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
    wd = _triggers(data).get("workflow_dispatch") or {}
    inputs = wd.get("inputs") or {}
    return inputs.get("config_string") or {}


class ReleaseNotesDraftPickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = yaml.safe_load(RELEASE_NOTES_WORKFLOW.read_text(encoding="utf-8"))
        wd = _triggers(cls.data).get("workflow_dispatch") or {}
        cls.inputs = wd.get("inputs") or {}

    def test_config_string_is_type_choice(self) -> None:
        cs = self.inputs.get("config_string") or {}
        self.assertEqual(
            cs.get("type"),
            "choice",
            "release-notes-draft.yml config_string must be a `type: choice` "
            "picker (RELEASE-PRODUCT-SELECTION-001) so the operator picks "
            "from the canonical release-eligible list rather than typing a "
            "free-text product name",
        )

    def test_config_string_options_match_release_matrix(self) -> None:
        cs = self.inputs.get("config_string") or {}
        options = list(cs.get("options") or [])
        expected = _release_eligible_config_strings()
        self.assertEqual(
            set(options),
            set(expected),
            f"release-notes-draft.yml config_string options {options!r} "
            f"must equal config/webflash-builds.json config_strings "
            f"{expected!r} (add the new release-eligible target to BOTH "
            "the workflow picker and the release matrix)",
        )

    def test_config_string_fan_options_are_never_stable(self) -> None:
        # HW-RELEASE-001: fan targets are pickable, but every fan option must
        # map to a non-stable build row (FanRelay: experimental; FanPWM /
        # FanDAC: preview). A fan option whose build row is stable — or that
        # has no build row — fails here.
        options = list((self.inputs.get("config_string") or {}).get("options") or [])
        channels = _release_channels_by_config()
        for opt in options:
            opt = str(opt)
            if not any(token.lower() in opt.lower() for token in FAN_TOKENS):
                continue
            self.assertIn(opt, channels)
            self.assertNotEqual(
                channels[opt],
                "stable",
                f"release-notes-draft.yml offers fan target {opt!r} on the "
                "stable channel; fan configs are NEVER stable "
                "(HW-RELEASE-001)",
            )
            if "fanrelay" in opt.lower():
                self.assertEqual(channels[opt], "experimental")
            else:
                self.assertEqual(channels[opt], "preview")

    def test_config_string_does_not_silently_default_to_one_product(self) -> None:
        # The picker has no `default:` — operator must select. This prevents
        # a silent default-scoped run that only documents stable RoomIQ.
        cs = self.inputs.get("config_string") or {}
        self.assertNotIn(
            "default",
            cs,
            "release-notes-draft.yml config_string must NOT declare a "
            "`default:`; forcing operator selection prevents the workflow "
            "from silently scoping every dispatch to a single product "
            "(RELEASE-PRODUCT-SELECTION-001)",
        )


class ReleasePickerLockStepTests(unittest.TestCase):
    """CI-PIPELINE-CLARITY-001 P2: single-source lock-step across the three
    esphome-public release pickers.

    The ``config_string`` dropdowns in the Bump (``bump-version.yml``),
    Create (``create-release.yml``), and Draft-notes
    (``release-notes-draft.yml``) workflows must all derive from the one
    canonical release-eligibility source, ``config/webflash-builds.json``
    (surfaced by ``scripts/list_release_targets.py``). This test makes any
    drift LOUD: adding a release-eligible build to that file without adding a
    matching picker option — or listing a picker option that no longer maps to
    a build — fails here, so no dropdown can silently fall out of sync.

    As of CI-PIPELINE-CLARITY-001 P3 every picker offers the full
    release-eligible set: FanTRIAC (``Ceiling-POE-VentIQ-FanTRIAC-RoomIQ``,
    experimental channel) was wired into the Bump / Create pickers and the
    ``PENDING_BUMP_CREATE_PICKER_ADDITIONS`` carve-out emptied in the same PR,
    so no picker carries a documented gap today.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.canonical = set(_release_eligible_config_strings())
        cls.bump = _picker(BUMP_WORKFLOW)
        cls.create = _picker(CREATE_WORKFLOW)
        cls.draft = _picker(RELEASE_NOTES_WORKFLOW)

    def _options(self, picker: dict) -> set[str]:
        return {str(opt) for opt in (picker.get("options") or [])}

    def test_single_source_list_release_targets_matches_builds(self) -> None:
        # The canonical helper and the raw file must agree; the helper is the
        # documented single source the workflow comments point operators to.
        mod = _load_module(
            "list_release_targets",
            REPO_ROOT / "scripts" / "list_release_targets.py",
        )
        self.assertEqual(
            set(mod.selectable_config_strings()),
            self.canonical,
            "scripts/list_release_targets.py must enumerate exactly the "
            "config/webflash-builds.json config_strings (the single source of "
            "truth the release pickers derive from)",
        )

    def test_all_pickers_are_type_choice(self) -> None:
        for name, picker in (
            ("bump-version.yml", self.bump),
            ("create-release.yml", self.create),
            ("release-notes-draft.yml", self.draft),
        ):
            self.assertEqual(
                picker.get("type"),
                "choice",
                f"{name} config_string must be a `type: choice` picker so an "
                "operator selects from the canonical release-eligible list "
                "rather than typing a free-text product name",
            )

    def test_no_picker_lists_an_off_source_option(self) -> None:
        # Forward-drift guard: nothing may appear in a picker that is not a
        # real release-eligible config_string (catches typos and stale options
        # left behind after a build is removed from the source).
        for name, picker in (
            ("bump-version.yml", self.bump),
            ("create-release.yml", self.create),
            ("release-notes-draft.yml", self.draft),
        ):
            extra = self._options(picker) - self.canonical
            self.assertEqual(
                extra,
                set(),
                f"{name} config_string lists {sorted(extra)!r} which is not a "
                "config_string in config/webflash-builds.json; every option "
                "must map to a release-eligible build (single source of "
                "truth)",
            )

    def test_fan_picker_options_are_never_stable(self) -> None:
        # HW-RELEASE-001: fan targets are pickable, but only on their lanes —
        # FanPWM / FanDAC on preview, FanRelay on experimental. A picker
        # option carrying a fan token whose build row is stable (or missing)
        # fails here; fan configs are NEVER stable.
        channels = _release_channels_by_config()
        for name, picker in (
            ("bump-version.yml", self.bump),
            ("create-release.yml", self.create),
            ("release-notes-draft.yml", self.draft),
        ):
            for opt in self._options(picker):
                if not any(
                    token.lower() in opt.lower() for token in FAN_TOKENS
                ):
                    continue
                self.assertIn(opt, channels, f"{name}: {opt!r} has no build row")
                self.assertNotEqual(
                    channels[opt],
                    "stable",
                    f"{name} offers fan target {opt!r} on the stable "
                    "channel; fan configs are NEVER stable (HW-RELEASE-001)",
                )
                if "fanrelay" in opt.lower():
                    self.assertEqual(channels[opt], "experimental")
                else:
                    self.assertEqual(channels[opt], "preview")

    def test_draft_notes_covers_every_release_eligible_build(self) -> None:
        # Draft-notes is the fully-wired picker: it must offer every
        # release-eligible target so adding a build to the source and
        # forgetting the picker fails here.
        self.assertEqual(
            self._options(self.draft),
            self.canonical,
            "release-notes-draft.yml config_string must equal the "
            "config/webflash-builds.json config_strings (add the new "
            "release-eligible target to BOTH the picker and the release "
            "matrix)",
        )

    def test_bump_and_create_cover_all_but_pending_additions(self) -> None:
        # Bump / Create must offer every release-eligible target EXCEPT the
        # documented pending set (FanTRIAC, closed by P3). This still makes a
        # forgotten NON-pending addition fail: a new build lands in the source
        # but not in these pickers -> mismatch here.
        expected = self.canonical - PENDING_BUMP_CREATE_PICKER_ADDITIONS
        for name, picker in (
            ("bump-version.yml", self.bump),
            ("create-release.yml", self.create),
        ):
            self.assertEqual(
                self._options(picker),
                expected,
                f"{name} config_string must equal the release-eligible "
                "config_strings from config/webflash-builds.json minus the "
                "documented PENDING_BUMP_CREATE_PICKER_ADDITIONS "
                f"({sorted(PENDING_BUMP_CREATE_PICKER_ADDITIONS)!r}, wired in "
                "by CI-PIPELINE-CLARITY-001 P3)",
            )

    def test_pending_additions_are_real_release_eligible_targets(self) -> None:
        # The pending set is an exclusion carve-out, not a place to hide a
        # bogus target: everything in it must be a real release-eligible build.
        self.assertTrue(
            PENDING_BUMP_CREATE_PICKER_ADDITIONS <= self.canonical,
            "PENDING_BUMP_CREATE_PICKER_ADDITIONS must be a subset of the "
            "config/webflash-builds.json config_strings; a pending picker "
            "addition that is not release-eligible is a contradiction",
        )

    def test_delisted_configs_are_not_release_eligible(self) -> None:
        # CI-PIPELINE-CLARITY-001 P4a: a de-listed config must not appear in
        # the single release-eligibility source. Re-adding a build row for it
        # without a deliberate re-list fails here.
        leaked = DELISTED_RELEASE_CONFIGS & self.canonical
        self.assertEqual(
            leaked,
            set(),
            f"{sorted(leaked)!r} was de-listed by CI-PIPELINE-CLARITY-001 P4a "
            "(never built or served) but is back in "
            "config/webflash-builds.json; a de-listed config must not be "
            "release-eligible until it is deliberately re-listed with a real "
            "build row",
        )

    def test_delisted_configs_are_in_no_picker(self) -> None:
        # A de-listed config must not be offered by any release picker.
        for name, picker in (
            ("bump-version.yml", self.bump),
            ("create-release.yml", self.create),
            ("release-notes-draft.yml", self.draft),
        ):
            leaked = DELISTED_RELEASE_CONFIGS & self._options(picker)
            self.assertEqual(
                leaked,
                set(),
                f"{name} config_string offers {sorted(leaked)!r}, which was "
                "de-listed by CI-PIPELINE-CLARITY-001 P4a (never built or "
                "served); remove it from the picker",
            )


class PlannerSelectionTests(unittest.TestCase):
    """RELEASE-PRODUCT-SELECTION-001 planner-level scoping contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = _load_module(
            "plan_room_release_notes",
            REPO_ROOT / "scripts" / "plan_room_release_notes.py",
        )

    def test_planner_scope_defaults_to_all(self) -> None:
        builds = self.plan.build_plan(commit="deadbeef")["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(
            configs,
            set(_release_eligible_config_strings()),
            "default plan must cover every release-eligible build",
        )

    def test_planner_scope_filters_to_single_config(self) -> None:
        target = "Ceiling-POE-VentIQ-RoomIQ"
        builds = self.plan.build_plan(
            commit="deadbeef", config_string=target
        )["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {target})

    def test_planner_scope_filters_to_led_preview(self) -> None:
        target = "Ceiling-POE-VentIQ-RoomIQ-LED"
        builds = self.plan.build_plan(
            commit="deadbeef", config_string=target
        )["builds"]
        configs = {b["config_string"] for b in builds}
        self.assertEqual(configs, {target})

    def test_planner_all_release_eligible_sentinel_is_equivalent(self) -> None:
        a = self.plan.build_plan(commit="deadbeef")["builds"]
        b = self.plan.build_plan(
            commit="deadbeef", config_string="all-release-eligible"
        )["builds"]
        self.assertEqual(
            {x["config_string"] for x in a},
            {x["config_string"] for x in b},
        )

    def test_planner_rejects_unknown_config_string(self) -> None:
        with self.assertRaises(self.plan.PlanError) as ctx:
            self.plan.build_plan(
                commit="deadbeef", config_string="Not-A-Real"
            )
        msg = str(ctx.exception)
        self.assertIn("not a release-eligible", msg)
        # Error must enumerate the legitimate alternatives.
        for cfg in _release_eligible_config_strings():
            self.assertIn(cfg, msg)

    def test_planner_accepts_release_eligible_fan_targets(self) -> None:
        # HW-RELEASE-001: the three VentIQ fan room bundles are now
        # release-eligible on their lanes, so the planner must scope to them.
        for token in FAN_TOKENS:
            target = f"Ceiling-POE-VentIQ-{token}-RoomIQ"
            builds = self.plan.build_plan(
                commit="deadbeef", config_string=target
            )["builds"]
            self.assertEqual({b["config_string"] for b in builds}, {target})

    def test_planner_rejects_non_eligible_fan_config(self) -> None:
        # A fan config with no build row stays rejected.
        with self.assertRaises(self.plan.PlanError):
            self.plan.build_plan(
                commit="deadbeef",
                config_string="Ceiling-USB-FanPWM",
            )


class GeneratorProductAwareLedTests(unittest.TestCase):
    """RELEASE-PRODUCT-SELECTION-001: the stale 'Release-One firmware' wording
    in the LED Known-Issues bullet is replaced by product-aware text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gen = _load_module(
            "generate_webflash_release_notes",
            REPO_ROOT / "scripts" / "generate_webflash_release_notes.py",
        )
        catalog = json.loads(
            (REPO_ROOT / "config" / "product-catalog.json").read_text(
                encoding="utf-8"
            )
        )
        cls.catalog_versions = {
            p.get("config_string"): p.get("version")
            for p in catalog.get("products", [])
            if isinstance(p, dict) and p.get("config_string")
        }

    def _live_version(self, config_string: str) -> str:
        # The generator fails closed when --version disagrees with the
        # catalog, so derive the live version instead of pinning one that
        # rots on every release bump.
        return self.catalog_versions[config_string]

    def test_led_known_issue_does_not_mention_release_one(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ",
            version=self._live_version("Ceiling-POE-VentIQ-RoomIQ"),
            channel="stable",
        )
        # The LED exclusion bullet appears under ## Known Issues. The full
        # body should no longer carry the stale 'Release-One firmware' phrasing.
        self.assertNotIn(
            "Release-One firmware",
            body,
            "generator must not emit hardcoded 'Release-One firmware' text "
            "in the LED Known-Issues bullet (RELEASE-PRODUCT-SELECTION-001)",
        )

    def test_led_known_issue_names_selected_config(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ",
            version=self._live_version("Ceiling-POE-VentIQ-RoomIQ"),
            channel="stable",
        )
        # The LED bullet should make it clear *this selected config* does
        # not include LED, rather than implying LED was forgotten or that
        # there is only one fixed product in the universe.
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ", body)
        self.assertIn("does not include LED", body)

    def test_changelog_placeholder_is_product_aware(self) -> None:
        version = self._live_version("Ceiling-POE-VentIQ-RoomIQ-LED")
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ-LED",
            version=version,
            channel="preview",
        )
        # The placeholder must name the selected config + version so a
        # multi-product draft can't be mistaken for the wrong product.
        self.assertIn("Ceiling-POE-VentIQ-RoomIQ-LED", body)
        self.assertIn(f"v{version}", body)
        # It must be unmistakable as a placeholder requiring operator action.
        lowered = body.lower()
        self.assertIn("todo", lowered)
        self.assertIn("operator", lowered)

    def test_led_preview_body_mentions_led_and_preview(self) -> None:
        body = self.gen.generate(
            config_string="Ceiling-POE-VentIQ-RoomIQ-LED",
            version=self._live_version("Ceiling-POE-VentIQ-RoomIQ-LED"),
            channel="preview",
        )
        # For the LED preview, ## Features should call out the LED ring and
        # the preview channel framing.
        self.assertIn("LED", body)
        self.assertIn("preview", body.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
