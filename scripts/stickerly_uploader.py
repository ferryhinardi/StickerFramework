#!/usr/bin/env python3
"""
Sticker.ly Uploader — Automated publishing via Android emulator.

Uses uiautomator2 to drive the Sticker.ly app on an Android emulator,
creating WhatsApp sticker packs and publishing them automatically.

First run requires --headful for manual Google login.
Subsequent runs work headless using saved AVD snapshots.

Actual flow (verified):
1. Push sticker images to emulator via ADB
2. Media-scan so gallery picks them up
3. Create pack (Profile -> New Pack -> Regular -> name -> Create)
4. Add stickers (Add sticker -> multi-select -> Next -> Save to pack + tags)
5. Capture share link (pack is public immediately on creation)

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
    REMOTE_STICKER_DIR,
)
from automation.stickerly.utils import (
    SessionExpired,
    adb_shell,
    human_delay,
    load_progress,
    media_scan,
    save_progress,
)

# Pipeline steps (simplified from old 4-step to actual flow)
STEPS = ["push_files", "create_pack", "add_stickers", "capture_link"]


# -- Pack config loading -------------------------------------------------------


def _load_pack_config(config_path: str) -> dict:
    """Dynamically import PACK_CONFIG from a pack_config.py file."""
    p = Path(config_path).resolve()
    if not p.exists():
        print(f"ERROR: Pack config not found: {p}")
        sys.exit(1)
    spec = importlib.util.spec_from_file_location("pack_config_dyn", p)
    mod = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(mod)  # type: ignore
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


# -- Push files to emulator ----------------------------------------------------


def push_sticker_files(pack_dir: Path, pack_id: str) -> list[Path]:
    """
    Push sticker PNG/WEBP files to emulator and trigger media scan.

    Returns the list of sticker files (excluding tray icon).
    """
    webp_files = sorted(pack_dir.glob("*.webp"))
    sticker_files = [f for f in webp_files if f.name != "tray_icon.webp"]

    if not sticker_files:
        # Also check for PNG files
        png_files = sorted(pack_dir.glob("*.png"))
        sticker_files = [f for f in png_files if "tray" not in f.name.lower()]

    if not sticker_files:
        print(f"  ERROR: No sticker files found in {pack_dir}")
        return []

    remote_dir = f"{REMOTE_STICKER_DIR}/{pack_id}"

    # Create remote directory
    adb_shell(f"mkdir -p {remote_dir}")

    # Push each file
    print(f"  Pushing {len(sticker_files)} sticker files...")
    from automation.stickerly.utils import adb_push

    for f in sticker_files:
        remote_path = f"{remote_dir}/{f.name}"
        adb_push(str(f), remote_path)

    # Trigger media scan so gallery picks up the files
    print("  Triggering media scan...")
    media_scan(remote_dir)
    # Also scan individual files for reliability
    for f in sticker_files:
        media_scan(f"{remote_dir}/{f.name}")
    human_delay(2000, 3000)  # Wait for media scanner

    print(f"  Pushed {len(sticker_files)} files to {remote_dir}")
    return sticker_files


# -- Single pack upload pipeline -----------------------------------------------


def upload_pack(
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
    pack_path = Path(pack_dir)

    # Determine sticker files
    webp_files = sorted(pack_path.glob("*.webp"))
    sticker_files = [f for f in webp_files if f.name != "tray_icon.webp"]

    if len(sticker_files) < 3:
        print(f"  ERROR: Pack has {len(sticker_files)} stickers (minimum 3).")
        return {"pack_id": pack_id, "error": "Too few stickers"}

    # Initialize progress
    progress = resume_from or {
        "pack_id": pack_id,
        "pack_dir": str(pack_path),
        "completed_steps": [],
        "pending_steps": list(STEPS),
        "pack_code": None,
        "share_link": None,
    }

    completed = progress["completed_steps"]

    # Derive metadata
    meta_builder = StickerlySetMetadata()
    pack_name = pack_id.replace("-", " ").title()
    character_type = meta_builder.detect_character_type(pack_id)
    custom_tags = None

    if pack_config:
        pack_name = pack_config.get("pack_name", pack_name)
        sticker_configs = pack_config.get("stickers", [])
        if sticker_configs:
            custom_tags = list(
                {
                    s.get("emotion", "").lower()
                    for s in sticker_configs
                    if s.get("emotion")
                }
            )

    tags_str = meta_builder.build_tags(
        custom_tags=custom_tags,
        character_type=character_type,
        pack_name=pack_name,
    )

    print(f"\n{'=' * 60}")
    print(f"  UPLOADING: {pack_name}")
    print(f"  Pack ID: {pack_id}")
    print(f"  Stickers: {len(sticker_files)}")
    print(f"  Tags: {tags_str[:60]}...")
    print(f"{'=' * 60}\n")

    # Step 1: Push files to emulator
    if "push_files" not in completed:
        print("STEP 1/4: Pushing files to emulator")
        pushed = push_sticker_files(pack_path, pack_id)
        if not pushed:
            progress["error"] = "No files pushed"
            save_progress(progress)
            return progress
        completed.append("push_files")
        if "push_files" in progress["pending_steps"]:
            progress["pending_steps"].remove("push_files")
        save_progress(progress)
    else:
        print("STEP 1/4: Push files (already done, skipping)")

    # Step 2: Create pack
    if "create_pack" not in completed:
        print("\nSTEP 2/4: Creating pack")
        creator = StickerlyCreatePack(device)
        pack_code = creator.create_pack(pack_name)
        progress["pack_code"] = pack_code
        completed.append("create_pack")
        if "create_pack" in progress["pending_steps"]:
            progress["pending_steps"].remove("create_pack")
        save_progress(progress)
    else:
        print("STEP 2/4: Create pack (already done, skipping)")

    # Step 3: Add stickers via gallery multi-select
    if "add_stickers" not in completed:
        print("\nSTEP 3/4: Adding stickers via gallery")
        creator = StickerlyCreatePack(device)
        added = creator.add_stickers_to_pack(
            pack_name=pack_name,
            pack_id=pack_id,
            sticker_files=sticker_files,
            tags=tags_str,
        )
        if added < 3:
            print(f"  ERROR: Only {added} stickers added (minimum 3). Aborting.")
            progress["error"] = f"Only {added} stickers added"
            save_progress(progress)
            return progress
        completed.append("add_stickers")
        if "add_stickers" in progress["pending_steps"]:
            progress["pending_steps"].remove("add_stickers")
        save_progress(progress)
    else:
        print("STEP 3/4: Add stickers (already done, skipping)")

    # Step 4: Capture share link
    if "capture_link" not in completed:
        print("\nSTEP 4/4: Capturing share link")
        pub = StickerlyPublish()
        result = pub.capture_share_link(
            device,
            pack_id,
            sticker_count=len(sticker_files),
            dry_run=dry_run,
        )
        progress["pack_code"] = result.get("pack_code") or progress.get("pack_code")
        progress["share_link"] = result.get("share_link")
        completed.append("capture_link")
        if "capture_link" in progress["pending_steps"]:
            progress["pending_steps"].remove("capture_link")
        save_progress(progress)
    else:
        print("STEP 4/4: Capture link (already done, skipping)")

    return progress


# -- Main entry point ----------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Sticker.ly Uploader — Automated publishing via Android emulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
        help="Run everything except share link capture",
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
    pack_code = result.get("pack_code")
    error = result.get("error")

    if error:
        print(f"  {pack_id}: FAILED - {error}")
    elif "capture_link" in completed:
        link_str = f" -> {share_link}" if share_link else ""
        code_str = f" (code: {pack_code})" if pack_code else ""
        print(f"  {pack_id}: PUBLISHED{code_str}{link_str}")
    else:
        print(f"  {pack_id}: PARTIAL ({len(completed)}/{len(STEPS)} steps)")


def _load_published() -> dict:
    """Load published packs log."""
    if PUBLISHED_PACKS_PATH.exists():
        return json.loads(PUBLISHED_PACKS_PATH.read_text())
    return {}


if __name__ == "__main__":
    main()
