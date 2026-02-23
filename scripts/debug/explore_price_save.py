#!/usr/bin/env python3
"""Explore the Price Tier tab save mechanism on draft 43202592."""

import asyncio
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from automation.config import SEL_TAB_PRICE_TIER, sticker_url, SCREENSHOT_DIR
from automation.line_auth import LineAuth
from automation.utils import human_delay


async def main():
    from playwright.async_api import async_playwright

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False, slow_mo=200)
        auth = LineAuth()
        context = await auth.restore_session(browser)
        page = await context.new_page()

        # Go to management page
        url = sticker_url("43202592")
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle")
        await human_delay(1000, 2000)

        # Click Price Tier tab
        await page.locator(SEL_TAB_PRICE_TIER).click()
        await human_delay(1000, 2000)

        # Take screenshot
        await page.screenshot(
            path=str(SCREENSHOT_DIR / "explore_price_tab.png"), full_page=True
        )

        # Dump all buttons, labels, inputs, and anchors on the price tab
        elements = await page.evaluate("""() => {
            const results = [];
            
            // Find all interactive elements
            const selectors = ['button', 'label', 'input[type="submit"]', 'a.mdBtn', 'a[data-test]', '[data-test]'];
            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 || el.type === 'hidden') {
                        results.push({
                            tag: el.tagName,
                            type: el.type || '',
                            text: (el.textContent || '').trim().slice(0, 100),
                            class: el.className.slice(0, 100),
                            id: el.id,
                            name: el.name || '',
                            dataTest: el.getAttribute('data-test') || '',
                            href: el.href || '',
                            visible: rect.width > 0 && rect.height > 0,
                            width: rect.width,
                            height: rect.height,
                        });
                    }
                });
            });
            return results;
        }""")

        print(f"\nFound {len(elements)} interactive elements on price tab:")
        for el in elements:
            vis = "VIS" if el["visible"] else "HID"
            text_preview = el["text"][:60] if el["text"] else ""
            print(
                f"  [{vis}] <{el['tag'].lower()}> dt={el['dataTest']} class={el['class'][:50]} text='{text_preview}'"
            )

        # Also look specifically for save/submit patterns
        save_elements = await page.evaluate("""() => {
            const results = [];
            const all = document.querySelectorAll('*');
            for (const el of all) {
                const text = (el.textContent || '').trim().toLowerCase();
                const dt = el.getAttribute('data-test') || '';
                if (
                    (text.includes('save') || text.includes('submit') || dt.includes('save') || dt.includes('submit')) &&
                    (el.tagName === 'BUTTON' || el.tagName === 'INPUT' || el.tagName === 'LABEL' || el.tagName === 'A')
                ) {
                    const rect = el.getBoundingClientRect();
                    results.push({
                        tag: el.tagName,
                        text: text.slice(0, 100),
                        class: el.className.slice(0, 80),
                        dataTest: dt,
                        visible: rect.width > 0 && rect.height > 0,
                        outerHTML: el.outerHTML.slice(0, 300),
                    });
                }
            }
            return results;
        }""")

        print(f"\n'Save/Submit' elements: {len(save_elements)}")
        for el in save_elements:
            vis = "VIS" if el["visible"] else "HID"
            print(
                f"  [{vis}] <{el['tag'].lower()}> dt={el['dataTest']} text='{el['text'][:60]}'"
            )
            print(f"         HTML: {el['outerHTML'][:200]}")

        print("\nKeeping browser open 30s for manual inspection...")
        await asyncio.sleep(30)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
