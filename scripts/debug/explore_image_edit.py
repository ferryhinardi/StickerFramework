#!/usr/bin/env python3
"""
Explorer: Navigate to sticker image EDIT page and discover upload mechanism.
URL: /my/{creator}/sticker/{id}/image
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
IMAGE_EDIT_URL = (
    f"https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/{STICKER_ID}/image"
)

SAMPLE_STICKER = (
    REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line" / "01_what.png"
)
SAMPLE_MAIN = (
    REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line_main" / "main.png"
)
SAMPLE_TAB = REPO_ROOT / "packs" / "chubby-mochi-cat" / "final" / "line_tab" / "tab.png"


async def capture_page(page, name: str):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    ss_path = SCREENSHOT_DIR / f"{name}.png"
    await page.screenshot(path=str(ss_path), full_page=True)
    html_path = SCREENSHOT_DIR / f"{name}.html"
    html = await page.content()
    html_path.write_text(html, encoding="utf-8")
    print(f"  Captured: {ss_path.name} + {html_path.name} ({len(html):,} chars)")
    return html


async def dump_all_elements(page, name: str):
    dump_path = SCREENSHOT_DIR / f"{name}_elements.json"
    elements = await page.evaluate("""() => {
        const result = {
            inputs: [],
            file_inputs: [],
            selects: [],
            radios: [],
            buttons_visible: [],
            data_test: [],
            image_slots: [],
            sections: [],
        };
        
        // All inputs
        document.querySelectorAll('input').forEach((el, i) => {
            result.inputs.push({
                index: i,
                type: el.type,
                name: el.name || null,
                value: el.value || null,
                accept: el.accept || null,
                multiple: el.multiple || false,
                dataTest: el.getAttribute('data-test') || null,
                visible: el.offsetParent !== null,
                display: window.getComputedStyle(el).display,
                className: el.className || null,
            });
        });
        
        // File inputs specifically
        document.querySelectorAll('input[type="file"]').forEach((el, i) => {
            const parent = el.parentElement;
            const grandparent = parent?.parentElement;
            result.file_inputs.push({
                index: i,
                name: el.name || null,
                accept: el.accept || null,
                multiple: el.multiple,
                dataTest: el.getAttribute('data-test') || null,
                visible: el.offsetParent !== null,
                parentTag: parent?.tagName,
                parentClass: parent?.className?.substring(0, 100),
                grandparentClass: grandparent?.className?.substring(0, 100),
            });
        });
        
        // Selects
        document.querySelectorAll('select').forEach((el, i) => {
            const options = Array.from(el.options).map(o => ({
                value: o.value, text: o.text.trim(), selected: o.selected,
            }));
            result.selects.push({
                index: i,
                name: el.name || null,
                dataTest: el.getAttribute('data-test') || null,
                value: el.value,
                options: options,
            });
        });
        
        // Radios
        document.querySelectorAll('input[type="radio"]').forEach((el, i) => {
            const label = el.closest('label');
            result.radios.push({
                index: i,
                name: el.name || null,
                value: el.value || null,
                checked: el.checked,
                labelText: label ? label.textContent.trim().substring(0, 80) : null,
                dataTest: el.getAttribute('data-test') || null,
                visible: el.offsetParent !== null,
            });
        });
        
        // Visible buttons
        document.querySelectorAll('button, input[type="submit"], a.mdBtn').forEach((el, i) => {
            if (el.offsetParent !== null) {
                result.buttons_visible.push({
                    index: i,
                    tag: el.tagName.toLowerCase(),
                    text: el.textContent?.trim().substring(0, 60) || null,
                    dataTest: el.getAttribute('data-test') || null,
                    className: el.className?.substring(0, 100) || null,
                    href: el.href || null,
                });
            }
        });
        
        // data-test elements
        document.querySelectorAll('[data-test]').forEach((el, i) => {
            result.data_test.push({
                index: i,
                tag: el.tagName.toLowerCase(),
                dataTest: el.getAttribute('data-test'),
                visible: el.offsetParent !== null,
                text: el.textContent?.trim().substring(0, 80) || null,
            });
        });
        
        // Image slots / upload areas
        document.querySelectorAll(
            '[class*="image"], [class*="upload"], [class*="sticker"], [class*="drop"]'
        ).forEach((el, i) => {
            if (el.offsetParent !== null && i < 50) {
                result.image_slots.push({
                    index: i,
                    tag: el.tagName.toLowerCase(),
                    className: el.className?.substring(0, 150) || null,
                    dataTest: el.getAttribute('data-test') || null,
                    text: el.textContent?.trim().substring(0, 60) || null,
                    childFileInput: !!el.querySelector('input[type="file"]'),
                });
            }
        });
        
        // Sections / headers
        document.querySelectorAll('h1, h2, h3, section > h2, .section-title').forEach((el, i) => {
            result.sections.push({
                tag: el.tagName.toLowerCase(),
                text: el.textContent?.trim().substring(0, 100),
            });
        });
        
        return result;
    }""")

    dump_path.write_text(json.dumps(elements, indent=2), encoding="utf-8")
    print(f"  Elements: {dump_path.name}")
    return elements


async def main():
    print("=" * 60)
    print("  LINE — Image Edit Page Explorer")
    print(f"  URL: {IMAGE_EDIT_URL}")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=200)
        context = await browser.new_context(storage_state=str(STORAGE_STATE))
        page = await context.new_page()

        try:
            # Navigate to image edit page
            print("\n[1] Navigating to image edit page...")
            await page.goto(IMAGE_EDIT_URL, wait_until="networkidle", timeout=30_000)
            await asyncio.sleep(3)

            if "login" in page.url.lower():
                print("ERROR: Session expired!")
                sys.exit(1)

            print(f"  URL: {page.url}")

            # Close popup
            try:
                popup = page.locator("button.FnCloseDialogBtn")
                if await popup.count() > 0:
                    await popup.first.click(timeout=3_000)
                    await asyncio.sleep(1)
            except Exception:
                pass

            # ── Capture initial state ──
            print("\n[2] Capturing image edit page...")
            await capture_page(page, "40_image_edit_page")
            elements = await dump_all_elements(page, "40_image_edit_page")

            print(f"\n  === SUMMARY ===")
            print(f"  Inputs: {len(elements['inputs'])}")
            print(f"  File inputs: {len(elements['file_inputs'])}")
            print(f"  Selects: {len(elements['selects'])}")
            print(f"  Radios: {len(elements['radios'])}")
            print(f"  Visible buttons: {len(elements['buttons_visible'])}")
            print(f"  data-test elements: {len(elements['data_test'])}")

            print(f"\n  --- Radios ---")
            for r in elements["radios"]:
                print(
                    f"  [{r['index']}] name={r['name']!r} value={r['value']!r} checked={r['checked']} label={r['labelText']!r}"
                )

            print(f"\n  --- Selects ---")
            for s in elements["selects"]:
                print(
                    f"  [{s['index']}] name={s['name']!r} dataTest={s['dataTest']!r} value={s['value']}"
                )
                for o in s["options"]:
                    sel = " *" if o["selected"] else ""
                    print(f"    {o['value']} = {o['text']}{sel}")

            print(f"\n  --- File Inputs ---")
            for f in elements["file_inputs"]:
                print(
                    f"  [{f['index']}] name={f['name']!r} accept={f['accept']!r} multiple={f['multiple']} visible={f['visible']}"
                )
                print(f"    parent: <{f['parentTag']}> class={f['parentClass']}")

            print(f"\n  --- Visible Buttons ---")
            for b in elements["buttons_visible"]:
                print(
                    f"  [{b['index']}] <{b['tag']}> text={b['text']!r} dataTest={b['dataTest']!r} href={b.get('href', '')}"
                )

            print(f"\n  --- data-test elements ---")
            for dt in elements["data_test"]:
                if dt["visible"]:
                    print(
                        f"  [{dt['index']}] <{dt['tag']}> [{dt['dataTest']}] {dt['text']}"
                    )

            print(f"\n  --- Sections ---")
            for s in elements["sections"]:
                print(f"  <{s['tag']}> {s['text']}")

            # ── Look for sticker count selector (8 vs 16) ──
            print("\n\n[3] Looking for sticker count selector...")
            count_selector = await page.evaluate("""() => {
                // Search for radio/select that controls 8/16 sticker count
                const radios = document.querySelectorAll('input[type="radio"]');
                const countRadios = [];
                radios.forEach(r => {
                    if (r.value === '8' || r.value === '16' || r.value === '24' || r.value === '32' || r.value === '40') {
                        const label = r.closest('label');
                        countRadios.push({
                            name: r.name,
                            value: r.value,
                            checked: r.checked,
                            labelText: label ? label.textContent.trim() : null,
                            dataTest: r.getAttribute('data-test'),
                        });
                    }
                });
                
                // Also check selects with numeric options
                const selects = document.querySelectorAll('select');
                const countSelects = [];
                selects.forEach(s => {
                    const opts = Array.from(s.options);
                    const hasNumeric = opts.some(o => ['8','16','24','32','40'].includes(o.value));
                    if (hasNumeric) {
                        countSelects.push({
                            name: s.name,
                            dataTest: s.getAttribute('data-test'),
                            options: opts.map(o => ({value: o.value, text: o.text, selected: o.selected})),
                        });
                    }
                });
                
                return { countRadios, countSelects };
            }""")

            print(f"  Count radios: {len(count_selector['countRadios'])}")
            for r in count_selector["countRadios"]:
                print(
                    f"    name={r['name']} value={r['value']} checked={r['checked']} label={r['labelText']}"
                )

            print(f"  Count selects: {len(count_selector['countSelects'])}")
            for s in count_selector["countSelects"]:
                print(f"    name={s['name']} dataTest={s['dataTest']}")
                for o in s["options"]:
                    sel = " *" if o["selected"] else ""
                    print(f"      {o['value']} = {o['text']}{sel}")

            # ── Try clicking an image slot to test file chooser ──
            print("\n\n[4] Testing file upload on a slot...")

            placeholders = page.locator('[data-test="no-product-image"]')
            count = await placeholders.count()
            print(f"  Placeholder slots: {count}")

            if count > 0:
                print("  Clicking first placeholder with file chooser listener...")
                try:
                    async with page.expect_file_chooser(timeout=10_000) as fc_info:
                        await placeholders.first.click()
                    fc = fc_info.value
                    print(f"  FILE CHOOSER TRIGGERED! multiple={fc.is_multiple()}")

                    # Upload test file
                    if SAMPLE_MAIN.exists():
                        await fc.set_files(str(SAMPLE_MAIN))
                        print(f"  Uploaded: {SAMPLE_MAIN.name}")
                        await asyncio.sleep(5)
                        await capture_page(page, "41_after_upload")
                except Exception as e:
                    print(f"  File chooser NOT triggered: {e}")
                    # Maybe need to click something else first
                    await capture_page(page, "41_no_filechooser")

                    # Check what appeared
                    after_state = await page.evaluate("""() => {
                        const visible_modals = [];
                        document.querySelectorAll('.cm-modal, [role="dialog"], [aria-modal="true"]').forEach(m => {
                            if (m.offsetParent !== null || m.getAttribute('aria-modal') === 'true') {
                                visible_modals.push({
                                    className: m.className?.substring(0, 100),
                                    ariaModal: m.getAttribute('aria-modal'),
                                    text: m.textContent?.trim().substring(0, 200),
                                });
                            }
                        });
                        
                        // Check for file inputs that may have appeared
                        const fileInputs = document.querySelectorAll('input[type="file"]');
                        
                        return {
                            visible_modals,
                            fileInputCount: fileInputs.length,
                        };
                    }""")
                    print(f"  Visible modals: {len(after_state['visible_modals'])}")
                    for m in after_state["visible_modals"]:
                        print(f"    class={m['className']} text={m['text'][:100]}")
                    print(f"  File inputs: {after_state['fileInputCount']}")

            # ── Check for zip upload option ──
            print("\n\n[5] Looking for ZIP upload option...")
            zip_elements = await page.evaluate("""() => {
                const results = [];
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const text = el.textContent?.toLowerCase() || '';
                    if ((text.includes('zip') || text.includes('batch') || text.includes('bulk')) && 
                        el.children.length < 3 && text.length < 200) {
                        results.push({
                            tag: el.tagName.toLowerCase(),
                            text: el.textContent.trim().substring(0, 150),
                            className: el.className?.substring(0, 80),
                            visible: el.offsetParent !== null,
                        });
                    }
                }
                return results.slice(0, 10);
            }""")
            print(f"  ZIP-related elements: {len(zip_elements)}")
            for el in zip_elements:
                print(f"    <{el['tag']}> visible={el['visible']} text={el['text']}")

            print("\n" + "=" * 60)
            print("  Browser staying open 30s — inspect manually!")
            print("=" * 60)
            await asyncio.sleep(30)

        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback

            traceback.print_exc()
            await capture_page(page, "99_image_edit_error")
            await asyncio.sleep(10)
        finally:
            await context.close()
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
