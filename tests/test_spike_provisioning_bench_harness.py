#!/usr/bin/env python3
"""Guard + shape tests for the SPIKE-PROVISIONING-BENCH-001 bench harness.

Programme: SEC-ESP-PROVISIONING-001 (ADR draft PR #821; procedure of record
draft PR #822, `docs/hardware/SPIKE-PROVISIONING-BENCH-001-procedure.md`).

The harness under test lives in `tests/bench/sec_esp_provisioning_001/` and
is TEST-ONLY — NOT FOR RELEASE OR CUSTOMER USE. It exists solely so the
owner can run the approved bench procedure against stock ESPHome mechanisms
(runtime API set-key, runtime OTA/AP password setters, NVS persistence,
stock factory reset). It is not production provisioning implementation.

Two test families:

1. **Isolation guards** (fail-closed, modelled on DEV-HARNESS-001 /
   `scripts/check_dev_harness_guard.py`): the harness must be unreachable
   from every production discovery path — product compositions, package
   layers, the declaration-driven release matrix (`config/*.json`,
   ESP-007), WebFlash build declarations, and the firmware publication
   workflows.

2. **Harness shape checks**: the committed harness matches the substrate
   shapes the procedure requires (empty-key API encryption, empty compiled
   OTA password, no compiled AP password literal, restore_value globals
   with a schema/version marker) and commits no credential literal and no
   credential-value logging.

Runtime behaviours (actual NVS erase on factory reset, boot-window timing,
AP pre-enforcement) cannot be unit-tested here; they are bench assertions
recorded — unclaimed — via the empty validation record on PR #822.

Uses stdlib unittest (repo convention). Run with:
    python3 tests/test_spike_provisioning_bench_harness.py
"""

import json
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HARNESS_DIR = REPO_ROOT / "tests" / "bench" / "sec_esp_provisioning_001"
HARNESS_YAML = HARNESS_DIR / "bench-spike.yaml"
HARNESS_SECRETS_EXAMPLE = HARNESS_DIR / "secrets.example.yaml"
HARNESS_HOST_HELPER = HARNESS_DIR / "bench_host.py"
HARNESS_README = HARNESS_DIR / "README.md"

CONFIG_DIR = REPO_ROOT / "config"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

TEST_ONLY_MARKER = "TEST-ONLY — NOT FOR RELEASE OR CUSTOMER USE"

# Strings that would indicate the harness leaked into a discovery surface.
HARNESS_PATH_TOKENS = (
    "tests/bench/sec_esp_provisioning_001",
    "bench-spike",
    "sec_esp_provisioning_001",
)

# Persisted bench globals the stock factory reset (full NVS erase, ADR E-6)
# must clear. The shape tests pin this exact set so a new persisted global
# cannot be added without extending the reset coverage expectation.
EXPECTED_RESTORE_GLOBALS = {
    "bench_boot_count",
    "bench_ota_password",
    "bench_ap_password",
    "bench_record_uuid",
    "bench_record_state",
    "bench_record_schema_version",
    "bench_record_checksum",
}

# Credential-bearing globals whose VALUE must never reach a log line or a
# diagnostic publish. State (set/unset) is derived into separate booleans.
SECRET_GLOBAL_IDS = ("bench_ota_password", "bench_ap_password")


