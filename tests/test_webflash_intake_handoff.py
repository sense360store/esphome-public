#!/usr/bin/env python3
"""CI-PIPELINE-CLARITY-002 contract tests for the WebFlash intake handoff.

``firmware-build-release.yml`` gained a ``webflash-handoff`` job that runs
only after the release-attachment job has succeeded and dispatches the
combined WebFlash firmware-intake workflow
(``sense360store/WebFlash`` / ``firmware-intake.yml`` on ``main``). This
suite locks the job's trust boundaries so they cannot silently regress:

  * the handoff depends on the SUCCESSFUL ``release`` (Attach to Release)
    job — no ``always()`` / ``failure()`` override;
  * the job never checks out repository code and never executes
    repo-local scripts — every step is a self-contained inline
    ``python3`` heredoc (no ``uses:``, no subprocess spawning);
  * raw release-body / tag values can never reach shell execution: the
    only GitHub expressions in the job are an allowlisted set of
    trusted values bound via ``env:``, and each ``run:`` block is
    exactly one fixed heredoc invocation;
  * malformed config / version / channel / artifact metadata fails
    closed, and the body's Version / Channel must equal the values
    Release 3 derived from the tag (``generate-matrix`` outputs);
  * stable and preview dispatch; experimental exits successfully
    WITHOUT dispatching;
  * upstream product/catalog status can neither grant nor deny WebFlash
    intake (the preamble's ``Catalog status`` line is never consulted);
  * the required assets are proven against the REMOTE Release via the
    GitHub API after the Release 3 upload (the ``release: published``
    event predates the upload, so the event's own assets array is not
    trusted);
  * the dispatch target is exactly ``sense360store/WebFlash`` /
    ``firmware-intake.yml`` @ ``main``, carrying only the minimum
    inputs (release_tag, config_string, source_repo, dry_run);
  * ``WEBFLASH_INTAKE_TOKEN`` is the only credential used for the
    cross-repo request, it is exposed to the final dispatch step ONLY,
    a missing token fails loudly with the manual-intake recovery path,
    and the token value is never printed;
  * no deployment / merge / publishing permission is introduced (the
    handoff job has no ``permissions:`` block and inherits the
    workflow's read-only default).

The behavioural tests execute the workflow's actual inline Python
(extracted from the heredocs) against synthetic event payloads and a
local loopback HTTP server standing in for the GitHub API — fully
deterministic, no network.

Run with::

    python3 tests/test_webflash_intake_handoff.py
"""

from __future__ import annotations

import contextlib
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"

JOB_ID = "webflash-handoff"
METADATA_STEP = "Parse and validate release metadata (untrusted input)"
ASSETS_STEP = "Verify required assets on the remote release"
DISPATCH_STEP = "Dispatch WebFlash firmware intake"

HEREDOC_PREFIX = "python3 - <<'PY'\n"
HEREDOC_SUFFIX = "PY"

# The complete set of GitHub expressions the handoff job may use. Everything
# else — in particular anything under github.event.* — must reach the job
# through GITHUB_EVENT_PATH inside Python, never through ${{ }} expansion.
ALLOWED_JOB_EXPRESSIONS = {
    "needs.generate-matrix.outputs.version",
    "needs.generate-matrix.outputs.channel",
    "github.token",
    "steps.metadata.outputs.release_id",
    "steps.metadata.outputs.artifact_name",
    "steps.metadata.outputs.release_tag",
    "steps.metadata.outputs.config_string",
    "secrets.WEBFLASH_INTAKE_TOKEN",
}

EXPRESSION_RE = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")

REQUIRED_SIDECAR_ASSETS = (
    "checksums-sha256.txt",
    "checksums-sha256.txt.sig",
    "checksums-sha256.txt.pem",
    "manifest.json",
)

DISPATCH_PATH = (
    "/repos/sense360store/WebFlash/actions/workflows/" "firmware-intake.yml/dispatches"
)


# ---------------------------------------------------------------------------
# Workflow loading / extraction helpers
# ---------------------------------------------------------------------------


def _load_workflow() -> dict:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _handoff_job() -> dict:
    return _load_workflow()["jobs"][JOB_ID]


def _steps_by_name(job: dict) -> dict:
    return {step.get("name"): step for step in job.get("steps", [])}


def _raw_job_text() -> str:
    """Return the raw YAML text of the handoff job (for expression checks)."""
    raw = WORKFLOW_PATH.read_text(encoding="utf-8")
    lines = raw.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.rstrip("\n") == f"  {JOB_ID}:":
            start = i
            break
    if start is None:
        raise AssertionError(f"job '{JOB_ID}' not found in {WORKFLOW_PATH}")
    end = len(lines)
    job_key_re = re.compile(r"^  [A-Za-z0-9_-]+:\s*$")
    for i in range(start + 1, len(lines)):
        if job_key_re.match(lines[i]):
            end = i
            break
    return "".join(lines[start:end])


