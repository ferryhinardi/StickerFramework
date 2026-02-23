#!/usr/bin/env python3
"""
E2E test: Upload images to existing draft using the real automation modules.

Tests LineStickerUpload against draft 43200641 with chubby-mochi-cat pack.
"""

import asyncio
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from playwright.async_api import async_playwright

from automation.config import SESSION_STATE_PATH, SCREENSHOT_DIR
from automation.line_auth import LineAuth
from automation.line_upload_images import LineStickerUpload
from automation.line_set_price import LinePriceTier
from automation.line_submit import LineSubmit

STICKER_ID = "43200641"
PACK_DIR = REPO_ROOT / "packs" / "chubby-mochi-cat" / "final"


async def main():
    print("=" * 60)
    print("  E2E Test — Image Upload + Price + Submit (dry-run)")
    print(f"  Sticker ID: {STICKER_ID}")
    print(f"  Pack: {PACK_DIR}")
    print("=" * 60)

    # Verify pack files
    line_dir = PACK_DIR / "line"
    stickers = sorted(line_dir.glob("*.png"))
    main_img = list((PACK_DIR / "line_main").glob("*.png"))
    tab_img = list((PACK_DIR / "line_tab").glob("*.png"))
    print(f"\n  Stickers: {len(stickers)} ({', '.join(s.name for s in stickers)})")
    print(f"  Main: {main_img[0].name if main_img else 'MISSING'}")
    print(f"  Tab: {tab_img[0].name if tab_img else 'MISSING'}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)

        # Restore session
        auth = LineAuth()
        try:
            context = await auth.restore_session(browser)
        except Exception as e:
            print(f"ERROR: {e}")
            await browser.close()
            return

        page = await context.new_page()

        try:
            # ── Step 1: Upload images ──
            print(f"\n{'=' * 60}")
            print("  STEP 1: Upload sticker images")
            print(f"{'=' * 60}\n")

            uploader = LineStickerUpload()

            # First, delete all existing images from previous test run
            print("  Deleting existing images first...")
            from automation.config import (
                sticker_image_url,
                SEL_DELETE_ALL,
                SEL_CONFIRM_OK,
                SEL_CONFIRM_OK_FALLBACK,
                SEL_CAMPAIGN_POPUP_CLOSE,
            )

            await page.goto(sticker_image_url(STICKER_ID), wait_until="networkidle")
            await asyncio.sleep(2)
            # Close popup
            try:
                popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
                if await popup.count() > 0 and await popup.first.is_visible():
                    await popup.first.click(timeout=3_000)
                    await asyncio.sleep(1)
            except Exception:
                pass
            # Click Delete All
            try:
                delete_all = page.locator(SEL_DELETE_ALL)
                if await delete_all.count() > 0 and await delete_all.first.is_visible():
                    await delete_all.first.click()
                    await asyncio.sleep(1)
                    # Confirm delete dialog
                    try:
                        await page.locator(SEL_CONFIRM_OK).click(timeout=5_000)
                    except Exception:
                        try:
                            await page.locator(SEL_CONFIRM_OK_FALLBACK).click(
                                timeout=3_000
                            )
                        except Exception:
                            pass
                    await asyncio.sleep(2)
                    print("  Deleted all existing images.")
            except Exception as e:
                print(f"  No images to delete or delete failed: {e}")

            # Now upload
            await uploader.upload_all(page, STICKER_ID, str(PACK_DIR))

            # Capture result
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            await page.screenshot(
                path=str(SCREENSHOT_DIR / "e2e_01_after_upload.png"),
                full_page=True,
            )
            print("\n  Upload step complete!")

            # Wait to observe
            await asyncio.sleep(3)

            # ── Step 2: Set price tier ──
            print(f"\n{'=' * 60}")
            print("  STEP 2: Set price tier (Rp23.000+)")
            print(f"{'=' * 60}\n")

            pricer = LinePriceTier()
            await pricer.set_price(page, STICKER_ID, "23000")

            await page.screenshot(
                path=str(SCREENSHOT_DIR / "e2e_02_after_price.png"),
                full_page=True,
            )
            print("\n  Price step complete!")

            await asyncio.sleep(3)

            # ── Step 3: Submit (DRY RUN) ──
            print(f"\n{'=' * 60}")
            print("  STEP 3: Submit (DRY RUN)")
            print(f"{'=' * 60}\n")

            submitter = LineSubmit()
            await submitter.submit(page, STICKER_ID, dry_run=True)

            print("\n  Submit dry-run complete!")

            # ── Summary ──
            print(f"\n{'=' * 60}")
            print("  E2E TEST COMPLETE")
            print(f"{'=' * 60}")
            print(f"  Screenshots in: {SCREENSHOT_DIR}")

            print("\n  Browser staying open 15s for inspection...")
            await asyncio.sleep(15)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            try:
                await page.screenshot(
                    path=str(SCREENSHOT_DIR / "e2e_99_error.png"),
                    full_page=True,
                )
            except Exception:
                pass
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
