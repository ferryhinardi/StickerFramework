#!/usr/bin/env python3
"""
Explorer: Create a test sticker draft and capture the management page.

This script:
1. Loads saved session
2. Navigates to the create page
3. Fills required fields with test data
4. Scrolls to bottom and clicks Save (data-test="btn-save")
5. Captures the resulting management page (HTML + screenshots)
6. Explores each tab if tabs exist
"""

import asyncio
import json
import sys
from pathlib import Path

# Ensure repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from playwright.async_api import async_playwright

STORAGE_STATE = Path.home() / ".line-sticker-automation" / "storage_state.json"
SCREENSHOT_DIR = REPO_ROOT / "automation" / "screenshots"
CREATE_URL = "https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/create"


async def capture_page(page, name: str):
    """Save screenshot + full HTML of the current page."""
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

    # Screenshot
    ss_path = SCREENSHOT_DIR / f"{name}.png"
    await page.screenshot(path=str(ss_path), full_page=True)
    print(f"  Screenshot: {ss_path}")

    # HTML
    html_path = SCREENSHOT_DIR / f"{name}.html"
    html = await page.content()
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML: {html_path} ({len(html):,} chars)")

    return html


async def dump_form_elements(page, name: str):
    """Dump all form-related elements for analysis."""
    dump_path = SCREENSHOT_DIR / f"{name}_elements.json"

    elements = await page.evaluate("""() => {
        const result = {
            inputs: [],
            selects: [],
            textareas: [],
            buttons: [],
            radios: [],
            checkboxes: [],
            file_inputs: [],
            links: [],
            tabs: [],
        };
        
        // All inputs
        document.querySelectorAll('input').forEach((el, i) => {
            result.inputs.push({
                index: i,
                type: el.type,
                name: el.name || null,
                value: el.value || null,
                id: el.id || null,
                className: el.className || null,
                dataTest: el.getAttribute('data-test') || null,
                checked: el.checked || false,
                disabled: el.disabled || false,
                visible: el.offsetParent !== null,
                placeholder: el.placeholder || null,
            });
        });
        
        // Radios separately for clarity
        document.querySelectorAll('input[type="radio"]').forEach((el, i) => {
            const label = el.closest('label');
            const labelText = label ? label.textContent.trim() : null;
            // Also check preceding/following text nodes
            const parent = el.parentElement;
            const parentText = parent ? parent.textContent.trim().substring(0, 100) : null;
            result.radios.push({
                index: i,
                name: el.name || null,
                value: el.value || null,
                checked: el.checked,
                labelText: labelText,
                parentText: parentText,
                dataTest: el.getAttribute('data-test') || null,
            });
        });
        
        // Checkboxes
        document.querySelectorAll('input[type="checkbox"]').forEach((el, i) => {
            const label = el.closest('label');
            result.checkboxes.push({
                index: i,
                name: el.name || null,
                value: el.value || null,
                checked: el.checked,
                labelText: label ? label.textContent.trim() : null,
            });
        });
        
        // File inputs
        document.querySelectorAll('input[type="file"]').forEach((el, i) => {
            result.file_inputs.push({
                index: i,
                name: el.name || null,
                accept: el.accept || null,
                multiple: el.multiple,
                dataTest: el.getAttribute('data-test') || null,
            });
        });
        
        // Selects
        document.querySelectorAll('select').forEach((el, i) => {
            const options = Array.from(el.options).map(opt => ({
                value: opt.value,
                text: opt.text.trim(),
                selected: opt.selected,
            }));
            result.selects.push({
                index: i,
                name: el.name || null,
                id: el.id || null,
                selectedValue: el.value,
                options: options.slice(0, 30),
                totalOptions: options.length,
            });
        });
        
        // Textareas
        document.querySelectorAll('textarea').forEach((el, i) => {
            result.textareas.push({
                index: i,
                name: el.name || null,
                id: el.id || null,
                value: el.value || null,
                placeholder: el.placeholder || null,
                maxLength: el.maxLength || null,
            });
        });
        
        // Buttons
        document.querySelectorAll('button, input[type="submit"]').forEach((el, i) => {
            result.buttons.push({
                index: i,
                tag: el.tagName.toLowerCase(),
                type: el.type || null,
                text: el.textContent?.trim().substring(0, 50) || null,
                className: el.className || null,
                dataTest: el.getAttribute('data-test') || null,
                visible: el.offsetParent !== null,
                disabled: el.disabled,
            });
        });
        
        // Tab-like links (for navigation)
        document.querySelectorAll('a[href*="sticker"], nav a, .tab, [role="tab"]').forEach((el, i) => {
            result.tabs.push({
                index: i,
                text: el.textContent?.trim().substring(0, 50) || null,
                href: el.href || null,
                className: el.className || null,
            });
        });
        
        // Links in the page
        document.querySelectorAll('a').forEach((el, i) => {
            if (el.href && el.href.includes('/sticker/')) {
                result.links.push({
                    index: i,
                    text: el.textContent?.trim().substring(0, 80) || null,
                    href: el.href || null,
                    className: el.className || null,
                });
            }
        });
        
        return result;
    }""")

    dump_path.write_text(json.dumps(elements, indent=2), encoding="utf-8")
    print(f"  Elements dump: {dump_path}")
    return elements


async def main():
    print("=" * 60)
    print("  LINE Creator Market — Create Draft Explorer")
    print("=" * 60)

    if not STORAGE_STATE.exists():
        print(f"ERROR: No saved session at {STORAGE_STATE}")
        print("Run the login test first!")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(storage_state=str(STORAGE_STATE))
        page = await context.new_page()

        try:
            # ── Step 1: Navigate to create page ──
            print("\n[Step 1] Navigating to create page...")
            await page.goto(CREATE_URL, wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(2)

            # Check if we got redirected to login
            if "login" in page.url.lower() or "access.line.me" in page.url:
                print("ERROR: Session expired! Need to re-login.")
                # Save screenshot for debugging
                await capture_page(page, "10_session_expired")
                sys.exit(1)

            print(f"  Current URL: {page.url}")

            # Close any campaign popup that might appear
            try:
                popup_close = page.locator("button.FnCloseDialogBtn")
                if await popup_close.count() > 0:
                    await popup_close.first.click(timeout=3_000)
                    print("  Closed campaign popup")
                    await asyncio.sleep(1)
            except Exception:
                pass

            # ── Step 2: Fill required fields ──
            print("\n[Step 2] Filling form fields...")

            # Title
            title_input = page.locator('input[name="meta[en][title]"]')
            await title_input.fill("Test Draft - Chubby Mochi Cat")
            print("  Filled title")

            # Description
            desc_input = page.locator('textarea[name="meta[en][description]"]')
            await desc_input.fill(
                "A cute chubby mochi cat sticker set for everyday use"
            )
            print("  Filled description")

            # Copyright
            copyright_input = page.locator('input[name="copyright"]')
            await copyright_input.fill("FHStudio")
            print("  Filled copyright")

            # Sticker type: static (should be default)
            static_radio = page.locator('input[name="sticker_type"][value="static"]')
            if not await static_radio.is_checked():
                await static_radio.click()
                print("  Selected static sticker type")
            else:
                print("  Static type already selected")

            # AI used: true
            ai_radio = page.locator('input[name="is_ai_generated"][value="true"]')
            if not await ai_radio.is_checked():
                await ai_radio.click()
                print("  Selected AI used: true")
            else:
                print("  AI used already selected")

            # Sale region: all
            region_radio = page.locator('input[name="area_group"][value="all"]')
            if not await region_radio.is_checked():
                await region_radio.click()
                print("  Selected sale region: all")
            else:
                print("  Sale region already selected")

            # Auto release: true
            auto_radio = page.locator('input[name="is_auto_release"][value="true"]')
            if not await auto_radio.is_checked():
                await auto_radio.click()
                print("  Selected auto release: true")
            else:
                print("  Auto release already selected")

            # ── Handle unnamed radios by section ──
            # We'll use JavaScript to find and click radios by their parent section context

            # Privacy: Show in LINE STORE (value="true")
            await page.evaluate("""() => {
                // Find the radio with value="true" that is near "LINE STORE" text
                // These are unnamed radios - we identify by section
                const sections = document.querySelectorAll('[data-test]');
                // Alternative: find all unnamed radios and match by context
            }""")

            # Style category - select "Cute" (value="1") from the second select
            selects = page.locator("select")
            select_count = await selects.count()
            print(f"  Found {select_count} select dropdowns")

            if select_count >= 2:
                # Index 1 should be style category
                await selects.nth(1).select_option("1")  # 1 = Cute
                print("  Selected style: Cute")

            if select_count >= 3:
                # Index 2 should be character category
                await selects.nth(2).select_option("10")  # 10 = Cats
                print("  Selected character: Cats")

            await asyncio.sleep(1)

            # ── Step 3: Capture filled form before submit ──
            print("\n[Step 3] Capturing filled form...")
            await capture_page(page, "11_create_filled")

            # ── Step 4: Scroll to bottom and find Save button ──
            print("\n[Step 4] Scrolling to Save button...")

            # Scroll to the submit area
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

            # Capture bottom of page
            await capture_page(page, "12_create_bottom")

            # Try to find and click Save
            save_btn = page.locator('[data-test="btn-save"]')
            save_count = await save_btn.count()
            print(f"  Save button count: {save_count}")

            if save_count > 0:
                is_visible = await save_btn.first.is_visible()
                is_enabled = await save_btn.first.is_enabled()
                print(f"  Save button visible: {is_visible}, enabled: {is_enabled}")

                # Get button's bounding box
                bbox = await save_btn.first.bounding_box()
                print(f"  Save button bounding box: {bbox}")

                if not is_visible:
                    print("  Button not visible — trying scroll into view...")
                    await save_btn.first.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    is_visible = await save_btn.first.is_visible()
                    print(f"  After scroll — visible: {is_visible}")

            # Also check the label wrapper
            save_label = page.locator('label.mdBtnLabel:has-text("Save")')
            label_count = await save_label.count()
            print(f"  Save label count: {label_count}")
            if label_count > 0:
                label_visible = await save_label.first.is_visible()
                print(f"  Save label visible: {label_visible}")

            # ── Step 5: Click Save ──
            print("\n[Step 5] Clicking Save...")

            try:
                # Strategy 1: Click the label (which wraps the submit input)
                await save_label.first.click(timeout=10_000)
                print("  Clicked Save label!")
            except Exception as e1:
                print(f"  Label click failed: {e1}")
                try:
                    # Strategy 2: Force click the input via JS
                    await page.evaluate("""() => {
                        const btn = document.querySelector('[data-test="btn-save"]');
                        if (btn) {
                            btn.click();
                            return true;
                        }
                        // Try form submit directly
                        const form = document.querySelector('form');
                        if (form) {
                            form.submit();
                            return true;
                        }
                        return false;
                    }""")
                    print("  Clicked via JS evaluate!")
                except Exception as e2:
                    print(f"  JS click also failed: {e2}")
                    # Strategy 3: Try the span.MdBtn01 parent
                    try:
                        await page.locator("span.MdBtn01.mdBtn01Cr01").click(
                            timeout=10_000
                        )
                        print("  Clicked parent span!")
                    except Exception as e3:
                        print(f"  All click strategies failed: {e3}")
                        await capture_page(page, "13_click_failed")
                        sys.exit(1)

            # ── Step 6: Handle "Save this form?" confirmation dialog ──
            print("\n[Step 6] Waiting for confirmation dialog...")

            # The dialog appears immediately after clicking Save
            # It has: "Save this form?" with OK and Cancel buttons
            confirm_ok = page.locator('[data-test="dialog-btn-ok"]')

            # Wait for ANY visible OK button (there are multiple cm-modal dialogs in DOM,
            # but only the active one is visible)
            try:
                # Wait for the dialog to become visible
                await page.locator(
                    '.cm-modal[aria-modal="true"] [data-test="dialog-btn-ok"]'
                ).click(timeout=10_000)
                print("  Clicked OK on confirmation dialog (aria-modal selector)!")
            except Exception:
                try:
                    # Fallback: find the visible OK button
                    ok_buttons = page.locator('[data-test="dialog-btn-ok"]')
                    count = await ok_buttons.count()
                    print(f"  Found {count} OK buttons, checking visibility...")
                    for i in range(count):
                        btn = ok_buttons.nth(i)
                        if await btn.is_visible():
                            await btn.click()
                            print(f"  Clicked visible OK button (index {i})!")
                            break
                    else:
                        # Last resort: click the primary confirm button
                        await page.locator(
                            "button.cm-confirm-button-primary:visible"
                        ).click(timeout=5_000)
                        print("  Clicked primary confirm button!")
                except Exception as e:
                    print(f"  WARNING: Could not click confirmation dialog: {e}")
                    # Take screenshot of the dialog state
                    await capture_page(page, "13_dialog_state")

            # Wait for navigation after confirming
            print("  Waiting for page navigation...")
            try:
                # After saving, we expect redirect to the sticker management page
                # URL pattern: /my/LQu3ADYzrcqp2KCs/sticker/<sticker_id>/...
                await page.wait_for_url("**/sticker/[0-9]*/**", timeout=15_000)
                print(f"  Redirected to: {page.url}")
            except Exception:
                # URL might not match the pattern exactly, just wait
                await asyncio.sleep(5)
                print(f"  Current URL: {page.url}")

            # Wait for page to settle
            await asyncio.sleep(3)

            # ── Step 7: Capture management page ──
            print("\n[Step 7] Capturing management page...")

            final_url = page.url
            print(f"  Final URL: {final_url}")

            html = await capture_page(page, "14_management_page")
            elements = await dump_form_elements(page, "14_management_page")

            # Print summary
            print(f"\n  Summary:")
            print(f"    Inputs: {len(elements['inputs'])}")
            print(f"    Radios: {len(elements['radios'])}")
            print(f"    Selects: {len(elements['selects'])}")
            print(f"    File inputs: {len(elements['file_inputs'])}")
            print(f"    Buttons: {len(elements['buttons'])}")
            print(f"    Tabs: {len(elements['tabs'])}")
            print(f"    Links: {len(elements['links'])}")

            # ── Step 8: Explore tabs if they exist ──
            print("\n[Step 8] Looking for navigation tabs...")

            # Try to find tab-like navigation
            tab_nav = await page.evaluate("""() => {
                const tabs = [];
                // Look for tab navigation patterns
                const navLinks = document.querySelectorAll(
                    '.tab-nav a, .tabs a, nav.sub-nav a, ' +
                    '.MdCMN01Tab a, [class*="tab"] a, ' +
                    'ul.nav-tabs a, ul.tabs a'
                );
                navLinks.forEach(a => {
                    tabs.push({
                        text: a.textContent.trim(),
                        href: a.href,
                        className: a.className,
                    });
                });
                
                // Also look for sections/headers
                const headers = document.querySelectorAll('h1, h2, h3, h4, .section-title');
                const sections = [];
                headers.forEach(h => {
                    sections.push({
                        tag: h.tagName,
                        text: h.textContent.trim().substring(0, 100),
                        className: h.className,
                    });
                });
                
                return { tabs, sections };
            }""")

            print(f"  Tab links found: {len(tab_nav['tabs'])}")
            for t in tab_nav["tabs"]:
                print(f"    - {t['text']} → {t['href']}")

            print(f"  Section headers found: {len(tab_nav['sections'])}")
            for s in tab_nav["sections"]:
                print(f"    - <{s['tag']}> {s['text']}")

            # If we see tabs, click through each one
            if tab_nav["tabs"]:
                for i, tab in enumerate(tab_nav["tabs"][:5]):
                    tab_name = tab["text"].replace(" ", "_").lower()[:20]
                    print(f"\n  Exploring tab: {tab['text']}...")
                    try:
                        await page.goto(
                            tab["href"], wait_until="networkidle", timeout=15_000
                        )
                        await asyncio.sleep(2)
                        await capture_page(page, f"15_tab_{i}_{tab_name}")
                        await dump_form_elements(page, f"15_tab_{i}_{tab_name}")
                    except Exception as e:
                        print(f"    Failed to explore tab: {e}")

            print("\n" + "=" * 60)
            print("  Exploration complete!")
            print(f"  Check screenshots in: {SCREENSHOT_DIR}")
            print("=" * 60)

            # Keep browser open for manual inspection
            print("\nBrowser will stay open for 30 seconds for manual inspection...")
            await asyncio.sleep(30)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            await capture_page(page, "99_error")
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
