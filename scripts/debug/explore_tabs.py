#!/usr/bin/env python3
"""
Explorer: Navigate to existing draft and capture each management tab.

Uses the draft created by explore_create_and_manage.py (sticker 43200641).
Clicks through Sticker Images, Tag Settings, and Price Tier tabs.
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
    print(f"  Screenshot: {ss_path}")
    html_path = SCREENSHOT_DIR / f"{name}.html"
    html = await page.content()
    html_path.write_text(html, encoding="utf-8")
    print(f"  HTML: {html_path} ({len(html):,} chars)")
    return html


async def dump_form_elements(page, name: str):
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
            data_test_elements: [],
        };
        
        document.querySelectorAll('input').forEach((el, i) => {
            const label = el.closest('label');
            const section = el.closest('section, article, [data-test]');
            result.inputs.push({
                index: i,
                type: el.type,
                name: el.name || null,
                value: el.value || null,
                id: el.id || null,
                className: el.className || null,
                dataTest: el.getAttribute('data-test') || null,
                accept: el.accept || null,
                multiple: el.multiple || false,
                checked: el.checked || false,
                disabled: el.disabled || false,
                visible: el.offsetParent !== null,
                labelText: label ? label.textContent.trim().substring(0, 80) : null,
                sectionDataTest: section ? section.getAttribute('data-test') : null,
            });
        });
        
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
                className: el.className || null,
                dataTest: el.getAttribute('data-test') || null,
                selectedValue: el.value,
                options: options,
            });
        });
        
        document.querySelectorAll('textarea').forEach((el, i) => {
            result.textareas.push({
                index: i,
                name: el.name || null,
                id: el.id || null,
                value: el.value || null,
                placeholder: el.placeholder || null,
            });
        });
        
        document.querySelectorAll('input[type="file"]').forEach((el, i) => {
            const parent = el.parentElement;
            const section = el.closest('[data-test]');
            result.file_inputs.push({
                index: i,
                name: el.name || null,
                accept: el.accept || null,
                multiple: el.multiple,
                dataTest: el.getAttribute('data-test') || null,
                parentClass: parent ? parent.className : null,
                sectionDataTest: section ? section.getAttribute('data-test') : null,
                parentHTML: parent ? parent.outerHTML.substring(0, 200) : null,
            });
        });
        
        // All elements with data-test
        document.querySelectorAll('[data-test]').forEach((el, i) => {
            result.data_test_elements.push({
                index: i,
                tag: el.tagName.toLowerCase(),
                dataTest: el.getAttribute('data-test'),
                text: el.textContent?.trim().substring(0, 60) || null,
                visible: el.offsetParent !== null || el.style.display !== 'none',
                className: el.className || null,
            });
        });
        
        document.querySelectorAll('button, input[type="submit"]').forEach((el, i) => {
            if (el.offsetParent !== null) {
                result.buttons.push({
                    index: i,
                    tag: el.tagName.toLowerCase(),
                    type: el.type || null,
                    text: el.textContent?.trim().substring(0, 60) || null,
                    className: el.className || null,
                    dataTest: el.getAttribute('data-test') || null,
                    disabled: el.disabled,
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
    print("  LINE Creator Market — Tab Explorer")
    print(f"  Sticker ID: {STICKER_ID}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(storage_state=str(STORAGE_STATE))
        page = await context.new_page()

        try:
            # Navigate to management page
            print("\n[1] Navigating to management page...")
            await page.goto(MANAGEMENT_URL, wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(2)

            if "login" in page.url.lower():
                print("ERROR: Session expired!")
                sys.exit(1)

            print(f"  URL: {page.url}")

            # Close any popup
            try:
                popup = page.locator("button.FnCloseDialogBtn")
                if await popup.count() > 0:
                    await popup.first.click(timeout=3_000)
                    print("  Closed popup")
                    await asyncio.sleep(1)
            except Exception:
                pass

            # ── Capture Display Information tab (default) ──
            print("\n[2] Capturing Display Information tab (default)...")
            await capture_page(page, "20_tab_display_info")
            elements = await dump_form_elements(page, "20_tab_display_info")
            print(f"  data-test elements: {len(elements['data_test_elements'])}")

            # ── Click and capture Sticker Images tab ──
            print("\n[3] Clicking Sticker Images tab...")
            await page.locator('[data-test="tab-image"]').click()
            await asyncio.sleep(3)
            await page.wait_for_load_state("networkidle")

            print(f"  URL: {page.url}")
            await capture_page(page, "21_tab_sticker_images")
            img_elements = await dump_form_elements(page, "21_tab_sticker_images")

            print(f"  File inputs: {len(img_elements['file_inputs'])}")
            for f in img_elements["file_inputs"]:
                print(
                    f"    - name={f['name']} accept={f['accept']} dataTest={f['dataTest']}"
                )

            print(f"  Buttons: {len(img_elements['buttons'])}")
            for b in img_elements["buttons"]:
                if b["dataTest"]:
                    print(f"    - [{b['dataTest']}] {b['text']}")

            # ── Click and capture Tag Settings tab ──
            print("\n[4] Clicking Tag Settings tab...")
            await page.locator('[data-test="tab-tag"]').click()
            await asyncio.sleep(3)
            await page.wait_for_load_state("networkidle")

            print(f"  URL: {page.url}")
            await capture_page(page, "22_tab_tag_settings")
            tag_elements = await dump_form_elements(page, "22_tab_tag_settings")

            print(f"  Selects: {len(tag_elements['selects'])}")
            for s in tag_elements["selects"]:
                print(
                    f"    - name={s['name']} dataTest={s['dataTest']} options: {s['options'][:5]}"
                )

            print(f"  data-test elements: {len(tag_elements['data_test_elements'])}")
            for dt in tag_elements["data_test_elements"]:
                if (
                    "tag" in dt["dataTest"].lower()
                    or "sticker" in dt["dataTest"].lower()
                    or "emoji" in dt["dataTest"].lower()
                ):
                    print(f"    - [{dt['dataTest']}] <{dt['tag']}> {dt['text']}")

            # ── Click and capture Price Tier tab ──
            print("\n[5] Clicking Price Tier tab...")
            await page.locator('[data-test="tab-price"]').click()
            await asyncio.sleep(3)
            await page.wait_for_load_state("networkidle")

            print(f"  URL: {page.url}")
            await capture_page(page, "23_tab_price_tier")
            price_elements = await dump_form_elements(page, "23_tab_price_tier")

            print(f"  Inputs: {len(price_elements['inputs'])}")
            for inp in price_elements["inputs"]:
                if inp["visible"] and inp["type"] != "hidden":
                    print(
                        f"    - name={inp['name']} type={inp['type']} value={inp['value']} dataTest={inp['dataTest']}"
                    )

            print(
                f"  Radios: {len(price_elements['radios']) if 'radios' in price_elements else 0}"
            )
            print(f"  Selects: {len(price_elements['selects'])}")
            for s in price_elements["selects"]:
                print(
                    f"    - name={s['name']} dataTest={s['dataTest']} selected={s['selectedValue']}"
                )
                for o in s["options"][:10]:
                    sel = " *" if o["selected"] else ""
                    print(f"      {o['value']} = {o['text']}{sel}")

            # ── Also check Terms of Agreement ──
            print("\n[6] Checking Terms of Agreement...")
            # Go back to display info tab first
            await page.locator('[data-test="tab-detail-information"]').click()
            await asyncio.sleep(2)

            # Check for agreement checkboxes
            agreement = await page.evaluate("""() => {
                const section = document.querySelector('[data-test="consent-part"]');
                if (!section) return { found: false };
                
                const checkboxes = section.querySelectorAll('input[type="checkbox"]');
                const result = {
                    found: true,
                    html: section.outerHTML.substring(0, 2000),
                    checkboxes: [],
                };
                checkboxes.forEach((cb, i) => {
                    const label = cb.closest('label') || cb.parentElement;
                    result.checkboxes.push({
                        index: i,
                        name: cb.name || null,
                        checked: cb.checked,
                        labelText: label ? label.textContent.trim().substring(0, 100) : null,
                        dataTest: cb.getAttribute('data-test') || null,
                    });
                });
                return result;
            }""")

            print(f"  Agreement section found: {agreement['found']}")
            if agreement["found"]:
                print(f"  Checkboxes: {len(agreement['checkboxes'])}")
                for cb in agreement["checkboxes"]:
                    print(f"    - checked={cb['checked']} label={cb['labelText']}")

            # ── Summary ──
            print("\n" + "=" * 60)
            print("  TAB EXPLORATION COMPLETE")
            print("=" * 60)
            print(f"  Management URL: {MANAGEMENT_URL}")
            print(f"  Sticker Images: {len(img_elements['file_inputs'])} file inputs")
            print(f"  Tag Settings: {len(tag_elements['selects'])} selects")
            print(
                f"  Price Tier: {len(price_elements['selects'])} selects, {len(price_elements['inputs'])} inputs"
            )

            print("\nBrowser will stay open for 20 seconds...")
            await asyncio.sleep(20)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            await capture_page(page, "99_tab_error")
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
