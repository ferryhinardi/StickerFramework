#!/usr/bin/env python3
"""
Explorer: Click image slot and observe what happens.
"""

import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from playwright.async_api import async_playwright

STORAGE_STATE = Path.home() / ".line-sticker-automation" / "storage_state.json"
SCREENSHOT_DIR = REPO_ROOT / "automation" / "screenshots"
STICKER_ID = "43200641"
MANAGEMENT_URL = f"https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/{STICKER_ID}"


async def capture_page(page, name: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ss_path = SCREENSHOT_DIR / f"{name}.png"
    await page.screenshot(path=str(ss_path), full_page=True)
    html_path = SCREENSHOT_DIR / f"{name}.html"
    html = await page.content()
    html_path.write_text(html, encoding="utf-8")
    print(f"  Captured: {ss_path.name} + {html_path.name} ({len(html):,} chars)")
    return html


async def main():
    print("=" * 60)
    print("  LINE — Image Click Explorer")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(storage_state=str(STORAGE_STATE))
        page = await context.new_page()

        try:
            print("\n[1] Navigating...")
            await page.goto(MANAGEMENT_URL, wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(2)

            # Close popup
            try:
                popup = page.locator("button.FnCloseDialogBtn")
                if await popup.count() > 0:
                    await popup.first.click(timeout=3_000)
                    await asyncio.sleep(1)
            except Exception:
                pass

            # Go to Sticker Images tab
            print("\n[2] Clicking Sticker Images tab...")
            await page.locator('[data-test="tab-image"]').click()
            await asyncio.sleep(2)

            # Check current state
            print("\n[3] State before click:")
            before_html = await page.content()

            # Count modals and their visibility
            modal_state = await page.evaluate("""() => {
                const modals = document.querySelectorAll('.cm-modal, [role="dialog"], [aria-modal]');
                return Array.from(modals).map((m, i) => ({
                    index: i,
                    ariaModal: m.getAttribute('aria-modal'),
                    visible: m.offsetParent !== null,
                    display: window.getComputedStyle(m).display,
                    className: m.className?.substring(0, 100),
                }));
            }""")
            print(f"  Modals: {len(modal_state)}")
            for m in modal_state:
                print(
                    f"    [{m['index']}] visible={m['visible']} display={m['display']} aria-modal={m['ariaModal']}"
                )

            # Click the FIRST placeholder (main image)
            print("\n[4] Clicking main image placeholder button...")
            main_btn = page.locator('[data-test="no-product-image"]').first
            await main_btn.click()
            await asyncio.sleep(3)

            # Check state after click
            print("  State after click:")
            after_html = await page.content()
            print(f"  HTML changed: {before_html != after_html}")
            print(f"  HTML size diff: {len(after_html) - len(before_html)}")

            # Check modals again
            modal_state_after = await page.evaluate("""() => {
                const modals = document.querySelectorAll('.cm-modal, [role="dialog"], [aria-modal]');
                return Array.from(modals).map((m, i) => ({
                    index: i,
                    ariaModal: m.getAttribute('aria-modal'),
                    visible: m.offsetParent !== null,
                    display: window.getComputedStyle(m).display,
                    className: m.className?.substring(0, 100),
                    innerHTML: m.innerHTML?.substring(0, 500),
                }));
            }""")
            print(f"  Modals after click: {len(modal_state_after)}")
            for m in modal_state_after:
                if m["visible"] or m["display"] != "none":
                    print(
                        f"    [{m['index']}] VISIBLE! aria-modal={m['ariaModal']} class={m['className']}"
                    )
                    print(f"      innerHTML: {m['innerHTML'][:200]}")

            # Check for newly appeared file inputs
            new_file_inputs = await page.evaluate("""() => {
                const inputs = document.querySelectorAll('input[type="file"]');
                return Array.from(inputs).map((el, i) => ({
                    index: i,
                    name: el.name,
                    accept: el.accept,
                    visible: el.offsetParent !== null,
                    display: window.getComputedStyle(el).display,
                    parentTag: el.parentElement?.tagName,
                    parentClass: el.parentElement?.className?.substring(0, 100),
                }));
            }""")
            print(f"  File inputs after click: {len(new_file_inputs)}")
            for fi in new_file_inputs:
                print(
                    f"    name={fi['name']} accept={fi['accept']} visible={fi['visible']} display={fi['display']}"
                )

            # Check for any overlay/popup that appeared
            new_elements = await page.evaluate("""() => {
                const result = [];
                // Check for popover, tooltip, upload area, or any newly visible element
                const candidates = document.querySelectorAll(
                    '.cm-modal-body, .cm-product-image-popup, ' +
                    '[class*="upload"], [class*="dialog"], [class*="popup"], ' +
                    '[class*="overlay"], [class*="drop"]'
                );
                candidates.forEach(el => {
                    result.push({
                        tag: el.tagName.toLowerCase(),
                        className: el.className?.substring(0, 200),
                        visible: el.offsetParent !== null,
                        display: window.getComputedStyle(el).display,
                        text: el.textContent?.trim().substring(0, 200),
                        innerHTML: el.innerHTML?.substring(0, 300),
                    });
                });
                return result;
            }""")
            print(f"\n  Upload/popup elements: {len(new_elements)}")
            for el in new_elements:
                print(f"    <{el['tag']}> class={el['className']}")
                print(f"      visible={el['visible']} display={el['display']}")
                print(f"      text: {el['text'][:100]}")

            await capture_page(page, "35_after_slot_click")

            # Also check the URL - maybe it navigates
            print(f"\n  Current URL: {page.url}")

            # Try double-clicking
            print("\n[5] Trying double-click on slot 01...")
            slot_01 = page.locator('[data-test="product-images-list-item"]').nth(
                2
            )  # 0=main, 1=tab, 2=01
            await slot_01.dblclick()
            await asyncio.sleep(3)

            await capture_page(page, "36_after_dblclick")

            # Check for file inputs again
            new_fi = await page.evaluate("""() => {
                return document.querySelectorAll('input[type="file"]').length;
            }""")
            print(f"  File inputs after dblclick: {new_fi}")

            # Check full DOM for any input file
            all_inputs = await page.evaluate("""() => {
                const all = document.querySelectorAll('input');
                return Array.from(all).map(el => ({
                    type: el.type,
                    name: el.name,
                    visible: el.offsetParent !== null,
                })).filter(x => x.type === 'file');
            }""")
            print(f"  All file type inputs in DOM: {len(all_inputs)}")

            print("\nBrowser staying open 30s for manual inspection...")
            print("Try clicking on image slots manually to observe behavior.")
            await asyncio.sleep(30)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            await capture_page(page, "99_click_error")
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
