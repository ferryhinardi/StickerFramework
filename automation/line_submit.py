"""
Final review and submission module for LINE Creator Market.

Navigates to the management page, ticks the consent checkbox,
takes a pre-submission screenshot, then clicks the "Request" button
(or skips in dry-run mode).

Confirmed structure (Feb 2026):
- Management page: /my/{creator}/sticker/{id}
- Status badge: [data-test="product-status"] (text: "Editing")
- Request button: [data-test="detail-btn-request"]
  (disabled until all images uploaded + consent checked)
- Consent section: [data-test="consent-part"]
  - 2 checkboxes: "I Agree" + "Get exclusive news..."
- After clicking Request: confirmation dialog
  [data-test="confirm-dialog-request"] with OK/Cancel
"""

from __future__ import annotations

from datetime import datetime

from playwright.async_api import Page

from automation.config import (
    SAVE_TIMEOUT,
    SCREENSHOT_DIR,
    SEL_CONFIRM_OK,
    SEL_CONFIRM_OK_FALLBACK,
    SEL_CONSENT_PART,
    SEL_REQUEST_BTN,
    SEL_STATUS_BADGE,
    sticker_url,
)
from automation.utils import human_delay, screenshot_on_failure


class LineSubmit:
    """Handles final review and submission of a sticker pack."""

    async def submit(
        self,
        page: Page,
        sticker_id: str,
        dry_run: bool = False,
    ) -> None:
        """
        Submit the sticker pack for review.

        Args:
            page: Playwright Page (authenticated).
            sticker_id: LINE sticker ID.
            dry_run: If True, take screenshot but do NOT click Request.
        """
        async with screenshot_on_failure(page, "submit"):
            # Navigate to management page — use load to ensure JS hydration
            await page.goto(sticker_url(sticker_id), wait_until="load")
            await human_delay(2000, 3000)

            # Close popup
            await self._close_popup(page)

            # Wait for status badge to appear (ensures page is hydrated)
            try:
                await page.locator(SEL_STATUS_BADGE).wait_for(
                    state="visible", timeout=SAVE_TIMEOUT
                )
            except Exception:
                pass

            # Check current status
            status = await self._get_status(page)
            print(f"  Current status: {status}")

            if "review" in status.lower() or "approved" in status.lower():
                print("  Already submitted or approved — skipping.")
                return

            # Tick consent checkboxes
            await self._tick_consent(page)

            # Take pre-submission screenshot
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ss_path = SCREENSHOT_DIR / f"pre_submit_{timestamp}.png"
            await page.screenshot(path=str(ss_path), full_page=True)
            print(f"  Pre-submit screenshot: {ss_path}")

            if dry_run:
                print("  DRY RUN: Would click 'Request' button. Skipping.")
                return

            # Check if Request button is enabled
            request_btn = page.locator(SEL_REQUEST_BTN)
            btn_classes = await request_btn.get_attribute("class") or ""
            if "disabled" in btn_classes:
                print(
                    "  ERROR: Request button is disabled. "
                    "Ensure all images are uploaded and consent is checked."
                )
                return

            # Click Request
            await request_btn.click()
            await human_delay(1000, 2000)

            # Handle confirmation dialog
            try:
                await page.locator(SEL_CONFIRM_OK).click(timeout=SAVE_TIMEOUT)
            except Exception:
                try:
                    await page.locator(SEL_CONFIRM_OK_FALLBACK).click(timeout=5_000)
                except Exception:
                    print("  WARNING: Could not find confirmation dialog.")

            await human_delay(2000, 3000)

            # Verify new status — reload page to get settled state
            await page.goto(sticker_url(sticker_id), wait_until="load")
            await human_delay(2000, 3000)
            new_status = await self._get_status(page)
            print(f"  New status: {new_status}")

            if "review" in new_status.lower() or "waiting" in new_status.lower():
                print("  Submission successful!")
            else:
                print(f"  WARNING: Expected 'Waiting for review', got: {new_status}")

    # ── Helpers ───────────────────────────────────────────────────────────

    async def _get_status(self, page: Page) -> str:
        """Read the current sticker status from the badge."""
        try:
            badge = page.locator(SEL_STATUS_BADGE)
            if await badge.count() > 0:
                return (await badge.text_content()) or "Unknown"
        except Exception:
            pass
        return "Unknown"

    async def _tick_consent(self, page: Page) -> None:
        """Tick the consent checkboxes in the Terms of Agreement section.

        The checkboxes have class 'mdInputCheck' and are visually hidden
        (styled via CSS). We use JavaScript to click them directly.
        Scrolls to bottom first to ensure the section is in the DOM.
        """
        # Scroll to bottom to ensure consent section is rendered
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await human_delay(1000, 1500)

        try:
            ticked = await page.evaluate("""() => {
                // Try data-test selector first
                let section = document.querySelector('[data-test="consent-part"]');
                // Fallback: look for any consent/agree section
                if (!section) {
                    const allSections = document.querySelectorAll('[class*="consent"], [class*="agree"], [class*="terms"]');
                    if (allSections.length > 0) section = allSections[0];
                }
                if (!section) {
                    // Last resort: find all checkboxes on page
                    const allCbs = document.querySelectorAll('input[type="checkbox"]');
                    if (allCbs.length === 0) return { found: false, ticked: 0 };
                    let ticked = 0;
                    allCbs.forEach(cb => {
                        if (!cb.checked) { cb.click(); ticked++; }
                    });
                    return { found: true, total: allCbs.length, ticked, method: 'all_checkboxes' };
                }
                const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                let ticked = 0;
                checkboxes.forEach(cb => {
                    if (!cb.checked) { cb.click(); ticked++; }
                });
                return { found: true, total: checkboxes.length, ticked, method: 'consent_section' };
            }""")
            if ticked.get("found"):
                method = ticked.get("method", "unknown")
                print(
                    f"  Ticked {ticked['ticked']}/{ticked['total']} consent checkboxes (via {method})"
                )
            else:
                print("  WARNING: Consent section not found — no checkboxes on page")
        except Exception as e:
            print(f"  WARNING: Could not tick consent: {e}")

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
