#!/usr/bin/env python3
"""Preflight for "Release 2: Draft Notes": is the requested version declared?

The WebFlash release chain runs in three manual steps:

    Release 1: Bump Version  ->  Release 2: Draft Notes  ->  Release 3: Build & Release

"Release 1: Bump Version" rewrites the ``version`` (and version-bearing
``artifact_name``) for one config in ``config/product-catalog.json`` and
``config/webflash-builds.json``, but it does this by **opening a pull
request** rather than committing to ``main``. So if an operator runs
"Release 2: Draft Notes" for the new version **before** that bump PR is
merged, ``scripts/generate_webflash_release_notes.py`` reads ``main`` (which
still carries the old version), hits ``_check_version_match``, and exits with
its generic ``exit 2`` mismatch:

    generate-release-notes: --version '1.0.2' does not match catalog
    'version' '1.0.1' for 'Ceiling-POE-VentIQ-RoomIQ'

That generic message does not tell the operator the real cause (the bump is
sitting in an unmerged PR) or the fix (merge it first). This preflight runs
**before** the generator and turns that failure into a specific, actionable
message, exiting with a **distinct exit code 3** so it is obvious the failure
came from the preflight and not from the generator.

This script is **additive guidance only**:

  * It does not change the generator's own validation.
  * It does not merge anything.
  * It does not write the catalog or any other file.
  * The pass / fail decision is derivable from the **local catalog alone**, so
    the preflight is reliable even with no GitHub API access. The list of open
    bump PRs is fetched best-effort via ``gh`` and only **enriches** the
    failure message (it never changes the decision).

Usage::

    python3 scripts/check_pending_version_bump.py \\
        --config Ceiling-POE-VentIQ-RoomIQ \\
        --version 1.0.2 \\
        --channel stable

Inputs:

  * ``--config``   WebFlash config string (e.g. Ceiling-POE-VentIQ-RoomIQ).
  * ``--version``  Requested release version, no leading 'v' (e.g. 1.0.2).
  * ``--channel``  Requested release channel (e.g. stable / preview).
  * ``GITHUB_REPOSITORY`` (env) ``owner/repo``; used to read the catalog at a
    PR head when enriching the message. Optional; absence only disables
    enrichment.
  * ``GITHUB_TOKEN`` (env) auth for the best-effort ``gh`` calls. Optional;
    absence only disables enrichment.

This is a version-declaration gate only: the pass/fail decision depends solely
on whether the catalog declares the requested ``--version``. Channel and status
are intentionally left to the generator, which has precise channel/status
errors of its own, so a channel-only mismatch (version already declared) is
deferred to the generator rather than blocked here. ``--channel`` is still
accepted and echoed in messages.

Exit codes:

  * ``0`` the requested version is declared in the catalog; the generator may
    proceed (it then validates channel/status).
  * ``3`` the requested version is **not** declared; the printed message
    explains whether a bump PR is already open (merge it) or whether
    "Release 1: Bump Version" still needs to be run. Distinct from the
    generator's ``exit 2`` on purpose.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.parse
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
# Path used both to detect catalog-touching PRs and to read the catalog at a
# PR head. Kept as a forward-slash repo-relative string because that is how
# both ``gh pr view --json files`` and the contents API report/accept it.
CATALOG_RELPATH = "config/product-catalog.json"

EXIT_OK = 0
# Distinct from the generator's exit 2 so the origin of a CI failure is
# unambiguous: a 3 means "the preflight blocked", a 2 means "the generator
# rejected".
EXIT_PREFLIGHT_BLOCK = 3

# Conservative per-call timeout (seconds) for the best-effort ``gh`` calls so a
# hung CLI can never wedge the preflight step.
_GH_TIMEOUT_SECONDS = 30
# Upper bound on how many open PRs we inspect for catalog changes.
_GH_PR_LIMIT = 100


class CatalogError(Exception):
    """Raised when the local catalog cannot be read or parsed."""


# ---------------------------------------------------------------------------
# Pure decision logic (unit-tested offline; no I/O, no network).
# ---------------------------------------------------------------------------
def decide(
    config: str,
    requested_version: str,
    requested_channel: str,
    catalog_version: Optional[str],
    catalog_channel: Optional[str],
    candidate_bumps: Optional[List[Dict[str, Any]]],
) -> Tuple[bool, Optional[str]]:
    """Decide whether "Release 2: Draft Notes" may proceed.

    This is a **version-declaration gate only**. The decision (``ok``) depends
    solely on whether the local catalog already declares the requested
    ``version`` for ``config``; channel is intentionally **not** part of the
    pass/fail decision. Channel and status stay owned by the generator
    (``generate_webflash_release_notes.py``), which emits precise channel/status
    errors of its own. So when the version matches but the requested channel
    differs (e.g. a preview entry dispatched on the default ``stable`` channel),
    this preflight passes and defers to the generator instead of printing a
    misleading "run Release 1: Bump Version" message for a bump that does not
    exist (Release 1 never changes channel).

    ``requested_channel`` is still echoed in the failure messages, and
    ``catalog_channel`` is accepted for signature stability, but neither affects
    ``ok``. ``candidate_bumps`` (open PRs that change
    ``config/product-catalog.json`` for this config, each a dict with
    ``pr_number`` / ``pr_url`` / ``proposed_version`` / ``proposed_channel``)
    only **enriches** the failure message; it never flips ``ok``.

    Returns ``(True, None)`` when the version is declared, otherwise
    ``(False, message)`` with an actionable message:

      * a matching open PR exists (one that introduces the requested version)
        -> point the operator at it to merge;
      * no matching PR -> direct the operator to run "Release 1: Bump Version",
        and (if any catalog-touching PR proposes a *different* version) list
        those PRs so the operator can spot a wrong-version dispatch.
    """
    # Version-declaration gate: if the catalog already declares the requested
    # version, the generator may proceed. It owns channel/status validation, so
    # a channel-only mismatch is deliberately deferred to it rather than blocked
    # here (channel is not part of this decision).
    if catalog_version == requested_version:
        return True, None

    candidates = candidate_bumps or []

    # Is the requested bump already in flight? A "matching" candidate is one that
    # introduces the requested version for this config. Channel is not part of
    # the gate, so the match is on version (a bump never changes channel).
    matching = next(
        (
            cand
            for cand in candidates
            if cand.get("proposed_version") == requested_version
        ),
        None,
    )
    if matching is not None:
        message = (
            f"Catalog declares {catalog_version} for {config}. "
            f"The bump to {requested_version} ({requested_channel}) is waiting "
            f"in open PR #{matching.get('pr_number')} "
            f"({matching.get('pr_url')}). "
            "Merge that PR, then re-run Release 2: Draft Notes."
        )
        return False, message

    # No matching bump PR: the operator needs to run Release 1 first.
    message = (
        f"Catalog declares {catalog_version} for {config}, not the requested "
        f"{requested_version} ({requested_channel}). Run Release 1: Bump "
        f"Version for {config} to {requested_version}, merge its PR, then "
        "re-run Release 2: Draft Notes."
    )

    # If other catalog-touching PRs propose a *different* version for this
    # config, surface them: this catches a wrong-version dispatch (e.g. the
    # operator asked for 2.0.0 but the open bump is for 1.0.2).
    different = [
        cand
        for cand in candidates
        if cand.get("proposed_version")
        and cand.get("proposed_version") != requested_version
    ]
    if different:
        listed = ", ".join(
            f"#{cand.get('pr_number')} proposes {cand.get('proposed_version')}"
            for cand in different
        )
        message += f" Open PRs changing the catalog: {listed}."

    return False, message


# ---------------------------------------------------------------------------
# Local catalog I/O (no network).
# ---------------------------------------------------------------------------
def _load_catalog(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise CatalogError(f"catalog not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CatalogError(f"catalog is not valid JSON: {exc}")


def _find_entry(catalog: Dict[str, Any], config: str) -> Optional[Dict[str, Any]]:
    for entry in catalog.get("products", []) or []:
        if isinstance(entry, dict) and entry.get("config_string") == config:
            return entry
    return None


# ---------------------------------------------------------------------------
# Best-effort GitHub enrichment via the ``gh`` CLI. Every helper swallows its
# own failures, logs a one-line note, and degrades to "no candidates" so the
# preflight never crashes and never depends on API access for its decision.
# ---------------------------------------------------------------------------
def _gh_env() -> Dict[str, str]:
    """Return an environment for ``gh`` with the token mirrored to GH_TOKEN.

    ``gh`` authenticates from ``GH_TOKEN`` or ``GITHUB_TOKEN``; the task wires
    ``GITHUB_TOKEN`` in, so mirror it to ``GH_TOKEN`` too for robustness.
    """
    env = dict(os.environ)
    token = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if token:
        env.setdefault("GH_TOKEN", token)
        env.setdefault("GITHUB_TOKEN", token)
    return env


def _run_gh(
    args: List[str], env: Dict[str, str]
) -> Tuple[int, str, str]:
    """Run ``gh <args>``; return ``(returncode, stdout, stderr)``. Never raises."""
    try:
        proc = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            check=False,
            timeout=_GH_TIMEOUT_SECONDS,
            env=env,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except FileNotFoundError:
        return 127, "", "gh CLI not found on PATH"
    except (OSError, subprocess.SubprocessError) as exc:  # pragma: no cover
        return 1, "", str(exc)


def _proposed_at_ref(
    config: str,
    repo: str,
    ref: str,
    env: Dict[str, str],
    log: Callable[[str], None],
    pr_number: Any,
) -> Tuple[Optional[str], Optional[str]]:
    """Read the proposed (version, channel) for ``config`` from the catalog at
    a PR head ``ref``. Returns ``(None, None)`` on any failure."""
    if not repo:
        log(
            "note: GITHUB_REPOSITORY not set; cannot read the catalog at the "
            f"head of PR #{pr_number}"
        )
        return None, None
    ref_q = urllib.parse.quote(str(ref), safe="")
    endpoint = f"repos/{repo}/contents/{CATALOG_RELPATH}?ref={ref_q}"
    rc, out, err = _run_gh(["api", endpoint], env=env)
    if rc != 0:
        log(
            f"note: could not read catalog at the head of PR #{pr_number} "
            f"(gh exit {rc}); skipping that PR"
        )
        return None, None
    try:
        payload = json.loads(out or "{}")
    except json.JSONDecodeError:
        log(f"note: could not parse catalog response for PR #{pr_number}; skipping")
        return None, None
    content_b64 = payload.get("content")
    if not content_b64 or payload.get("encoding") != "base64":
        log(f"note: unexpected catalog payload for PR #{pr_number}; skipping")
        return None, None
    try:
        raw = base64.b64decode(content_b64)
        catalog = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        log(f"note: could not decode catalog at the head of PR #{pr_number}; skipping")
        return None, None
    entry = _find_entry(catalog, config)
    if entry is None:
        return None, None
    return entry.get("version"), entry.get("channel")


def _collect_candidate_bumps(
    config: str,
    repo: str,
    env: Dict[str, str],
    log: Callable[[str], None],
) -> List[Dict[str, Any]]:
    """Best-effort: list open PRs that change the catalog for ``config`` and
    read each one's proposed version/channel. Returns ``[]`` on any failure."""
    rc, out, err = _run_gh(
        [
            "pr",
            "list",
            "--state",
            "open",
            "--limit",
            str(_GH_PR_LIMIT),
            "--json",
            "number,url,headRefName",
        ],
        env=env,
    )
    if rc != 0:
        log(
            f"note: could not list open PRs (gh exit {rc}); proceeding without "
            "PR enrichment"
        )
        return []
    try:
        prs = json.loads(out or "[]")
    except json.JSONDecodeError:
        log("note: could not parse `gh pr list` output; proceeding without PR enrichment")
        return []

    candidates: List[Dict[str, Any]] = []
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        number = pr.get("number")
        url = pr.get("url")
        head = pr.get("headRefName")
        if number is None or not head:
            continue
        rc, out, err = _run_gh(["pr", "view", str(number), "--json", "files"], env=env)
        if rc != 0:
            log(f"note: could not read changed files for PR #{number} (gh exit {rc}); skipping")
            continue
        try:
            files = (json.loads(out or "{}") or {}).get("files", []) or []
        except json.JSONDecodeError:
            log(f"note: could not parse changed files for PR #{number}; skipping")
            continue
        touches_catalog = any(
            isinstance(f, dict) and f.get("path") == CATALOG_RELPATH for f in files
        )
        if not touches_catalog:
            continue
        proposed_version, proposed_channel = _proposed_at_ref(
            config, repo, head, env, log, number
        )
        if proposed_version is None and proposed_channel is None:
            # Either the read failed (already logged) or the PR's catalog has no
            # entry for this config; nothing useful to enrich with.
            continue
        candidates.append(
            {
                "pr_number": number,
                "pr_url": url,
                "proposed_version": proposed_version,
                "proposed_channel": proposed_channel,
            }
        )
    return candidates


