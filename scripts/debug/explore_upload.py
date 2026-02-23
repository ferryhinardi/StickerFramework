#!/usr/bin/env python3
"""
Explorer: Click a sticker image slot to discover the upload mechanism.
Also explores Tag Settings interaction.
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

# Use a real sticker image for testing
SAMPLE_STICKER = (
    REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line" / "01_what.png"
)
SAMPLE_MAIN = REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line_main"
SAMPLE_TAB = REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line_tab"


async def capture_page(page, name: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ss_path = SCREENSHOT_DIR / f"{name}.png"
    await page.screenshot(path=str(ss_path), full_page=True)
    print(f"  Screenshot: {ss_path}")
    html_path = SCREENSHOT_DIR / f"{name}.html"
    html = await page.content()
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML: {html_path} ({len(html):,} chars)")
    return html


async def dump_elements(page, name: str):
    dump_path = SCREENSHOT_DIR / f"{name}_elements.json"
    elements = await page.evaluate("""() => {
        const result = {
            file_inputs: [],
            data_test: [],
            dialogs: [],
            images: [],
        };
        
        document.querySelectorAll('input[type="file"]').forEach((el, i) => {
            result.file_inputs.push({
                index: i,
                name: el.name || null,
                accept: el.accept || null,
                multiple: el.multiple,
                visible: el.offsetParent !== null,
                parentTag: el.parentElement?.tagName,
                parentClass: el.parentElement?.className,
            });
        });
        
        document.querySelectorAll('[data-test]').forEach((el, i) => {
            result.data_test.push({
                index: i,
                tag: el.tagName.toLowerCase(),
                dataTest: el.getAttribute('data-test'),
                visible: el.offsetParent !== null || el.style.display !== 'none',
                text: el.textContent?.trim().substring(0, 60) || null,
            });
        });
        
        // Find any modal/dialog that became visible
        document.querySelectorAll('.cm-modal, [role="dialog"], [aria-modal]').forEach((el, i) => {
            result.dialogs.push({
                index: i,
                ariaModal: el.getAttribute('aria-modal'),
                visible: el.offsetParent !== null,
                className: el.className?.substring(0, 100),
                childrenCount: el.children.length,
                innerHTML: el.innerHTML?.substring(0, 500),
            });
        });
        
        // Find img tags that appeared
        document.querySelectorAll('img[src*="sticker"], img[src*="upload"], img[src*="blob"]').forEach((el, i) => {
            result.images.push({
                index: i,
                src: el.src?.substring(0, 200),
                alt: el.alt,
                width: el.width,
                height: el.height,
            });
        });
        
        return result;
    }""")
    dump_path.write_text(json.dumps(elements, indent=2), encoding="utf-8")
    return elements


async def main():
    print("=" * 60)
    print("  LINE — Upload Mechanism Explorer")
    print("=" * 60)

    # Check sample files exist
    if not SAMPLE_STICKER.exists():
        print(f"WARNING: Sample sticker not found at {SAMPLE_STICKER}")
        # Try to find any sticker
        for pack in (REPO_ROOT / "packs").iterdir():
            test = pack / "final" / "line" / "01.png"
            if test.exists():
                print(f"  Using: {test}")
                sample = test
                break
        else:
            print("ERROR: No sample sticker found!")
            sample = None
    else:
        sample = SAMPLE_STICKER
        print(f"  Sample sticker: {sample}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(storage_state=str(STORAGE_STATE))
        page = await context.new_page()

        try:
            # Navigate
            print("\n[1] Navigating to management page...")
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

            # ── Try clicking the first sticker slot (index 0 = main) ──
            print("\n[3] Testing image upload mechanism...")
            print("  Clicking 'main' image placeholder...")

            # Set up file chooser listener BEFORE clicking
            # Playwright can intercept file chooser events
            async with page.expect_file_chooser(timeout=10_000) as fc_info:
                # Click the first placeholder (main image)
                main_placeholder = page.locator('[data-test="no-product-image"]').first
                await main_placeholder.click()

            file_chooser = fc_info.value
            print(f"  File chooser intercepted!")
            print(f"    Is multiple: {file_chooser.is_multiple()}")
            print(f"    Page URL: {file_chooser.page.url}")

            # Upload a test file
            if sample:
                print(f"  Setting file: {sample}")
                await file_chooser.set_files(str(sample))
                await asyncio.sleep(3)

                # Capture after upload
                await capture_page(page, "30_after_main_upload")
                elements = await dump_elements(page, "30_after_main_upload")
                print(f"  File inputs after upload: {len(elements['file_inputs'])}")
                print(f"  Images found: {len(elements['images'])}")
                for img in elements["images"]:
                    print(f"    - {img['src'][:100]} ({img['width']}x{img['height']})")
            else:
                # Cancel the file chooser
                print("  No sample file — canceling...")

            # ── Now try uploading to the 'tab' image slot ──
            print("\n[4] Clicking 'tab' image placeholder...")
            tab_placeholder = page.locator(
                '[data-test="no-product-image"]'
            ).first  # should be tab now

            # Check what's the key of the first remaining placeholder
            first_key = await page.evaluate("""() => {
                const items = document.querySelectorAll('[data-test="product-images-list-item"]');
                const result = [];
                items.forEach(item => {
                    const key = item.querySelector('[data-test="product-image-key"]');
                    const placeholder = item.querySelector('[data-test="no-product-image"]');
                    const hasImage = item.querySelector('img.cm-product-image');
                    result.push({
                        key: key ? key.textContent.trim() : null,
                        hasPlaceholder: !!placeholder,
                        hasImage: !!hasImage,
                    });
                });
                return result;
            }""")
            print(f"  Image slots status:")
            for slot in first_key:
                status = (
                    "HAS IMAGE"
                    if slot["hasImage"]
                    else ("EMPTY" if slot["hasPlaceholder"] else "???")
                )
                print(f"    {slot['key']}: {status}")

            # Upload tab image
            tab_dir = SAMPLE_TAB
            if tab_dir.exists():
                tab_pngs = sorted(tab_dir.glob("*.png"))
                if tab_pngs:
                    print(f"\n  Uploading tab image: {tab_pngs[0]}")
                    async with page.expect_file_chooser(timeout=10_000) as fc_info:
                        await tab_placeholder.click()
                    fc = fc_info.value
                    await fc.set_files(str(tab_pngs[0]))
                    await asyncio.sleep(3)
                    await capture_page(page, "31_after_tab_upload")

            # ── Upload a sticker image to slot 01 ──
            print("\n[5] Uploading sticker to slot 01...")
            # Re-check slots
            first_key = await page.evaluate("""() => {
                const items = document.querySelectorAll('[data-test="product-images-list-item"]');
                const result = [];
                items.forEach(item => {
                    const key = item.querySelector('[data-test="product-image-key"]');
                    const placeholder = item.querySelector('[data-test="no-product-image"]');
                    const hasImage = item.querySelector('img.cm-product-image');
                    result.push({
                        key: key ? key.textContent.trim() : null,
                        hasPlaceholder: !!placeholder,
                        hasImage: !!hasImage,
                    });
                });
                return result;
            }""")
            print(f"  Slots after tab upload:")
            for slot in first_key:
                status = (
                    "HAS IMAGE"
                    if slot["hasImage"]
                    else ("EMPTY" if slot["hasPlaceholder"] else "???")
                )
                print(f"    {slot['key']}: {status}")

            # Find and click the first empty sticker slot
            placeholders = page.locator('[data-test="no-product-image"]')
            count = await placeholders.count()
            print(f"  Remaining placeholders: {count}")

            if count > 0 and sample:
                async with page.expect_file_chooser(timeout=10_000) as fc_info:
                    await placeholders.first.click()
                fc = fc_info.value
                await fc.set_files(str(sample))
                await asyncio.sleep(3)
                await capture_page(page, "32_after_sticker_upload")

            # ── Now explore Tag Settings ──
            print("\n[6] Exploring Tag Settings...")
            await page.locator('[data-test="tab-tag"]').click()
            await asyncio.sleep(3)

            await capture_page(page, "33_tag_settings")
            tag_elements = await dump_elements(page, "33_tag_settings")

            # Get detailed tag UI structure
            tag_structure = await page.evaluate("""() => {
                const result = {
                    sections: [],
                    selectElements: [],
                    buttons: [],
                    stickerItems: [],
                };
                
                // All visible sections
                document.querySelectorAll('section, article, [class*="tag"]').forEach(el => {
                    if (el.offsetParent !== null) {
                        result.sections.push({
                            tag: el.tagName.toLowerCase(),
                            className: el.className?.substring(0, 100),
                            text: el.textContent?.trim().substring(0, 200),
                        });
                    }
                });
                
                // Find anything that looks like a tag selector
                document.querySelectorAll('select, [class*="tag"], [class*="emoji"]').forEach(el => {
                    if (el.tagName === 'SELECT') {
                        result.selectElements.push({
                            name: el.name,
                            options: Array.from(el.options).map(o => ({value: o.value, text: o.text})).slice(0, 10),
                        });
                    }
                });
                
                // Sticker items in tag view
                document.querySelectorAll('[data-test*="tag"], [data-test*="sticker"], [data-test*="emoji"]').forEach(el => {
                    result.stickerItems.push({
                        dataTest: el.getAttribute('data-test'),
                        tag: el.tagName.toLowerCase(),
                        text: el.textContent?.trim().substring(0, 100),
                        visible: el.offsetParent !== null,
                    });
                });
                
                return result;
            }""")

            print(f"  Tag sections: {len(tag_structure['sections'])}")
            print(f"  Select elements: {len(tag_structure['selectElements'])}")
            print(f"  Tag-related data-test: {len(tag_structure['stickerItems'])}")
            for item in tag_structure["stickerItems"]:
                print(f"    [{item['dataTest']}] <{item['tag']}> {item['text']}")

            # ── Explore Price Tier ──
            print("\n[7] Exploring Price Tier...")
            await page.locator('[data-test="tab-price"]').click()
            await asyncio.sleep(3)

            await capture_page(page, "34_price_tier")

            # Get price tier details
            price_info = await page.evaluate("""() => {
                const result = {
                    selects: [],
                    buttons: [],
                    dataTestElements: [],
                };
                
                document.querySelectorAll('select').forEach((el, i) => {
                    result.selects.push({
                        index: i,
                        name: el.name,
                        dataTest: el.getAttribute('data-test'),
                        className: el.className,
                        value: el.value,
                        options: Array.from(el.options).map(o => ({
                            value: o.value,
                            text: o.text.trim(),
                            selected: o.selected,
                        })),
                    });
                });
                
                document.querySelectorAll('[data-test]').forEach(el => {
                    if (el.getAttribute('data-test').includes('price') || 
                        el.getAttribute('data-test').includes('save') ||
                        el.getAttribute('data-test').includes('btn')) {
                        result.dataTestElements.push({
                            dataTest: el.getAttribute('data-test'),
                            tag: el.tagName.toLowerCase(),
                            text: el.textContent?.trim().substring(0, 80),
                            visible: el.offsetParent !== null,
                        });
                    }
                });
                
                return result;
            }""")

            print(f"  Price selects:")
            for s in price_info["selects"]:
                print(
                    f"    name={s['name']} dataTest={s['dataTest']} value={s['value']}"
                )
                for o in s["options"]:
                    sel = " *" if o["selected"] else ""
                    print(f"      {o['value']} = {o['text']}{sel}")

            print(f"  Price data-test elements:")
            for dt in price_info["dataTestElements"]:
                print(f"    [{dt['dataTest']}] <{dt['tag']}> {dt['text']}")

            # ── Summary ──
            print("\n" + "=" * 60)
            print("  UPLOAD MECHANISM EXPLORATION COMPLETE")
            print("=" * 60)

            print("\nBrowser staying open 20s for inspection...")
            await asyncio.sleep(20)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            await capture_page(page, "99_upload_error")
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
