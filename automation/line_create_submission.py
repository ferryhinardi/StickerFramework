"""
Create a new sticker submission on LINE Creator Market.

Fills the single-page create form with all display information fields:
title, description, copyright, sticker type, AI usage, categories,
privacy, premium, sale region, etc. Then clicks Save and confirms
the "Save this form?" dialog.

Returns the new sticker ID and management URL.

Confirmed form structure (Feb 2026):
- All display info fields are on the create page (NOT separate tabs).
- Save button: label.mdBtnLabel wrapping input[data-test="btn-save"]
- After Save: "Save this form?" confirmation dialog → OK
- After OK: redirects to /my/{creator}/sticker/{sticker_id}
"""

from __future__ import annotations

from playwright.async_api import Page

from automation.config import (
    CHARACTER_CATEGORIES,
    CREATE_URL,
    DEFAULTS,
    SAVE_TIMEOUT,
    SEL_AI_GENERATED,
    SEL_AREA_GROUP,
    SEL_AUTO_RELEASE,
    SEL_CAMPAIGN_POPUP_CLOSE,
    SEL_CONFIRM_OK,
    SEL_CONFIRM_OK_FALLBACK,
    SEL_COPYRIGHT,
    SEL_DESCRIPTION,
    SEL_SAVE_LABEL,
    SEL_STICKER_TYPE,
    SEL_TITLE,
    STYLE_CATEGORIES,
)
from automation.utils import human_delay, screenshot_on_failure


class LineCreateSubmission:
    """Creates a new sticker submission with all display info pre-filled."""

    async def create(self, page: Page, config: dict) -> dict[str, str]:
        """
        Create a new sticker submission.

        Args:
            config: Must contain ``title`` and ``description``.
                    Optional keys override DEFAULTS: ``copyright``,
                    ``ai_used``, ``style_category``, ``character_category``,
                    ``sale_region``, ``auto_release``, ``sticker_type``.

        Returns:
            ``{"sticker_id": "43200641", "url": "https://..."}``
        """
        async with screenshot_on_failure(page, "create_submission"):
            # Navigate to the create page
            await page.goto(CREATE_URL, wait_until="networkidle")
            await human_delay(1000, 2000)

            # Dismiss campaign popup if present
            await self._close_popup(page)

            # ── Fill text fields ──
            await page.fill(SEL_TITLE, config["title"])
            await human_delay(200, 400)

            await page.fill(SEL_DESCRIPTION, config["description"])
            await human_delay(200, 400)

            await page.fill(
                SEL_COPYRIGHT,
                config.get("copyright", DEFAULTS["copyright"]),
            )
            await human_delay(200, 400)

            # ── Named radio buttons ──
            sticker_type = config.get("sticker_type", DEFAULTS["sticker_type"])
            await self._check_radio(page, SEL_STICKER_TYPE, sticker_type)

            ai_val = "true" if config.get("ai_used", DEFAULTS["ai_used"]) else "false"
            await self._check_radio(page, SEL_AI_GENERATED, ai_val)

            region = config.get("sale_region", DEFAULTS["sale_region"])
            await self._check_radio(page, SEL_AREA_GROUP, region)

            auto_val = (
                "true"
                if config.get("auto_release", DEFAULTS["auto_release"])
                else "false"
            )
            await self._check_radio(page, SEL_AUTO_RELEASE, auto_val)

            # ── Category selects (positional — no name attrs) ──
            selects = page.locator("select")
            count = await selects.count()

            if count >= 2:
                style_key = config.get("style_category", DEFAULTS["style_category"])
                style_val = STYLE_CATEGORIES.get(style_key, style_key)
                await selects.nth(1).select_option(style_val)
                await human_delay(200, 400)

            if count >= 3:
                char_key = config.get(
                    "character_category", DEFAULTS["character_category"]
                )
                char_val = CHARACTER_CATEGORIES.get(char_key, char_key)
                await selects.nth(2).select_option(char_val)
                await human_delay(200, 400)

            # ── Click Save ──
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await human_delay(500, 800)

            await page.locator(SEL_SAVE_LABEL).click(timeout=SAVE_TIMEOUT)
            await human_delay(500, 1000)

            # ── Handle "Save this form?" confirmation ──
            try:
                await page.locator(SEL_CONFIRM_OK).click(timeout=SAVE_TIMEOUT)
            except Exception:
                # Fallback: find any visible OK button
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=5_000)

            # ── Wait for redirect to management page ──
            # The redirect happens but Playwright's wait_for_url can miss
            # the domcontentloaded event. Poll the URL instead.
            import asyncio as _asyncio
            import re

            deadline = SAVE_TIMEOUT * 4  # 60s
            poll_interval = 0.5
            elapsed = 0.0
            sticker_id = None
            while elapsed < deadline:
                current = page.url
                match = re.search(r"/sticker/(\d+)", current)
                if match:
                    sticker_id = match.group(1)
                    break
                await _asyncio.sleep(poll_interval)
                elapsed += poll_interval

            if not sticker_id:
                # Last chance — check URL one more time after a long wait
                await human_delay(3000, 5000)
                match = re.search(r"/sticker/(\d+)", page.url)
                if match:
                    sticker_id = match.group(1)
                else:
                    raise TimeoutError(
                        f"Redirect to /sticker/ID not detected after {deadline}s. "
                        f"Current URL: {page.url}"
                    )

            await human_delay(500, 1000)

            result = {
                "sticker_id": sticker_id,
                "url": page.url,
            }
            print(f"  Created submission: {result['sticker_id']} → {result['url']}")
            return result

    # ── Helpers ───────────────────────────────────────────────────────────

    async def _check_radio(self, page: Page, base_selector: str, value: str) -> None:
        """Click a named radio if not already checked."""
        radio = page.locator(f'{base_selector}[value="{value}"]')
        if not await radio.is_checked():
            await radio.click()
            await human_delay(200, 400)

    async def _close_popup(self, page: Page) -> None:
        """Dismiss campaign popup if visible."""
        try:
            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass
