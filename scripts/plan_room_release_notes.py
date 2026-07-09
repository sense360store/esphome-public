#!/usr/bin/env python3
"""RELEASE-NOTES-PIPELINE-001: dry-run release-notes plan for room firmware.

This script is a **dry-run planner**. It enumerates every release-eligible
firmware build in ``config/webflash-builds.json`` and emits a Markdown
release-notes plan that records, per build, exactly what a real GitHub
Release body and its pinning metadata would contain. It is read-only and
preflight only:

  * it does NOT create a GitHub Release;
  * it does NOT build, compile, or attach any firmware artifact;
  * it does NOT write ``firmware/sources.json`` or ``manifest.json``
    (it never writes any file other than an optional ``--output`` plan);
  * it does NOT promote any product or flip any ``webflash_build_matrix``.

Release-eligibility is driven **exclusively** by
``config/webflash-builds.json`` — the same single source of truth the
release workflow (``.github/workflows/firmware-build-release.yml``) uses to
generate its build matrix. Per owner decision HW-RELEASE-001
(``docs/hw-release-001.md``, 2026-07-09) the FanRelay / FanPWM / FanDAC
families are release-eligible on **non-stable channels only**: a FanRelay
row must be exactly ``experimental`` and a FanPWM / FanDAC row exactly
``preview``. The planner refuses any fan-token build row on the ``stable``
channel (or any channel other than the family's approved one). The manual
candidates in ``config/manual-firmware-artifacts.json`` remain a parallel
point-to-point handoff lane — no longer the only path for fan firmware —
and are recorded under a "manual-lane candidates" section.

For each release-eligible build the plan records:

  * version / tag and release channel
  * config string and canonical / WebFlash-wrapper YAML paths
  * artifact name and chip family
  * commit SHA the notes would be pinned to
  * ESPHome version (read from the release workflow)
  * source YAML GitHub URL pinned to the release tag and to the commit
  * package / external-component pin status
  * a structural validation summary (the draft body is run through
    ``scripts/validate-webflash-release-notes.py``)
  * known limitations, derived from the committed catalog only

The per-build draft body is produced by the existing
``scripts/generate_webflash_release_notes.py`` so this planner stays a thin,
read-only aggregator and inherits that generator's refusal rules (it refuses
``blocked`` / ``hardware-pending`` / ``compile-only`` / ``legacy-compatible``
entries and ``preview``-on-``stable``).

Usage:

    python3 scripts/plan_room_release_notes.py
    python3 scripts/plan_room_release_notes.py --output release-notes-plan.md
    python3 scripts/plan_room_release_notes.py --commit "$GITHUB_SHA"

Exits 0 on success, 2 on a planning error (e.g. a fan-token build row on the
stable channel, or a build the generator refuses).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
DEFAULT_MANUAL_PATH = REPO_ROOT / "config" / "manual-firmware-artifacts.json"
DEFAULT_WORKFLOW_PATH = (
    REPO_ROOT / ".github" / "workflows" / "firmware-build-release.yml"
)
DEFAULT_EXTERNAL_COMPONENTS_PATH = (
    REPO_ROOT / "packages" / "base" / "external_components.yaml"
)
GENERATOR_SCRIPT = REPO_ROOT / "scripts" / "generate_webflash_release_notes.py"
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"

DEFAULT_REPO_URL = "https://github.com/sense360store/esphome-public"

# HW-RELEASE-001 (docs/hw-release-001.md, 2026-07-09) retired the blanket
# "no fan row in the release matrix" guardrail and replaced it with channel
# teeth: fan families are release-eligible on non-stable channels ONLY.
# FanRelay rows must be exactly "experimental" (mains-adjacent lane per
# COMPLIANCE-001) and FanPWM / FanDAC rows exactly "preview". Any fan-token
# row on "stable" (or any other channel) is refused. Kept as a literal
# guardrail alongside the data-driven product_yaml check against
# config/manual-firmware-artifacts.json so the channel teeth hold even if
# that file is edited.
FAN_FAMILY_TOKENS = ("FanRelay", "FanPWM", "FanDAC")
FAN_ALLOWED_CHANNELS = {
    "FanRelay": ("experimental",),
    "FanPWM": ("preview",),
    "FanDAC": ("preview",),
}


class PlanError(Exception):
    """Raised when a release-notes plan cannot be produced safely."""


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise PlanError(f"cannot load module {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_json(path: Path, label: str) -> Dict[str, Any]:
    if not path.is_file():
        raise PlanError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlanError(f"{label} is not valid JSON: {exc}")


def _release_builds(builds_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    builds = builds_doc.get("builds", [])
    if not isinstance(builds, list):
        raise PlanError("config/webflash-builds.json: 'builds' must be a list")
    out: List[Dict[str, Any]] = []
    for entry in builds:
        if isinstance(entry, dict):
            out.append(entry)
    if not out:
        raise PlanError(
            "config/webflash-builds.json has no builds; nothing is "
            "release-eligible"
        )
    return out


def _fan_candidates(manual_doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = manual_doc.get("candidates", [])
    if not isinstance(candidates, list):
        raise PlanError(
            "config/manual-firmware-artifacts.json: 'candidates' must be a list"
        )
    return [c for c in candidates if isinstance(c, dict)]


def _assert_no_fan_in_release(
    builds: List[Dict[str, Any]], fan_candidates: List[Dict[str, Any]]
) -> None:
    """Guardrail (HW-RELEASE-001): fan builds are never on the stable channel.

    A FanRelay / FanPWM / FanDAC token in a release row is allowed only on
    the family's owner-approved non-stable channel (FanRelay: exactly
    ``experimental``; FanPWM / FanDAC: exactly ``preview``). A ``stable``
    fan-token row — or any other channel — is refused. A manual candidate's
    canonical ``product_yaml`` must still never double as a release row's
    ``product_yaml`` (release rows use ``products/webflash/`` wrappers;
    manual candidates use top-level ``products/sense360-*.yaml``).
    """
    fan_yamls = {
        c.get("product_yaml")
        for c in fan_candidates
        if isinstance(c.get("product_yaml"), str)
    }
    for build in builds:
        config_string = str(build.get("config_string", ""))
        product_yaml = str(build.get("product_yaml", ""))
        channel = str(build.get("channel", "")).strip().lower()
        for token in FAN_FAMILY_TOKENS:
            if token.lower() in config_string.lower():
                allowed = FAN_ALLOWED_CHANNELS[token]
                if channel not in allowed:
                    raise PlanError(
                        f"guardrail violation (HW-RELEASE-001): release "
                        f"build {config_string!r} carries fan family token "
                        f"{token!r} on channel {channel!r}; {token} builds "
                        f"are allowed only on the "
                        f"{' / '.join(allowed)} channel and are never a "
                        "stable release artifact"
                    )
        if product_yaml in fan_yamls:
            raise PlanError(
                f"guardrail violation: release build product_yaml "
                f"{product_yaml!r} matches a manual fan candidate's "
                "canonical YAML; release rows must address fan builds via "
                "their products/webflash/ wrappers, not the manual lane's "
                "top-level product YAML"
            )


def _esphome_version(workflow_path: Path) -> str:
    if not workflow_path.is_file():
        return "<unknown>"
    text = workflow_path.read_text(encoding="utf-8")
    match = re.search(
        r"^\s*ESPHOME_VERSION:\s*[\"']?([^\"'\s]+)", text, re.MULTILINE
    )
    return match.group(1) if match else "<unknown>"


def _external_components_ref(path: Path) -> str:
    """Return the git ``ref`` declared in the shared external_components file."""
    if not path.is_file():
        return "<unknown>"
    saw_git = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue
        if re.match(r"type:\s*git\b", line):
            saw_git = True
            continue
        if saw_git:
            m = re.match(r"ref:\s*(\S+)", line)
            if m:
                return m.group(1)
    return "<unknown>"


def _resolve_commit(explicit: Optional[str]) -> str:
    if explicit:
        return explicit
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "<unknown>"
    sha = result.stdout.strip()
    return sha if result.returncode == 0 and sha else "<unknown>"


def _catalog_entry(
    catalog: Dict[str, Any], config_string: str
) -> Optional[Dict[str, Any]]:
    for entry in catalog.get("products", []) or []:
        if isinstance(entry, dict) and entry.get("config_string") == config_string:
            return entry
    return None


def _canonical_yaml(
    build: Dict[str, Any], catalog_entry: Optional[Dict[str, Any]]
) -> str:
    if catalog_entry and isinstance(catalog_entry.get("product_yaml"), str):
        return catalog_entry["product_yaml"]
    wrapper = str(build.get("product_yaml", ""))
    stem = Path(wrapper).stem
    return f"products/sense360-{stem}.yaml" if stem else "<unknown>"


def _wrapper_yaml(
    build: Dict[str, Any], catalog_entry: Optional[Dict[str, Any]]
) -> str:
    if catalog_entry and isinstance(catalog_entry.get("webflash_wrapper"), str):
        return catalog_entry["webflash_wrapper"]
    return str(build.get("product_yaml", "<unknown>"))


def _blob_url(repo_url: str, ref: str, path: str) -> str:
    return f"{repo_url.rstrip('/')}/blob/{ref}/{path}"


def _known_limitations(
    catalog_entry: Optional[Dict[str, Any]],
    channel: str,
    version: str,
    external_ref: str,
) -> List[str]:
    """Limitations grounded in the committed catalog — never invented claims."""
    bullets: List[str] = []
    status = (catalog_entry or {}).get("status")
    hardware_status = (catalog_entry or {}).get("hardware_status")

    if status == "preview" or channel != "stable":
        bullets.append(
            "Preview channel: not promoted to stable. Preview-stage caveats "
            "in the product-catalog notes still apply and must resolve before "
            "any stable promotion."
        )

    for mod in (catalog_entry or {}).get("blocked_modules", []) or []:
        if isinstance(mod, str) and mod:
            bullets.append(
                f"Excludes {mod} (carried in the catalog's blocked_modules; "
                "not part of this firmware)."
            )

    if hardware_status:
        bullets.append(
            f"Hardware status is `{hardware_status}` per the product catalog; "
            "this plan makes no hardware-stability or compliance claim beyond "
            "that recorded state."
        )

    if not re.fullmatch(r"v?\d+\.\d+\.\d+", str(external_ref)):
        bullets.append(
            f"Shared `packages/base/external_components.yaml` declares git "
            f"`ref: {external_ref}`; pin it to `v{version}` at release time "
            "for a reproducible tagged build (see packages/README.md)."
        )

    if not bullets:
        bullets.append("None recorded in the catalog beyond the above.")
    return bullets


def build_plan(
    *,
    builds_path: Path = DEFAULT_BUILDS_PATH,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    manual_path: Path = DEFAULT_MANUAL_PATH,
    workflow_path: Path = DEFAULT_WORKFLOW_PATH,
    external_components_path: Path = DEFAULT_EXTERNAL_COMPONENTS_PATH,
    repo_url: str = DEFAULT_REPO_URL,
    commit: Optional[str] = None,
    config_string: Optional[str] = None,
) -> Dict[str, Any]:
    """Assemble the structured (read-only) release-notes plan.

    When ``config_string`` is ``None`` or ``"all-release-eligible"``, the
    plan covers every release-eligible build in
    ``config/webflash-builds.json``. When ``config_string`` names a
    specific release target, the plan covers only that one build —
    operator-driven scoping for RELEASE-PRODUCT-SELECTION-001. The
    fan channel guardrail (HW-RELEASE-001) still runs across the full
    release matrix so a fan-token row on a forbidden channel (stable)
    in ``config/webflash-builds.json`` is caught even when an operator
    scoped the plan to a single non-fan build.
    """
    gen = _load_module("generate_webflash_release_notes", GENERATOR_SCRIPT)
    val = _load_module("validate_webflash_release_notes", VALIDATOR_SCRIPT)

    builds_doc = _load_json(builds_path, "config/webflash-builds.json")
    catalog = _load_json(catalog_path, "config/product-catalog.json")
    manual_doc = _load_json(manual_path, "config/manual-firmware-artifacts.json")

    builds = _release_builds(builds_doc)
    fan_candidates = _fan_candidates(manual_doc)
    _assert_no_fan_in_release(builds, fan_candidates)

    selected = (config_string or "").strip()
    if selected and selected != "all-release-eligible":
        matched = [
            b for b in builds if str(b.get("config_string", "")) == selected
        ]
        if not matched:
            valid = ", ".join(str(b.get("config_string", "")) for b in builds)
            raise PlanError(
                f"--config-string {selected!r} is not a release-eligible target; "
                f"valid options are: all-release-eligible, {valid}"
            )
        builds = matched

    esphome_version = _esphome_version(workflow_path)
    external_ref = _external_components_ref(external_components_path)
    resolved_commit = _resolve_commit(commit)

    plan_builds: List[Dict[str, Any]] = []
    for build in builds:
        config_string = str(build.get("config_string", ""))
        version = str(build.get("version", ""))
        channel = str(build.get("channel", ""))
        catalog_entry = _catalog_entry(catalog, config_string)

        try:
            body = gen.generate(
                config_string=config_string,
                version=version,
                channel=channel,
                catalog_path=catalog_path,
                builds_path=builds_path,
            )
        except gen.GeneratorError as exc:
            raise PlanError(
                f"release matrix entry {config_string!r} is not "
                f"release-notes-eligible: {exc}"
            )

        validation_errors = val.validate_body(body, channel=channel)
        canonical = _canonical_yaml(build, catalog_entry)
        wrapper = _wrapper_yaml(build, catalog_entry)
        tag = f"v{version}"

        plan_builds.append(
            {
                "config_string": config_string,
                "version": version,
                "tag": tag,
                "channel": channel,
                "commit": resolved_commit,
                "esphome_version": esphome_version,
                "artifact_name": build.get("artifact_name", "<unset>"),
                "chip_family": build.get("chip_family", "<unset>"),
                "canonical_yaml": canonical,
                "wrapper_yaml": wrapper,
                "catalog_status": (catalog_entry or {}).get("status", "<none>"),
                "hardware_status": (catalog_entry or {}).get(
                    "hardware_status", "<none>"
                ),
                "source_yaml_url_tag": _blob_url(repo_url, tag, canonical),
                "source_yaml_url_commit": _blob_url(
                    repo_url, resolved_commit, canonical
                ),
                "external_components_ref": external_ref,
                "validation_errors": validation_errors,
                "known_limitations": _known_limitations(
                    catalog_entry, channel, version, external_ref
                ),
                "draft_body": body,
            }
        )

    return {
        "esphome_version": esphome_version,
        "commit": resolved_commit,
        "external_components_ref": external_ref,
        "repo_url": repo_url,
        "builds": plan_builds,
        "fan_candidates": fan_candidates,
        "selection": selected or "all-release-eligible",
    }


def _render_build(index: int, build: Dict[str, Any]) -> str:
    errors = build["validation_errors"]
    if errors:
        validation = "FAILED: " + "; ".join(errors)
    else:
        validation = f"PASSED (structural, channel={build['channel']})"

    lines = [
        f"### {index}. {build['config_string']} — {build['channel']}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Version / tag | `{build['version']}` / `{build['tag']}` |",
        f"| Channel | `{build['channel']}` |",
        f"| Config string | `{build['config_string']}` |",
        f"| Canonical YAML path | `{build['canonical_yaml']}` |",
        f"| WebFlash wrapper YAML | `{build['wrapper_yaml']}` |",
        f"| Artifact name | `{build['artifact_name']}` |",
        f"| Chip family | `{build['chip_family']}` |",
        f"| Commit SHA | `{build['commit']}` |",
        f"| ESPHome version | `{build['esphome_version']}` |",
        f"| Source YAML URL (tag-pinned) | {build['source_yaml_url_tag']} |",
        f"| Source YAML URL (commit-pinned) | {build['source_yaml_url_commit']} |",
        f"| external_components pin | `ref: {build['external_components_ref']}` |",
        f"| Catalog status | `{build['catalog_status']}` |",
        f"| Hardware status | `{build['hardware_status']}` |",
        f"| Validation summary | {validation} |",
        "",
        "**Known limitations:**",
        "",
    ]
    lines.extend(f"- {b}" for b in build["known_limitations"])
    lines.extend(
        [
            "",
            "**Draft release-notes body (preview — human review of "
            "`## Changelog` required before publishing):**",
            "",
            "```markdown",
            build["draft_body"].rstrip("\n"),
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_markdown(plan: Dict[str, Any]) -> str:
    builds = plan["builds"]
    lines = [
        "# Room Firmware Release-Notes Plan (RELEASE-NOTES-PIPELINE-001) — DRY RUN",
        "",
        "> **Dry run only.** This plan does not create a GitHub Release, does "
        "not build or attach any firmware artifact, and does not write "
        "`firmware/sources.json` or `manifest.json`. Human review of each "
        "`## Changelog` section is required before any real release.",
        "",
        "## Inputs",
        "",
        "| Source | Value |",
        "|---|---|",
        "| Release matrix (sole release-eligibility source) | "
        "`config/webflash-builds.json` |",
        "| Lifecycle / hardware status | `config/product-catalog.json` |",
        "| Manual-lane fan candidates (parallel path) | "
        "`config/manual-firmware-artifacts.json` |",
        f"| ESPHome version | `{plan['esphome_version']}` "
        "(from `.github/workflows/firmware-build-release.yml`) |",
        f"| Commit SHA | `{plan['commit']}` |",
        f"| external_components git ref | `{plan['external_components_ref']}` |",
        f"| Repository | {plan['repo_url']} |",
        f"| Selected target | `{plan.get('selection', 'all-release-eligible')}` |",
        "",
        f"## Release-eligible builds ({len(builds)})",
        "",
    ]
    for idx, build in enumerate(builds, start=1):
        lines.append(_render_build(idx, build))

    lines.extend(
        [
            "## Manual-lane candidates — parallel point-to-point path",
            "",
            "The following are also tracked as **manual-lane candidates** "
            "(`config/manual-firmware-artifacts.json`). Per owner decision "
            "HW-RELEASE-001 (`docs/hw-release-001.md`) the manual lane is "
            "**no longer the only path** for fan firmware — fan configs are "
            "release-eligible above on non-stable channels — but it remains "
            "available for point-to-point handoff:",
            "",
        ]
    )
    for cand in plan["fan_candidates"]:
        family = cand.get("family", "<unknown>")
        sku = cand.get("sku", "<unknown>")
        product_yaml = cand.get("product_yaml", "<unknown>")
        lines.append(
            f"- **{family}** (`{sku}`, `{product_yaml}`) — manual-lane "
            "candidate (point-to-point handoff)."
        )
    lines.extend(
        [
            "",
            "For FanRelay / FanPWM / FanDAC this plan explicitly asserts:",
            "",
            "- they are release-eligible on **non-stable channels only** "
            "(HW-RELEASE-001): FanRelay exactly `experimental`, FanPWM / "
            "FanDAC exactly `preview`; a fan build is **never** a stable "
            "release artifact;",
            "- their release rows in `config/webflash-builds.json` are "
            "acknowledgement-gated and not buyable / recommended / "
            "customer-default / kit-exposed;",
            "- this plan makes **no** hardware-stable / compliance / safety "
            "claim for them beyond the catalog's recorded owner-declared "
            "`hardware_status` (HW-RELEASE-001 owner declaration, not bench "
            "proof).",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-run release-notes plan for the release-eligible room "
            "firmware builds in config/webflash-builds.json. Read-only: "
            "creates no GitHub Release, builds no firmware, and never writes "
            "firmware/sources.json or manifest.json."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the plan to PATH (default: stdout).",
    )
    parser.add_argument(
        "--commit",
        default=None,
        help="Commit SHA to pin notes to (default: current git HEAD).",
    )
    parser.add_argument(
        "--repo-url",
        default=DEFAULT_REPO_URL,
        help=f"Repository URL for source-YAML links (default: {DEFAULT_REPO_URL}).",
    )
    parser.add_argument(
        "--config-string",
        default=None,
        help=(
            "Plan only the given release target (a config_string in "
            "config/webflash-builds.json). Defaults to all release-eligible "
            "builds; pass 'all-release-eligible' for the same effect."
        ),
    )
    # Test-only path overrides, hidden from --help.
    parser.add_argument(
        "--builds",
        type=Path,
        default=DEFAULT_BUILDS_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--manual",
        type=Path,
        default=DEFAULT_MANUAL_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--workflow",
        type=Path,
        default=DEFAULT_WORKFLOW_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--external-components",
        type=Path,
        default=DEFAULT_EXTERNAL_COMPONENTS_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        plan = build_plan(
            builds_path=args.builds,
            catalog_path=args.catalog,
            manual_path=args.manual,
            workflow_path=args.workflow,
            external_components_path=args.external_components,
            repo_url=args.repo_url,
            commit=args.commit,
            config_string=args.config_string,
        )
    except PlanError as exc:
        print(f"plan-room-release-notes: {exc}", file=sys.stderr)
        return 2

    body = render_markdown(plan)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
