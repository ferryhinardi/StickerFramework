#!/usr/bin/env python3
"""
LINE Emoji Uploader — CLI entry point.

Orchestrates the full Playwright automation pipeline for LINE Emoji:
    1. Authenticate (restore session or interactive login)
    2. Create a new emoji submission (fills all display info)
    3. Upload images (tab icon + emoji PNGs)
    4. Set Price Tier
    5. Submit for review (optional, requires --submit)

Usage:
    # First run — headful so you can log in manually:
    python scripts/line_emoji_uploader.py \\
        --pack-dir packs/chubby-mochi-hamster-emoji-1/final \\
        --title "Chubby Mochi Hamster Emoji" \\
        --description "Cute round hamster emoji for everyday chat" \\
        --headful --dry-run

    # After session is saved, run headless:
    python scripts/line_emoji_uploader.py \\
        --pack-dir packs/chubby-mochi-hamster-emoji-1/final \\
        --title "Chubby Mochi Hamster Emoji" \\
        --description "Cute round hamster emoji for everyday chat" \\
        --submit

    # Resume from last saved progress:
    python scripts/line_emoji_uploader.py --resume --headful
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Ensure automation package is importable
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from automation.config import (
    EMOJI_DEFAULTS,
    EMOJI_PROGRESS_STATE_PATH,
    PAGE_LOAD_TIMEOUT,
    emoji_url,
)
from automation.line_auth import LineAuth
from automation.line_emoji_create import LineEmojiCreate
from automation.line_emoji_price_submit import LineEmojiPrice, LineEmojiSubmit
from automation.line_emoji_upload import LineEmojiUpload
from automation.utils import SessionNotFound, human_delay


# ─── Progress persistence (emoji-specific path) ─────────────────────────────


def _save_progress(progress: dict) -> None:
    """Persist emoji progress to disk."""
    progress["timestamp"] = datetime.now().isoformat()
    EMOJI_PROGRESS_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EMOJI_PROGRESS_STATE_PATH.write_text(json.dumps(progress, indent=2, default=str))


def _load_progress() -> dict | None:
    """Load emoji progress from disk, or None."""
    if not EMOJI_PROGRESS_STATE_PATH.exists():
        return None
    return json.loads(EMOJI_PROGRESS_STATE_PATH.read_text())


# ─── Step runner ─────────────────────────────────────────────────────────────

STEPS = [
    "create_submission",
    "upload_images",
    "set_price",
    "submit",
]


async def run_pipeline(args: argparse.Namespace) -> None:
    """Execute the full emoji upload pipeline."""
    from playwright.async_api import async_playwright

    headless = not args.headful

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            slow_mo=200 if not headless else 0,
        )

        # ── Authentication ───────────────────────────────────────────
        auth = LineAuth()

        try:
            context = await auth.restore_session(browser)
            page = await context.new_page()
            await auth.ensure_authenticated(page)
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
            await auth.login(page)

        page.set_default_timeout(PAGE_LOAD_TIMEOUT)

        # ── Resume or fresh start ────────────────────────────────────
        progress: dict | None = None
        if args.resume:
            progress = _load_progress()
            if progress:
                print(f"Resuming from: {progress.get('completed_steps', [])}")
            else:
                print("No saved emoji progress — starting fresh.")

        completed: list[str] = progress.get("completed_steps", []) if progress else []
        emoji_id: str | None = progress.get("emoji_id") if progress else None
        pack_dir = (
            Path(progress["pack_dir"])
            if progress and progress.get("pack_dir")
            else Path(args.pack_dir)
            if args.pack_dir
            else None
        )

        # ── Step 1: Create emoji submission ──────────────────────────
        if "create_submission" not in completed:
            print(f"\n{'=' * 60}")
            print("STEP 1: Creating emoji submission")
            print(f"{'=' * 60}")

            creator = LineEmojiCreate()
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
                },
            )
            emoji_id = result["emoji_id"]
            completed.append("create_submission")
            _save_progress(
                {
                    "emoji_id": emoji_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                    "title": args.title,
                }
            )

        if not emoji_id:
            print("ERROR: No emoji ID — cannot continue.")
            await browser.close()
            return

        # ── Step 2: Upload images ────────────────────────────────────
        if "upload_images" not in completed and pack_dir:
            print(f"\n{'=' * 60}")
            print("STEP 2: Uploading emoji images")
            print(f"{'=' * 60}")

            uploader = LineEmojiUpload()
            await uploader.upload_all(page, emoji_id, str(pack_dir))
            completed.append("upload_images")
            _save_progress(
                {
                    "emoji_id": emoji_id,
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

            pricer = LineEmojiPrice()
            await pricer.set_price(page, emoji_id, args.price_tier)
            completed.append("set_price")
            _save_progress(
                {
                    "emoji_id": emoji_id,
                    "completed_steps": completed,
                    "pending_steps": [s for s in STEPS if s not in completed],
                    "pack_dir": str(pack_dir) if pack_dir else None,
                }
            )

        # ── Step 4: Submit ───────────────────────────────────────────
        if "submit" not in completed:
            print(f"\n{'=' * 60}")
            print("STEP 4: Final submission")
            print(f"{'=' * 60}")

            submitter = LineEmojiSubmit()
            dry_run = not args.submit
            await submitter.submit(page, emoji_id, dry_run=dry_run)
            if not dry_run:
                completed.append("submit")
                _save_progress(
                    {
                        "emoji_id": emoji_id,
                        "completed_steps": completed,
                        "pending_steps": [],
                        "pack_dir": str(pack_dir) if pack_dir else None,
                    }
                )

        # ── Summary ──────────────────────────────────────────────────
        print(f"\n{'=' * 60}")
        print("  EMOJI UPLOAD PIPELINE COMPLETE")
        print(f"{'=' * 60}")
        print(f"  Emoji ID:    {emoji_id}")
        print(f"  URL:         {emoji_url(emoji_id)}")
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
        description="Upload LINE Emoji pack via Playwright automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # First-time login (headful, dry-run):
  python scripts/line_emoji_uploader.py \\
      --pack-dir packs/chubby-mochi-hamster-emoji-1/final \\
      --title "Chubby Mochi Hamster Emoji" \\
      --description "Cute round hamster emoji for everyday chat" \\
      --headful --dry-run

  # Upload and submit:
  python scripts/line_emoji_uploader.py \\
      --pack-dir packs/chubby-mochi-hamster-emoji-1/final \\
      --title "Chubby Mochi Hamster Emoji" \\
      --description "Cute round hamster emoji for everyday chat" \\
      --submit

  # Resume from last progress:
  python scripts/line_emoji_uploader.py --resume --headful
""",
    )
    parser.add_argument(
        "--pack-dir",
        type=str,
        help="Path to final/ dir (containing line_emoji/, line_emoji_tab/)",
    )
    parser.add_argument(
        "--title",
        type=str,
        help="Emoji pack title (max 40 chars)",
    )
    parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Emoji description (max 160 chars)",
    )
    parser.add_argument(
        "--style-category",
        type=str,
        default=EMOJI_DEFAULTS["style_category"],
        help=f"LINE style category (default: {EMOJI_DEFAULTS['style_category']})",
    )
    parser.add_argument(
        "--character-category",
        type=str,
        default=EMOJI_DEFAULTS["character_category"],
        help=f"LINE character category (default: {EMOJI_DEFAULTS['character_category']})",
    )
    parser.add_argument(
        "--sale-region",
        type=str,
        default=EMOJI_DEFAULTS["sale_region"],
        help=f"Sale region: all, customized (default: {EMOJI_DEFAULTS['sale_region']})",
    )
    parser.add_argument(
        "--price-tier",
        type=str,
        default=EMOJI_DEFAULTS["price_tier"],
        help=f"Price in IDR (default: {EMOJI_DEFAULTS['price_tier']})",
    )
    parser.add_argument(
        "--copyright",
        type=str,
        default=EMOJI_DEFAULTS["copyright"],
        help=f"Copyright text (default: {EMOJI_DEFAULTS['copyright']})",
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
        help="Resume from last saved emoji progress state",
    )

    args = parser.parse_args()

    # Validation
    if not args.resume and not args.pack_dir:
        parser.error("--pack-dir is required (or use --resume)")
    if not args.resume and not args.title:
        parser.error("--title is required (or use --resume)")

    asyncio.run(run_pipeline(args))


if __name__ == "__main__":
    main()
