"""
LINE Emoji image upload automation for the image edit page.

Navigates to /emoji/{id}/image and uploads all emoji images via ZIP file.

The emoji image page does NOT have a count dropdown like the sticker page.
Instead it has an "Upload ZIP File" button that accepts a ZIP containing
tab.png (96x74) and 001.png through 040.png (180x180).

Key differences from sticker upload:
- URL: /my/{creator}/emoji/{id}/image (not /sticker/{id}/image)
- No count selector — all images are uploaded via ZIP
- Slot keys: 3-digit (001-040) not 2-digit (01-40)
- No "main image" slot — emoji only has tab icon + emoji PNGs
- Emoji images: 180x180 PNG (not 370x320)
- Tab icon: 96x74 PNG (same as stickers)
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page

from automation.config import (
    SEL_CAMPAIGN_POPUP_CLOSE,
    SCREENSHOT_DIR,
    emoji_image_url,
    emoji_slot_key,
)
from automation.utils import human_delay, screenshot_on_failure


class LineEmojiUpload:
    """Handles image uploads on the /emoji/{id}/image page."""

    async def upload_all(self, page: Page, emoji_id: str, pack_dir: str) -> None:
        """
        Upload all images for an emoji pack via ZIP upload.

        Expects the pack_dir to contain::

            line_emoji/       — emoji PNGs (180x180), named 001*.png .. 040*.png
            line_emoji_tab/   — tab icon PNG (96x74)

        Args:
            page: Authenticated Playwright Page.
            emoji_id: LINE emoji ID (e.g. "12345678").
            pack_dir: Path to the ``final/`` directory of a processed pack.
        """
        pack_path = Path(pack_dir)

        async with screenshot_on_failure(page, "emoji_upload"):
            # Navigate to emoji image edit page
            await page.goto(
                emoji_image_url(emoji_id),
                wait_until="commit",
                timeout=60_000,
            )
            # Wait for the page to render — look for file inputs or upload buttons
            try:
                await page.wait_for_selector(
                    'input[type="file"], button:has-text("Upload"), [data-test="btn-upload-zip"]',
                    timeout=30_000,
                )
            except Exception:
                pass  # Proceed anyway; page may have different structure
            await human_delay(1000, 2000)

            # Dismiss popup
            await self._close_popup(page)

            # Take debug screenshot of image page
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(
                path=str(SCREENSHOT_DIR / f"emoji_image_page_{ts}.png"),
                full_page=True,
            )

            # ── Collect images ────────────────────────────────────────
            emoji_dir = pack_path / "line_emoji"
            emoji_images = sorted(emoji_dir.glob("*.png")) if emoji_dir.exists() else []
            emoji_count = len(emoji_images)

            if emoji_count < 8:
                raise ValueError(
                    f"Need at least 8 emoji images but found {emoji_count} in {emoji_dir}. "
                    f"LINE requires a minimum of 8 emoji per set."
                )

            target_count = self._snap_to_valid_count(emoji_count)
            images_to_upload = emoji_images[:target_count]

            tab_image = self._find_image(pack_path / "line_emoji_tab")

            print(f"  Preparing ZIP with {len(images_to_upload)} emoji + tab icon...")

            # ── Build ZIP file ────────────────────────────────────────
            zip_path = self._create_upload_zip(tab_image, images_to_upload)

            try:
                # ── Upload via ZIP button ─────────────────────────────
                await self._upload_zip(page, zip_path)
            finally:
                # Clean up temp ZIP
                try:
                    zip_path.unlink()
                except Exception:
                    pass

            # Wait for all uploads to process
            await human_delay(3000, 5000)

            # Take post-upload screenshot
            ts2 = datetime.now().strftime("%Y%m%d_%H%M%S")
            await page.screenshot(
                path=str(SCREENSHOT_DIR / f"emoji_post_upload_{ts2}.png"),
                full_page=True,
            )

            # Verify uploads
            await self._verify_uploads(page, tab_image, images_to_upload)

            # ── Set Main Image (4 emoji numbers) ─────────────────────
            await self._set_main_image(page)

            print("  All emoji images uploaded successfully.")

    # ── ZIP creation ──────────────────────────────────────────────────────

    def _create_upload_zip(
        self,
        tab_image: Path | None,
        emoji_images: list[Path],
    ) -> Path:
        """Create a ZIP file with LINE's expected naming convention.

        LINE expects::

            tab.png          — chat thumbnail icon (96x74)
            001.png          — first emoji (180x180)
            002.png          — second emoji
            ...
            040.png          — last emoji

        Returns:
            Path to the temporary ZIP file.
        """
        tmp_dir = Path(tempfile.mkdtemp(prefix="line_emoji_"))
        zip_path = tmp_dir / "emoji_upload.zip"

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add tab icon
            if tab_image:
                zf.write(tab_image, "tab.png")
                print(f"    ZIP: tab.png ← {tab_image.name}")

            # Add emoji images with canonical 3-digit names
            for i, img_path in enumerate(emoji_images):
                canonical_name = f"{emoji_slot_key(i)}.png"  # "001.png", "002.png", ...
                zf.write(img_path, canonical_name)

            count = (1 if tab_image else 0) + len(emoji_images)
            print(
                f"    ZIP created: {count} files, {zip_path.stat().st_size / 1024:.1f} KB"
            )

        return zip_path

    # ── ZIP upload ────────────────────────────────────────────────────────

    async def _upload_zip(self, page: Page, zip_path: Path) -> None:
        """Upload ZIP via the 'Upload ZIP File' button.

        The button triggers a file chooser dialog.  We intercept it with
        Playwright's ``expect_file_chooser`` and set the ZIP path.
        """
        # Find the Upload ZIP File button — try multiple selectors
        zip_button = None
        selectors = [
            'button:has-text("Upload ZIP File")',
            'a:has-text("Upload ZIP File")',
            '[data-test="btn-upload-zip"]',
            'button:has-text("Upload ZIP")',
            # Generic fallback: any element containing "ZIP"
            ':text("Upload ZIP File")',
        ]

        for sel in selectors:
            try:
                loc = page.locator(sel)
                if await loc.count() > 0 and await loc.first.is_visible():
                    zip_button = loc.first
                    print(f"  Found ZIP upload button: {sel}")
                    break
            except Exception:
                continue

        if not zip_button:
            # Last resort: find by evaluating DOM text content
            btn_index = await page.evaluate("""() => {
                const buttons = document.querySelectorAll('button, a, [role="button"]');
                for (let i = 0; i < buttons.length; i++) {
                    const text = buttons[i].textContent || '';
                    if (text.includes('ZIP') || text.includes('zip')) {
                        return i;
                    }
                }
                return -1;
            }""")
            if btn_index >= 0:
                zip_button = page.locator('button, a, [role="button"]').nth(btn_index)
                print(f"  Found ZIP button via DOM scan at index {btn_index}")

        if not zip_button:
            raise RuntimeError(
                "Could not find 'Upload ZIP File' button on the emoji image page. "
                "Check automation/screenshots/ for the page state."
            )

        # Click and handle file chooser
        print(f"  Uploading ZIP file ({zip_path.stat().st_size / 1024:.1f} KB)...")
        async with page.expect_file_chooser(timeout=15_000) as fc_info:
            await zip_button.click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(str(zip_path))

        # Wait for upload processing — ZIP extraction can take a while.
        # The page shows a spinner while processing; we poll until it disappears
        # or until images start appearing in the slots.
        print("  Waiting for ZIP processing...")
        await self._wait_for_zip_processing(page)

    # ── Verification ─────────────────────────────────────────────────────

    async def _verify_uploads(
        self,
        page: Page,
        tab_image: Path | None,
        emoji_images: list[Path],
    ) -> None:
        """Check how many slots now have images vs placeholders."""
        # Count filled upload slots by checking for actual images
        slot_info = await page.evaluate("""() => {
            // Count file inputs (each slot has one)
            const fileInputs = document.querySelectorAll('input[type="file"]');
            const totalSlots = fileInputs.length;

            // Count upload buttons still visible (empty slots show upload button)
            const uploadButtons = document.querySelectorAll('[id^="upload-button-"]');
            const emptySlots = uploadButtons.length;

            // Count actual images displayed
            const imgs = document.querySelectorAll('img[src*="blob:"], img[src*="data:"], canvas');
            const filledSlots = imgs.length;

            // Also try product-image-list-item approach
            const items = document.querySelectorAll('[data-test="product-images-list-item"]');
            let itemFilled = 0;
            let itemEmpty = 0;
            items.forEach(item => {
                const placeholder = item.querySelector('[data-test="no-product-image"]');
                const hasImg = item.querySelector('img');
                const hasCanvas = item.querySelector('canvas');
                if (hasImg || hasCanvas || !placeholder) itemFilled++;
                else itemEmpty++;
            });

            return {
                totalSlots,
                emptySlots,
                filledSlots,
                itemFilled,
                itemEmpty,
                itemTotal: items.length
            };
        }""")

        expected = (1 if tab_image else 0) + len(emoji_images)

        # Use whichever metric has data
        if slot_info["itemTotal"] > 0:
            filled = slot_info["itemFilled"]
            total = slot_info["itemTotal"]
        else:
            filled = slot_info["filledSlots"]
            total = slot_info["totalSlots"]

        print(
            f"  Upload verification: {filled}/{total} slots filled "
            f"(expected {expected})"
        )

        if filled < expected:
            print(
                f"  WARNING: Only {filled} of {expected} images uploaded successfully!"
            )
        else:
            print(f"  All {expected} images verified.")

    # ── Main Image ─────────────────────────────────────────────────────

    async def _set_main_image(
        self,
        page: Page,
        emoji_numbers: tuple[str, ...] = ("001", "002", "003", "004"),
    ) -> None:
        """Fill in the 4 Main Image input fields and click Save Main Image.

        The Main Image section has 4 text ``<input>`` fields where you type
        3-digit emoji numbers (e.g. "001").  LINE composes these into a
        2×2 thumbnail preview for the emoji set.

        Uses Playwright's native ``fill()`` method for each input, which
        properly triggers React/framework state updates (unlike direct
        JS value setters which only change the DOM).

        Args:
            page: Playwright page on the emoji image edit page.
            emoji_numbers: 4 emoji IDs to use for the main image.
        """
        print("  Setting Main Image...")

        # ── Debug: dump input field info ──────────────────────────────
        debug_info = await page.evaluate("""() => {
            const saveBtn = Array.from(
                document.querySelectorAll('button, a, [role="button"]')
            ).find(el => (el.textContent || '').includes('Save Main Image'));
            if (!saveBtn) return { found: false, reason: 'no Save Main Image button' };

            let section = saveBtn.parentElement;
            for (let i = 0; i < 8 && section; i++) {
                const inputs = section.querySelectorAll('input');
                const visible = Array.from(inputs).filter(
                    inp => inp.offsetParent !== null
                );
                if (visible.length >= 4) {
                    return {
                        found: true,
                        inputCount: visible.length,
                        sectionTag: section.tagName,
                        inputs: visible.slice(0, 6).map(inp => ({
                            type: inp.type,
                            name: inp.name || '',
                            id: inp.id || '',
                            placeholder: inp.placeholder || '',
                            value: inp.value,
                            className: inp.className.substring(0, 80),
                            maxLength: inp.maxLength,
                        })),
                    };
                }
                section = section.parentElement;
            }
            return { found: false, reason: 'fewer than 4 visible inputs near button' };
        }""")

        print(f"    Main Image DOM debug: {debug_info}")

        if not debug_info.get("found"):
            print(
                f"  WARNING: Could not find Main Image inputs: "
                f"{debug_info.get('reason')}"
            )

        # ── Mark the 4 inputs with temporary IDs for Playwright fill() ──
        marked = await page.evaluate("""() => {
            const saveBtn = Array.from(
                document.querySelectorAll('button, a, [role="button"]')
            ).find(el => (el.textContent || '').includes('Save Main Image'));
            if (!saveBtn) return 0;

            let section = saveBtn.parentElement;
            for (let i = 0; i < 8 && section; i++) {
                const inputs = Array.from(
                    section.querySelectorAll('input')
                ).filter(inp => {
                    // Visible, not hidden/file type
                    if (inp.offsetParent === null) return false;
                    if (inp.type === 'file' || inp.type === 'hidden') return false;
                    return true;
                });
                if (inputs.length >= 4) {
                    for (let j = 0; j < 4; j++) {
                        inputs[j].setAttribute(
                            'data-emoji-main-input', String(j)
                        );
                    }
                    return inputs.length;
                }
                section = section.parentElement;
            }
            return 0;
        }""")

        if marked < 4:
            print(f"  WARNING: Only marked {marked} inputs (need 4)")

        # ── Fill each input using Playwright's fill() ─────────────────
        filled_count = 0
        for i, num in enumerate(emoji_numbers[:4]):
            sel = f'input[data-emoji-main-input="{i}"]'
            loc = page.locator(sel)
            if await loc.count() > 0:
                await loc.click()
                await loc.fill("")  # clear first
                await loc.fill(num)
                await human_delay(300, 500)
                filled_count += 1
            else:
                print(f"    WARNING: Input #{i} not found ({sel})")

        if filled_count == 4:
            print(f"  Filled 4 main image inputs: {', '.join(emoji_numbers[:4])}")
        else:
            print(f"  WARNING: Only filled {filled_count}/4 main image inputs")

        await human_delay(500, 1000)

        # ── Click "Save Main Image" button ────────────────────────────
        save_btn = None
        for sel in [
            'button:has-text("Save Main Image")',
            'a:has-text("Save Main Image")',
            ':text("Save Main Image")',
        ]:
            try:
                loc = page.locator(sel)
                if await loc.count() > 0 and await loc.first.is_visible():
                    save_btn = loc.first
                    break
            except Exception:
                continue

        if save_btn:
            await save_btn.click()
            await human_delay(2000, 3000)

            # Handle any confirmation dialog (e.g. "Save this form?")
            try:
                ok_btn = page.locator('button:has-text("OK")')
                if await ok_btn.count() > 0 and await ok_btn.first.is_visible():
                    await ok_btn.first.click()
                    await human_delay(2000, 3000)
                    print("  Main Image — confirmed save dialog.")
            except Exception:
                pass

            print("  Main Image saved.")
        else:
            print("  WARNING: Could not find 'Save Main Image' button.")

        # ── Wait for the page to settle after save ────────────────────
        await human_delay(1000, 2000)

        # ── Take screenshot after main image save ─────────────────────
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        await page.screenshot(
            path=str(SCREENSHOT_DIR / f"emoji_main_image_{ts}.png"),
            full_page=True,
        )

    # ── Wait for ZIP processing ────────────────────────────────────────

    async def _wait_for_zip_processing(
        self, page: Page, timeout_ms: int = 120_000
    ) -> None:
        """Wait for the ZIP upload spinner to finish and images to load.

        The page shows a spinning loader while the server unpacks and validates
        images.  We poll every 2 seconds until either:
        - The spinner disappears, OR
        - At least one ``<img>`` with a real ``src`` appears in the slots, OR
        - We hit *timeout_ms*.
        """
        import asyncio
        import time

        start = time.monotonic()
        poll_interval = 2  # seconds
        last_status = ""

        while (time.monotonic() - start) * 1000 < timeout_ms:
            status = await page.evaluate("""() => {
                // Detect spinner — LINE uses an animated img or CSS spinner
                const spinners = document.querySelectorAll(
                    'img[src*="loading"], img[src*="spinner"], '
                    + '.spinner, .loading, [class*="spinner"], [class*="loading"]'
                );
                let spinnerVisible = false;
                for (const s of spinners) {
                    if (s.offsetParent !== null) { spinnerVisible = true; break; }
                }

                // Count real images in slots (exclude placeholders)
                const imgs = document.querySelectorAll(
                    '[data-test="product-images-list-item"] img'
                );
                let loadedImages = 0;
                for (const img of imgs) {
                    const src = img.getAttribute('src') || '';
                    // Real uploaded images use blob: URLs or https: URLs
                    if (src.startsWith('blob:') || src.startsWith('https:')
                        || src.startsWith('data:image/png')) {
                        loadedImages++;
                    }
                }

                // Also count slot items that have canvas elements (rendered previews)
                const canvases = document.querySelectorAll(
                    '[data-test="product-images-list-item"] canvas'
                );
                loadedImages += canvases.length;

                // Check for error banners
                const alerts = document.querySelectorAll(
                    '.alert-danger, .alert-error, [role="alert"]'
                );
                let errorText = null;
                for (const el of alerts) {
                    if (el.offsetParent !== null) {
                        errorText = el.textContent.trim().substring(0, 200);
                        break;
                    }
                }

                return { spinnerVisible, loadedImages, errorText };
            }""")

            spinner = status["spinnerVisible"]
            loaded = status["loadedImages"]
            error = status.get("errorText")

            msg = f"spinner={'YES' if spinner else 'no'}, images loaded={loaded}"
            if msg != last_status:
                elapsed = int(time.monotonic() - start)
                print(f"    [{elapsed}s] {msg}")
                last_status = msg

            if error:
                print(f"  ERROR from page: {error}")
                raise RuntimeError(f"ZIP upload failed: {error}")

            # Done when spinner is gone AND we have at least some images
            if not spinner and loaded >= 8:
                print(f"  ZIP processing complete: {loaded} images loaded.")
                return

            # Also done if no spinner and all slots are filled (even without img src detection)
            if not spinner:
                # Give a little extra time after spinner disappears
                await human_delay(3000, 5000)
                # Re-check
                recheck = await page.evaluate("""() => {
                    const items = document.querySelectorAll(
                        '[data-test="product-images-list-item"]'
                    );
                    let filled = 0;
                    items.forEach(item => {
                        const noImg = item.querySelector('[data-test="no-product-image"]');
                        if (!noImg) filled++;
                    });
                    return filled;
                }""")
                if recheck >= 8:
                    print(f"  ZIP processing complete: {recheck} slots filled.")
                    return

            await asyncio.sleep(poll_interval)

        elapsed = int(time.monotonic() - start)
        print(f"  WARNING: ZIP processing timed out after {elapsed}s")

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_image(self, directory: Path) -> Path | None:
        """Return the first PNG in *directory*, or None."""
        if not directory.exists():
            return None
        pngs = sorted(directory.glob("*.png"))
        return pngs[0] if pngs else None

    @staticmethod
    def _snap_to_valid_count(count: int) -> int:
        """Snap file count DOWN to largest valid LINE emoji count.

        Valid: 8, 16, 24, 32, 40. All slots must be filled.
        """
        valid = [8, 16, 24, 32, 40]
        best = valid[0]
        for v in valid:
            if v <= count:
                best = v
        return best

    async def _close_popup(self, page: Page) -> None:
        """Dismiss campaign popup if visible."""
        try:
            popup = page.locator(SEL_CAMPAIGN_POPUP_CLOSE)
            if await popup.count() > 0 and await popup.first.is_visible():
                await popup.first.click(timeout=3_000)
                await human_delay(500, 800)
        except Exception:
            pass
