#!/usr/bin/env python3
"""Fail if any secrets.yaml is tracked in git, at any depth.

SEC-ESP-SECRET-GUARD-001 (security.md finding #2): the repo ships
``secrets.example.yaml`` (and ``products/secrets.example.yaml``) as tracked
templates. The real ``secrets.yaml`` is gitignored and must stay local. This
guard catches regressions where someone re-adds a ``secrets.yaml`` to the
index.

The previous version only checked the repo-root ``secrets.yaml`` via
``git ls-files --error-unmatch secrets.yaml``, so a tracked
``products/secrets.yaml`` (or any other nested ``secrets.yaml``) slipped
through. This version inspects every tracked path and fails on any whose
basename is exactly ``secrets.yaml`` — ``secrets.example.yaml`` templates are
deliberately allowed.
"""

import subprocess
import sys
from pathlib import PurePosixPath


def tracked_secrets_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [
        path
        for path in result.stdout.split("\0")
        if path and PurePosixPath(path).name == "secrets.yaml"
    ]


def main() -> int:
    offenders = tracked_secrets_files()
    if offenders:
        sys.stderr.write(
            "ERROR: secrets.yaml is tracked in git at:\n"
            + "".join(f"    {path}\n" for path in offenders)
            + "It must remain gitignored at every depth. Use the tracked\n"
            "secrets.example.yaml templates and copy them locally, e.g.:\n"
            "    cp secrets.example.yaml secrets.yaml\n"
            "    cp products/secrets.example.yaml products/secrets.yaml\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
