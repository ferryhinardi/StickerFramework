#!/usr/bin/env python3
"""
Verify LINE Creator Market image assets are present and meet spec.

Exit 0 = all assets valid. Exit 1 = failures found.

Usage: check_line_assets.py <pack_id>
"""

import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[4]

REQUIRED_ASSETS = [
    # (relative_to_final, glob_pattern, expected_w, expected_h, max_bytes)
    ("line_main", "*.png", 240, 240, 1_048_576),
    ("line_tab", "*.png", 96, 74, 1_048_576),
]

LINE_STICKER_SPEC = ("line", "*.png", 370, 320, 1_048_576)


def check(pack_id: str) -> list[str]:
    errors = []
    final = REPO_ROOT / "packs" / pack_id / "final"

    if not final.exists():
        errors.append(
            f"packs/{pack_id}/final/ does not exist — run process-pipeline first."
        )
        return errors

    # Check main image and tab icon
    for subdir, pattern, w, h, max_b in REQUIRED_ASSETS:
        d = final / subdir
        files = list(d.glob(pattern)) if d.exists() else []
        files = [f for f in files if f.name != ".gitkeep"]
        if not files:
            errors.append(f"Missing: final/{subdir}/ has no {pattern} files.")
            continue
        for f in files:
            _check_image(f, w, h, max_b, errors, subdir)

    # Check sticker images
    sticker_dir = final / "line"
    stickers = (
        [f for f in sticker_dir.glob("*.png") if f.name != ".gitkeep"]
        if sticker_dir.exists()
        else []
    )
    if not stickers:
        errors.append("Missing: final/line/ has no PNG sticker files.")
    else:
        valid_counts = {8, 16, 24, 32, 40}
        if len(stickers) not in valid_counts:
            errors.append(
                f"LINE requires 8/16/24/32/40 stickers — found {len(stickers)}."
            )
        for f in stickers:
            _check_image(f, 370, 320, 1_048_576, errors, "line")

    return errors


def _check_image(
    path: Path, exp_w: int, exp_h: int, max_bytes: int, errors: list, label: str
) -> None:
    size = path.stat().st_size
    if size > max_bytes:
        errors.append(
            f"{label}/{path.name}: {size / 1024:.1f} KB exceeds {max_bytes // 1024} KB limit."
        )
    try:
        with Image.open(path) as img:
            if img.width != exp_w or img.height != exp_h:
                errors.append(
                    f"{label}/{path.name}: {img.width}×{img.height} px — "
                    f"expected {exp_w}×{exp_h} px."
                )
    except Exception as e:
        errors.append(f"{label}/{path.name}: cannot open image — {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: check_line_assets.py <pack_id>", file=sys.stderr)
        sys.exit(2)

    errs = check(sys.argv[1])
    if errs:
        for e in errs:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("LINE asset check passed.")
