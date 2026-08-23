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

import ast
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
    "needs.generate-matrix.outputs.built_config_strings",
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


def _config_from_body(body: str) -> str:
    match = re.search(r"^Config string\s*:\s*(.+?)\s*$", body or "", re.MULTILINE)
    return match.group(1) if match else "Ceiling-POE-VentIQ-RoomIQ"


def _run_metadata_step(
    event: dict,
    derived_version: str,
    derived_channel: str,
    built_config_strings: str | None = None,
) -> _MetadataResult:
    code = _extract_python(_steps_by_name(_handoff_job())[METADATA_STEP]["run"])
    if built_config_strings is None:
        # Default: the config named in the body is the (only) built config,
        # matching the common single-config release. Tests that exercise the
        # multi-config smuggling guard pass an explicit built set.
        body = (event.get("release") or {}).get("body") or ""
        built_config_strings = _config_from_body(body)
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
                "BUILT_CONFIG_STRINGS": built_config_strings,
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


def _make_redirect_handler(location: str):
    """A server that 302-redirects every request to ``location``, recording
    whether the incoming request carried an Authorization header."""
    saw_auth: list[str | None] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def _redirect(self):
            saw_auth.append(self.headers.get("Authorization"))
            length = int(self.headers.get("Content-Length", "0"))
            if length:
                self.rfile.read(length)
            self.send_response(302)
            self.send_header("Location", location)
            self.send_header("Content-Length", "0")
            self.end_headers()

        do_GET = _redirect  # noqa: N815
        do_POST = _redirect  # noqa: N815

        def log_message(self, *args):
            pass

    return Handler, saw_auth


def _make_recording_handler():
    """A second-host server that records the Authorization header of any
    request it receives (it should receive none when redirects are refused)."""
    received: list[dict] = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def _record(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length:
                self.rfile.read(length)
            received.append({"authorization": self.headers.get("Authorization")})
            payload = b"[]"
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        do_GET = _record  # noqa: N815
        do_POST = _record  # noqa: N815

        def log_message(self, *args):
            pass

    return Handler, received


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
        # Fast substring backstop for the obvious offenders. The AST test
        # below is the authoritative, fail-closed guard.
        for step in self.job.get("steps", []):
            code = _strip_python_comments(_extract_python(step.get("run", "")))
            for forbidden in (
                "scripts/",
                "tests/",
                "subprocess",
                "os.system",
                "os.popen",
                "os.exec",
                "os.spawn",
                "os.posix_spawn",
                "os.fork",
                "popen2",
                "runpy",
                "commands",
                "checkout",
                "pty.",
                "__import__",
            ):
                self.assertNotIn(
                    forbidden,
                    code,
                    f"handoff step {step.get('name')!r} inline Python must "
                    f"not contain {forbidden!r}: the job never executes "
                    "repo-local scripts or child processes",
                )

    def test_inline_python_imports_and_calls_are_allowlisted(self) -> None:
        # Authoritative fail-closed guard for the "no checkout / no repo
        # scripts / no child process / no dynamic eval" contract: parse each
        # step's inline Python with the ast module and reject any import
        # outside a small allowlist and any call to a shell/process/eval
        # spawner. Unknown FUTURE spawners are caught by default, unlike a
        # substring denylist that only names what someone remembered.
        allowed_modules = {
            "json",
            "os",
            "re",
            "sys",
            "time",
            "urllib",
            "urllib.request",
            "urllib.error",
            "urllib.parse",
            "pathlib",
        }
        # Bare built-in names that execute code / import dynamically.
        forbidden_names = {"eval", "exec", "compile", "__import__"}
        # Dotted module.attr calls that spawn a shell / process. re.compile,
        # json.loads etc. are dotted too but are NOT in this set, so they are
        # allowed; only the process/shell spawners are rejected.
        forbidden_dotted = {
            "os.system",
            "os.popen",
            "os.fork",
            "os.posix_spawn",
            "os.execv",
            "os.execve",
            "os.execvp",
            "os.execvpe",
            "os.execl",
            "os.execle",
            "os.execlp",
            "os.spawnv",
            "os.spawnve",
            "os.spawnl",
            "os.spawnlp",
            "subprocess.run",
            "subprocess.Popen",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
        }
        for step in self.job.get("steps", []):
            name = step.get("name")
            tree = ast.parse(_extract_python(step.get("run", "")))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.assertIn(
                            alias.name,
                            allowed_modules,
                            f"handoff step {name!r} imports {alias.name!r}, "
                            "which is not in the allowlist; a handoff step "
                            "must not pull in modules that can execute code "
                            "or touch the repo",
                        )
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    self.assertIn(
                        module,
                        allowed_modules,
                        f"handoff step {name!r} imports from {module!r}, "
                        "which is not in the allowlist",
                    )
                elif isinstance(node, ast.Call):
                    func = node.func
                    bare = None
                    dotted = None
                    if isinstance(func, ast.Name):
                        bare = func.id
                    elif isinstance(func, ast.Attribute) and isinstance(
                        func.value, ast.Name
                    ):
                        dotted = f"{func.value.id}.{func.attr}"
                    self.assertNotIn(
                        bare,
                        forbidden_names,
                        f"handoff step {name!r} calls the built-in "
                        f"{bare!r}, a dynamic-eval/import primitive forbidden "
                        "in the handoff job",
                    )
                    self.assertNotIn(
                        dotted,
                        forbidden_dotted,
                        f"handoff step {name!r} calls {dotted!r}, a "
                        "shell/process spawner forbidden in the handoff job",
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
        # Exact-match: the two gated steps run ONLY on the validated dispatch
        # flag. An exact equality (not just `in`) means an injected status
        # function or an extra clause would fail this test — the implicit
        # step-level success() chain that the remote-asset proof and the
        # experimental-skip both depend on cannot be silently weakened.
        for name in (ASSETS_STEP, DISPATCH_STEP):
            condition = str(self.steps[name].get("if", ""))
            self.assertEqual(
                condition,
                "steps.metadata.outputs.dispatch == 'true'",
                f"step {name!r} must run only when the validated metadata "
                "selected a WebFlash-served channel, with no extra clause",
            )

    def test_no_step_if_uses_a_status_override_function(self) -> None:
        # A step-level if: that used always() / success() / failure() /
        # cancelled() would run (or skip) regardless of whether the prior
        # step actually succeeded, silently defeating the ordered gates
        # (metadata validation -> remote-asset proof -> dispatch). Forbid
        # them on every step.
        for step in self.job.get("steps", []):
            condition = str(step.get("if", ""))
            for override in ("always(", "success(", "failure(", "cancelled("):
                self.assertNotIn(
                    override,
                    condition,
                    f"handoff step {step.get('name')!r} if: must not use "
                    f"{override}); the ordered success chain is the gate",
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

    def test_token_bearing_steps_refuse_http_redirects(self) -> None:
        # Both API-calling steps carry a credential (github.token / the
        # WEBFLASH_INTAKE_TOKEN). urllib's default opener would follow a 30x
        # AND re-send the Authorization header to the redirect host, leaking
        # the token. Each such step must install a redirect-refusing opener.
        steps = _steps_by_name(self.job)
        for name in (ASSETS_STEP, DISPATCH_STEP):
            code = _extract_python(steps[name]["run"])
            self.assertIn(
                "HTTPRedirectHandler",
                code,
                f"step {name!r} must install a redirect-refusing opener so a "
                "token-bearing request never follows a cross-host redirect",
            )
            self.assertIn("build_opener", code)
            self.assertNotIn(
                "urllib.request.urlopen(",
                code,
                f"step {name!r} must not use the default urlopen (which "
                "follows redirects); use the no-redirect opener",
            )

    def test_untrusted_values_flow_env_only(self) -> None:
        # The metadata step exposes only the trusted generate-matrix outputs;
        # the assets/dispatch steps take only validated step outputs + tokens.
        steps = _steps_by_name(self.job)
        self.assertEqual(
            set(steps[METADATA_STEP].get("env", {})),
            {"DERIVED_VERSION", "DERIVED_CHANNEL", "BUILT_CONFIG_STRINGS"},
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

    def test_config_must_be_in_built_set(self) -> None:
        # A well-formed body config that is NOT among the configs Release 3
        # built for this (version, channel) fails closed, even though its
        # version/channel/artifact are internally consistent.
        result = _run_metadata_step(
            _make_event(
                "v1.0.0-preview",
                _make_release_body(
                    "Ceiling-POE-RoomIQ", "1.0.0", "preview", status="preview"
                ),
            ),
            "1.0.0",
            "preview",
            built_config_strings="Ceiling-POE-FanPWM Ceiling-POE-FanDAC",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not among", result.log)

    def test_co_built_config_in_set_dispatches(self) -> None:
        # A multi-config release: the body names one of the co-built configs
        # (which is legitimately in the trusted built set) -> dispatch.
        result = _run_metadata_step(
            _make_event(
                "v1.0.0-preview",
                _make_release_body(
                    "Ceiling-POE-FanPWM", "1.0.0", "preview", status="preview"
                ),
            ),
            "1.0.0",
            "preview",
            built_config_strings="Ceiling-POE-FanPWM Ceiling-POE-FanDAC",
        )
        self.assertEqual(result.returncode, 0, result.log)
        self.assertEqual(result.outputs.get("dispatch"), "true")
        self.assertEqual(result.outputs.get("config_string"), "Ceiling-POE-FanPWM")

    def test_empty_built_set_fails_closed(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
            built_config_strings="",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("built config", result.log)

    def test_malformed_built_set_entry_fails_closed(self) -> None:
        result = _run_metadata_step(
            _make_event(
                "v1.0.7",
                _make_release_body("Ceiling-POE-VentIQ-RoomIQ", "1.0.7", "stable"),
            ),
            "1.0.7",
            "stable",
            built_config_strings="Ceiling-POE-VentIQ-RoomIQ $(evil)",
        )
        self.assertNotEqual(result.returncode, 0)

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

    def test_cross_host_redirect_is_refused_and_token_not_resent(self) -> None:
        token = "read-token-must-not-leak-42"
        recorder, received = _make_recording_handler()
        with _serve(recorder) as second_url:
            redirector, _ = _make_redirect_handler(second_url + "/assets")
            with _serve(redirector) as api_url:
                proc = _run_assets_step(api_url, artifact=self.ARTIFACT, token=token)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(
            received,
            [],
            "the github.token must never be re-sent to a redirect target",
        )
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

    def test_cross_host_redirect_is_refused_and_token_not_resent(self) -> None:
        token = "intake-token-must-not-leak-77"
        recorder, received = _make_recording_handler()
        with _serve(recorder) as second_url:
            redirector, _ = _make_redirect_handler(second_url + "/dispatches")
            with _serve(redirector) as api_url:
                proc, summary = _run_dispatch_step(api_url, token=token)
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(
            received,
            [],
            "WEBFLASH_INTAKE_TOKEN must never be re-sent to a redirect target",
        )
        self.assertNotIn(token, proc.stdout + proc.stderr + summary)


# ---------------------------------------------------------------------------
# generate-matrix emits the trusted built-config set the handoff consumes
# ---------------------------------------------------------------------------


def _extract_inner_heredoc(run_text: str) -> str:
    marker = "python3 - <<'PY'\n"
    start = run_text.index(marker) + len(marker)
    end = run_text.index("\nPY", start)
    return run_text[start:end]


def _run_generate_matrix(version: str, channel: str):
    job = _load_workflow()["jobs"]["generate-matrix"]
    step = {s.get("id"): s for s in job["steps"]}["generate"]
    code = _extract_inner_heredoc(step["run"])
    with tempfile.TemporaryDirectory() as tmp:
        output_path = Path(tmp) / "output.txt"
        proc = subprocess.run(
            [sys.executable, "-c", code],
            env={
                "PATH": os.environ.get("PATH", ""),
                "VERSION": version,
                "CHANNEL": channel,
                "GITHUB_OUTPUT": str(output_path),
            },
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
        outputs = {}
        if output_path.exists():
            for line in output_path.read_text(encoding="utf-8").splitlines():
                key, _, value = line.partition("=")
                outputs[key] = value
        return proc, outputs


class GenerateMatrixBuiltConfigOutputTests(unittest.TestCase):
    """The handoff's trusted built-config set comes from generate-matrix;
    prove that job actually emits it and that it matches the release matrix."""

    def _eligible(self, version, channel):
        doc = json.loads(
            (REPO_ROOT / "config" / "webflash-builds.json").read_text(encoding="utf-8")
        )
        return {
            e["config_string"]
            for e in doc.get("builds", [])
            if isinstance(e, dict)
            and e.get("version") == version
            and e.get("channel") == channel
        }

    def test_built_config_strings_output_matches_release_matrix(self) -> None:
        # Use the live stable Release-One row so the test tracks the real
        # source of truth rather than a pinned version.
        version, channel = "1.0.7", "stable"
        expected = self._eligible(version, channel)
        self.assertTrue(expected, "expected at least one 1.0.7/stable build row")
        proc, outputs = _run_generate_matrix(version, channel)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        emitted = set(outputs.get("built_config_strings", "").split())
        self.assertEqual(emitted, expected)

    def test_built_config_strings_covers_multi_config_channel(self) -> None:
        # A (version, channel) with several rows must list every one, so the
        # handoff's membership check accepts each co-built config.
        version, channel = "1.0.0", "preview"
        expected = self._eligible(version, channel)
        if len(expected) < 2:
            self.skipTest("no multi-config (1.0.0, preview) matrix to check")
        proc, outputs = _run_generate_matrix(version, channel)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        emitted = set(outputs.get("built_config_strings", "").split())
        self.assertEqual(emitted, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