def _extract_python(run_text: str) -> str:
    """Extract the inline Python source from a single-heredoc run block."""
    if not run_text.startswith(HEREDOC_PREFIX):
        raise AssertionError(
            "run block is not a single fixed python3 heredoc: " f"{run_text[:60]!r}"
        )
    body = run_text[len(HEREDOC_PREFIX) :]
    body, sep, tail = body.rpartition(f"\n{HEREDOC_SUFFIX}")
    if not sep or tail.strip():
        raise AssertionError("run block heredoc is not terminated by PY")
    return body


def _strip_python_comments(code: str) -> str:
    return "\n".join(
        line for line in code.splitlines() if not line.lstrip().startswith("#")
    )


# ---------------------------------------------------------------------------
# Subprocess execution helpers (run the workflow's actual inline Python)
# ---------------------------------------------------------------------------


def _run_python(code: str, env_extra: dict) -> subprocess.CompletedProcess:
    env = {"PATH": os.environ.get("PATH", "")}
    env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _make_release_body(
    config: str,
    version: str,
    channel: str,
    artifact: str | None = None,
    status: str = "production",
    extra_lines: list[str] | None = None,
) -> str:
    """A body matching the generate_webflash_release_notes.py preamble."""
    if artifact is None:
        artifact = f"Sense360-{config}-v{version}-{channel}.bin"
    lines = [
        "<!--",
        "Sense360 WebFlash release-notes draft.",
        "Generated by scripts/generate_webflash_release_notes.py.",
        "",
        f"Config string : {config}",
        f"Version       : {version}",
        f"Channel       : {channel}",
        f"Artifact      : {artifact}",
        f"Catalog status: {status}",
        "Hardware:",
        "  - Sense360 Core (`S360-100`)",
        "",
        "Human review required before publishing.",
        "-->",
        "",
        "## Changelog",
        "",
        "- Something changed.",
        "",
        "## Known Issues",
        "",
        "- None.",
        "",
        "## Features",
        "",
        "- A feature.",
        "",
        "## Hardware Requirements",
        "",
        "- Sense360 Core (`S360-100`)",
    ]
    if extra_lines:
        lines.extend(extra_lines)
    return "\n".join(lines)


class _MetadataResult:
    def __init__(self, returncode, outputs, log, summary):
        self.returncode = returncode
        self.outputs = outputs
        self.log = log
        self.summary = summary


def _run_metadata_step(
    event: dict,
    derived_version: str,
    derived_channel: str,
) -> _MetadataResult:
    code = _extract_python(_steps_by_name(_handoff_job())[METADATA_STEP]["run"])
    with tempfile.TemporaryDirectory() as tmp:
        event_path = Path(tmp) / "event.json"
        output_path = Path(tmp) / "output.txt"
        summary_path = Path(tmp) / "summary.md"
        event_path.write_text(json.dumps(event), encoding="utf-8")
        proc = _run_python(
            code,
            {
                "GITHUB_EVENT_PATH": str(event_path),
                "GITHUB_OUTPUT": str(output_path),
                "GITHUB_STEP_SUMMARY": str(summary_path),
                "DERIVED_VERSION": derived_version,
                "DERIVED_CHANNEL": derived_channel,
            },
        )
        outputs = {}
        if output_path.exists():
            for line in output_path.read_text(encoding="utf-8").splitlines():
                key, _, value = line.partition("=")
                outputs[key] = value
        summary = ""
        if summary_path.exists():
            summary = summary_path.read_text(encoding="utf-8")
        return _MetadataResult(
            proc.returncode, outputs, proc.stdout + proc.stderr, summary
        )


def _make_event(tag: str, body: str, release_id=987654321) -> dict:
    return {"release": {"tag_name": tag, "id": release_id, "body": body}}


# ---------------------------------------------------------------------------
# Local loopback HTTP servers standing in for the GitHub API
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _serve(handler_cls):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)


def _make_assets_handler(asset_names):
    requests_seen: list[str] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 (stdlib API name)
            requests_seen.append(self.path)
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            page = int(query.get("page", ["1"])[0])
            per_page = int(query.get("per_page", ["30"])[0])
            start = (page - 1) * per_page
            batch = asset_names[start : start + per_page]
            payload = json.dumps([{"name": n} for n in batch]).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    return Handler, requests_seen


