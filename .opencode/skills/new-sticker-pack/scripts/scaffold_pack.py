#!/usr/bin/env python3
"""
Create the standard StickerFramework directory layout for a new pack.

Exit 0 = success. Exit 1 = error.

Usage: scaffold_pack.py <pack_id>
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

SUBDIRS = [
    "raw",
    "split",
    "final/line",
    "final/line_main",
    "final/line_tab",
    "final/whatsapp",
    "final/whatsapp_native",
    "final/telegram",
    "final/telegram_animated",
    "final/telegram_video",
    "final/imessage_large",
    "final/print_etsy",
    "metadata",
    "dist",
]


def scaffold(pack_id: str) -> None:
    pack_dir = REPO_ROOT / "packs" / pack_id
    if pack_dir.exists():
        print(f"ERROR: packs/{pack_id}/ already exists.", file=sys.stderr)
        sys.exit(1)

    for sub in SUBDIRS:
        (pack_dir / sub).mkdir(parents=True, exist_ok=True)
        # Place a .gitkeep so git tracks empty dirs
        (pack_dir / sub / ".gitkeep").touch()

    print(f"Scaffolded packs/{pack_id}/ with {len(SUBDIRS)} subdirectories.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: scaffold_pack.py <pack_id>", file=sys.stderr)
        sys.exit(2)
    scaffold(sys.argv[1])