def _iter_json_strings(node):
    """Yield every string anywhere inside a parsed JSON document."""
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for key, value in node.items():
            yield from _iter_json_strings(key)
            yield from _iter_json_strings(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_json_strings(item)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestHarnessFilesExist(unittest.TestCase):
    """The harness ships as a complete, clearly-marked unit."""

    def test_harness_yaml_exists(self):
        self.assertTrue(HARNESS_YAML.is_file(), f"missing {HARNESS_YAML}")

    def test_secrets_example_exists(self):
        self.assertTrue(
            HARNESS_SECRETS_EXAMPLE.is_file(), f"missing {HARNESS_SECRETS_EXAMPLE}"
        )

    def test_host_helper_exists(self):
        self.assertTrue(HARNESS_HOST_HELPER.is_file(), f"missing {HARNESS_HOST_HELPER}")

    def test_readme_exists(self):
        self.assertTrue(HARNESS_README.is_file(), f"missing {HARNESS_README}")

    def test_every_harness_file_carries_the_test_only_marker(self):
        for path in (
            HARNESS_YAML,
            HARNESS_SECRETS_EXAMPLE,
            HARNESS_HOST_HELPER,
            HARNESS_README,
        ):
            with self.subTest(file=path.name):
                self.assertIn(
                    TEST_ONLY_MARKER,
                    _read(path),
                    f"{path} must carry the marker {TEST_ONLY_MARKER!r}",
                )


class TestProductionDiscoveryExclusion(unittest.TestCase):
    """The harness cannot enter any production discovery path."""

    def test_no_config_json_references_the_harness(self):
        """The release/build matrix is declaration-driven (ESP-007): every
        build, compile-only, preview, and WebFlash declaration lives in
        config/*.json. None may reference the harness."""
        offenders = []
        for json_path in sorted(CONFIG_DIR.glob("*.json")):
            doc = json.loads(_read(json_path))
            for value in _iter_json_strings(doc):
                for token in HARNESS_PATH_TOKENS:
                    if token in value:
                        offenders.append(f"{json_path.name}: {value!r}")
        self.assertEqual(
            offenders,
            [],
            "harness reference found in declaration files:\n" + "\n".join(offenders),
        )

    def test_no_workflow_references_the_harness(self):
        """No CI or release workflow (including firmware-build-release.yml,
        the publication workflow) may address the harness."""
        offenders = []
        for wf in sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(
            WORKFLOWS_DIR.glob("*.yaml")
        ):
            text = _read(wf)
            for token in HARNESS_PATH_TOKENS:
                if token in text:
                    offenders.append(f"{wf.name}: {token}")
        self.assertEqual(offenders, [], f"workflow references harness: {offenders}")

    def test_no_product_or_package_yaml_includes_the_harness(self):
        """No customer product shim, bundle, webflash wrapper, compile-only
        skeleton, or package layer may include or mention the harness."""
        offenders = []
        for scan_dir in ("products", "packages", "examples", "dev"):
            root = REPO_ROOT / scan_dir
            if not root.is_dir():
                continue
            for yaml_path in sorted(root.rglob("*.yaml")):
                text = _read(yaml_path)
                for token in HARNESS_PATH_TOKENS:
                    if token in text:
                        offenders.append(f"{yaml_path.relative_to(REPO_ROOT)}: {token}")
        self.assertEqual(
            offenders, [], f"production YAML references harness: {offenders}"
        )

    def test_harness_is_outside_all_scanned_composition_roots(self):
        """Placement guard: the harness must live under tests/bench/, not
        under products/, packages/, dev/, or examples/."""
        rel = HARNESS_DIR.relative_to(REPO_ROOT).as_posix()
        self.assertTrue(rel.startswith("tests/bench/"), rel)

    def test_release_matrix_and_catalogs_do_not_gain_a_bench_row(self):
        """Belt-and-braces on the four highest-risk declarations."""
        for name in (
            "webflash-builds.json",
            "product-catalog.json",
            "compile-only-targets.json",
            "preview-release-targets.json",
        ):
            path = CONFIG_DIR / name
            self.assertTrue(path.is_file(), f"expected declaration file {name}")
            with self.subTest(declaration=name):
                text = _read(path)
                for token in HARNESS_PATH_TOKENS:
                    self.assertNotIn(token, text, f"{name} references {token}")


class TestNoCommittedCredentialLiterals(unittest.TestCase):
    """No fixed API / OTA / AP / WiFi / web credential literal is committed."""

    def _harness_text(self) -> str:
        return _read(HARNESS_YAML)

    def test_api_encryption_block_has_no_key(self):
        """H-01 substrate (ADR E-1): `encryption:` with NO key — the
        noise-capable-no-key shape. A committed key literal (or even a
        !secret key) would break the empty-key claim-state under test."""
        text = self._harness_text()
        self.assertRegex(text, r"(?m)^api:")
        self.assertRegex(text, r"(?m)^\s+encryption:\s*(\{\}\s*)?$")
        self.assertNotRegex(text, r"(?m)^\s+key\s*:")

    def test_ota_password_is_compiled_empty(self):
        """H-02 substrate (ADR E-4): `password: ""` compiles the auth path
        so set_auth_password() is callable; any non-empty literal is a
        committed credential."""
        text = self._harness_text()
        self.assertRegex(text, r'(?m)^\s+password:\s*""\s*(#.*)?$')

    def test_fallback_ap_has_no_compiled_password(self):
        """H-03 substrate (ADR E-8): the AP block must carry no password
        key at all — the throwaway value is applied at runtime so the bench
        can observe whether a pre-enforcement window exists."""
        text = self._harness_text()
        ap_match = re.search(r"(?ms)^\s+ap:\n(.*?)(?=^\S|\Z)", text)
        self.assertIsNotNone(ap_match, "wifi must declare a fallback ap: block")
        self.assertNotIn("password", ap_match.group(1))

    def test_wifi_credentials_come_from_secrets_only(self):
        text = self._harness_text()
        self.assertIn("ssid: !secret bench_wifi_ssid", text)
        self.assertIn("password: !secret bench_wifi_password", text)

    def test_no_web_server_is_configured(self):
        """OD-06 posture and one less credential surface: the harness
        must not compile a web server at all."""
        self.assertNotRegex(self._harness_text(), r"(?m)^web_server\s*:")

    def test_credential_globals_have_empty_initial_values(self):
        """The persisted OTA/AP password globals must initialise empty; the
        throwaway values arrive only via bench-time actions."""
        text = self._harness_text()
        for global_id in SECRET_GLOBAL_IDS:
            with self.subTest(global_id=global_id):
                block = self._global_block(text, global_id)
                self.assertRegex(
                    block,
                    r"initial_value:\s*'\"\"'|initial_value:\s*\"''\"",
                    f"{global_id} must initialise to the empty string",
                )

    def _global_block(self, text: str, global_id: str) -> str:
        match = re.search(
            r"(?ms)^  - id: " + re.escape(global_id) + r"\n(.*?)(?=^  - id: |^\S|\Z)",
            text,
        )
        self.assertIsNotNone(match, f"global {global_id} not found")
        return match.group(0)

    def test_secrets_example_contains_only_obvious_placeholders(self):
        """The bench secrets template must ship placeholder values only."""
        text = _read(HARNESS_SECRETS_EXAMPLE)
        self.assertIn("bench_wifi_ssid", text)
        self.assertIn("bench_wifi_password", text)
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            key, _, value = stripped.partition(":")
            value = value.strip().strip("\"'")
            with self.subTest(key=key):
                self.assertTrue(
                    value.startswith("REPLACE_WITH_"),
                    f"secrets.example.yaml value for {key} must be an "
                    f"obvious REPLACE_WITH_* placeholder, got {value!r}",
                )

    def test_host_helper_commits_no_credential_literal(self):
        """The host helper must generate/accept throwaway values at runtime
        — no default credential strings."""
        text = _read(HARNESS_HOST_HELPER)
        banned = re.findall(
            r"(?i)(?:password|psk|key)\s*=\s*[\"'][^\"']{4,}[\"']", text
        )
        self.assertEqual(
            banned, [], f"credential-like literal assignments found: {banned}"
        )


class TestNoCredentialLogging(unittest.TestCase):
    """Diagnostic output can never contain credential values."""

    def test_no_log_line_touches_a_secret_global(self):
        """No ESP_LOG / logger.log statement in the harness may reference a
        credential global (or the noise PSK) at all — states are logged via
        derived booleans only."""
        offenders = []
        for lineno, line in enumerate(_read(HARNESS_YAML).splitlines(), start=1):
            if "ESP_LOG" not in line and "logger.log" not in line:
                continue
            for token in (*SECRET_GLOBAL_IDS, "get_psk", "noise_psk"):
                if token in line:
                    offenders.append(f"line {lineno}: {line.strip()}")
        self.assertEqual(offenders, [], "credential id on a log line:\n%s" % offenders)

    def test_no_text_sensor_publishes_a_secret_global(self):
        """Template text sensors may publish derived set/unset states, never
        the credential globals themselves."""
        text = _read(HARNESS_YAML)
        ts_match = re.search(r"(?ms)^text_sensor:\n(.*?)(?=^\S|\Z)", text)
        self.assertIsNotNone(ts_match, "harness must expose text_sensor diagnostics")
        block = ts_match.group(1)
        for token in (*SECRET_GLOBAL_IDS, "get_psk"):
            self.assertNotIn(
                token, block, f"text_sensor block references credential {token}"
            )

    def test_host_helper_never_prints_supplied_credentials(self):
        """Static check: no print/log call in the helper references the
        credential-holding variables."""
        text = _read(HARNESS_HOST_HELPER)
        offenders = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not re.search(r"\bprint\(|logging\.|logger\.", line):
                continue
            if re.search(r"\b(secret_value|new_key|password_value)\b", line):
                offenders.append(f"line {lineno}: {line.strip()}")
        self.assertEqual(offenders, [], f"helper logs credential vars: {offenders}")


class TestPersistenceRecordShape(unittest.TestCase):
    """H-04: the synthetic persistence record is versioned and validatable."""

    def _text(self) -> str:
        return _read(HARNESS_YAML)

    def test_all_expected_restore_globals_are_declared(self):
        text = self._text()
        declared = set(re.findall(r"(?m)^  - id: (\w+)", text))
        missing = EXPECTED_RESTORE_GLOBALS - declared
        self.assertEqual(missing, set(), f"missing persisted globals: {missing}")

    def test_every_bench_global_is_nvs_backed(self):
        """Every bench_* global must set restore_value: true so the stock
        factory reset (full NVS erase, ADR E-6) provably owns its erasure.
        The erase itself is a bench assertion (V-07), not unit-testable."""
        text = self._text()
        for global_id in EXPECTED_RESTORE_GLOBALS:
            with self.subTest(global_id=global_id):
                match = re.search(
                    r"(?ms)^  - id: "
                    + re.escape(global_id)
                    + r"\n(.*?)(?=^  - id: |^\S|\Z)",
                    text,
                )
                self.assertIsNotNone(match, f"global {global_id} not declared")
                self.assertIn("restore_value: true", match.group(0))

    def test_record_carries_a_schema_version_marker(self):
        """The synthetic record must declare a non-zero schema version so a
        future reader can distinguish record generations."""
        text = self._text()
        match = re.search(
            r"(?ms)^  - id: bench_record_schema_version\n(.*?)(?=^  - id: |^\S|\Z)",
            text,
        )
        self.assertIsNotNone(match)
        # std::string globals take a C++ expression: initial_value: '"1"'
        self.assertRegex(match.group(0), r"initial_value:\s*'\"1\"'")

    def test_record_has_a_checksum_field_and_validation(self):
        text = self._text()
        self.assertIn("bench_record_checksum", text)
        self.assertIn("bench_record_valid", text)

    def test_synthetic_values_are_not_hardcoded(self):
        """The UUID/state fields initialise empty — synthetic values are
        set only via bench-time test actions, never committed."""
        text = self._text()
        for global_id in ("bench_record_uuid", "bench_record_state"):
            with self.subTest(global_id=global_id):
                match = re.search(
                    r"(?ms)^  - id: "
                    + re.escape(global_id)
                    + r"\n(.*?)(?=^  - id: |^\S|\Z)",
                    text,
                )
                self.assertIsNotNone(match, f"global {global_id} not declared")
                self.assertRegex(
                    match.group(0),
                    r"initial_value:\s*'\"\"'|initial_value:\s*\"''\"",
                    f"{global_id} must initialise empty",
                )


class TestHarnessConfigShape(unittest.TestCase):
    """The harness is a complete standalone ESPHome config for the bench
    target (S360-100 R4 / ESP32-S3) with the required test surfaces."""

    def _text(self) -> str:
        return _read(HARNESS_YAML)

    def test_targets_esp32_s3(self):
        text = self._text()
        self.assertRegex(text, r"(?m)^esp32:")
        self.assertIn("variant: esp32s3", text)
        self.assertIn("type: esp-idf", text)

    def test_device_name_is_unmistakably_bench(self):
        self.assertRegex(
            self._text(), r'(?m)^\s+device_name:\s*"?sense360-bench-spike"?\s*$'
        )

    def test_factory_reset_surfaces_present(self):
        """H-06/H-07: stock factory_reset button on SW3 (IO0) plus the stock
        power-cycle-count trigger must both be configured."""
        text = self._text()
        self.assertRegex(text, r"(?m)^factory_reset:")
        self.assertIn("resets_required:", text)
        self.assertIn("platform: factory_reset", text)
        self.assertIn("GPIO0", text)

    def test_h05_diagnostics_present(self):
        """H-05: set/unset states, record validity, boot count, reset
        reason, MAC — all non-secret."""
        text = self._text()
        for needle in (
            "api_key_state",
            "ota_password_state",
            "ap_password_state",
            "bench_record_valid",
            "bench_boot_count",
            "platform: debug",
            "mac_address",
            "platform: version",
        ):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)

    def test_bench_set_actions_are_exposed(self):
        """H-02/H-03/H-04: bench-time set actions exist for the OTA
        password, AP password, and synthetic record (stock user-defined
        API services — no custom protocol)."""
        text = self._text()
        for action in (
            "bench_set_ota_password",
            "bench_set_ap_password",
            "bench_set_synthetic_record",
            "bench_clear_synthetic_record",
        ):
            with self.subTest(action=action):
                self.assertIn(action, text)

    def test_harness_yaml_is_yaml_parseable(self):
        """Same loader discipline as tests/validate_configs.py (safe_load
        with registered ESPHome tag constructors)."""
        import yaml

        def _tag(loader, node):
            if isinstance(node, yaml.ScalarNode):
                return loader.construct_scalar(node)
            if isinstance(node, yaml.SequenceNode):
                return loader.construct_sequence(node)
            if isinstance(node, yaml.MappingNode):
                return loader.construct_mapping(node)
            return None

        class _Loader(yaml.SafeLoader):
            pass

        for tag in ("!secret", "!include", "!extend", "!lambda", "!remove"):
            yaml.add_constructor(tag, _tag, Loader=_Loader)
        doc = yaml.load(_read(HARNESS_YAML), Loader=_Loader)
        self.assertIsInstance(doc, dict)
        for key in ("esphome", "esp32", "api", "ota", "wifi", "logger", "globals"):
            self.assertIn(key, doc, f"harness must declare top-level {key}:")


if __name__ == "__main__":
    unittest.main()
