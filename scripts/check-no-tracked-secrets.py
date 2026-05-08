#!/usr/bin/env python3
"""Fail if root secrets.yaml is tracked in git.

The repo ships secrets.example.yaml as the tracked template. The real
secrets.yaml is gitignored and must stay local. This guard catches
regressions where someone re-adds secrets.yaml to the index.
"""

import subprocess
import sys


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "secrets.yaml"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        sys.stderr.write(
            "ERROR: secrets.yaml is tracked in git.\n"
            "It must remain gitignored. Use secrets.example.yaml as the\n"
            "tracked template and copy it locally:\n"
            "    cp secrets.example.yaml secrets.yaml\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