def _make_dispatch_handler(status=204, message="boom"):
    captured: list[dict] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):  # noqa: N802 (stdlib API name)
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            try:
                body = json.loads(raw.decode("utf-8")) if raw else None
            except ValueError:
                body = raw.decode("utf-8", "replace")
            captured.append(
                {
                    "path": self.path,
                    "authorization": self.headers.get("Authorization"),
                    "body": body,
                }
            )
            if status == 204:
                self.send_response(204)
                self.send_header("Content-Length", "0")
                self.end_headers()
            else:
                payload = json.dumps({"message": message}).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        def log_message(self, *args):
            pass

    return Handler, captured


def _run_assets_step(
    api_url: str,
    release_id: str = "987654321",
    artifact: str = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin",
    token: str = "read-only-token",
    repository: str = "sense360store/esphome-public",
) -> subprocess.CompletedProcess:
    code = _extract_python(_steps_by_name(_handoff_job())[ASSETS_STEP]["run"])
    return _run_python(
        code,
        {
            "GITHUB_API_URL": api_url,
            "GITHUB_REPOSITORY": repository,
            "GH_API_TOKEN": token,
            "RELEASE_ID": release_id,
            "ARTIFACT_NAME": artifact,
        },
    )


def _run_dispatch_step(
    api_url: str,
    token: str | None = "intake-token-abc123",
    tag: str = "v1.0.7",
    config: str = "Ceiling-POE-VentIQ-RoomIQ",
):
    code = _extract_python(_steps_by_name(_handoff_job())[DISPATCH_STEP]["run"])
    with tempfile.TemporaryDirectory() as tmp:
        summary_path = Path(tmp) / "summary.md"
        env = {
            "GITHUB_API_URL": api_url,
            "RELEASE_TAG": tag,
            "CONFIG_STRING": config,
            "GITHUB_STEP_SUMMARY": str(summary_path),
        }
        if token is not None:
            env["WEBFLASH_INTAKE_TOKEN"] = token
        proc = _run_python(code, env)
        summary = ""
        if summary_path.exists():
            summary = summary_path.read_text(encoding="utf-8")
        return proc, summary


# ---------------------------------------------------------------------------
# Structural contract: job shape, dependencies, no checkout, no scripts
# ---------------------------------------------------------------------------


class HandoffJobShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = _load_workflow()
        cls.job = cls.workflow["jobs"][JOB_ID]
        cls.steps = _steps_by_name(cls.job)
        cls.raw_job = _raw_job_text()

    def test_existing_jobs_are_untouched(self) -> None:
        self.assertEqual(
            list(self.workflow["jobs"]),
            ["generate-matrix", "build", "release", "summary", JOB_ID],
            "firmware-build-release.yml must keep its four existing jobs "
            "and add exactly the webflash-handoff job",
        )

    def test_handoff_needs_successful_release_job(self) -> None:
        needs = self.job.get("needs")
        self.assertIsInstance(needs, list)
        self.assertIn(
            "release",
            needs,
            "the handoff must depend on the release (Attach to Release) job",
        )
        self.assertIn(
            "generate-matrix",
            needs,
            "the handoff must consume the generate-matrix derived "
            "version/channel outputs, so it must depend on that job",
        )

    def test_handoff_runs_only_on_release_job_success(self) -> None:
        condition = str(self.job.get("if", ""))
        for override in ("always()", "failure()", "cancelled()"):
            self.assertNotIn(
                override,
                condition,
                f"the handoff job's if: must not use {override}; the "
                "default needs semantics (run only when every needed job "
                "succeeded) are the success gate",
            )

    def test_handoff_is_pinned_to_the_canonical_repository(self) -> None:
        condition = str(self.job.get("if", ""))
        self.assertIn(
            "github.repository == 'sense360store/esphome-public'",
            condition,
            "the handoff must be pinned to sense360store/esphome-public so "
            "a fork cannot dispatch a handoff claiming upstream provenance",
        )

    def test_no_step_uses_any_action(self) -> None:
        # No uses: at all => no actions/checkout, no third-party actions,
        # nothing that could read repository code into the job.
        for step in self.job.get("steps", []):
            self.assertNotIn(
                "uses",
                step,
                f"handoff step {step.get('name')!r} must not use any "
                "action (no repository checkout, no third-party code)",
            )

    def test_every_step_is_a_single_fixed_python_heredoc(self) -> None:
        # The shell never sees anything but the fixed `python3 - <<'PY'`
        # invocation, so no untrusted value can reach shell execution.
        for step in self.job.get("steps", []):
            run_text = step.get("run", "")
            self.assertRegex(
                run_text,
                r"(?s)^python3 - <<'PY'\n.*\nPY\n?$",
                f"handoff step {step.get('name')!r} run block must be "
                "exactly one quoted python3 heredoc and nothing else",
            )

    def test_no_repo_local_scripts_and_no_subprocesses(self) -> None:
        for step in self.job.get("steps", []):
            code = _strip_python_comments(_extract_python(step.get("run", "")))
            for forbidden in (
                "scripts/",
                "tests/",
                "subprocess",
                "os.system",
                "os.exec",
                "os.spawn",
                "checkout",
                "pty.",
            ):
                self.assertNotIn(
                    forbidden,
                    code,
                    f"handoff step {step.get('name')!r} inline Python must "
                    f"not contain {forbidden!r}: the job never executes "
                    "repo-local scripts or child processes",
                )

    def test_expected_steps_exist_in_order(self) -> None:
        names = [s.get("name") for s in self.job.get("steps", [])]
        self.assertEqual(
            names,
            [METADATA_STEP, ASSETS_STEP, DISPATCH_STEP],
            "the handoff job must be exactly: parse/validate metadata -> "
            "verify remote assets -> dispatch",
        )

    def test_asset_and_dispatch_steps_are_gated_on_dispatch_output(self) -> None:
        for name in (ASSETS_STEP, DISPATCH_STEP):
            condition = str(self.steps[name].get("if", ""))
            self.assertIn(
                "steps.metadata.outputs.dispatch == 'true'",
                condition,
                f"step {name!r} must run only when the validated metadata "
                "selected a WebFlash-served channel",
            )

    def test_handoff_job_has_no_permissions_block(self) -> None:
        self.assertNotIn(
            "permissions",
            self.job,
            "the handoff job must not add a permissions block; it inherits "
            "the workflow's read-only default (no deployment / merge / "
            "publishing permission is introduced)",
        )

    def test_workflow_top_level_permissions_stay_read_only(self) -> None:
        self.assertEqual(
            self.workflow.get("permissions"),
            {"contents": "read"},
            "firmware-build-release.yml top-level permissions must stay "
            "contents: read",
        )

    def test_release_job_permissions_unchanged(self) -> None:
        release = self.workflow["jobs"]["release"]
        self.assertEqual(
            release.get("permissions"),
            {"contents": "write", "id-token": "write"},
            "the release job's job-scoped permissions must not change",
        )
        for job_id, job in self.workflow["jobs"].items():
            if job_id == "release":
                continue
            self.assertNotIn(
                "permissions",
                job,
                f"job {job_id!r} must not gain a permissions block",
            )

    def test_metadata_step_does_not_trust_event_assets_array(self) -> None:
        code = _strip_python_comments(_extract_python(self.steps[METADATA_STEP]["run"]))
        self.assertNotIn(
            '"assets"',
            code,
            "the metadata step must not read the release event's assets "
            "array; the published event predates the Release 3 upload, so "
            "assets are proven via the GitHub API in the assets step",
        )

    def test_metadata_step_ignores_catalog_status(self) -> None:
        code = _strip_python_comments(_extract_python(self.steps[METADATA_STEP]["run"]))
        self.assertNotIn(
            "catalog",
            code.lower(),
            "the metadata step must not consult catalog/lifecycle status: "
            "upstream product status can neither grant nor deny WebFlash "
            "intake (WebFlash owns eligibility)",
        )

    def test_assets_step_queries_the_remote_release(self) -> None:
        code = _strip_python_comments(_extract_python(self.steps[ASSETS_STEP]["run"]))
        self.assertIn("/releases/", code)
        self.assertIn("/assets", code)
        for sidecar in REQUIRED_SIDECAR_ASSETS:
            self.assertIn(
                f'"{sidecar}"',
                code,
                f"the assets step must require {sidecar} on the remote "
                "release before any dispatch",
            )

    def test_dispatch_targets_exactly_webflash_intake_on_main(self) -> None:
        code = _strip_python_comments(_extract_python(self.steps[DISPATCH_STEP]["run"]))
        self.assertIn('WEBFLASH_REPO = "sense360store/WebFlash"', code)
        self.assertIn('INTAKE_WORKFLOW = "firmware-intake.yml"', code)
        self.assertIn('INTAKE_REF = "main"', code)
        self.assertIn('SOURCE_REPO = "sense360store/esphome-public"', code)


# ---------------------------------------------------------------------------
# Expression safety: raw event values can never reach shell execution
# ---------------------------------------------------------------------------


class HandoffExpressionSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_job = _raw_job_text()
        cls.job = _handoff_job()

    def test_job_expressions_are_allowlisted(self) -> None:
        found = set(EXPRESSION_RE.findall(self.raw_job))
        offending = found - ALLOWED_JOB_EXPRESSIONS
        self.assertEqual(
            offending,
            set(),
            "the handoff job may only use the allowlisted trusted GitHub "
            f"expressions; found unexpected: {sorted(offending)!r}",
        )

    def test_no_event_payload_expression_in_job(self) -> None:
        self.assertNotIn(
            "github.event.",
            self.raw_job.replace("github.event_name", ""),
            "the handoff job must never expand github.event.* (release "
            "body/tag/metadata) via ${{ }}; the event is read from "
            "GITHUB_EVENT_PATH inside Python instead",
        )

    def test_run_blocks_contain_no_github_expressions(self) -> None:
        for step in self.job.get("steps", []):
            self.assertNotIn(
                "${{",
                step.get("run", ""),
                f"step {step.get('name')!r} run block must not expand any "
                "GitHub expression into script text; values are bound via "
                "env: only",
            )

    def test_untrusted_values_flow_env_only(self) -> None:
        # The metadata step exposes only the two derived values; the
        # assets/dispatch steps take only validated step outputs + tokens.
        steps = _steps_by_name(self.job)
        self.assertEqual(
            set(steps[METADATA_STEP].get("env", {})),
            {"DERIVED_VERSION", "DERIVED_CHANNEL"},
        )
        self.assertEqual(
            set(steps[ASSETS_STEP].get("env", {})),
            {"GH_API_TOKEN", "RELEASE_ID", "ARTIFACT_NAME"},
        )
        self.assertEqual(
            set(steps[DISPATCH_STEP].get("env", {})),
            {"WEBFLASH_INTAKE_TOKEN", "RELEASE_TAG", "CONFIG_STRING"},
        )


# ---------------------------------------------------------------------------
# Token scoping
# ---------------------------------------------------------------------------


class TokenScopingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw_workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        cls.steps = _steps_by_name(_handoff_job())

    def test_intake_secret_is_referenced_exactly_once(self) -> None:
        self.assertEqual(
            self.raw_workflow.count("secrets.WEBFLASH_INTAKE_TOKEN"),
            1,
            "secrets.WEBFLASH_INTAKE_TOKEN must be referenced exactly once "
            "in firmware-build-release.yml (the final dispatch step's env)",
        )

    def test_intake_secret_is_bound_only_to_the_dispatch_step(self) -> None:
        dispatch_env = self.steps[DISPATCH_STEP].get("env", {})
        self.assertEqual(
            dispatch_env.get("WEBFLASH_INTAKE_TOKEN"),
            "${{ secrets.WEBFLASH_INTAKE_TOKEN }}",
        )
        for name, step in self.steps.items():
            if name == DISPATCH_STEP:
                continue
            env_text = json.dumps(step.get("env", {}))
            self.assertNotIn(
                "WEBFLASH_INTAKE_TOKEN",
                env_text,
                f"step {name!r} must not see WEBFLASH_INTAKE_TOKEN "
                "(checkout, parsing, validation, asset inspection and "
                "summaries are all out of the secret's scope)",
            )

    def test_dispatch_step_uses_no_other_credential(self) -> None:
        step_env = self.steps[DISPATCH_STEP].get("env", {})
        for key, value in step_env.items():
            if key == "WEBFLASH_INTAKE_TOKEN":
                continue
            self.assertNotIn("secrets.", str(value))
            self.assertNotIn("github.token", str(value))
        code = _extract_python(self.steps[DISPATCH_STEP]["run"])
        self.assertNotIn("GITHUB_TOKEN", code)
        self.assertNotIn("GH_API_TOKEN", code)

    def test_asset_step_uses_only_the_read_only_workflow_token(self) -> None:
        env = self.steps[ASSETS_STEP].get("env", {})
        self.assertEqual(env.get("GH_API_TOKEN"), "${{ github.token }}")

    def test_release_pat_is_not_touched(self) -> None:
        self.assertNotIn(
            "RELEASE_PAT",
            self.raw_workflow,
            "firmware-build-release.yml must not reference RELEASE_PAT; "
            "that secret belongs to create-release.yml and is unchanged",
        )


# ---------------------------------------------------------------------------
# Behaviour: metadata parsing / validation (executes the real inline Python)
# ---------------------------------------------------------------------------


class MetadataStepBehaviourTests(unittest.TestCase):
    def test_stable_release_dispatches(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(result.outputs.get("dispatch"), "true")
        self.assertEqual(result.outputs.get("release_tag"), "v1.0.7")
        self.assertEqual(
            result.outputs.get("config_string"), "Ceiling-POE-VentIQ-RoomIQ"
        )
        self.assertEqual(
            result.outputs.get("artifact_name"),
            "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin",
        )
        self.assertEqual(result.outputs.get("release_id"), "987654321")

    def test_preview_release_dispatches(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.1-preview",
                _make_release_body(
                    "Ceiling-POE-VentIQ-RoomIQ-LED",
                    "1.0.1",
                    "preview",
                    status="preview",
                ),
            ),
            "1.0.1",
            "preview",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(result.outputs.get("dispatch"), "true")

    def test_led_preview_tag_dispatches(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.1-led-preview",
                _make_release_body(
                    "Ceiling-POE-VentIQ-RoomIQ-LED",
                    "1.0.1",
                    "preview",
                    status="preview",
                ),
            ),
            "1.0.1",
            "preview",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(result.outputs.get("dispatch"), "true")

    def test_experimental_release_skips_successfully(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.0-experimental",
                _make_release_body(
                    "Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
                    "1.0.0",
                    "experimental",
                    status="preview",
                ),
            ),
            "1.0.0",
            "experimental",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(result.outputs.get("dispatch"), "false")
        self.assertIn("not", result.summary.lower())
        self.assertIn("experimental", result.summary.lower())
        self.assertIn("No WebFlash dispatch", result.log)

    def test_upstream_status_cannot_grant_or_deny_intake(self) -> None:
        # Identical release, three different upstream lifecycle claims —
        # the handoff outcome must be identical: status is never consulted.
        outcomes = []
        for status in ("production", "blocked", "definitely-not-a-status"):
            result = _run_metadata_step(
                _make_event(
                    "v1.0.7",
                    _make_release_body(
                        "Ceiling-POE-VentIQ-RoomIQ",
                        "1.0.7",
                        "stable",
                        status=status,
                    ),
                ),
                "1.0.7",
                "stable",
            )
            outcomes.append((result.returncode, result.outputs.get("dispatch")))
        self.assertEqual(
            outcomes,
            [(0, "true")] * 3,
            "upstream catalog/lifecycle status must neither grant nor deny "
            "WebFlash intake",
        )

    def test_malformed_config_string_fails_closed(self) -> None:
        for config in (
            "Ceiling POE VentIQ",
            "X-$(id)-Y",
            "Ceiling-POE-VentIQ-RoomIQ;rm",
            "Ceiling",
            "-leading-hyphen",
            "",
            "A" * 200,
        ):
            result = _run_metadata_step(
                _make_event(
                    "v1.0.7",
                    _make_release_body(config, "1.0.7", "stable"),
                ),
                "1.0.7",
                "stable",
            )
            self.assertNotEqual(
                result.returncode,
                0,
                f"config {config!r} must fail closed",
            )
            self.assertNotIn("dispatch", result.outputs)

    def test_malformed_version_fails_closed(self) -> None:
        for version in ("1.0", "v1.0.7", "1.0.7.8", "1.0.7-rc1", "junk"):
            result = _run_metadata_step(
                _make_event(
                    "v1.0.7",
                    _make_release_body("Ceiling-POE-VentIQ-RoomIQ", version, "stable"),
                ),
                "1.0.7",
                "stable",
            )
            self.assertNotEqual(
                result.returncode,
                0,
                f"version {version!r} must fail closed",
            )

    def test_unknown_channel_fails_closed(self) -> None:
        for channel in ("beta", "dev", "rescue", "Stable", "junk"):
            result = _run_metadata_step(
                _make_event(
                    "v1.0.7",
                    _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", channel),
                ),
                "1.0.7",
                channel,
            )
            self.assertNotEqual(
                result.returncode,
                0,
                f"channel {channel!r} must fail closed (not silently skip)",
            )

    def test_body_version_must_equal_derived_version(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.6", "stable"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("derived version", result.log)

    def test_body_channel_must_equal_derived_channel(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "preview"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("derived channel", result.log)

    def test_tag_version_must_equal_derived_version(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.8",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_tag_suffix_must_be_coherent_with_channel(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7-experimental",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_malformed_tag_fails_closed(self) -> None:
        for tag in (
            "1.0.7",
            "v1.0.7-evil",
            "v1.0.7-preview; rm -rf /",
            "v1.0.7 && echo pwned",
            "refs/tags/v1.0.7",
        ):
            result = _run_metadata_step(
                _make_event(
                    tag,
                    _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
                ),
                "1.0.7",
                "stable",
            )
            self.assertNotEqual(result.returncode, 0, f"tag {tag!r} must fail closed")

    def test_artifact_mismatch_fails_closed(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body(
                    "Ceiling-POE-VentIQ-RoomIQ",
                    "1.0.7",
                    "stable",
                    artifact=("Sense360-Ceiling-POE-RoomIQ-v1.0.7-stable.bin"),
                ),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical artifact name", result.log)

    def test_unset_artifact_fails_closed(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body(
                    "Ceiling-POE-VentIQ-RoomIQ",
                    "1.0.7",
                    "stable",
                    artifact="<unset>",
                ),
            ),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)

    def test_missing_preamble_labels_fail_closed(self) -> None:
        result = _run_metadata_step(
            _make_event("v1.0.7", "## Changelog\n\n- No preamble here.\n"),
            "1.0.7",
            "stable",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing", result.log)

    def test_conflicting_duplicate_labels_fail_closed(self) -> None:
        body = _make_release_body(
            "Ceiling-POE-VentIQ-RoomIQ",
            "1.0.7",
            "stable",
            extra_lines=["", "Config string : Ceiling-POE-RoomIQ"],
        )
        result = _run_metadata_step(_make_event("v1.0.7", body), "1.0.7", "stable")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflicting", result.log)

    def test_repeated_identical_labels_are_tolerated(self) -> None:
        # An exact duplicate of the same line is not a conflict.
        body = _make_release_body(
            "Ceiling-POE-VentIQ-RoomIQ",
            "1.0.7",
            "stable",
            extra_lines=["", "Config string : Ceiling-POE-VentIQ-RoomIQ"],
        )
        result = _run_metadata_step(_make_event("v1.0.7", body), "1.0.7", "stable")
        self.assertEqual(result.returncode, 0, result.log)

    def test_non_integer_release_id_fails_closed(self) -> None:
        for bogus in ("123", None, True, -5, 0):
            event = _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
                release_id=bogus,
            )
            result = _run_metadata_step(event, "1.0.7", "stable")
            self.assertNotEqual(
                result.returncode,
                0,
                f"release id {bogus!r} must fail closed",
            )

    def test_missing_or_empty_body_fails_closed(self) -> None:
        for body in ("", "   \n  "):
            result = _run_metadata_step(_make_event("v1.0.7", body), "1.0.7", "stable")
            self.assertNotEqual(result.returncode, 0)

    def test_step_outputs_cannot_be_injected(self) -> None:
        # Every emitted output value is allowlist-checked; the parsed
        # values themselves cannot contain whitespace, so a crafted body
        # cannot smuggle extra `key=value` lines into GITHUB_OUTPUT.
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(
            sorted(result.outputs),
            [
                "artifact_name",
                "config_string",
                "dispatch",
                "release_id",
                "release_tag",
            ],
        )


# ---------------------------------------------------------------------------
# Behaviour: remote asset verification (loopback GitHub API)
# ---------------------------------------------------------------------------


class AssetsStepBehaviourTests(unittest.TestCase):
    ARTIFACT = "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin"
    FULL_SET = [
        "Sense360-Ceiling-POE-VentIQ-RoomIQ-v1.0.7-stable.bin",
        "checksums-sha256.txt",
        "checksums-sha256.txt.sig",
        "checksums-sha256.txt.pem",
        "checksums-md5.txt",
        "manifest.json",
    ]

    def test_all_required_assets_present_passes(self) -> None:
        handler, seen = _make_assets_handler(self.FULL_SET)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertTrue(seen, "the step must query the remote release")
        self.assertIn("/releases/987654321/assets", seen[0])

    def test_missing_manifest_refuses_dispatch(self) -> None:
        assets = [a for a in self.FULL_SET if a != "manifest.json"]
        handler, _ = _make_assets_handler(assets)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("manifest.json", proc.stdout + proc.stderr)

    def test_missing_signature_refuses_dispatch(self) -> None:
        assets = [a for a in self.FULL_SET if a != "checksums-sha256.txt.sig"]
        handler, _ = _make_assets_handler(assets)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("checksums-sha256.txt.sig", proc.stdout + proc.stderr)

    def test_missing_selected_artifact_refuses_dispatch(self) -> None:
        assets = [a for a in self.FULL_SET if a != self.ARTIFACT]
        handler, _ = _make_assets_handler(assets)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn(self.ARTIFACT, proc.stdout + proc.stderr)

    def test_asset_listing_is_paginated(self) -> None:
        padding = [f"Extra-{i:03d}.txt" for i in range(220)]
        handler, seen = _make_assets_handler(padding + self.FULL_SET)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertGreaterEqual(
            len(seen),
            3,
            "the step must page through the asset listing rather than "
            "trusting the first page",
        )

    def test_invalid_release_id_fails_before_any_request(self) -> None:
        handler, seen = _make_assets_handler(self.FULL_SET)
        with _serve(handler) as api_url:
            proc = _run_assets_step(
                api_url, release_id="123; rm -rf /", artifact=self.ARTIFACT
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(
            seen, [], "no API request may be made with an " "invalid release id"
        )

    def test_invalid_artifact_name_fails_before_any_request(self) -> None:
        handler, seen = _make_assets_handler(self.FULL_SET)
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact="../../evil.bin")
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(seen, [])

    def test_read_token_is_never_printed(self) -> None:
        handler, _ = _make_assets_handler(self.FULL_SET)
        token = "super-secret-read-token-xyz"
        with _serve(handler) as api_url:
            proc = _run_assets_step(api_url, artifact=self.ARTIFACT, token=token)
        self.assertNotIn(token, proc.stdout + proc.stderr)


# ---------------------------------------------------------------------------
# Behaviour: WebFlash dispatch (loopback GitHub API)
# ---------------------------------------------------------------------------


class DispatchStepBehaviourTests(unittest.TestCase):
    def test_successful_dispatch_sends_minimum_trustworthy_inputs(self) -> None:
        handler, captured = _make_dispatch_handler(status=204)
        with _serve(handler) as api_url:
            proc, summary = _run_dispatch_step(
                api_url,
                token="intake-token-abc123",
                tag="v1.0.7",
                config="Ceiling-POE-VentIQ-RoomIQ",
            )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertEqual(len(captured), 1)
        request = captured[0]
        self.assertEqual(request["path"], DISPATCH_PATH)
        self.assertEqual(request["authorization"], "Bearer intake-token-abc123")
        self.assertEqual(
            request["body"],
            {
                "ref": "main",
                "inputs": {
                    "release_tag": "v1.0.7",
                    "config_string": "Ceiling-POE-VentIQ-RoomIQ",
                    "source_repo": "sense360store/esphome-public",
                    "dry_run": "false",
                },
            },
            "the dispatch must carry exactly the minimum trustworthy "
            "inputs; version/channel are omitted so WebFlash derives them "
            "from the tag",
        )
        # A 204 means only "handoff accepted", never "import succeeded".
        output = proc.stdout + summary
        self.assertIn("ACCEPTED", output)
        self.assertIn("NOT", output)

    def test_token_is_never_printed(self) -> None:
        handler, _ = _make_dispatch_handler(status=204)
        token = "intake-token-do-not-print-9f8e7d"
        with _serve(handler) as api_url:
            proc, summary = _run_dispatch_step(api_url, token=token)
        self.assertNotIn(token, proc.stdout + proc.stderr + summary)

    def test_missing_token_fails_loudly_with_recovery_path(self) -> None:
        # Point at a closed port: if the step wrongly attempted a request
        # without the token it would fail differently; asserting on the
        # message proves the guard fired first.
        proc, _ = _run_dispatch_step("http://127.0.0.1:9", token=None)
        self.assertNotEqual(proc.returncode, 0)
        output = proc.stdout + proc.stderr
        self.assertIn("WEBFLASH_INTAKE_TOKEN", output)
        self.assertIn("already", output)
        self.assertIn("manual", output.lower())
        self.assertIn("Release: Firmware Intake", output)

    def test_empty_token_fails_loudly(self) -> None:
        proc, _ = _run_dispatch_step("http://127.0.0.1:9", token="")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("WEBFLASH_INTAKE_TOKEN", proc.stdout + proc.stderr)

    def test_refused_dispatch_fails_without_leaking_token(self) -> None:
        handler, captured = _make_dispatch_handler(status=404)
        token = "intake-token-abc123"
        with _serve(handler) as api_url:
            proc, summary = _run_dispatch_step(api_url, token=token)
        self.assertNotEqual(proc.returncode, 0)
        output = proc.stdout + proc.stderr + summary
        self.assertIn("404", output)
        self.assertNotIn(token, output)
        self.assertEqual(len(captured), 1)

    def test_experimental_tag_is_refused_even_here(self) -> None:
        # Defense in depth: the dispatch step's own allowlist excludes
        # -experimental tags, so a broken upstream gate still cannot
        # dispatch the experimental lane.
        handler, captured = _make_dispatch_handler(status=204)
        with _serve(handler) as api_url:
            proc, _ = _run_dispatch_step(
                api_url,
                tag="v1.0.0-experimental",
                config="Ceiling-POE-VentIQ-FanTRIAC-RoomIQ",
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(
            captured, [], "no dispatch request may be sent " "for an experimental tag"
        )

    def test_malformed_tag_or_config_refused_before_any_request(self) -> None:
        cases = [
            ("v1.0.7; rm -rf /", "Ceiling-POE-VentIQ-RoomIQ"),
            ("v1.0.7", "X-$(id)-Y"),
            ("", "Ceiling-POE-VentIQ-RoomIQ"),
            ("v1.0.7", ""),
        ]
        for tag, config in cases:
            handler, captured = _make_dispatch_handler(status=204)
            with _serve(handler) as api_url:
                proc, _ = _run_dispatch_step(api_url, tag=tag, config=config)
            self.assertNotEqual(
                proc.returncode,
                0,
                f"tag={tag!r} config={config!r} must be refused",
            )
            self.assertEqual(captured, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
