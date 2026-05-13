#!/usr/bin/env python3
"""RELEASE-001: Generate a WebFlash release-notes draft from the product catalog.

This script is read-only. It does not create GitHub releases, publish
firmware, call any external service, or infer changelog content from
git history. It loads the product catalog
(``config/product-catalog.json``), the WebFlash build matrix
(``config/webflash-builds.json``), and the hardware catalog
(``config/hardware-catalog.json``), and emits a Markdown draft body
that matches the format enforced by
``scripts/validate-webflash-release-notes.py``.

The draft must still be reviewed by a human before being attached to a
GitHub Release. The default ``## Changelog`` section is a TODO bullet
that the user is expected to replace with the actual user-visible
changes for the release. The TODO bullet is intentionally worded so
that the structural release-notes validator still passes, but the
human-review intent is obvious from the text.

Refuses to generate notes for:

- ``blocked`` catalog entries (e.g. FanTRIAC pending HW-005)
- ``legacy-compatible`` catalog entries (manual / custom users only)
- ``deprecated`` / ``removed`` entries
- ``compile-only`` / ``hardware-pending`` entries
- ``preview`` entries on the ``stable`` channel
- ``production`` entries on a non-``stable`` channel
- unknown / mistyped config strings

Usage:

    python3 scripts/generate_webflash_release_notes.py \\
        --config-string Ceiling-POE-VentIQ-RoomIQ \\
        --version 1.0.0 \\
        --channel stable

Optional:

    --output PATH           Write the draft to PATH (default: stdout).
    --changelog TEXT        Provide changelog bullets directly. Newlines
                            separate bullets; a leading ``-``/``*``/``+``
                            is stripped so input may be plain or
                            already in bullet form.
    --changelog-file PATH   Read changelog bullets from PATH (same
                            shape as --changelog).
    --require-changelog     Exit non-zero if no changelog text/file was
                            supplied. Use this in stricter callers that
                            never want a TODO placeholder.
    --validate              After generating, invoke
                            ``scripts/validate-webflash-release-notes.py``
                            on the output and propagate its exit code.
    --catalog PATH          Override config/product-catalog.json (testing).
    --builds PATH           Override config/webflash-builds.json (testing).
    --hardware-catalog PATH Override config/hardware-catalog.json (testing).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = REPO_ROOT / "config" / "product-catalog.json"
DEFAULT_BUILDS_PATH = REPO_ROOT / "config" / "webflash-builds.json"
DEFAULT_HARDWARE_PATH = REPO_ROOT / "config" / "hardware-catalog.json"
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate-webflash-release-notes.py"

# Statuses that are not WebFlash-shippable. ``preview`` is excluded from
# this set because it is shippable on the preview channel.
REFUSED_STATUSES = frozenset({
    "blocked",
    "legacy-compatible",
    "deprecated",
    "removed",
    "compile-only",
    "hardware-pending",
})

# Wording for known blocked-module exclusions in ## Known Issues. Mirrors
# the example in docs/release-one.md and the RELEASE-001 task description.
# Unknown blocked-module names fall through to a generic bullet so the
# generator never silently drops an exclusion.
BLOCKED_MODULE_BULLETS = {
    "FanTRIAC": (
        "FanTRIAC is not included in this Release-One firmware and remains "
        "blocked pending HW-005."
    ),
    "LED": (
        "Sense360 LED is not included in this Release-One firmware because "
        "the config string has no LED token."
    ),
}


class GeneratorError(Exception):
    """Raised when generation cannot proceed (refused entry, missing data)."""


def _load_json(path: Path, label: str) -> Dict[str, Any]:
    if not path.is_file():
        raise GeneratorError(f"{label} not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GeneratorError(f"{label} is not valid JSON: {exc}")


def _find_catalog_entry(
    catalog: Dict[str, Any], identifier: str
) -> Optional[Dict[str, Any]]:
    """Return the catalog entry whose ``config_string`` or ``legacy_config_id``
    equals ``identifier``. Returns ``None`` if no entry matches."""
    for entry in catalog.get("products", []) or []:
        if not isinstance(entry, dict):
            continue
        if entry.get("config_string") == identifier:
            return entry
        if entry.get("legacy_config_id") == identifier:
            return entry
    return None


def _find_build_entry(
    builds: Dict[str, Any], config_string: str
) -> Optional[Dict[str, Any]]:
    for entry in builds.get("builds", []) or []:
        if isinstance(entry, dict) and entry.get("config_string") == config_string:
            return entry
    return None


def _hardware_friendly_names(hardware_doc: Dict[str, Any]) -> Dict[str, str]:
    """Map SKU → friendly name from ``config/hardware-catalog.json``."""
    out: Dict[str, str] = {}
    for item in hardware_doc.get("items", []) or []:
        if not isinstance(item, dict):
            continue
        sku = item.get("sku")
        name = item.get("friendly_name")
        if isinstance(sku, str) and isinstance(name, str):
            out[sku] = name
    return out


def _resolve_changelog_bullets(
    changelog: Optional[str],
    changelog_file: Optional[Path],
    require: bool,
    *,
    config_string: str,
    version: str,
) -> List[str]:
    """Parse user-supplied changelog text into a list of bullet strings.

    Returns a single-element TODO list when nothing was supplied and
    ``--require-changelog`` was not set. Raises ``GeneratorError`` when
    ``--require-changelog`` is set and no content was supplied, or when
    parsed input yielded zero non-empty bullets.
    """
    if changelog is not None and changelog_file is not None:
        raise GeneratorError(
            "specify either --changelog or --changelog-file, not both"
        )

    raw: Optional[str] = None
    if changelog is not None:
        raw = changelog
    elif changelog_file is not None:
        if not changelog_file.is_file():
            raise GeneratorError(
                f"--changelog-file path does not exist: {changelog_file}"
            )
        raw = changelog_file.read_text(encoding="utf-8")

    if raw is None:
        if require:
            raise GeneratorError(
                "no changelog supplied; pass --changelog TEXT or "
                "--changelog-file PATH (or drop --require-changelog)"
            )
        return [
            f"TODO: Summarize user-visible changes for v{version} "
            f"({config_string}). Replace this line before publishing."
        ]

    bullets: List[str] = []
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ", "+ ")):
            line = line[2:].strip()
        if line:
            bullets.append(line)
    if not bullets:
        raise GeneratorError(
            "changelog input is empty after parsing; supply at least one "
            "non-blank bullet"
        )
    return bullets


def _build_known_issues_bullets(entry: Dict[str, Any]) -> List[str]:
    blocked = entry.get("blocked_modules", []) or []
    bullets: List[str] = []
    for mod in blocked:
        if isinstance(mod, str) and mod:
            bullets.append(
                BLOCKED_MODULE_BULLETS.get(
                    mod, f"{mod} is excluded from this firmware."
                )
            )
    if not bullets:
        bullets.append("None.")
    return bullets


def _build_features_bullets(build_entry: Dict[str, Any]) -> List[str]:
    feats = build_entry.get("features", []) or []
    bullets = [f for f in feats if isinstance(f, str) and f.strip()]
    if not bullets:
        raise GeneratorError(
            "matching WebFlash build entry has no 'features' bullets; "
            "config/webflash-builds.json is malformed for this config"
        )
    return bullets


def _build_hardware_bullets(
    entry: Dict[str, Any], friendly_names: Dict[str, str]
) -> List[str]:
    hardware = entry.get("hardware") or {}
    if not isinstance(hardware, dict) or not hardware:
        raise GeneratorError(
            "catalog entry has no 'hardware' SKU map; cannot build "
            "Hardware Requirements section"
        )
    bullets: List[str] = []
    for sku in hardware.values():
        if not isinstance(sku, str) or not sku:
            continue
        friendly = friendly_names.get(sku)
        if friendly:
            bullets.append(f"{friendly} (`{sku}`)")
        else:
            bullets.append(f"`{sku}`")
    if not bullets:
        raise GeneratorError(
            "catalog 'hardware' map produced no bullets; check SKU values"
        )
    return bullets


def _check_status_and_channel(
    entry: Dict[str, Any], channel: str, config_string: str
) -> None:
    status = entry.get("status")
    if status in REFUSED_STATUSES:
        raise GeneratorError(
            f"refusing to generate release notes for "
            f"{config_string!r}: catalog status is {status!r} (not "
            "WebFlash-shippable)"
        )
    if status == "production":
        if channel != "stable":
            raise GeneratorError(
                f"refusing to generate notes for production entry "
                f"{config_string!r} on channel {channel!r}; production "
                "entries use the 'stable' channel"
            )
    elif status == "preview":
        if channel == "stable":
            raise GeneratorError(
                f"refusing to generate stable-channel notes for preview "
                f"entry {config_string!r}; promote to production first"
            )
    else:
        raise GeneratorError(
            f"refusing to generate notes for {config_string!r}: catalog "
            f"status is {status!r} (only production and preview are "
            "WebFlash-shippable)"
        )


def _check_version_match(
    entry: Dict[str, Any], version: str, config_string: str
) -> None:
    entry_version = entry.get("version")
    if entry_version is not None and entry_version != version:
        raise GeneratorError(
            f"--version {version!r} does not match catalog 'version' "
            f"{entry_version!r} for {config_string!r}"
        )


def _check_channel_match(
    entry: Dict[str, Any], channel: str, config_string: str
) -> None:
    entry_channel = entry.get("channel")
    if entry_channel is not None and entry_channel != channel:
        raise GeneratorError(
            f"--channel {channel!r} does not match catalog 'channel' "
            f"{entry_channel!r} for {config_string!r}"
        )


def _render_section(name: str, bullets: List[str]) -> str:
    body = "\n".join(f"- {b}" for b in bullets)
    return f"## {name}\n\n{body}\n"


def _render_preamble(
    config_string: str,
    version: str,
    channel: str,
    artifact: Optional[str],
    status: str,
    hardware_bullets: List[str],
) -> str:
    lines = [
        "<!--",
        "Sense360 WebFlash release-notes draft.",
        "Generated by scripts/generate_webflash_release_notes.py.",
        "",
        f"Config string : {config_string}",
        f"Version       : {version}",
        f"Channel       : {channel}",
        f"Artifact      : {artifact or '<unset>'}",
        f"Catalog status: {status}",
        "Hardware:",
    ]
    for b in hardware_bullets:
        lines.append(f"  - {b}")
    lines.extend([
        "",
        "Human review required before publishing. Replace the TODO bullet",
        "in the Changelog section with the real user-visible changes for",
        "this release, then re-run scripts/validate-webflash-release-notes.py.",
        "-->",
    ])
    return "\n".join(lines) + "\n"


def generate(
    *,
    config_string: str,
    version: str,
    channel: str,
    changelog: Optional[str] = None,
    changelog_file: Optional[Path] = None,
    require_changelog: bool = False,
    catalog_path: Path = DEFAULT_CATALOG_PATH,
    builds_path: Path = DEFAULT_BUILDS_PATH,
    hardware_path: Path = DEFAULT_HARDWARE_PATH,
) -> str:
    """Produce the Markdown draft body for the requested release."""
    catalog = _load_json(catalog_path, "config/product-catalog.json")
    builds = _load_json(builds_path, "config/webflash-builds.json")
    hardware = _load_json(hardware_path, "config/hardware-catalog.json")

    entry = _find_catalog_entry(catalog, config_string)
    if entry is None:
        raise GeneratorError(
            f"no catalog entry found for {config_string!r}; check "
            "config/product-catalog.json"
        )

    if entry.get("legacy_config_id") == config_string:
        raise GeneratorError(
            f"refusing to generate release notes for {config_string!r}: "
            "matches a legacy-compatible product (legacy products are not "
            "WebFlash-shippable)"
        )

    _check_status_and_channel(entry, channel, config_string)
    _check_version_match(entry, version, config_string)
    _check_channel_match(entry, channel, config_string)

    build_entry = _find_build_entry(builds, config_string)
    if build_entry is None:
        raise GeneratorError(
            f"no WebFlash build entry found for {config_string!r}; "
            "config/webflash-builds.json must contain this config"
        )

    friendly = _hardware_friendly_names(hardware)
    hardware_bullets = _build_hardware_bullets(entry, friendly)
    features_bullets = _build_features_bullets(build_entry)
    known_issues_bullets = _build_known_issues_bullets(entry)
    changelog_bullets = _resolve_changelog_bullets(
        changelog,
        changelog_file,
        require_changelog,
        config_string=config_string,
        version=version,
    )

    parts = [
        _render_preamble(
            config_string=config_string,
            version=version,
            channel=channel,
            artifact=entry.get("artifact_name"),
            status=str(entry.get("status")),
            hardware_bullets=hardware_bullets,
        ),
        _render_section("Changelog", changelog_bullets),
        _render_section("Known Issues", known_issues_bullets),
        _render_section("Features", features_bullets),
        _render_section("Hardware Requirements", hardware_bullets),
    ]
    return "\n".join(parts).rstrip() + "\n"


def _run_validator(body: str, channel: str) -> int:
    """Write ``body`` to a temp file and shell out to the validator."""
    if not VALIDATOR_SCRIPT.is_file():
        print(
            f"ERROR: validator script not found: {VALIDATOR_SCRIPT}",
            file=sys.stderr,
        )
        return 1
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(body)
        tmp_path = Path(tmp.name)
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_SCRIPT),
                str(tmp_path),
                "--channel",
                channel,
            ],
            check=False,
        )
        return proc.returncode
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a WebFlash release-notes draft from the product "
            "catalog. Read-only: does not create releases, publish "
            "firmware, infer changelog content from git history, or call "
            "any external service. Human review of the Changelog section "
            "is still required before publishing."
        ),
    )
    parser.add_argument(
        "--config-string",
        required=True,
        help="WebFlash config string (e.g. Ceiling-POE-VentIQ-RoomIQ)",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Release version, no leading 'v' (e.g. 1.0.0)",
    )
    parser.add_argument(
        "--channel",
        required=True,
        choices=("stable", "preview", "beta"),
        help="Release channel",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write the draft to PATH (default: stdout)",
    )
    parser.add_argument(
        "--changelog",
        default=None,
        help="Changelog content (newlines separate bullets)",
    )
    parser.add_argument(
        "--changelog-file",
        type=Path,
        default=None,
        help="Read changelog content from PATH",
    )
    parser.add_argument(
        "--require-changelog",
        action="store_true",
        help="Exit non-zero if no changelog text/file was supplied",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help=(
            "After generating, run scripts/validate-webflash-release-notes.py "
            "on the output and propagate its exit code"
        ),
    )
    # Test-only path overrides. Hidden from --help so the public surface
    # stays focused on the documented inputs.
    parser.add_argument(
        "--catalog", type=Path, default=DEFAULT_CATALOG_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--builds", type=Path, default=DEFAULT_BUILDS_PATH,
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--hardware-catalog", type=Path, default=DEFAULT_HARDWARE_PATH,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    try:
        body = generate(
            config_string=args.config_string,
            version=args.version,
            channel=args.channel,
            changelog=args.changelog,
            changelog_file=args.changelog_file,
            require_changelog=args.require_changelog,
            catalog_path=args.catalog,
            builds_path=args.builds,
            hardware_path=args.hardware_catalog,
        )
    except GeneratorError as exc:
        print(f"generate-release-notes: {exc}", file=sys.stderr)
        return 2

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body, encoding="utf-8")
    else:
        sys.stdout.write(body)

    if args.validate:
        return _run_validator(body, args.channel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
