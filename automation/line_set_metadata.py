"""
Tag Settings tab automation for LINE Creator Market.

Navigates to the Tag Settings tab on the management page and assigns
emoji tags to each sticker based on keyword matching.

Note: The Tag Settings tab on the management page is read-only in the
current LINE UI (Feb 2026). Tag assignment may need to happen through
the sticker editing flow or might not be available for new submissions
until images are uploaded. This module is a placeholder that will be
completed once the tag editing interface is confirmed.

Display Information is now handled by line_create_submission.py
(it's part of the create/update form, NOT a separate tab).
"""

from __future__ import annotations

from playwright.async_api import Page

from automation.config import (
    SEL_TAB_TAG_SETTINGS,
    sticker_url,
)
from automation.utils import human_delay, screenshot_on_failure


# Keyword → emoji tag mapping for automatic tag assignment
TAG_MAP: dict[str, list[str]] = {
    "hello": ["waving_hand", "smile"],
    "hi": ["waving_hand", "smile"],
    "morning": ["sun", "yawning"],
    "night": ["moon", "sleeping"],
    "love": ["heart", "smiling_hearts"],
    "thank": ["folded_hands", "smile"],
    "sorry": ["bowing", "crying"],
    "angry": ["angry_face", "pouting"],
    "sad": ["crying", "broken_heart"],
    "fighting": ["flexed_bicep", "fire"],
    "semangat": ["flexed_bicep", "fire"],
    "eat": ["fork_knife", "yummy"],
    "lunch": ["fork_knife"],
    "bye": ["waving_hand"],
    "laugh": ["laughing_tears"],
    "sleepy": ["sleeping", "zzz"],
    "tired": ["sleeping", "yawning"],
    "busy": ["laptop", "running"],
    "deadline": ["alarm_clock", "fire"],
    "celebrate": ["party_popper", "confetti"],
    "yay": ["party_popper", "star"],
    "ok": ["thumbs_up"],
    "good_job": ["thumbs_up", "star"],
    "what": ["question_mark", "confused"],
    "lol": ["laughing_tears", "joy"],
    "nope": ["cross_mark", "no_gesture"],
    "pray": ["folded_hands"],
    "peace": ["dove", "heart"],
    "miss": ["heart", "crying"],
}


class LineSetMetadata:
    """Handles Tag Settings on the management page."""

    async def fill_tag_settings(
        self,
        page: Page,
        sticker_id: str,
        sticker_names: list[str],
    ) -> None:
        """
        Navigate to Tag Settings tab and assign emoji tags per sticker.

        Args:
            page: Authenticated Playwright Page.
            sticker_id: LINE sticker ID.
            sticker_names: List of sticker display names for keyword matching
                          (e.g. ["what", "lol", "ok", "nope", "bye", ...]).
        """
        async with screenshot_on_failure(page, "fill_tag_settings"):
            # Navigate to management page
            await page.goto(sticker_url(sticker_id), wait_until="domcontentloaded")
            await human_delay(1000, 1500)

            # Close popup
            await self._close_popup(page)

            # Click Tag Settings tab
            await page.locator(SEL_TAB_TAG_SETTINGS).click()
            await human_delay(1000, 2000)

            # Check if tag editing is available
            # The tag tab may show a read-only view until images are uploaded
            tag_state = await page.evaluate("""() => {
                const selects = document.querySelectorAll('select');
                const inputs = document.querySelectorAll('input:not([type="hidden"])');
                const buttons = document.querySelectorAll('[data-test*="tag"]');
                return {
                    selectCount: selects.length,
                    inputCount: inputs.length,
                    tagButtons: buttons.length,
                };
            }""")

            if tag_state["selectCount"] == 0 and tag_state["inputCount"] == 0:
                print(
                    "  Tag Settings: No editable elements found (images may need to be uploaded first)."
                )
                print(f"  Tag state: {tag_state}")
                return

            # If editable elements exist, attempt tag assignment
            for i, name in enumerate(sticker_names):
                tags = self._infer_tags(name)
                if tags:
                    print(f"  Sticker {i + 1} ({name}): tags = {tags}")
                    await self._assign_tags(page, sticker_index=i, tag_ids=tags)

            print("  Tag settings processing complete.")

    # ── Private helpers ───────────────────────────────────────────────────

    @staticmethod
    def _infer_tags(name: str) -> list[str]:
        """Infer emoji tags from a sticker name using keyword matching."""
        tags: list[str] = []
        name_lower = name.lower()
        for keyword, emojis in TAG_MAP.items():
            if keyword in name_lower:
                tags.extend(emojis)
        # Dedupe while keeping order, limit to 3
        seen: set[str] = set()
        unique: list[str] = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                unique.append(t)
        return unique[:3]

    async def _assign_tags(
        self, page: Page, sticker_index: int, tag_ids: list[str]
    ) -> None:
        """
        Assign emoji tags to a specific sticker.

        This is a best-effort operation — the LINE tag interface varies
        and may not be available until images are uploaded.
        """
        try:
            thumbnails = await page.query_selector_all(
                ".sticker-thumbnail, .sticker-item, [class*='sticker'], "
                "[class*='cm-product-image']"
            )
            if sticker_index < len(thumbnails):
                await thumbnails[sticker_index].click()
                await human_delay(300, 600)

                for tag_id in tag_ids:
                    try:
                        # Try common tag selector patterns
                        for selector in [
                            f"[data-tag='{tag_id}']",
                            f"[title*='{tag_id}']",
                            f"button:has-text('{tag_id}')",
                        ]:
                            elem = await page.query_selector(selector)
                            if elem:
                                await elem.click()
                                await human_delay(200, 400)
                                break
                    except Exception:
                        pass
        except Exception:
            pass

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
