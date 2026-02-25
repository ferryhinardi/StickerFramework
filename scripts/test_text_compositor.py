#!/usr/bin/env python3
"""
Test / Preview script for the TextCompositor.

Loads benchmark sticker images and overlays text to validate styling
without requiring ComfyUI to be running.

Usage:
    # Test all benchmark stickers (uses chubby-mochi-cat images):
    python test_text_compositor.py

    # Test only a specific pack:
    python test_text_compositor.py --pack chubby-mochi-cat

    # Test with a single custom image + text:
    python test_text_compositor.py --image sticker.png --text "WOW" --color "#FF3333"

    # Generate a grid preview of all results:
    python test_text_compositor.py --grid

Output is saved to packs/<pack_id>/text_preview/ by default.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure scripts/ is on the path
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from PIL import Image

from text_compositor import TextCompositor

_REPO_ROOT = _SCRIPTS_DIR.parent
_PACKS_DIR = _REPO_ROOT / "packs"

# ---------------------------------------------------------------------------
# Benchmark test data — matches the sticker IDs + text from pack configs
# ---------------------------------------------------------------------------
BENCHMARK_TESTS: dict[str, list[dict]] = {
    "chubby-mochi-cat": [
        {"image": "01_what.png", "text": {"content": "WHAT?!", "color": "#3366FF"}},
        {"image": "02_lol.png", "text": {"content": "LOL", "color": "#FF3333"}},
        {"image": "03_ok.png", "text": {"content": "OK", "color": "#33AA55"}},
        {"image": "04_nope.png", "text": {"content": "NOPE", "color": "#FF6633"}},
        {"image": "05_bye.png", "text": {"content": "BYE", "color": "#9966CC"}},
        {
            "image": "06_lets_go.png",
            "text": {"content": "LET'S GO", "color": "#FF9900"},
        },
        {
            "image": "07_im_done.png",
            "text": {"content": "I'M DONE", "color": "#888888"},
        },
        {"image": "08_perfect.png", "text": {"content": "PERFECT", "color": "#FFD700"}},
        {"image": "09_sure.png", "text": {"content": "SURE", "color": "#33BBCC"}},
        {"image": "10_yesss.png", "text": {"content": "YESSS", "color": "#FF69B4"}},
    ],
    "chubby-mochi-hamster": [
        {
            "image": "sticker_pack.png",
            "text": {"content": "HELLO!", "color": "#FF9900"},
        },
    ],
}

# Default text styling matching benchmark analysis
BENCHMARK_DEFAULTS = {
    "font": "FredokaOne-Regular.ttf",
    "font_size": 90,
    "outline_width": 6,
    "outline_color": "#1a1a1a",
    "shadow_offset": [4, 5],
    "shadow_color": "#00000080",
    "position": "top-center",
    "padding_top": 25,
}


def _load_pack_config(pack_id: str) -> dict | None:
    """Try to load a pack's pack_config.py for its text_defaults and sticker configs."""
    config_path = _PACKS_DIR / pack_id / "pack_config.py"
    if not config_path.exists():
        return None
    import importlib.util

    spec = importlib.util.spec_from_file_location("pack_config", config_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, "PACK_CONFIG", None)


def run_benchmark_tests(
    pack_id: str,
    output_dir: Path | None = None,
    make_grid: bool = False,
) -> list[Path]:
    """
    Run text overlay tests for a benchmark pack.

    Returns list of saved preview image paths.
    """
    pack_dir = _PACKS_DIR / pack_id
    if not pack_dir.exists():
        print(f"SKIP: Pack directory not found: {pack_dir}")
        return []

    # Try loading pack config for better defaults
    pack_config = _load_pack_config(pack_id)
    if pack_config and "text_defaults" in pack_config:
        defaults = pack_config["text_defaults"]
        print(f"  Using text_defaults from {pack_id}/pack_config.py")
    else:
        defaults = BENCHMARK_DEFAULTS
        print(f"  Using built-in benchmark defaults")

    # Collect sticker test data
    if pack_config and "stickers" in pack_config:
        # Build test entries from real pack config
        tests = []
        for s in pack_config["stickers"]:
            text_field = s.get("text")
            if not text_field:
                continue
            # Find matching image file
            img_file = pack_dir / f"{s['id']}.png"
            if not img_file.exists():
                # Try without numbered prefix
                candidates = list(pack_dir.glob(f"*{s['id']}*.png"))
                img_file = candidates[0] if candidates else None
            if img_file and img_file.exists():
                text_cfg = (
                    text_field
                    if isinstance(text_field, dict)
                    else {"content": text_field}
                )
                tests.append({"image": img_file.name, "text": text_cfg})
        if not tests:
            # Fall back to hardcoded benchmark tests
            tests = BENCHMARK_TESTS.get(pack_id, [])
    else:
        tests = BENCHMARK_TESTS.get(pack_id, [])

    if not tests:
        print(f"SKIP: No test data for pack '{pack_id}'")
        return []

    # Output directory
    if output_dir is None:
        output_dir = pack_dir / "text_preview"
    output_dir.mkdir(parents=True, exist_ok=True)

    compositor = TextCompositor()
    results: list[Path] = []

    for i, test in enumerate(tests):
        img_path = pack_dir / test["image"]
        if not img_path.exists():
            print(f"  SKIP: Image not found: {img_path.name}")
            continue

        text_cfg = test["text"]
        content = (
            text_cfg if isinstance(text_cfg, str) else text_cfg.get("content", "?")
        )
        label = content if isinstance(content, str) else "?"

        print(f'  [{i + 1}/{len(tests)}] {img_path.name} -> "{label}"')

        try:
            img = Image.open(img_path).convert("RGBA")
            result = compositor.composite_text(img, text_cfg, defaults)

            out_name = f"{img_path.stem}_text.png"
            out_path = output_dir / out_name
            result.save(str(out_path), "PNG")
            results.append(out_path)
            print(f"         Saved: {out_path.relative_to(_REPO_ROOT)}")
        except Exception as e:
            print(f"         ERROR: {e}")

    # Optional grid preview
    if make_grid and results:
        grid_path = _make_grid(results, output_dir / "_grid_preview.png")
        if grid_path:
            print(f"\n  Grid saved: {grid_path.relative_to(_REPO_ROOT)}")

    return results


def run_single_test(
    image_path: Path,
    text: str,
    color: str = "#FFFFFF",
    output_path: Path | None = None,
) -> Path | None:
    """Test text overlay on a single image."""
    if not image_path.exists():
        print(f"ERROR: Image not found: {image_path}")
        return None

    compositor = TextCompositor()
    img = Image.open(image_path).convert("RGBA")

    text_cfg = {"content": text, "color": color}
    result = compositor.composite_text(img, text_cfg, BENCHMARK_DEFAULTS)

    if output_path is None:
        output_path = image_path.parent / f"{image_path.stem}_text.png"

    result.save(str(output_path), "PNG")
    print(f"Saved: {output_path}")
    return output_path


def _make_grid(
    image_paths: list[Path],
    output_path: Path,
    thumb_size: int = 256,
    cols: int = 5,
) -> Path | None:
    """Stitch preview images into a grid for quick visual comparison."""
    if not image_paths:
        return None

    images = [Image.open(p).convert("RGBA") for p in image_paths]

    # Resize to uniform thumbnails
    thumbs = []
    for img in images:
        img.thumbnail((thumb_size, thumb_size), Image.LANCZOS)
        # Paste onto a white square
        bg = Image.new("RGBA", (thumb_size, thumb_size), (255, 255, 255, 255))
        offset = ((thumb_size - img.width) // 2, (thumb_size - img.height) // 2)
        bg.paste(img, offset, img)
        thumbs.append(bg)

    rows = (len(thumbs) + cols - 1) // cols
    grid_w = cols * thumb_size
    grid_h = rows * thumb_size
    grid = Image.new("RGBA", (grid_w, grid_h), (245, 245, 245, 255))

    for idx, thumb in enumerate(thumbs):
        r, c = divmod(idx, cols)
        grid.paste(thumb, (c * thumb_size, r * thumb_size), thumb)

    grid.save(str(output_path), "PNG")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Test text compositor on benchmark sticker images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all benchmark packs:
  python test_text_compositor.py

  # Test a specific pack:
  python test_text_compositor.py --pack chubby-mochi-cat

  # Test single image:
  python test_text_compositor.py --image ../packs/chubby-mochi-cat/01_what.png \\
      --text "WHAT?!" --color "#3366FF"

  # Generate grid preview:
  python test_text_compositor.py --grid
""",
    )
    parser.add_argument(
        "--pack",
        type=str,
        default=None,
        help="Pack ID to test (default: all benchmark packs)",
    )
    parser.add_argument(
        "--image",
        type=str,
        default=None,
        help="Single image path for one-off test",
    )
    parser.add_argument("--text", type=str, default="TEST", help="Text for single test")
    parser.add_argument(
        "--color", type=str, default="#FFFFFF", help="Text color for single test"
    )
    parser.add_argument(
        "--grid", action="store_true", help="Generate a grid preview image"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Override output directory",
    )
    args = parser.parse_args()

    # Single-image mode
    if args.image:
        run_single_test(
            image_path=Path(args.image),
            text=args.text,
            color=args.color,
        )
        sys.exit(0)

    # Benchmark mode
    packs_to_test = [args.pack] if args.pack else list(BENCHMARK_TESTS.keys())
    out_dir = Path(args.output_dir) if args.output_dir else None

    all_results: list[Path] = []
    for pack_id in packs_to_test:
        print(f"\n{'=' * 50}")
        print(f"Testing: {pack_id}")
        print(f"{'=' * 50}")
        results = run_benchmark_tests(pack_id, output_dir=out_dir, make_grid=args.grid)
        all_results.extend(results)

    print(f"\n{'=' * 50}")
    print(f"Total previews generated: {len(all_results)}")
    if all_results:
        print(f"Preview directory: {all_results[0].parent.relative_to(_REPO_ROOT)}")
    print(f"{'=' * 50}")
