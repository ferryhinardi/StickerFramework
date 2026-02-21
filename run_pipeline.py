#!/usr/bin/env python3
"""
Master Pipeline Orchestrator - End-to-end sticker pack creation.

Runs the complete pipeline:
    1. Generate raw images via DALL-E 3 (or skip if images exist)
    2. Process images (background removal, outline, resize, convert)
    3. Generate platform metadata
    4. Create print sheets and distribution packages
    5. Optionally publish to Telegram

Usage:
    # Full pipeline (generate + process + package):
    export OPENAI_API_KEY="sk-..."
    python run_pipeline.py

    # Process only (skip generation, use existing raw images):
    python run_pipeline.py --process-only

    # Process your existing stickers directory:
    python run_pipeline.py --process-only --input stickers/

    # Generate only (no processing):
    python run_pipeline.py --generate-only

    # Use standard quality to save money ($0.04 vs $0.08 per image):
    python run_pipeline.py --standard

    # Publish to Telegram after processing:
    python run_pipeline.py --process-only --telegram
"""

import argparse
import json
import os
import sys
from pathlib import Path

from pack_config import PACK_CONFIG


def stage_generate(config: dict, quality: str = "hd") -> list[Path]:
    """Stage 1: Generate raw images via DALL-E 3."""
    from image_generator import StickerGenerator

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: Set OPENAI_API_KEY environment variable")
        print("  export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    generator = StickerGenerator(api_key=api_key)
    return generator.generate_pack(config, quality=quality)


def stage_process(
    config: dict,
    input_dir: str | None = None,
    skip_bg: bool = False,
) -> list[dict]:
    """Stage 2: Process images for all platforms."""
    from sticker_processor import StickerProcessor

    pack_id = config["pack_id"]
    raw_dir = input_dir or os.path.join(pack_id, "raw")
    final_dir = os.path.join(pack_id, "final")

    if not Path(raw_dir).exists():
        print(f"ERROR: Input directory not found: {raw_dir}")
        print("Run generation first, or specify --input <dir>")
        sys.exit(1)

    processor = StickerProcessor(outline_width=10)
    return processor.process_batch(
        input_dir=raw_dir,
        output_dir=final_dir,
        platforms=config["platforms"],
        skip_bg_removal=skip_bg,
    )


def stage_metadata(config: dict):
    """Stage 3: Generate platform metadata files."""
    pack_id = config["pack_id"]
    meta_dir = Path(pack_id) / "metadata"
    meta_dir.mkdir(parents=True, exist_ok=True)

    # WhatsApp metadata (for third-party sticker apps)
    whatsapp_meta = {
        "android_play_store_link": "",
        "ios_app_store_link": "",
        "sticker_packs": [
            {
                "identifier": pack_id,
                "name": config["pack_name"],
                "publisher": config.get("publisher", "Your Brand Name"),
                "tray_image_file": "tray_icon.webp",
                "publisher_website": "",
                "privacy_policy_website": "",
                "stickers": [
                    {
                        "image_file": f"{s['id']}.webp",
                        "emojis": [s["emoji"]],
                    }
                    for s in config["stickers"]
                ],
            }
        ],
    }
    with open(meta_dir / "whatsapp_contents.json", "w") as f:
        json.dump(whatsapp_meta, f, indent=2)

    # Telegram emoji mapping
    telegram_meta = {s["id"]: s["emoji"] for s in config["stickers"]}
    with open(meta_dir / "telegram_emojis.json", "w") as f:
        json.dump(telegram_meta, f, indent=2)

    # LINE metadata
    line_meta = {
        "title": {"en": config["pack_name"]},
        "author": {"en": config.get("publisher", "Your Brand Name")},
        "stickers": [
            {
                "id": i + 1,
                "filename": f"{s['id']}.png",
                "emoji": s["emoji"],
            }
            for i, s in enumerate(config["stickers"])
        ],
    }
    with open(meta_dir / "line_metadata.json", "w") as f:
        json.dump(line_meta, f, indent=2)

    # Pack summary
    summary = {
        "pack_id": pack_id,
        "pack_name": config["pack_name"],
        "publisher": config.get("publisher", "Your Brand Name"),
        "sticker_count": len(config["stickers"]),
        "platforms": config["platforms"],
        "stickers": [
            {"id": s["id"], "emotion": s["emotion"], "emoji": s["emoji"]}
            for s in config["stickers"]
        ],
    }
    with open(meta_dir / "pack_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  Metadata written to {meta_dir}/")
    print(f"    - whatsapp_contents.json")
    print(f"    - telegram_emojis.json")
    print(f"    - line_metadata.json")
    print(f"    - pack_summary.json")


def stage_package(config: dict):
    """Stage 4: Create print sheets and distribution packages."""
    from create_print_sheet import (
        create_distribution_zip,
        create_social_preview,
        create_sticker_sheet,
    )

    pack_id = config["pack_id"]
    pack_name = config["pack_name"]
    etsy_dir = os.path.join(pack_id, "final", "print_etsy")
    dist_dir = os.path.join(pack_id, "dist")

    if not Path(etsy_dir).exists():
        print(f"  Skipping packaging: {etsy_dir} not found")
        return

    sheets = []

    # US Letter sticker sheet
    sheet = create_sticker_sheet(
        etsy_dir,
        f"{dist_dir}/sheets/sticker_sheet_letter.png",
        page_size="us_letter",
        title=pack_name,
    )
    if sheet:
        sheets.append(str(sheet))

    # A4 sticker sheet
    sheet = create_sticker_sheet(
        etsy_dir,
        f"{dist_dir}/sheets/sticker_sheet_a4.png",
        page_size="a4",
        title=pack_name,
    )
    if sheet:
        sheets.append(str(sheet))

    # Social media preview
    create_social_preview(
        etsy_dir,
        f"{dist_dir}/social_preview.png",
        title=pack_name,
    )

    # Distribution ZIP
    create_distribution_zip(
        pack_id=pack_id,
        pack_name=pack_name,
        sticker_dir=etsy_dir,
        sheet_paths=sheets,
        output_path=f"{dist_dir}/{pack_id}_digital_download.zip",
        publisher=config.get("publisher", "Your Brand Name"),
    )


def stage_tray_icon(config: dict):
    """Create tray/tab icons from the first sticker."""
    from sticker_processor import StickerProcessor

    pack_id = config["pack_id"]
    processor = StickerProcessor()

    # Use the first processed WhatsApp sticker as tray icon source
    wa_dir = Path(pack_id) / "final" / "whatsapp"
    if wa_dir.exists():
        first_sticker = sorted(wa_dir.glob("*.webp"))
        if first_sticker:
            tray_path = wa_dir / "tray_icon.webp"
            processor.create_tray_icon(
                str(first_sticker[0]),
                str(tray_path),
                platform="whatsapp_tray",
            )
            print(f"  WhatsApp tray icon: {tray_path}")


def stage_telegram(config: dict):
    """Stage 5 (optional): Publish to Telegram."""
    from telegram_publisher import TelegramStickerPublisher, load_emojis_from_config

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    user_id = os.environ.get("TELEGRAM_USER_ID")

    if not bot_token or not user_id:
        print("\n  Telegram publishing skipped.")
        print("  Set TELEGRAM_BOT_TOKEN and TELEGRAM_USER_ID to enable.")
        return

    pack_id = config["pack_id"]
    tg_dir = Path(pack_id) / "final" / "telegram"

    if not tg_dir.exists():
        print(f"  Telegram stickers not found in {tg_dir}")
        return

    sticker_files = sorted(tg_dir.glob("*.webp"))
    if not sticker_files:
        print(f"  No WebP files in {tg_dir}")
        return

    emojis = load_emojis_from_config(config)
    emojis = emojis[: len(sticker_files)]
    if len(emojis) < len(sticker_files):
        emojis.extend(["\U0001f60a"] * (len(sticker_files) - len(emojis)))

    publisher = TelegramStickerPublisher(bot_token)
    pack_name = pack_id.replace("-", "_")
    publisher.create_sticker_set(
        user_id=int(user_id),
        name=pack_name,
        title=config["pack_name"],
        sticker_paths=[str(f) for f in sticker_files],
        emojis_list=emojis,
    )


def stage_imessage(config: dict):
    """Stage 6 (optional): Prepare iMessage Xcode project."""
    from prepare_imessage_pack import create_xcode_project

    pack_id = config["pack_id"]
    imessage_dir = os.path.join(pack_id, "final", "imessage_large")

    if not Path(imessage_dir).exists():
        print(f"  iMessage stickers not found in {imessage_dir}")
        return

    project_name = config["pack_name"].replace(" ", "")
    create_xcode_project(
        project_name=project_name,
        sticker_dir=imessage_dir,
        output_dir=os.path.join(pack_id, "xcode"),
    )


# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Sticker Pack Pipeline - Generate, process, and package stickers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (generate + process + package):
  export OPENAI_API_KEY="sk-..."
  python run_pipeline.py

  # Process existing images only:
  python run_pipeline.py --process-only

  # Process your existing stickers folder:
  python run_pipeline.py --process-only --input stickers/

  # Skip background removal (images already transparent):
  python run_pipeline.py --process-only --skip-bg

  # Use cheaper standard quality images:
  python run_pipeline.py --standard

  # Also publish to Telegram:
  python run_pipeline.py --telegram

  # Also create iMessage Xcode project:
  python run_pipeline.py --imessage
""",
    )
    parser.add_argument(
        "--process-only",
        action="store_true",
        help="Skip image generation, process existing raw images",
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate images, skip processing",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Custom input directory for processing (default: <pack_id>/raw)",
    )
    parser.add_argument(
        "--skip-bg",
        action="store_true",
        help="Skip background removal (images already have transparent bg)",
    )
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Use standard quality ($0.04/image) instead of HD ($0.08/image)",
    )
    parser.add_argument(
        "--telegram",
        action="store_true",
        help="Also publish to Telegram",
    )
    parser.add_argument(
        "--imessage",
        action="store_true",
        help="Also prepare iMessage Xcode project",
    )
    args = parser.parse_args()

    config = PACK_CONFIG

    print("\n" + "=" * 70)
    print(f"  STICKER PIPELINE: {config['pack_name']}")
    print(f"  Pack ID: {config['pack_id']}")
    print(f"  Stickers: {len(config['stickers'])}")
    print(f"  Platforms: {', '.join(config['platforms'])}")
    print("=" * 70)

    # Stage 1: Generate
    if not args.process_only:
        print(f"\n{'=' * 60}")
        print("STAGE 1: Generating sticker images via DALL-E 3")
        print(f"{'=' * 60}")
        quality = "standard" if args.standard else "hd"
        stage_generate(config, quality=quality)

    if args.generate_only:
        print("\n--generate-only: Stopping after generation.")
        return

    # Stage 2: Process
    print(f"\n{'=' * 60}")
    print("STAGE 2: Processing images")
    print(f"{'=' * 60}")
    stage_process(config, input_dir=args.input, skip_bg=args.skip_bg)

    # Stage 3: Tray icons
    print(f"\n{'=' * 60}")
    print("STAGE 3: Creating tray/tab icons")
    print(f"{'=' * 60}")
    stage_tray_icon(config)

    # Stage 4: Metadata
    print(f"\n{'=' * 60}")
    print("STAGE 4: Generating metadata")
    print(f"{'=' * 60}")
    stage_metadata(config)

    # Stage 5: Package
    print(f"\n{'=' * 60}")
    print("STAGE 5: Creating print sheets & distribution packages")
    print(f"{'=' * 60}")
    stage_package(config)

    # Stage 6: Telegram (optional)
    if args.telegram:
        print(f"\n{'=' * 60}")
        print("STAGE 6: Publishing to Telegram")
        print(f"{'=' * 60}")
        stage_telegram(config)

    # Stage 7: iMessage (optional)
    if args.imessage:
        print(f"\n{'=' * 60}")
        print("STAGE 7: Preparing iMessage Xcode project")
        print(f"{'=' * 60}")
        stage_imessage(config)

    # Final summary
    pack_id = config["pack_id"]
    print(f"\n{'=' * 70}")
    print("  PIPELINE COMPLETE")
    print(f"{'=' * 70}")
    print(f"\n  Output directory: {pack_id}/")
    print(f"  ├── raw/          - Original generated images")
    print(f"  ├── final/        - Processed platform-ready stickers")
    for p in config["platforms"]:
        print(f"  │   ├── {p}/")
    print(f"  ├── metadata/     - Platform metadata files")
    print(f"  ├── dist/         - Distribution packages (ZIP, sheets)")
    if args.imessage:
        print(f"  └── xcode/        - iMessage Xcode project")
    print()
    print("  Next steps:")
    print("  1. Upload to Sticker.ly (see guides/stickerly_guide.md)")
    print("  2. Publish on LINE, Etsy, Gumroad (see guides/distribution_guide.md)")
    if not args.telegram:
        print("  3. Publish to Telegram: python run_pipeline.py --telegram")
    if not args.imessage:
        print("  4. iMessage project: python run_pipeline.py --imessage")
    print()


if __name__ == "__main__":
    main()
