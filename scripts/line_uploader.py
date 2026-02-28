#!/usr/bin/env python3
"""
LINE Creator Market Uploader — CLI entry point.

Orchestrates the full Playwright automation pipeline:
    1. Authenticate (restore session or interactive login)
    2. Create a new sticker submission (fills all display info)
    3. Upload images (main + tab + sticker PNGs)
    4. Set Price Tier
    5. Fill Tag Settings (emoji tags per sticker)
    6. Submit for review (optional, requires --submit)

Usage:
    # First run — headful so you can log in manually:
    python scripts/line_uploader.py \\
        --pack-dir packs/chubby-mochi-cat/final \\
        --title "Chubby Mochi Cat" \\
        --description "A cute chubby mochi cat sticker set" \\
        --headful --dry-run

    # After session is saved, run headless:
    python scripts/line_uploader.py \\
        --pack-dir packs/boba-milo-5/final \\
        --title "Boba & Milo Cheerful Otter Duo 5" \\
        --description "A fun, caring otter duo for everyday chat" \\
        --submit

    # Resume from last saved progress:
    python scripts/line_uploader.py --resume --headful
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path
import os

# Ensure automation package is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from automation.config import DEFAULTS, PAGE_LOAD_TIMEOUT
from automation.line_auth import LineAuth
from automation.line_create_submission import LineCreateSubmission
from automation.line_set_metadata import LineSetMetadata
from automation.line_set_price import LinePriceTier
from automation.line_submit import LineSubmit
from automation.line_upload_images import LineStickerUpload
from automation.utils import (
    SessionNotFound,
    load_progress,
    save_progress,
)
from scripts.line_preflight_check import (
    CheckResult,
    check_metadata_file,
    check_sticker_filenames,
    check_title_description,
    check_theme,
)


# ─── Pre-flight check ───────────────────────────────────────────────────────


def run_preflight_gate(
    pack_dir: Path, title: str | None, description: str | None
) -> bool:
    """Run LINE pre-flight checks before upload. Returns True if safe to proceed."""
    print(f"\n{'=' * 60}")
    print("  LINE PRE-FLIGHT CONTENT CHECK")
    print(f"{'=' * 60}\n")

    result = CheckResult()

    # Check pack metadata
    # pack_dir is typically packs/<name>/final, go up one level for metadata
    pack_root = pack_dir.parent if pack_dir.name == "final" else pack_dir
    metadata = check_metadata_file(pack_root, result)

    # Check sticker filenames
    check_sticker_filenames(pack_root, result)

    # Check CLI-provided title/description
    check_title_description(title, description, result)

    # Check theme from metadata
    if metadata:
        check_theme(metadata, result)

    for msg in result.info:
        print(f"  INFO: {msg}")
    if result.errors:
        for msg in result.errors:
            print(f"  FAIL: {msg}")
    if result.warnings:
        for msg in result.warnings:
            print(f"  WARN: {msg}")

    if not result.passed:
        print(
            f"\n  BLOCKED: Pack failed pre-flight check ({len(result.errors)} error(s))"
        )
        print(
            "  This pack will be rejected by LINE under guideline 3.13 (religious content)."
        )
        print("  Use --skip-preflight to bypass this check.\n")
        return False

    print("  Pre-flight check PASSED\n")
    return True


# ─── Step runner ─────────────────────────────────────────────────────────────

STEPS = [
    "create_submission",
    "upload_images",
    "set_price",
    "fill_tag_settings",
    "submit",
]


def _save(progress: dict) -> None:
    """Persist progress to disk."""
    progress["timestamp"] = datetime.now().isoformat()
    save_progress(progress)


async def run_pipeline(args: argparse.Namespace) -> None:
    """Execute the full upload pipeline."""
    from playwright.async_api import async_playwright

    headless = not args.headful

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            slow_mo=200 if not headless else 0,
        )

        # ── Authentication ───────────────────────────────────────────
        auth = LineAuth()
        line_email = os.environ.get("LINE_EMAIL", "")
        line_password = os.environ.get("LINE_PASSWORD", "")

        try:
            context = await auth.restore_session(browser)
            page = await context.new_page()
            await auth.ensure_authenticated(
                page, email=line_email, password=line_password
            )
            print("Session restored and valid.")
        except SessionNotFound:
            if headless:
                print(
                    "ERROR: No saved session. Run with --headful first to "
                    "log in interactively."
                )
                await browser.close()
                return
            context = await browser.new_context()
            page = await context.new_page()
            await auth.login(page, email=line_email, password=line_password)

        page.set_default_timeout(PAGE_LOAD_TIMEOUT)

        # ── Resume or fresh start ────────────────────────────────────
        progress: dict | None = None
        if args.resume:
            progress = load_progress()
            if progress:
                print(f"Resuming from: {progress.get('completed_steps', [])}")
            else:
                print("No saved progress — starting fresh.")

        completed: list[str] = progress.get("completed_steps", []) if progress else []
        sticker_id: str | None = progress.get("sticker_id") if progress else None
        pack_dir = (
            Path(progress["pack_dir"])
            if progress and progress.get("pack_dir")
            else Path(args.pack_dir)
            if args.pack_dir
            else None
        )

        # ── Determine sticker names for tag settings ─────────────────
        sticker_names: list[str] = []
        if pack_dir:
            line_dir = pack_dir / "line"
            if line_dir.exists():
                sticker_names = [p.stem for p in sorted(line_dir.glob("*.png"))]

        # ── Step 1: Create submission ────────────────────────────────
        if "create_submission" not in completed:
            print(f"\n{'=' * 60}")
            print("STEP 1: Creating sticker submission")
            print(f"{'=' * 60}")

            creator = LineCreateSubmission()
            result = await creator.create(
                page,
                {
                    "title": args.title,
                    "description": args.description or "",
                    "copyright": args.copyright,
                    "ai_used": True,
                    "style_category": args.style_category,
                    "character_category": args.character_category,
                    "sale_region": args.sale_region,
                    "auto_release": True,
                    "sticker_type": "static",
                },
            )
            sticker_id = result["sticker_id"]
            completed.append("create_submission")
            _save(
                {
                    "sticker_id": sticker_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                    "title": args.title,
                }
            )

        if not sticker_id:
            print("ERROR: No sticker ID — cannot continue.")
            await browser.close()
            return

        # ── Step 2: Upload images ────────────────────────────────────
        if "upload_images" not in completed and pack_dir:
            print(f"\n{'=' * 60}")
            print("STEP 2: Uploading sticker images")
            print(f"{'=' * 60}")

            uploader = LineStickerUpload()
            await uploader.upload_all(page, sticker_id, str(pack_dir))
            completed.append("upload_images")
            _save(
                {
                    "sticker_id": sticker_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                }
            )

        # ── Step 3: Set Price Tier ───────────────────────────────────
        if "set_price" not in completed:
            print(f"\n{'=' * 60}")
            print("STEP 3: Setting price tier")
            print(f"{'=' * 60}")

            pricer = LinePriceTier()
            await pricer.set_price(page, sticker_id, args.price_tier)
            completed.append("set_price")
            _save(
                {
                    "sticker_id": sticker_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                }
            )

        # ── Step 4: Tag Settings ─────────────────────────────────────
        if "fill_tag_settings" not in completed and sticker_names:
            print(f"\n{'=' * 60}")
            print("STEP 4: Filling tag settings")
            print(f"{'=' * 60}")

            metadata = LineSetMetadata()
            await metadata.fill_tag_settings(page, sticker_id, sticker_names)
            completed.append("fill_tag_settings")
            _save(
                {
                    "sticker_id": sticker_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                }
            )

        # ── Step 5: Submit ───────────────────────────────────────────
        if "submit" not in completed:
            print(f"\n{'=' * 60}")
            print("STEP 5: Final submission")
            print(f"{'=' * 60}")

            submitter = LineSubmit()
            dry_run = not args.submit
            await submitter.submit(page, sticker_id, dry_run=dry_run)
            if not dry_run:
                completed.append("submit")
                _save(
                    {
                        "sticker_id": sticker_id,
                        "completed_steps": completed,
                        "pending_steps": [],
                        "pack_dir": str(pack_dir) if pack_dir else None,
                    }
                )

        # ── Summary ──────────────────────────────────────────────────
        from automation.config import sticker_url

        print(f"\n{'=' * 60}")
        print("  UPLOAD PIPELINE COMPLETE")
        print(f"{'=' * 60}")
        print(f"  Sticker ID:  {sticker_id}")
        print(f"  URL:         {sticker_url(sticker_id)}")
        print(f"  Completed:   {', '.join(completed)}")
        if not args.submit:
            print(
                "\n  NOTE: --submit was not set. "
                "Run again with --submit to request review."
            )
        print()

        await browser.close()


# ─── CLI ─────────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upload sticker pack to LINE Creator Market via Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time login (headful, dry-run):
  python scripts/line_uploader.py \\
      --pack-dir packs/chubby-mochi-cat/final \\
      --title "Chubby Mochi Cat" \\
      --description "A cute chubby mochi cat sticker set" \\
      --headful --dry-run

  # Upload and submit:
  python scripts/line_uploader.py \\
      --pack-dir packs/boba-milo-5/final \\
      --title "Boba & Milo 5" \\
      --description "Fun otter duo for everyday chat" \\
      --submit

  # Resume from last progress:
  python scripts/line_uploader.py --resume --headful
""",
    )
    parser.add_argument(
        "--pack-dir",
        type=str,
        help="Path to final/ dir (containing line/, line_main/, line_tab/)",
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Sticker pack title (max 40 chars)",
    )
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Sticker description (max 160 chars)",
    )
    parser.add_argument(
        "--style-category",
        type=str,
        default=DEFAULTS["style_category"],
        help=f"LINE style category (default: {DEFAULTS['style_category']})",
    )
    parser.add_argument(
        "--character-category",
        type=str,
        default=DEFAULTS["character_category"],
        help=f"LINE character category (default: {DEFAULTS['character_category']})",
    )
    parser.add_argument(
        "--sale-region",
        type=str,
        default=DEFAULTS["sale_region"],
        help=f"Sale region: all, lgbt, customized (default: {DEFAULTS['sale_region']})",
    )
    parser.add_argument(
        "--price-tier",
        type=str,
        default=DEFAULTS["price_tier"],
        help=f"Price in IDR (default: {DEFAULTS['price_tier']})",
    )
    parser.add_argument(
        "--copyright",
        type=str,
        default=DEFAULTS["copyright"],
        help=f"Copyright text (default: {DEFAULTS['copyright']})",
    )
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Show browser window (required for first login)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run pipeline but skip the final submit step",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Actually click the Request button to submit for review",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume from last saved progress state",
    )
    parser.add_argument(
        "--skip-preflight",
        action="store_true",
        help="Skip LINE content pre-flight check (not recommended)",
    )

    args = parser.parse_args()

    # Validation
    if not args.resume and not args.pack_dir:
        parser.error("--pack-dir is required (or use --resume)")
    if not args.resume and not args.title:
        parser.error("--title is required (or use --resume)")

    # Pre-flight content check (before launching browser)
    if not args.resume and not args.skip_preflight:
        pack_path = Path(args.pack_dir)
        if not pack_path.is_absolute():
            pack_path = Path(__file__).resolve().parent.parent / pack_path
        if not run_preflight_gate(pack_path, args.title, args.description):
            sys.exit(1)

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
