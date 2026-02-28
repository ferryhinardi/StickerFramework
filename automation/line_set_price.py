"""
Price Tier tab automation for LINE Creator Market.

Navigates to the Price Tier tab on the management page and selects
the desired price from the dropdown.

Confirmed structure (Feb 2026):
- Tab: button[data-test="tab-price"]
- Select: select[data-test="select-price-tier"]
- Options: 10006=Rp7.200+, 1=Rp12.000+, 2=Rp23.000+,
           3=Rp35.000+, 4=Rp45.000+, 5=Rp59.000+
"""

from __future__ import annotations

from playwright.async_api import Page

from automation.config import (
    DEFAULTS,
    PRICE_TIERS,
    SAVE_TIMEOUT,
    SEL_CONFIRM_OK,
    SEL_CONFIRM_OK_FALLBACK,
    SEL_PRICE_SAVE,
    SEL_PRICE_TIER,
    SEL_TAB_PRICE_TIER,
    sticker_url,
)
from automation.utils import human_delay, screenshot_on_failure


class LinePriceTier:
    """Sets the price tier on the Price Tier tab."""

    async def set_price(
        self,
        page: Page,
        sticker_id: str,
        tier: str | None = None,
    ) -> None:
        """
        Select a price tier and save.

        Args:
            page: Playwright Page (authenticated).
            sticker_id: LINE sticker ID.
            tier: Price tier key (e.g. "23000"). Defaults to config value.
                  Maps to internal select values via PRICE_TIERS.
        """
        tier = tier or DEFAULTS["price_tier"]

        async with screenshot_on_failure(page, "set_price"):
            # Navigate to management page
            await page.goto(sticker_url(sticker_id), wait_until="commit")
            await page.wait_for_selector(SEL_TAB_PRICE_TIER, timeout=30_000)
            await human_delay(1000, 1500)

            # Close popup
            await self._close_popup(page)

            # Click Price Tier tab
            await page.locator(SEL_TAB_PRICE_TIER).click()
            await human_delay(1000, 2000)

            # Select price from dropdown
            select_value = PRICE_TIERS.get(tier, tier)
            await page.locator(SEL_PRICE_TIER).select_option(select_value)
            await human_delay(500, 800)

            # Click Save button to persist the price change
            await page.locator(SEL_PRICE_SAVE).click()
            await human_delay(500, 1000)

            # Handle confirmation dialog if it appears
            await self._handle_confirm_dialog(page)
            await human_delay(500, 1000)

            print(
                f"  Price tier set to {self._format_idr(tier)} (select value: {select_value}) — saved."
            )

    @staticmethod
    def _format_idr(tier: str) -> str:
        """Format a numeric tier string as IDR."""
        try:
            return f"Rp{int(tier):,}+".replace(",", ".")
        except ValueError:
            return tier

    async def _close_popup(self, page: Page) -> None:
        """Dismiss campaign popup if visible."""
        try:
            from automation.config import SEL_CAMPAIGN_POPUP_CLOSE

            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass

    async def _handle_confirm_dialog(self, page: Page) -> None:
        """Handle confirmation dialog after saving price."""
        try:
            ok_btn = page.locator(SEL_CONFIRM_OK)
            await ok_btn.click(timeout=5_000)
            print("  Confirmed price save dialog.")
        except Exception:
            try:
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=3_000)
                print("  Confirmed price save dialog (fallback).")
            except Exception:
                # No dialog appeared — save may not require confirmation
                pass
