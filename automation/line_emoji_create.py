"""
Create a new LINE Emoji submission on LINE Creator Market.

Fills the emoji registration form with display information fields:
title, description, copyright, emoji type, AI usage, categories,
privacy, sale region, etc. Then clicks Save and confirms the dialog.

Returns the new emoji ID and management URL.

Key differences from sticker submission:
- URL: /my/{creator}/emoji/register (not /sticker/create)
- Redirect after save: /emoji/{id} (not /sticker/{id})
- No "sticker_type" field — emoji has its own type field
- Form structure is assumed similar to stickers but verified at integration
"""

from __future__ import annotations

import asyncio
import re

from playwright.async_api import Page

from automation.config import (
    CHARACTER_CATEGORIES,
    EMOJI_CREATE_URL,
    EMOJI_DEFAULTS,
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
    SEL_TITLE,
    STYLE_CATEGORIES,
)
from automation.utils import human_delay, screenshot_on_failure


class LineEmojiCreate:
    """Creates a new emoji submission with all display info pre-filled."""

    async def create(self, page: Page, config: dict) -> dict[str, str]:
        """
        Create a new emoji submission.

        Args:
            config: Must contain ``title`` and ``description``.
                    Optional keys override EMOJI_DEFAULTS: ``copyright``,
                    ``ai_used``, ``style_category``, ``character_category``,
                    ``sale_region``, ``auto_release``.

        Returns:
            ``{"emoji_id": "12345678", "url": "https://..."}``
        """
        async with screenshot_on_failure(page, "emoji_create"):
            # Navigate to emoji registration page
            await page.goto(EMOJI_CREATE_URL, wait_until="commit")
            await page.wait_for_selector(SEL_TITLE, timeout=30_000)
            await human_delay(1000, 2000)

            # Dismiss campaign popup if present
            await self._close_popup(page)

            # Take a screenshot of the blank form for debugging
            from automation.config import SCREENSHOT_DIR
            from datetime import datetime

            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(
                path=str(SCREENSHOT_DIR / f"emoji_form_blank_{ts}.png"),
                full_page=True,
            )
            print("  Captured blank emoji form screenshot.")

            # ── Dump form structure for debugging ──
            form_info = await page.evaluate("""() => {
                const inputs = Array.from(document.querySelectorAll('input')).map(el => ({
                    name: el.name, type: el.type, value: el.value, id: el.id,
                    dataTest: el.getAttribute('data-test')
                }));
                const textareas = Array.from(document.querySelectorAll('textarea')).map(el => ({
                    name: el.name, id: el.id, dataTest: el.getAttribute('data-test')
                }));
                const selects = Array.from(document.querySelectorAll('select')).map(el => ({
                    name: el.name, id: el.id, dataTest: el.getAttribute('data-test'),
                    optionCount: el.options.length
                }));
                return { inputs, textareas, selects };
            }""")
            print(
                f"  Form structure: {len(form_info['inputs'])} inputs, "
                f"{len(form_info['textareas'])} textareas, "
                f"{len(form_info['selects'])} selects"
            )

            # ── Fill text fields ──
            # Try standard sticker selectors first; fall back to first input/textarea
            await self._fill_field(page, SEL_TITLE, config["title"], "title")
            await human_delay(200, 400)

            await self._fill_field(
                page, SEL_DESCRIPTION, config.get("description", ""), "description"
            )
            await human_delay(200, 400)

            await self._fill_field(
                page,
                SEL_COPYRIGHT,
                config.get("copyright", EMOJI_DEFAULTS["copyright"]),
                "copyright",
            )
            await human_delay(200, 400)

            # ── Named radio buttons ──
            # AI usage
            ai_val = (
                "true" if config.get("ai_used", EMOJI_DEFAULTS["ai_used"]) else "false"
            )
            await self._try_radio(page, SEL_AI_GENERATED, ai_val, "ai_generated")

            # Sale region
            region = config.get("sale_region", EMOJI_DEFAULTS["sale_region"])
            await self._try_radio(page, SEL_AREA_GROUP, region, "area_group")

            # Auto release
            auto_val = (
                "true"
                if config.get("auto_release", EMOJI_DEFAULTS["auto_release"])
                else "false"
            )
            await self._try_radio(page, SEL_AUTO_RELEASE, auto_val, "auto_release")

            # ── Category selects ──
            style_key = config.get("style_category", EMOJI_DEFAULTS["style_category"])
            await self._try_select_category(page, style_key, "style")
            await human_delay(200, 400)

            char_key = config.get(
                "character_category", EMOJI_DEFAULTS["character_category"]
            )
            await self._try_select_character(page, char_key)
            await human_delay(200, 400)

            # ── Click Save ──
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await human_delay(500, 800)

            # Try multiple save button selectors
            saved = False
            for save_sel in [
                SEL_SAVE_LABEL,
                '[data-test="btn-save"]',
                'label:has-text("Save")',
                'button:has-text("Save")',
                'input[type="submit"]',
            ]:
                try:
                    loc = page.locator(save_sel)
                    if await loc.count() > 0:
                        await loc.first.click(timeout=SAVE_TIMEOUT)
                        saved = True
                        print(f"  Clicked save via: {save_sel}")
                        break
                except Exception:
                    continue

            if not saved:
                raise RuntimeError("Could not find Save button on emoji form")

            await human_delay(500, 1000)

            # ── Handle confirmation dialog ──
            await self._handle_confirm_dialog(page)

            # ── Wait for redirect to management page ──
            # Emoji redirect: /emoji/{id} or /emoji/{id}/...
            deadline = SAVE_TIMEOUT * 4  # 60s
            poll_interval = 0.5
            elapsed = 0.0
            emoji_id = None
            while elapsed < deadline:
                current = page.url
                match = re.search(r"/emoji/(\d+)", current)
                if match:
                    emoji_id = match.group(1)
                    break
                await asyncio.sleep(poll_interval)
                elapsed += poll_interval

            if not emoji_id:
                await human_delay(3000, 5000)
                match = re.search(r"/emoji/(\d+)", page.url)
                if match:
                    emoji_id = match.group(1)
                else:
                    # Also try sticker-like redirect pattern (LINE may reuse)
                    match = re.search(
                        r"/(\d+)",
                        page.url.split("/emoji/")[-1] if "/emoji/" in page.url else "",
                    )
                    if match:
                        emoji_id = match.group(1)
                    else:
                        raise TimeoutError(
                            f"Redirect to /emoji/ID not detected after {deadline}s. "
                            f"Current URL: {page.url}"
                        )

            await human_delay(500, 1000)

            result = {
                "emoji_id": emoji_id,
                "url": page.url,
            }
            print(f"  Created emoji submission: {result['emoji_id']} → {result['url']}")
            return result

    # ── Helpers ───────────────────────────────────────────────────────────

    async def _fill_field(
        self, page: Page, selector: str, value: str, field_name: str
    ) -> None:
        """Fill a text field, with fallback for emoji-specific selectors."""
        try:
            loc = page.locator(selector)
            if await loc.count() > 0:
                await loc.first.fill(value)
                return
        except Exception:
            pass
        # Fallback: try by placeholder or label text
        print(
            f"  WARNING: Primary selector for {field_name} not found, trying fallback"
        )
        try:
            if field_name == "title":
                for fallback in [
                    'input[placeholder*="title" i]',
                    'input[placeholder*="name" i]',
                    'input:not([type="hidden"]):not([type="radio"]):not([type="checkbox"]) >> nth=0',
                ]:
                    loc = page.locator(fallback)
                    if await loc.count() > 0:
                        await loc.first.fill(value)
                        print(f"    Filled {field_name} via fallback: {fallback}")
                        return
            elif field_name == "description":
                loc = page.locator("textarea >> nth=0")
                if await loc.count() > 0:
                    await loc.first.fill(value)
                    print(f"    Filled {field_name} via first textarea")
                    return
        except Exception as e:
            print(f"  ERROR: Could not fill {field_name}: {e}")

    async def _try_radio(
        self, page: Page, base_selector: str, value: str, field_name: str
    ) -> None:
        """Click a named radio if not already checked. Silent on failure."""
        try:
            radio = page.locator(f'{base_selector}[value="{value}"]')
            if await radio.count() > 0 and not await radio.is_checked():
                await radio.click()
                await human_delay(200, 400)
        except Exception:
            print(f"  NOTE: Radio '{field_name}' not found (may differ for emoji)")

    async def _try_select_category(
        self, page: Page, style_key: str, category_type: str
    ) -> None:
        """Try to set style category select."""
        try:
            style_sel = page.locator('select[data-test="select-style-category"]')
            if await style_sel.count() > 0:
                style_val = STYLE_CATEGORIES.get(style_key, style_key)
                await style_sel.select_option(style_val)
                return
            # Fallback: positional
            selects = page.locator("select")
            count = await selects.count()
            if count >= 2:
                style_val = STYLE_CATEGORIES.get(style_key, style_key)
                await selects.nth(1).select_option(style_val)
        except Exception:
            print(f"  NOTE: Style category select not found on emoji form")

    async def _try_select_character(self, page: Page, char_key: str) -> None:
        """Try to set character category select."""
        char_label = CHARACTER_CATEGORIES.get(char_key, char_key)
        try:
            char_sel = page.locator('select[data-test="select-character-category"]')
            if await char_sel.count() == 0:
                selects = page.locator("select")
                if await selects.count() >= 3:
                    char_sel = selects.nth(2)
                else:
                    print("  NOTE: Character category select not found on emoji form")
                    return

            options = await char_sel.evaluate(
                """el => Array.from(el.options).map(o => ({
                    value: o.value, text: o.textContent.trim(), label: o.label
                }))"""
            )
            print(f"  Character category options: {options}")

            for opt in options:
                if opt["text"] == char_label or opt["label"] == char_label:
                    await char_sel.select_option(value=opt["value"])
                    print(f"  ✓ Selected: {opt['text']} (value={opt['value']})")
                    return

            # Fuzzy match
            target = char_label.lower()
            for opt in options:
                if target in opt["text"].lower() or target in opt["label"].lower():
                    await char_sel.select_option(value=opt["value"])
                    print(f"  ✓ Selected (fuzzy): {opt['text']}")
                    return

            print(f"  WARNING: Could not match '{char_label}'")
        except Exception as e:
            print(f"  NOTE: Character category error: {e}")

    async def _handle_confirm_dialog(self, page: Page) -> None:
        """Handle "Save this form?" confirmation dialog."""
        try:
            await page.locator(SEL_CONFIRM_OK).click(timeout=SAVE_TIMEOUT)
        except Exception:
            try:
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=5_000)
            except Exception:
                try:
                    await page.locator(
                        'button:visible:has-text("OK"), '
                        'button:visible:has-text("Save"), '
                        ".cm-modal button:visible >> nth=0"
                    ).first.click(timeout=5_000)
                except Exception:
                    print("  NOTE: No confirmation dialog appeared")

    async def _close_popup(self, page: Page) -> None:
        """Dismiss campaign popup if visible."""
        try:
            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass
