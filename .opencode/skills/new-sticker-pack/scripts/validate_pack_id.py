#!/usr/bin/env python3
"""
Validate a pack_id meets StickerFramework naming rules.

Exit 0 = valid. Exit 1 = invalid (prints reason to stderr).
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
PACKS_DIR = REPO_ROOT / "packs"

PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate(pack_id: str) -> list[str]:
    errors = []
    if not PATTERN.match(pack_id):
        errors.append(
            f"'{pack_id}' must be kebab-case: lowercase letters, digits, "
            "single hyphens, no leading/trailing hyphens."
        )
    if len(pack_id) > 64:
        errors.append(f"pack_id must be ≤ 64 characters (got {len(pack_id)}).")
    if (PACKS_DIR / pack_id).exists():
        errors.append(
            f"Directory packs/{pack_id}/ already exists. "
            "Choose a different name or delete the existing directory."
        )
    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_pack_id.py <pack_id>", file=sys.stderr)
        sys.exit(2)

    errs = validate(sys.argv[1])
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"OK: '{sys.argv[1]}' is a valid pack_id.")
