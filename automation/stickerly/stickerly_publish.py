"""
Sticker.ly share link capture.

In Sticker.ly, packs are PUBLIC by default when created (no separate
"publish" step). This module captures the share link and pack code.

Flow:
1. From Pack Detail screen, click share button
2. Share bottom sheet appears with "Copy code", "Copy link", "More"
3. Click "Copy link" -> URL copied to clipboard
4. Read clipboard -> https://sticker.ly/s/{PACK_CODE}
"""

from __future__ import annotations

import re
import time

import uiautomator2 as u2

from automation.stickerly.config import (
    SEL_PACK_CODE_TEXT,
    SEL_PACK_SHARE_IMAGE,
    SEL_SHARE_COPY_LINK,
    SEL_SHARE_TOUCH_OUTSIDE,
)
from automation.stickerly.utils import (
    ElementNotFound,
    find_element,
    human_delay,
    safe_click,
    save_published_pack,
    screenshot_on_failure,
    take_screenshot,
)


class StickerlyPublish:
    """Capture share links for published Sticker.ly packs."""

    def capture_share_link(
        self,
        device: u2.Device,
        pack_id: str,
        sticker_count: int = 0,
        dry_run: bool = False,
    ) -> dict:
        """
        Capture the share link and pack code from the Pack Detail screen.

        The pack is already public (no publish step needed). This just
        extracts the share URL.

        Args:
            device: uiautomator2 Device instance.
            pack_id: Pack identifier for logging and storage.
            sticker_count: Number of stickers in the pack.
            dry_run: If True, take screenshot but skip clipboard capture.

        Returns:
            Dict with keys: pack_code, share_link
        """
        result: dict[str, str | None] = {"pack_code": None, "share_link": None}

        with screenshot_on_failure(device, f"capture_link_{pack_id}"):
            # 1. Get pack code from detail screen
            try:
                el = find_element(device, SEL_PACK_CODE_TEXT, timeout=5)
                result["pack_code"] = el.get_text()
                print(f"  Pack code: {result['pack_code']}")
            except ElementNotFound:
                print("  WARNING: Could not find pack code on screen")

            if dry_run:
                take_screenshot(device, f"dry_run_{pack_id}")
                print("  [DRY RUN] Skipping share link capture.")
                return result

            # 2. Click share button
            print("  Opening share sheet...")
            safe_click(device, SEL_PACK_SHARE_IMAGE)
            human_delay(1500, 2500)

            # 3. Click "Copy link"
            try:
                safe_click(device, SEL_SHARE_COPY_LINK, timeout=5)
                human_delay(1000, 2000)
                print("  Copied link to clipboard.")
            except ElementNotFound:
                print("  WARNING: Could not find 'Copy link' button")
                # Try to dismiss the bottom sheet
                self._dismiss_share_sheet(device)
                return result

            # 4. Read clipboard
            try:
                link = device.clipboard
                if link and "sticker.ly" in link:
                    result["share_link"] = link
                    print(f"  Share link: {link}")
                else:
                    # Fallback: construct from pack code
                    if result["pack_code"]:
                        result["share_link"] = (
                            f"https://sticker.ly/s/{result['pack_code']}"
                        )
                        print(f"  Share link (constructed): {result['share_link']}")
            except Exception as exc:
                print(f"  WARNING: Could not read clipboard: {exc}")
                if result["pack_code"]:
                    result["share_link"] = f"https://sticker.ly/s/{result['pack_code']}"

            # 5. Dismiss share bottom sheet (toast may dismiss it already)
            self._dismiss_share_sheet(device)

            # 6. Save to published packs log
            save_published_pack(
                pack_id,
                pack_code=result["pack_code"],
                share_link=result["share_link"],
                sticker_count=sticker_count,
            )

            take_screenshot(device, f"published_{pack_id}")

        return result

    def _dismiss_share_sheet(self, device: u2.Device) -> None:
        """Dismiss the share bottom sheet by tapping outside."""
        try:
            safe_click(device, SEL_SHARE_TOUCH_OUTSIDE, timeout=2)
            human_delay(500, 1000)
        except ElementNotFound:
            # Sheet may already be dismissed
            pass
