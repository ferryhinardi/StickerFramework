#!/usr/bin/env python3
"""
Sticker.ly Uploader — Automated publishing via Android emulator.

Uses uiautomator2 to drive the Sticker.ly app on an Android emulator,
creating WhatsApp sticker packs and publishing them automatically.

First run requires --headful for manual Google login.
Subsequent runs work headless using saved AVD snapshots.

Usage:
    # First run: show emulator GUI for login
    python stickerly_uploader.py \\
        --pack-dir packs/chubby-mochi-panda/final/whatsapp \\
        --headful --dry-run

    # Automated headless upload
    python stickerly_uploader.py \\
        --pack-dir packs/chubby-mochi-panda/final/whatsapp

    # Batch mode: upload all packs with final/whatsapp/ directories
    python stickerly_uploader.py --batch

    # Resume interrupted upload
    python stickerly_uploader.py --resume

    # Just setup login (no upload)
    python stickerly_uploader.py --setup-only --headful
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

# Ensure sibling scripts and repo root are importable
_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from automation.stickerly import (
    EmulatorManager,
    StickerlyAuth,
    StickerlyCreatePack,
    StickerlyPublish,
    StickerlySetMetadata,
)
from automation.stickerly.config import (
    DEFAULT_AVD_NAME,
    PUBLISHED_PACKS_PATH,
    SESSION_STATE_DIR,
    TAG_TEMPLATES,
)
from automation.stickerly.utils import (
    SessionExpired,
    human_delay,
    load_progress,
    save_progress,
)

# Pipeline steps
STEPS = ["push_files", "create_pack", "set_metadata", "publish"]


# -- Pack config loading -------------------------------------------------------


def _load_pack_config(config_path: str) -> dict:
    """Dynamically import PACK_CONFIG from a pack_config.py file."""
    p = Path(config_path).resolve()
    if not p.exists():
        print(f"ERROR: Pack config not found: {p}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("pack_config_dyn", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PACK_CONFIG


def _find_pack_config(pack_dir: Path) -> Path | None:
    """Walk up from pack_dir to find a pack_config.py."""
    current = pack_dir.resolve()
    for _ in range(5):  # Max 5 levels up
        candidate = current / "pack_config.py"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


def _detect_character_type(config: dict) -> str | None:
    """Infer character type from pack config for tag generation."""
    character = config.get("character", {})
    species = character.get("species", "").lower()
    name = character.get("name", "").lower()

    for key in TAG_TEMPLATES:
        if key in species or key in name:
            return key
    return None


# -- Pack discovery for batch mode ---------------------------------------------


def _discover_packs() -> list[dict]:
    """Find all packs with final/whatsapp/ directories."""
    packs_dir = _REPO_ROOT / "packs"
    found = []

    for pack_path in sorted(packs_dir.iterdir()):
        if not pack_path.is_dir():
            continue
        whatsapp_dir = pack_path / "final" / "whatsapp"
        if not whatsapp_dir.exists():
            continue

        webp_files = sorted(whatsapp_dir.glob("*.webp"))
        sticker_files = [f for f in webp_files if f.name != "tray_icon.webp"]
        if len(sticker_files) < 3:
            continue  # WhatsApp minimum is 3 stickers

        config_path = _find_pack_config(whatsapp_dir)
        pack_info = {
            "pack_id": pack_path.name,
            "pack_dir": str(whatsapp_dir),
            "config_path": str(config_path) if config_path else None,
            "sticker_count": len(sticker_files),
        }
        found.append(pack_info)

    return found


# -- Single pack upload pipeline -----------------------------------------------


def upload_pack(
    emulator: EmulatorManager,
    device,
    pack_dir: str,
    pack_config: dict | None,
    pack_id: str,
    dry_run: bool = False,
    resume_from: dict | None = None,
) -> dict:
    """
    Run the full upload pipeline for a single pack.

    Returns:
        Progress dict with completed steps and share link.
    """
    pack_dir = Path(pack_dir)

    # Determine sticker files (exclude tray icon)
    webp_files = sorted(pack_dir.glob("*.webp"))
    sticker_files = [f for f in webp_files if f.name != "tray_icon.webp"]
    has_tray = (pack_dir / "tray_icon.webp").exists()

    if len(sticker_files) < 3:
        print(f"  ERROR: Pack has {len(sticker_files)} stickers (minimum 3).")
        return {"error": "Too few stickers"}

    # Initialize progress
    progress = resume_from or {
        "pack_id": pack_id,
        "pack_dir": str(pack_dir),
        "completed_steps": [],
        "pending_steps": list(STEPS),
        "share_link": None,
    }

    completed = progress["completed_steps"]

    # Derive metadata from config
    pack_name = pack_id.replace("-", " ").title()
    publisher = None
    character_type = None
    custom_tags = None

    if pack_config:
        pack_name = pack_config.get("pack_name", pack_name)
        publisher = pack_config.get("publisher")
        character_type = _detect_character_type(pack_config)

        # Extract emotion keywords as tags
        sticker_configs = pack_config.get("stickers", [])
        if sticker_configs:
            custom_tags = [
                s.get("emotion", "").lower()
                for s in sticker_configs
                if s.get("emotion")
            ]

    print(f"\n{'=' * 60}")
    print(f"  UPLOADING: {pack_name}")
    print(f"  Pack ID: {pack_id}")
    print(f"  Stickers: {len(sticker_files)}")
    print(f"  Tray icon: {'yes' if has_tray else 'no'}")
    print(f"{'=' * 60}\n")

    # Step 1: Push files to emulator
    if "push_files" not in completed:
        print("STEP 1/4: Pushing files to emulator")
        emulator.push_stickers(pack_dir, pack_id)
        completed.append("push_files")
        progress["pending_steps"].remove("push_files")
        save_progress(progress)
    else:
        print("STEP 1/4: Push files (already done, skipping)")

    # Step 2: Create pack + add stickers
    if "create_pack" not in completed:
        print("\nSTEP 2/4: Creating pack and adding stickers")
        creator = StickerlyCreatePack(device)
        creator.create_new_pack()
        human_delay(1000, 2000)

        # Add all stickers
        added = creator.add_all_stickers(device, pack_id, sticker_files)
        if added < 3:
            print(f"  ERROR: Only {added} stickers added (minimum 3). Aborting.")
            progress["error"] = f"Only {added} stickers added"
            save_progress(progress)
            return progress

        # Set tray icon
        if has_tray:
            creator.set_tray_icon(device, pack_id)

        completed.append("create_pack")
        progress["pending_steps"].remove("create_pack")
        save_progress(progress)
    else:
        print("STEP 2/4: Create pack (already done, skipping)")

    # Step 3: Set metadata
    if "set_metadata" not in completed:
        print("\nSTEP 3/4: Setting metadata")
        meta = StickerlySetMetadata()
        meta.set_metadata(
            device,
            pack_name=pack_name,
            publisher=publisher,
            tags=custom_tags,
            character_type=character_type,
        )
        completed.append("set_metadata")
        progress["pending_steps"].remove("set_metadata")
        save_progress(progress)
    else:
        print("STEP 3/4: Set metadata (already done, skipping)")

    # Step 4: Publish
    if "publish" not in completed:
        print("\nSTEP 4/4: Publishing")
        pub = StickerlyPublish()
        share_link = pub.publish(device, pack_id, dry_run=dry_run)
        progress["share_link"] = share_link
        completed.append("publish")
        progress["pending_steps"].remove("publish")
        save_progress(progress)
    else:
        print("STEP 4/4: Publish (already done, skipping)")

    return progress


# -- Main entry point ----------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Sticker.ly Uploader — Automated publishing via Android emulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--pack-dir",
        help="Path to the pack's final/whatsapp/ directory",
    )
    parser.add_argument(
        "--pack-config",
        help="Path to pack_config.py (auto-detected if omitted)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Upload all packs with final/whatsapp/ directories",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Show emulator GUI (required for first-time login)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run everything except the final publish tap",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last saved progress",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only set up login (no pack upload)",
    )
    parser.add_argument(
        "--avd",
        default=DEFAULT_AVD_NAME,
        help=f"AVD name (default: {DEFAULT_AVD_NAME})",
    )
    parser.add_argument(
        "--no-stop",
        action="store_true",
        help="Don't stop emulator after upload (useful for debugging)",
    )

    args = parser.parse_args()

    # Validate args
    if not args.batch and not args.pack_dir and not args.setup_only and not args.resume:
        parser.error("Provide --pack-dir, --batch, --setup-only, or --resume")

    # Initialize emulator manager
    emulator = EmulatorManager(avd_name=args.avd)
    auth = StickerlyAuth(emulator)
    device = None

    try:
        # -- Authentication ------------------------------------------------
        if args.headful or args.setup_only:
            device = auth.setup_first_run()
            if args.setup_only:
                print("\n  Setup complete! You can now run without --headful.")
                return
        else:
            try:
                device = auth.restore_session()
            except SessionExpired as exc:
                print(f"\n  {exc}")
                print("  Run with --headful for first-time login.")
                sys.exit(1)

        # -- Resume mode ---------------------------------------------------
        if args.resume:
            progress = load_progress()
            if not progress:
                print("  No saved progress found.")
                sys.exit(1)
            print(f"  Resuming upload for: {progress['pack_id']}")
            pack_dir = progress["pack_dir"]
            config_path = _find_pack_config(Path(pack_dir))
            pack_config = _load_pack_config(str(config_path)) if config_path else None
            result = upload_pack(
                emulator,
                device,
                pack_dir,
                pack_config,
                progress["pack_id"],
                args.dry_run,
                resume_from=progress,
            )
            _print_result(result)
            return

        # -- Batch mode ----------------------------------------------------
        if args.batch:
            packs = _discover_packs()
            if not packs:
                print("  No packs found with final/whatsapp/ directories.")
                sys.exit(1)

            # Check for already-published packs
            published = _load_published()

            print(f"\n  Found {len(packs)} packs to upload:")
            for p in packs:
                status = "PUBLISHED" if p["pack_id"] in published else "pending"
                print(
                    f"    - {p['pack_id']} ({p['sticker_count']} stickers) [{status}]"
                )

            results = []
            for pack_info in packs:
                if pack_info["pack_id"] in published:
                    print(f"\n  Skipping {pack_info['pack_id']} (already published)")
                    continue

                config_path = pack_info.get("config_path")
                pack_config = _load_pack_config(config_path) if config_path else None
                result = upload_pack(
                    emulator,
                    device,
                    pack_info["pack_dir"],
                    pack_config,
                    pack_info["pack_id"],
                    args.dry_run,
                )
                results.append(result)
                human_delay(3000, 5000)  # Brief pause between packs

            print("\n" + "=" * 60)
            print("  BATCH UPLOAD COMPLETE")
            print("=" * 60)
            for r in results:
                _print_result(r)
            return

        # -- Single pack mode ----------------------------------------------
        pack_dir = Path(args.pack_dir).resolve()
        if not pack_dir.exists():
            print(f"  ERROR: Directory not found: {pack_dir}")
            sys.exit(1)

        # Find pack config
        if args.pack_config:
            pack_config = _load_pack_config(args.pack_config)
        else:
            config_path = _find_pack_config(pack_dir)
            pack_config = _load_pack_config(str(config_path)) if config_path else None

        # Derive pack_id from directory structure
        pack_id = pack_dir.parent.parent.name  # packs/<pack_id>/final/whatsapp

        result = upload_pack(
            emulator,
            device,
            str(pack_dir),
            pack_config,
            pack_id,
            args.dry_run,
        )
        _print_result(result)

    except KeyboardInterrupt:
        print("\n  Interrupted by user.")
    except Exception as exc:
        print(f"\n  ERROR: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        if not args.no_stop and not args.headful:
            emulator.stop()


# -- Helpers -------------------------------------------------------------------


def _print_result(result: dict) -> None:
    """Print upload result summary."""
    pack_id = result.get("pack_id", "unknown")
    completed = result.get("completed_steps", [])
    share_link = result.get("share_link")
    error = result.get("error")

    if error:
        print(f"  {pack_id}: FAILED - {error}")
    elif "publish" in completed:
        link_str = f" -> {share_link}" if share_link else ""
        print(f"  {pack_id}: PUBLISHED{link_str}")
    else:
        print(f"  {pack_id}: PARTIAL ({len(completed)}/{len(STEPS)} steps)")


def _load_published() -> dict:
    """Load published packs log."""
    if PUBLISHED_PACKS_PATH.exists():
        return json.loads(PUBLISHED_PACKS_PATH.read_text())
    return {}


if __name__ == "__main__":
    main()
