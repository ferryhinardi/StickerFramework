"""
Sticker image upload automation for the image edit page.

Navigates to /sticker/{id}/image, sets sticker count, then uploads
images per-slot via hidden file inputs or optionally via ZIP upload.

Confirmed page structure (Feb 2026):
- URL: /my/{creator}/sticker/{id}/image
- Sticker count: select[data-test="select-image-amount"] (8/16/24/32/40)
- Per-slot: #upload-file-input-{key} (hidden, accept="image/png")
  where key = "main", "tab", "01"-"40"
- ZIP upload: input[name="file"] (visible form)
- Back: a[data-test="btn-back"]
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import Page

from automation.config import (
    SEL_IMAGE_AMOUNT,
    SEL_IMAGE_BACK,
    SEL_IMAGE_KEY,
    SEL_IMAGE_LIST_ITEM,
    UPLOAD_TIMEOUT,
    sel_upload_file_input,
    sticker_image_url,
)
from automation.utils import human_delay, screenshot_on_failure


class LineStickerUpload:
    """Handles image uploads on the /sticker/{id}/image page."""

    async def upload_all(self, page: Page, sticker_id: str, pack_dir: str) -> None:
        """
        Upload all images for a sticker pack.

        Expects the pack_dir to contain::

            line/       — sticker PNGs (370x320), named 01*.png .. 08*.png
            line_main/  — main image PNG (240x240)
            line_tab/   — tab icon PNG (96x74)

        Args:
            page: Authenticated Playwright Page.
            sticker_id: LINE sticker ID (e.g. "43200641").
            pack_dir: Path to the ``final/`` directory of a processed pack.
        """
        pack_path = Path(pack_dir)

        async with screenshot_on_failure(page, "upload_images"):
            # Navigate to image edit page
            await page.goto(
                sticker_image_url(sticker_id),
                wait_until="networkidle",
                timeout=60_000,
            )
            await human_delay(1000, 2000)

            # Dismiss popup
            await self._close_popup(page)

            # Determine sticker count from available files
            sticker_dir = pack_path / "line"
            sticker_images = (
                sorted(sticker_dir.glob("*.png")) if sticker_dir.exists() else []
            )
            sticker_count = len(sticker_images)

            if sticker_count < 8:
                raise ValueError(
                    f"Need at least 8 sticker images but found {sticker_count} in {sticker_dir}. "
                    f"LINE requires a minimum of 8 stickers per set."
                )

            # Set sticker count (must be 8, 16, 24, 32, or 40)
            target_count = self._snap_to_valid_count(sticker_count)
            current_count = await page.locator(SEL_IMAGE_AMOUNT).input_value()
            if str(target_count) != current_count:
                await page.locator(SEL_IMAGE_AMOUNT).select_option(str(target_count))
                await human_delay(500, 800)

                # Handle confirmation dialog:
                # "The number of stickers in this set will be changed. Continue?"
                await self._handle_confirm_dialog(page)
                await human_delay(1000, 2000)
                print(
                    f"  Changed sticker count from {current_count} to {target_count} (have {sticker_count} images)"
                )
            else:
                print(
                    f"  Sticker count already {target_count} (have {sticker_count} images)"
                )

            # Upload main image
            main_image = self._find_image(pack_path / "line_main")
            if main_image:
                print(f"  Uploading main image: {main_image.name}")
                await self._upload_to_slot(page, "main", main_image)
            else:
                print("  WARNING: No main image found")

            # Upload tab image
            tab_image = self._find_image(pack_path / "line_tab")
            if tab_image:
                print(f"  Uploading tab image: {tab_image.name}")
                await self._upload_to_slot(page, "tab", tab_image)
            else:
                print("  WARNING: No tab image found")

            # Upload sticker images (only first target_count to match available slots)
            if not sticker_images:
                print(f"  WARNING: No sticker PNGs found in {sticker_dir}")
                return

            images_to_upload = sticker_images[:target_count]
            if len(sticker_images) > target_count:
                print(
                    f"  Uploading {target_count} of {len(sticker_images)} sticker images "
                    f"(skipping last {len(sticker_images) - target_count} to match slot count)"
                )
            else:
                print(f"  Uploading {len(images_to_upload)} sticker images...")

            for i, img_path in enumerate(images_to_upload):
                key = f"{i + 1:02d}"  # "01", "02", etc.
                await self._upload_to_slot(page, key, img_path)
                print(
                    f"    [{i + 1}/{len(images_to_upload)}] {img_path.name} → slot {key}"
                )

            # Wait for all uploads to complete
            await human_delay(2000, 3000)

            # Verify uploads
            await self._verify_uploads(page, main_image, tab_image, images_to_upload)

            print("  All images uploaded successfully.")

    # ── Per-slot upload ───────────────────────────────────────────────────

    async def _upload_to_slot(self, page: Page, key: str, file_path: Path) -> None:
        """
        Upload an image to a specific slot using its hidden file input.

        Args:
            key: Slot key — "main", "tab", "01"-"40".
            file_path: Path to the PNG file.
        """
        selector = sel_upload_file_input(key)
        try:
            # The file input is hidden but we can set_input_files on it
            file_input = page.locator(selector)
            await file_input.set_input_files(str(file_path))
            # Wait for upload to process
            await human_delay(1000, 2000)
        except Exception as e:
            print(f"    WARNING: Failed to upload to slot {key}: {e}")
            # Fallback: try clicking the Upload button which may trigger file chooser
            try:
                from automation.config import sel_upload_button

                async with page.expect_file_chooser(timeout=10_000) as fc_info:
                    await page.locator(sel_upload_button(key)).click()
                file_chooser = fc_info.value
                await file_chooser.set_files(str(file_path))
                await human_delay(1000, 2000)
            except Exception as e2:
                print(f"    ERROR: Both upload methods failed for slot {key}: {e2}")
                raise

    # ── Verification ─────────────────────────────────────────────────────

    async def _verify_uploads(
        self,
        page: Page,
        main_image: Path | None,
        tab_image: Path | None,
        sticker_images: list[Path],
    ) -> None:
        """Check how many slots now have images vs placeholders."""
        slot_status = await page.evaluate("""() => {
            const items = document.querySelectorAll('[data-test="product-images-list-item"]');
            let filled = 0;
            let empty = 0;
            items.forEach(item => {
                // Check for uploaded image (could be img tag, canvas, or absence of placeholder)
                const placeholder = item.querySelector('[data-test="no-product-image"]');
                const hasImg = item.querySelector('img');
                const hasCanvas = item.querySelector('canvas');
                if (hasImg || hasCanvas || !placeholder) filled++;
                else empty++;
            });
            return { filled, empty, total: items.length };
        }""")

        expected = (
            (1 if main_image else 0) + (1 if tab_image else 0) + len(sticker_images)
        )
        print(
            f"  Upload verification: {slot_status['filled']}/{slot_status['total']} slots filled (expected {expected})"
        )

        if slot_status["filled"] < expected:
            print(
                f"  WARNING: Only {slot_status['filled']} of {expected} images uploaded successfully!"
            )

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_image(self, directory: Path) -> Path | None:
        """Return the first PNG in *directory*, or None."""
        if not directory.exists():
            return None
        pngs = sorted(directory.glob("*.png"))
        return pngs[0] if pngs else None

    @staticmethod
    def _snap_to_valid_count(count: int) -> int:
        """Snap actual file count DOWN to the largest valid LINE sticker count
        that the images can fully fill.

        Valid counts: 8, 16, 24, 32, 40.
        All slots MUST be filled for the Request button to become enabled,
        so we always snap DOWN (not up).

        Caller must ensure count >= 8 before calling.

        Examples:
            10 images → 8  (upload first 8, skip 2)
            16 images → 16 (perfect fit)
            20 images → 16 (upload first 16, skip 4)
            40 images → 40 (maximum)
        """
        valid = [8, 16, 24, 32, 40]
        best = valid[0]  # minimum is always 8
        for v in valid:
            if v <= count:
                best = v
        return best

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
        """
        Handle confirmation dialogs that appear after changing sticker count.

        Dialog: "The number of stickers in this set will be changed. Continue?"
        with OK [data-test="dialog-btn-ok"] and Cancel buttons.
        """
        from automation.config import SEL_CONFIRM_OK, SEL_CONFIRM_OK_FALLBACK

        try:
            ok_btn = page.locator(SEL_CONFIRM_OK)
            await ok_btn.click(timeout=5_000)
            print("  Confirmed sticker count change dialog.")
        except Exception:
            try:
                await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=3_000)
                print("  Confirmed sticker count change dialog (fallback).")
            except Exception:
                # No dialog appeared — count change might not require confirmation
                # (e.g. if going from empty to first selection)
                pass