# ---------------------------------------------------------------------------
# CLI wrapper.
# ---------------------------------------------------------------------------
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight for 'Release 2: Draft Notes': verify the requested "
            "version + channel are declared in config/product-catalog.json "
            "before the release-notes generator runs. Additive guidance only; "
            "does not change the generator's validation. Exits 0 when declared, "
            "3 when a bump is still pending (distinct from the generator's "
            "exit 2)."
        ),
    )
    parser.add_argument(
        "--config",
        required=True,
        help="WebFlash config string (e.g. Ceiling-POE-VentIQ-RoomIQ)",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Requested release version, no leading 'v' (e.g. 1.0.2)",
    )
    parser.add_argument(
        "--channel",
        required=True,
        help="Requested release channel (e.g. stable, preview)",
    )
    # Test-only override, hidden from --help, mirroring the generator's surface.
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    def log(note: str) -> None:
        print(f"check-pending-version-bump: {note}", file=sys.stderr)

    try:
        catalog = _load_catalog(args.catalog)
    except CatalogError as exc:
        # Cannot read the local catalog at all. Do not block: let the generator
        # be the authority. In CI the file always exists; this is defensive.
        log(f"{exc}; deferring to the generator's own validation")
        return EXIT_OK

    entry = _find_entry(catalog, args.config)
    if entry is None:
        # An unknown config is the generator's job to reject (with its own
        # message). The preflight only handles the version-bump-pending case.
        log(
            f"{args.config!r} is not in {CATALOG_RELPATH}; deferring to the "
            "generator's own validation"
        )
        return EXIT_OK

    catalog_version = entry.get("version")
    catalog_channel = entry.get("channel")

    # Version-declaration gate: the pass/fail decision depends only on whether
    # the catalog already declares the requested version. Channel/status stays
    # the generator's responsibility.
    version_declared = catalog_version == args.version

    candidate_bumps: List[Dict[str, Any]] = []
    if not version_declared:
        # Only reach out to GitHub when the version does not match. The
        # candidates only enrich the message; the decision is already made from
        # the local catalog.
        repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
        candidate_bumps = _collect_candidate_bumps(args.config, repo, _gh_env(), log)

    ok, message = decide(
        config=args.config,
        requested_version=args.version,
        requested_channel=args.channel,
        catalog_version=catalog_version,
        catalog_channel=catalog_channel,
        candidate_bumps=candidate_bumps,
    )

    if ok:
        print(
            "check-pending-version-bump: catalog declares version "
            f"{catalog_version} for {args.config}; matches the requested "
            f"{args.version}. Proceeding (channel/status is validated by the "
            "release-notes generator)."
        )
        return EXIT_OK

    print(f"check-pending-version-bump: {message}", file=sys.stderr)
    return EXIT_PREFLIGHT_BLOCK


if __name__ == "__main__":
    sys.exit(main())
