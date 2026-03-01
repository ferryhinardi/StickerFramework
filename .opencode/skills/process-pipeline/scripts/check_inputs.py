#!/usr/bin/env python3
"""
Verify that raw input images exist for a pack before processing.

Exit 0 = OK. Exit 1 = missing inputs.

Usage: check_inputs.py <pack_id>
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]


def check(pack_id: str) -> list[str]:
    errors = []
    pack_dir = REPO_ROOT / "packs" / pack_id

    if not pack_dir.exists():
        errors.append(f"Pack directory packs/{pack_id}/ does not exist.")
        return errors

    raw_dir = pack_dir / "raw"
    if not raw_dir.exists():
        errors.append(f"packs/{pack_id}/raw/ directory does not exist.")
    else:
        pngs = list(raw_dir.glob("*.png"))
        if not pngs:
            errors.append(
                f"No PNG files found in packs/{pack_id}/raw/. "
                "Run the generation stage first."
            )
        else:
            print(f"Found {len(pngs)} PNG file(s) in packs/{pack_id}/raw/")
            for p in sorted(pngs):
                print(f"  {p.name}")

    config_file = pack_dir / "pack_config.py"
    if not config_file.exists():
        errors.append(
            f"packs/{pack_id}/pack_config.py not found. "
            "Run the new-sticker-pack skill first."
        )

    return errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_inputs.py <pack_id>", file=sys.stderr)
        sys.exit(2)

    errs = check(sys.argv[1])
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("Input check passed.")
