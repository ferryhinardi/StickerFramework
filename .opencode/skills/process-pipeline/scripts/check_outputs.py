#!/usr/bin/env python3
"""
Verify that processing produced the expected output files per platform.

Exit 0 = all outputs present. Exit 1 = missing files.

Usage: check_outputs.py <pack_id>
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

# (directory_relative_to_final, expected_extension, min_count)
PLATFORM_CHECKS = [
    ("line", ".png", 1),
    ("line_main", ".png", 1),
    ("line_tab", ".png", 1),
    ("whatsapp", ".webp", 1),
    ("telegram", ".webp", 1),
    ("imessage_large", ".png", 1),
    ("print_etsy", ".png", 1),
]


def check(pack_id: str) -> tuple[list[str], list[str]]:
    errors = []
    infos = []
    final_dir = REPO_ROOT / "packs" / pack_id / "final"

    if not final_dir.exists():
        errors.append(
            f"packs/{pack_id}/final/ does not exist — pipeline may not have run."
        )
        return errors, infos

    for subdir, ext, min_count in PLATFORM_CHECKS:
        d = final_dir / subdir
        if not d.exists():
            errors.append(f"Missing output directory: final/{subdir}/")
            continue
        files = [f for f in d.iterdir() if f.suffix == ext and f.name != ".gitkeep"]
        if len(files) < min_count:
            errors.append(
                f"final/{subdir}/ has {len(files)} {ext} file(s), expected ≥ {min_count}."
            )
        else:
            infos.append(f"  {subdir:<25} {len(files):>3} {ext} file(s)  ✓")

    return errors, infos


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_outputs.py <pack_id>", file=sys.stderr)
        sys.exit(2)

    errs, infos = check(sys.argv[1])

    print("\nOutput verification:")
    for info in infos:
        print(info)

    if errs:
        print()
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nAll outputs verified.")
