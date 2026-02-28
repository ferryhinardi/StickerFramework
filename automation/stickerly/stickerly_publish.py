"""
Sticker.ly publish automation.

Handles the final publish step: tapping Publish, confirming,
and capturing the share link.
"""

from __future__ import annotations

import re
import time

import uiautomator2 as u2

from automation.stickerly.config import (
    PUBLISH_TIMEOUT,
    SEL_PUBLISH_BUTTON,
    SEL_PUBLISH_CONFIRM,
)
from automation.stickerly.utils import (
    ElementNotFound,
    human_delay,
    safe_click,
    save_published_pack,
    screenshot_on_failure,
)


class StickerlyPublish:
    """Publish a sticker pack on Sticker.ly."""

    def publish(
        self,
        device: u2.Device,
        pack_id: str,
        dry_run: bool = False,
    ) -> str | None:
        """
        Publish the current pack to Sticker.ly.

        Args:
            device: uiautomator2 Device instance.
            pack_id: Pack identifier for logging and storage.
            dry_run: If True, skip the actual publish tap (for testing).

        Returns:
            Share link URL if captured, or None.
        """
        share_link = None

        with screenshot_on_failure(device, "publish"):
            if dry_run:
                print("  [DRY RUN] Would tap Publish here. Skipping.")
                self._take_pre_publish_screenshot(device, pack_id)
                return None

            # Tap Publish / Save & Publish
            print("  Publishing sticker pack...")
            safe_click(device, SEL_PUBLISH_BUTTON)
            human_delay(1000, 2000)

            # Handle confirmation dialog if it appears
            try:
                safe_click(device, SEL_PUBLISH_CONFIRM, timeout=5)
                human_delay(1000, 2000)
            except ElementNotFound:
                pass  # No confirmation dialog needed

            # Wait for publish to complete
            print("  Waiting for publish confirmation...")
            time.sleep(5)

            # Try to capture the share link
            share_link = self._capture_share_link(device)

            if share_link:
                print(f"  Published! Share link: {share_link}")
            else:
                print("  Published! (Share link not captured)")

            # Save to published packs log
            save_published_pack(pack_id, share_link)

            # Take post-publish screenshot
            self._take_post_publish_screenshot(device, pack_id)

        return share_link

    def _capture_share_link(self, device: u2.Device) -> str | None:
        """
        Try to find and extract the share link from the screen.

        Sticker.ly share links follow the pattern: https://sticker.ly/s/XXXXXX
        """
        try:
            # Look for text containing sticker.ly URL
            el = device(textContains="sticker.ly/s/")
            if el.exists(timeout=5):
                text = el.get_text()
                match = re.search(r"https?://sticker\.ly/s/\w+", text)
                if match:
                    return match.group(0)

            # Try getting from clipboard or other UI elements
            # Look for any element with a shareable URL
            page_source = device.dump_hierarchy()
            matches = re.findall(r"https?://sticker\.ly/s/\w+", page_source)
            if matches:
                return matches[0]

        except Exception as exc:
            print(f"    Could not capture share link: {exc}")

        return None

    def _take_pre_publish_screenshot(self, device: u2.Device, pack_id: str) -> None:
        """Take a screenshot before publishing for dry-run verification."""
        from automation.stickerly.config import SCREENSHOT_DIR
        from datetime import datetime

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"{timestamp}_pre_publish_{pack_id}.png"
        try:
            device.screenshot(str(path))
            print(f"  Pre-publish screenshot: {path}")
        except Exception as exc:
            print(f"  Could not take screenshot: {exc}")

    def _take_post_publish_screenshot(self, device: u2.Device, pack_id: str) -> None:
        """Take a screenshot after publishing for confirmation."""
        from automation.stickerly.config import SCREENSHOT_DIR
        from datetime import datetime

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOT_DIR / f"{timestamp}_post_publish_{pack_id}.png"
        try:
            device.screenshot(str(path))
            print(f"  Post-publish screenshot: {path}")
        except Exception as exc:
            print(f"  Could not take screenshot: {exc}")
