#!/usr/bin/env python3
"""
Master Pipeline Orchestrator - End-to-end sticker pack creation.

Runs the complete pipeline:
    1. Generate raw images via DALL-E 3 (or skip if images exist)
    2. Process images (background removal, outline, resize, convert)
    2b. (Optional) Create animated TGS / video WebM variants
    3. Generate platform metadata
    4. Create print sheets and distribution packages
    5. Optionally publish static stickers to Telegram
    6b. Optionally publish animated stickers to Telegram (TGS)
    6c. Optionally publish video stickers to Telegram (WebM)
    7. Optionally prepare iMessage Xcode project
    8. Optionally build & submit iMessage app to App Store via Fastlane
    9. Optionally export stickers for WhatsApp native Android app

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

    # Create and publish animated Telegram stickers:
    python run_pipeline.py --process-only --telegram-animated --animation-preset bounce

    # Create and publish video Telegram stickers:
    python run_pipeline.py --process-only --telegram-video

    # Build & submit iMessage sticker app to App Store:
    python run_pipeline.py --process-only --imessage --imessage-publish

    # Export stickers for WhatsApp native Android app:
    python run_pipeline.py --process-only --whatsapp-native
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Repo root (parent of scripts/)
REPO_ROOT = _SCRIPTS_DIR.parent

from pack_config import PACK_CONFIG


def stage_generate(
    config: dict, quality: str = "hd", engine: str = "dalle", seed: int | None = None
) -> list[Path]:
    """Stage 1: Generate raw images via DALL-E 3 or ComfyUI."""
    if engine == "comfyui":
        from comfyui_generator import ComfyUIStickerGenerator

        comfyui_url = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8000")
        try:
            generator = ComfyUIStickerGenerator(comfyui_url=comfyui_url)
        except ConnectionError as e:
            print(f"ERROR: {e}")
            sys.exit(1)
        return generator.generate_pack(config, seed=seed)
    else:
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
    raw_dir = input_dir or str(REPO_ROOT / "packs" / pack_id / "raw")
    final_dir = str(REPO_ROOT / "packs" / pack_id / "final")

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
    meta_dir = REPO_ROOT / "packs" / pack_id / "metadata"
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
    etsy_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "print_etsy")
    dist_dir = str(REPO_ROOT / "packs" / pack_id / "dist")

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
    wa_dir = REPO_ROOT / "packs" / pack_id / "final" / "whatsapp"
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
    tg_dir = REPO_ROOT / "packs" / pack_id / "final" / "telegram"

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
    imessage_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "imessage_large")

    if not Path(imessage_dir).exists():
        print(f"  iMessage stickers not found in {imessage_dir}")
        return

    project_name = config["pack_name"].replace(" ", "")
    create_xcode_project(
        project_name=project_name,
        sticker_dir=imessage_dir,
        output_dir=str(REPO_ROOT / "packs" / pack_id / "xcode"),
    )


def stage_imessage_publish(
    config: dict, dry_run: bool = False, skip_submit: bool = False
):
    """Stage 8 (optional): Build & submit iMessage app to App Store via Fastlane."""
    from imessage_publisher import IMessagePublisher

    pack_id = config["pack_id"]
    sticker_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "imessage_large")

    if not Path(sticker_dir).exists():
        print(f"  iMessage stickers not found in {sticker_dir}")
        print("  Run with --imessage first to prepare the Xcode project.")
        return

    publisher = IMessagePublisher(
        pack_config=config,
        sticker_dir=sticker_dir,
        output_dir=str(REPO_ROOT / "packs" / pack_id / "xcode"),
    )
    publisher.publish(dry_run=dry_run, skip_submit=skip_submit)


def stage_whatsapp_export(config: dict, server_url: str | None = None):
    """Stage 9 (optional): Export stickers for WhatsApp native app.

    Converts processed stickers to WhatsApp-native format (512x512 WebP,
    96x96 tray icon) and optionally pushes them to the WhatsApp sticker server.

    Args:
        config: Pack configuration dict.
        server_url: Optional server URL to push the pack to.
    """
    from whatsapp_exporter import WhatsAppExporter

    pack_id = config["pack_id"]
    # Use processed whatsapp_native stickers if available, else fall back to telegram
    whatsapp_dir = REPO_ROOT / "packs" / pack_id / "final" / "whatsapp_native"
    telegram_dir = REPO_ROOT / "packs" / pack_id / "final" / "telegram"

    if whatsapp_dir.exists() and list(whatsapp_dir.glob("*.webp")):
        sticker_dir = str(whatsapp_dir)
    elif telegram_dir.exists():
        sticker_dir = str(telegram_dir)
    else:
        print(f"  Source stickers not found.")
        print("  Run processing stage first (needs 'telegram' in platforms).")
        return

    output_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "whatsapp_native_export")

    exporter = WhatsAppExporter()
    try:
        pack_dir = exporter.export_pack(
            pack_config=config,
            sticker_dir=sticker_dir,
            output_dir=output_dir,
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"  WhatsApp export failed: {e}")
        return

    # Validate the exported pack
    errors = exporter.validate_pack(str(pack_dir))
    if errors:
        print(f"  WARNING: Exported pack has {len(errors)} validation issue(s):")
        for err in errors:
            print(f"    - {err}")

    # Optionally push to server
    push_url = server_url or os.environ.get("WHATSAPP_SERVER_URL")
    if push_url:
        api_key = os.environ.get("WHATSAPP_SERVER_API_KEY")
        print(f"\n  Pushing pack to server at {push_url} ...")
        exporter.push_to_server(str(pack_dir), push_url, api_key=api_key)
    else:
        print(
            "\n  Set WHATSAPP_SERVER_URL or --whatsapp-server-url to auto-push packs."
        )


def stage_process_animated(
    config: dict, formats: list[str] | None = None, animation_type: str = "bounce"
):
    """Stage 2b: Create animated/video versions of processed stickers.

    Converts processed PNGs into TGS (animated) and/or WebM (video) files
    for Telegram animated sticker publishing.

    Args:
        config: Pack configuration dict.
        formats: List of formats to generate, e.g. ["tgs", "webm"].
                 Defaults to both.
        animation_type: Animation preset name (e.g. "bounce", "pulse", "pop_in").
    """
    from sticker_processor import StickerProcessor

    if formats is None:
        formats = ["tgs", "webm"]

    pack_id = config["pack_id"]
    # Use the base telegram processed PNGs as source
    telegram_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "telegram")

    if not Path(telegram_dir).exists():
        print(f"  Telegram stickers not found in {telegram_dir}")
        print("  Run processing stage first (needs 'telegram' in platforms).")
        return

    processor = StickerProcessor()
    processor.process_batch_animated(
        input_dir=telegram_dir,
        animation_type=animation_type,
        formats=formats,
    )


def stage_telegram_animated(config: dict, sticker_format: str = "animated"):
    """Stage 6b: Publish animated/video stickers to Telegram.

    Args:
        config: Pack configuration dict.
        sticker_format: "animated" for TGS or "video" for WebM.
    """
    from telegram_publisher import TelegramStickerPublisher, load_emojis_from_config

    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    user_id = os.environ.get("TELEGRAM_USER_ID")

    if not bot_token or not user_id:
        print("\n  Telegram publishing skipped.")
        print("  Set TELEGRAM_BOT_TOKEN and TELEGRAM_USER_ID to enable.")
        return

    pack_id = config["pack_id"]
    # Determine directory based on format
    if sticker_format == "animated":
        tg_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "telegram_animated")
    else:
        tg_dir = str(REPO_ROOT / "packs" / pack_id / "final" / "telegram_video")

    if not Path(tg_dir).exists():
        print(f"  {sticker_format.title()} stickers not found in {tg_dir}")
        print(
            "  Run with --telegram-animated or --telegram-video to generate them first."
        )
        return

    emojis = load_emojis_from_config(config)

    publisher = TelegramStickerPublisher(bot_token)
    # Use a distinct pack name to avoid colliding with the static set
    pack_name = f"{pack_id.replace('-', '_')}_{sticker_format}"
    title_suffix = "Animated" if sticker_format == "animated" else "Video"
    title = f"{config['pack_name']} ({title_suffix})"

    publisher.create_animated_sticker_set(
        user_id=int(user_id),
        name=pack_name,
        title=title,
        sticker_dir=tg_dir,
        emojis_list=emojis,
        sticker_format=sticker_format,
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

  # Create and publish animated Telegram stickers (TGS):
  python run_pipeline.py --telegram-animated

  # Create and publish video Telegram stickers (WebM):
  python run_pipeline.py --telegram-video

  # Use a specific animation preset:
  python run_pipeline.py --telegram-animated --animation-preset pop_in

  # All Telegram formats at once:
  python run_pipeline.py --telegram --telegram-animated --telegram-video

  # Also create iMessage Xcode project:
  python run_pipeline.py --imessage

  # Build & submit iMessage app to App Store:
  python run_pipeline.py --imessage-publish

  # Dry-run iMessage publish (no actual Fastlane):
  python run_pipeline.py --imessage-publish --imessage-dry-run

  # Export stickers for WhatsApp native Android app:
  python run_pipeline.py --process-only --whatsapp-native

  # Export and push to WhatsApp sticker server:
  python run_pipeline.py --process-only --whatsapp-native --whatsapp-server-url http://localhost:8080
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
        "--engine",
        type=str,
        choices=["dalle", "comfyui"],
        default="dalle",
        help="Image generation engine: 'dalle' (cloud, paid) or 'comfyui' (local, free)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base seed for ComfyUI generation (for reproducibility)",
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
    parser.add_argument(
        "--telegram-animated",
        action="store_true",
        help="Also create and publish animated Telegram stickers (TGS/Lottie)",
    )
    parser.add_argument(
        "--telegram-video",
        action="store_true",
        help="Also create and publish video Telegram stickers (WebM VP9)",
    )
    parser.add_argument(
        "--animation-preset",
        type=str,
        default="bounce",
        help="Animation preset for animated/video stickers (default: bounce). "
        "Options: bounce, shake, pulse, pop_in, spin, wave, float",
    )
    parser.add_argument(
        "--imessage-publish",
        action="store_true",
        help="Build & submit iMessage sticker app to App Store via Fastlane",
    )
    parser.add_argument(
        "--imessage-dry-run",
        action="store_true",
        help="iMessage publish dry run (prepare everything but skip Fastlane)",
    )
    parser.add_argument(
        "--imessage-skip-submit",
        action="store_true",
        help="iMessage publish: build & upload but skip App Store submission",
    )
    parser.add_argument(
        "--whatsapp-native",
        action="store_true",
        help="Export stickers for WhatsApp native Android app (512x512 WebP)",
    )
    parser.add_argument(
        "--whatsapp-server-url",
        type=str,
        default=None,
        help="WhatsApp sticker server URL to push packs to (e.g. http://localhost:8080)",
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
        engine_label = (
            "ComfyUI (local, free)" if args.engine == "comfyui" else "DALL-E 3 (cloud)"
        )
        print(f"STAGE 1: Generating sticker images via {engine_label}")
        print(f"{'=' * 60}")
        quality = "standard" if args.standard else "hd"
        stage_generate(config, quality=quality, engine=args.engine, seed=args.seed)

    if args.generate_only:
        print("\n--generate-only: Stopping after generation.")
        return

    # Stage 2: Process
    print(f"\n{'=' * 60}")
    print("STAGE 2: Processing images")
    print(f"{'=' * 60}")
    stage_process(config, input_dir=args.input, skip_bg=args.skip_bg)

    # Stage 2b: Animated/video conversion (optional)
    if args.telegram_animated or args.telegram_video:
        print(f"\n{'=' * 60}")
        print("STAGE 2b: Creating animated/video sticker variants")
        print(f"{'=' * 60}")
        formats = []
        if args.telegram_animated:
            formats.append("tgs")
        if args.telegram_video:
            formats.append("webm")
        stage_process_animated(
            config, formats=formats, animation_type=args.animation_preset
        )

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

    # Stage 6b: Telegram Animated (optional)
    if args.telegram_animated:
        print(f"\n{'=' * 60}")
        print("STAGE 6b: Publishing animated stickers to Telegram (TGS)")
        print(f"{'=' * 60}")
        stage_telegram_animated(config, sticker_format="animated")

    # Stage 6c: Telegram Video (optional)
    if args.telegram_video:
        print(f"\n{'=' * 60}")
        print("STAGE 6c: Publishing video stickers to Telegram (WebM)")
        print(f"{'=' * 60}")
        stage_telegram_animated(config, sticker_format="video")

    # Stage 7: iMessage (optional)
    if args.imessage:
        print(f"\n{'=' * 60}")
        print("STAGE 7: Preparing iMessage Xcode project")
        print(f"{'=' * 60}")
        stage_imessage(config)

    # Stage 8: iMessage Publish (optional)
    if args.imessage_publish:
        print(f"\n{'=' * 60}")
        print("STAGE 8: Building & submitting iMessage app to App Store")
        print(f"{'=' * 60}")
        stage_imessage_publish(
            config,
            dry_run=args.imessage_dry_run,
            skip_submit=args.imessage_skip_submit,
        )

    # Stage 9: WhatsApp Native Export (optional)
    if args.whatsapp_native:
        print(f"\n{'=' * 60}")
        print("STAGE 9: Exporting stickers for WhatsApp native app")
        print(f"{'=' * 60}")
        stage_whatsapp_export(config, server_url=args.whatsapp_server_url)

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
    if args.telegram_animated:
        print(f"  │   ├── telegram_animated/   - TGS animated stickers")
    if args.telegram_video:
        print(f"  │   ├── telegram_video/      - WebM video stickers")
    if args.whatsapp_native:
        print(f"  │   ├── whatsapp_native/     - WhatsApp 512x512 WebP stickers")
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
    if not args.telegram_animated:
        print("  4. Animated Telegram: python run_pipeline.py --telegram-animated")
    if not args.telegram_video:
        print("  5. Video Telegram: python run_pipeline.py --telegram-video")
    if not args.imessage:
        print("  6. iMessage project: python run_pipeline.py --imessage")
    if not args.imessage_publish:
        print("  7. iMessage App Store: python run_pipeline.py --imessage-publish")
    if not args.whatsapp_native:
        print("  8. WhatsApp native:   python run_pipeline.py --whatsapp-native")
    print()


if __name__ == "__main__":
    main()
