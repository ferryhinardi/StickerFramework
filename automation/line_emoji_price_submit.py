"""
Price Tier and final submission for LINE Emoji.

Reuses the same tab/button selectors as sticker price and submit,
but navigates to emoji management URLs.

These are thin wrappers that delegate to the existing LinePriceTier
and LineSubmit logic with emoji-specific URL routing.
"""

from __future__ import annotations

from playwright.async_api import Page

from automation.config import (
    DEFAULTS,
    EMOJI_DEFAULTS,
    EMOJI_PRICE_TIERS,
    PRICE_TIERS,
    SAVE_TIMEOUT,
    SCREENSHOT_DIR,
    SEL_CAMPAIGN_POPUP_CLOSE,
    SEL_CONFIRM_OK,
    SEL_CONFIRM_OK_FALLBACK,
    SEL_CONSENT_PART,
    SEL_PRICE_SAVE,
    SEL_PRICE_TIER,
    SEL_REQUEST_BTN,
    SEL_STATUS_BADGE,
    SEL_TAB_PRICE_TIER,
    emoji_url,
)
from automation.utils import human_delay, screenshot_on_failure


class LineEmojiPrice:
    """Sets price tier on emoji management page."""

    async def set_price(
        self,
        page: Page,
        emoji_id: str,
        tier: str | None = None,
    ) -> None:
        """
        Select a price tier and save.

        Args:
            page: Playwright Page (authenticated).
            emoji_id: LINE emoji ID.
            tier: Price tier key (e.g. "6000"). Defaults to EMOJI_DEFAULTS value.
        """
        tier = tier or EMOJI_DEFAULTS["price_tier"]

        async with screenshot_on_failure(page, "emoji_set_price"):
            # Navigate to emoji management page
            await page.goto(emoji_url(emoji_id), wait_until="commit")
            await page.wait_for_selector(SEL_TAB_PRICE_TIER, timeout=30_000)
            await human_delay(1000, 1500)
            await self._close_popup(page)

            # Click Price Tier tab
            try:
                await page.locator(SEL_TAB_PRICE_TIER).click()
                await human_delay(1000, 2000)
            except Exception:
                # Try text-based fallback
                try:
                    await page.locator(
                        'a:has-text("Price"), [role="tab"]:has-text("Price")'
                    ).first.click()
                    await human_delay(1000, 2000)
                except Exception:
                    print("  WARNING: Could not find Price Tier tab")
                    return

            # Select price from dropdown
            # Try emoji-specific tiers first, fall back to sticker tiers
            select_value = EMOJI_PRICE_TIERS.get(tier) or PRICE_TIERS.get(tier, tier)

            try:
                price_sel = page.locator(SEL_PRICE_TIER)
                if await price_sel.count() > 0:
                    await price_sel.select_option(select_value)
                else:
                    # Fallback: first select on the price tab
                    await page.locator("select >> nth=0").select_option(select_value)
                await human_delay(500, 800)
            except Exception as e:
                print(f"  WARNING: Could not set price: {e}")
                # Dump available options for debugging
                try:
                    options = await page.evaluate("""() => {
                        const sel = document.querySelector('select');
                        if (!sel) return [];
                        return Array.from(sel.options).map(o => ({value: o.value, text: o.text}));
                    }""")
                    print(f"  Available price options: {options}")
                except Exception:
                    pass
                return

            # Save
            try:
                await page.locator(SEL_PRICE_SAVE).click()
                await human_delay(500, 1000)
            except Exception:
                # Try generic save button
                try:
                    await page.locator(
                        'button:has-text("Save"), [data-test*="save"]'
                    ).first.click()
                    await human_delay(500, 1000)
                except Exception:
                    print("  WARNING: Could not find price Save button")

            # Confirm dialog
            await self._handle_confirm(page)

            try:
                formatted = f"Rp{int(tier):,}+".replace(",", ".")
            except ValueError:
                formatted = tier
            print(f"  Emoji price set to {formatted} — saved.")

    async def _handle_confirm(self, page: Page) -> None:
        try:
            await page.locator(SEL_CONFIRM_OK).click(timeout=5_000)
        except Exception:
            try:
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=3_000)
            except Exception:
                pass

    async def _close_popup(self, page: Page) -> None:
        try:
            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass


class LineEmojiSubmit:
    """Handles final review and submission of an emoji pack."""

    async def submit(
        self,
        page: Page,
        emoji_id: str,
        dry_run: bool = False,
    ) -> None:
        """
        Submit the emoji pack for review.

        Args:
            page: Playwright Page (authenticated).
            emoji_id: LINE emoji ID.
            dry_run: If True, take screenshot but do NOT click Request.
        """
        from datetime import datetime

        async with screenshot_on_failure(page, "emoji_submit"):
            await page.goto(emoji_url(emoji_id), wait_until="commit")
            await human_delay(2000, 3000)
            await self._close_popup(page)

            # Wait for status badge
            try:
                await page.locator(SEL_STATUS_BADGE).wait_for(
                    state="visible", timeout=SAVE_TIMEOUT
                )
            except Exception:
                pass

            status = await self._get_status(page)
            print(f"  Current status: {status}")

            if "review" in status.lower() or "approved" in status.lower():
                print("  Already submitted or approved — skipping.")
                return

            # Tick consent checkboxes
            await self._tick_consent(page)

            # Pre-submission screenshot
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ss_path = SCREENSHOT_DIR / f"emoji_pre_submit_{timestamp}.png"
            await page.screenshot(path=str(ss_path), full_page=True)
            print(f"  Pre-submit screenshot: {ss_path}")

            if dry_run:
                print("  DRY RUN: Would click 'Request' button. Skipping.")
                return

            # Check if Request button is enabled
            request_btn = page.locator(SEL_REQUEST_BTN)
            if await request_btn.count() == 0:
                print("  ERROR: Request button not found on page")
                return

            btn_classes = await request_btn.get_attribute("class") or ""
            if "disabled" in btn_classes:
                print(
                    "  ERROR: Request button is disabled. "
                    "Ensure all images are uploaded and consent is checked."
                )
                return

            await request_btn.click()
            await human_delay(1000, 2000)

            # Confirm dialog
            await self._handle_confirm(page)
            await human_delay(2000, 3000)

            # Verify new status
            await page.goto(emoji_url(emoji_id), wait_until="commit")
            await human_delay(2000, 3000)
            new_status = await self._get_status(page)
            print(f"  New status: {new_status}")

            if "review" in new_status.lower() or "waiting" in new_status.lower():
                print("  Emoji submission successful!")
            else:
                print(f"  WARNING: Expected 'Waiting for review', got: {new_status}")

    async def _get_status(self, page: Page) -> str:
        try:
            badge = page.locator(SEL_STATUS_BADGE)
            if await badge.count() > 0:
                return (await badge.text_content()) or "Unknown"
        except Exception:
            pass
        return "Unknown"

    async def _tick_consent(self, page: Page) -> None:
        """Tick consent checkboxes."""
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await human_delay(1000, 1500)

        try:
            ticked = await page.evaluate("""() => {
                let section = document.querySelector('[data-test="consent-part"]');
                if (!section) {
                    const allSections = document.querySelectorAll('[class*="consent"], [class*="agree"], [class*="terms"]');
                    if (allSections.length > 0) section = allSections[0];
                }
                if (!section) {
                    const allCbs = document.querySelectorAll('input[type="checkbox"]');
                    if (allCbs.length === 0) return { found: false, ticked: 0 };
                    let ticked = 0;
                    allCbs.forEach(cb => { if (!cb.checked) { cb.click(); ticked++; } });
                    return { found: true, total: allCbs.length, ticked, method: 'all_checkboxes' };
                }
                const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                let ticked = 0;
                checkboxes.forEach(cb => { if (!cb.checked) { cb.click(); ticked++; } });
                return { found: true, total: checkboxes.length, ticked, method: 'consent_section' };
            }""")
            if ticked.get("found"):
                print(
                    f"  Ticked {ticked['ticked']}/{ticked['total']} consent checkboxes"
                )
            else:
                print("  WARNING: No consent checkboxes found")
        except Exception as e:
            print(f"  WARNING: Could not tick consent: {e}")

    async def _handle_confirm(self, page: Page) -> None:
        try:
            await page.locator(SEL_CONFIRM_OK).click(timeout=SAVE_TIMEOUT)
        except Exception:
            try:
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=5_000)
            except Exception:
                print("  WARNING: No confirmation dialog found")

    async def _close_popup(self, page: Page) -> None:
        try:
            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass
