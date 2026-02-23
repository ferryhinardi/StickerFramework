#!/usr/bin/env python3
"""
Delete rejected LINE sticker submissions.

Navigates to the Manage Items page, finds rejected submissions by title,
and deletes them so the titles can be reused.

Usage:
    python scripts/line_delete_rejected.py --title "Boba & Milo Cheerful Otter Duo 3" --headful
    python scripts/line_delete_rejected.py --all-rejected --headful
    python scripts/line_delete_rejected.py --all-rejected --headful --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from automation.config import MY_STICKERS_URL, PAGE_LOAD_TIMEOUT
from automation.line_auth import LineAuth
from automation.utils import SessionNotFound, human_delay

# Selectors based on LINE Creator Market DOM (Feb 2026)
SEL_CARD = "article.product-info-card"
SEL_STATUS_REJECTED = "ldsg-tag.tag-error"
SEL_PRODUCT_NAME = ".product-name"
SEL_DELETE_BTN = "ldsg-button.action-button-danger"
SEL_CONFIRM_OK = (
    "button.cm-confirm-button-primary:visible, ldsg-button.button-primary:visible"
)


async def delete_rejected(args: argparse.Namespace) -> None:
    from playwright.async_api import async_playwright

    headless = not args.headful

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=headless,
            slow_mo=300 if not headless else 100,
        )

        auth = LineAuth()
        try:
            context = await auth.restore_session(browser)
            page = await context.new_page()
            await auth.ensure_authenticated(page)
            print("Session restored and valid.")
        except SessionNotFound:
            if headless:
                print("ERROR: No saved session. Run with --headful first.")
                await browser.close()
                return
            context = await browser.new_context()
            page = await context.new_page()
            await auth.login(page)

        page.set_default_timeout(PAGE_LOAD_TIMEOUT)

        # Navigate to Manage Items page
        print(f"\nNavigating to: {MY_STICKERS_URL}")
        await page.goto(MY_STICKERS_URL, wait_until="networkidle")
        await human_delay(2000, 3000)

        # Close popup if visible
        close_btn = page.locator('button:has-text("Close")')
        if await close_btn.count() > 0:
            await close_btn.first.click()
            await human_delay(1000, 1500)
            print("Closed popup dialog.")

        # Find all product cards
        cards = await page.locator(SEL_CARD).all()
        print(f"Found {len(cards)} sticker items.\n")

        # Collect rejected items
        rejected_items = []
        for card in cards:
            # Get full card text and extract name from first lines
            full_text = await card.inner_text()
            lines = [l.strip() for l in full_text.split("\n") if l.strip()]
            # Name is typically the first 1-2 lines before the price
            name_parts = []
            for line in lines:
                if line.startswith("Rp") or line in (
                    "Rejected",
                    "On Sale",
                    "Preview",
                    "Edit",
                    "Delete",
                    "Editing",
                ):
                    break
                name_parts.append(line)
            # Join and collapse whitespace (line breaks in card can split words mid-word)
            raw_name = " ".join(name_parts)
            # Remove double spaces but preserve word boundaries
            name = " ".join(raw_name.split()).strip()

            # Check if rejected
            status_el = card.locator(SEL_STATUS_REJECTED)
            is_rejected = await status_el.count() > 0

            status_label = "Rejected" if is_rejected else "On Sale/Other"
            print(f"  [{status_label}] {name}")

            if is_rejected:
                should_delete = False
                if args.all_rejected:
                    should_delete = True
                elif args.title:
                    # Normalize: remove ALL whitespace then compare
                    # This handles line-break mid-word artifacts like "Ott\ner" -> "Otter"
                    norm_name = "".join(name.split()).lower()
                    norm_title = "".join(args.title.split()).lower()
                    if norm_title in norm_name or norm_name in norm_title:
                        should_delete = True

                if should_delete:
                    rejected_items.append((name, card))

        if not rejected_items:
            print("\nNo matching rejected items to delete.")
            await browser.close()
            return

        print(f"\n{'=' * 60}")
        print(f"  Items to delete: {len(rejected_items)}")
        for name, _ in rejected_items:
            print(f"    - {name}")
        print(f"{'=' * 60}")

        if args.dry_run:
            print("\n  DRY RUN — no items were deleted.")
            await browser.close()
            return

        # Delete each rejected item
        deleted_count = 0
        for name, card in rejected_items:
            print(f"\n  Deleting: {name}")

            # Click the Delete button within this card
            delete_btn = card.locator(SEL_DELETE_BTN)
            if await delete_btn.count() > 0:
                await delete_btn.first.click()
                await human_delay(1000, 2000)

                # Handle confirmation dialog
                confirm_btn = page.locator(SEL_CONFIRM_OK)
                if await confirm_btn.count() > 0:
                    await confirm_btn.first.click()
                    await human_delay(2000, 3000)
                    deleted_count += 1
                    print(f"    DELETED successfully")
                else:
                    # Try alternate confirm selectors
                    alt_confirm = page.locator(
                        'button:has-text("OK"):visible, '
                        'button:has-text("Yes"):visible, '
                        'button:has-text("Confirm"):visible, '
                        'button:has-text("Delete"):visible'
                    )
                    if await alt_confirm.count() > 0:
                        await alt_confirm.first.click()
                        await human_delay(2000, 3000)
                        deleted_count += 1
                        print(f"    DELETED successfully (alt confirm)")
                    else:
                        screenshot_path = (
                            _REPO_ROOT
                            / "automation"
                            / "screenshots"
                            / f"delete_confirm_{deleted_count}.png"
                        )
                        await page.screenshot(path=str(screenshot_path), full_page=True)
                        print(
                            f"    FAILED: No confirm button found. Screenshot: {screenshot_path}"
                        )
            else:
                print(f"    FAILED: No delete button found in card")

            # Wait for page to update
            await human_delay(1000, 2000)

        print(f"\n{'=' * 60}")
        print(
            f"  Done. Deleted {deleted_count} of {len(rejected_items)} submission(s)."
        )
        print(f"{'=' * 60}\n")

        await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Delete rejected LINE sticker submissions"
    )
    parser.add_argument(
        "--title", type=str, help="Delete rejected submissions matching this title"
    )
    parser.add_argument(
        "--all-rejected", action="store_true", help="Delete ALL rejected submissions"
    )
    parser.add_argument("--headful", action="store_true", help="Show browser window")
    parser.add_argument(
        "--dry-run", action="store_true", help="List items without deleting"
    )

    args = parser.parse_args()
    if not args.title and not args.all_rejected:
        parser.error("--title or --all-rejected is required")

    asyncio.run(delete_rejected(args))


if __name__ == "__main__":
    main()
