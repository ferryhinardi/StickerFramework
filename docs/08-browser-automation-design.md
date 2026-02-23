# Browser Automation Design (Playwright)

> Technical design specification for automating LINE Creator Market sticker submissions using Playwright.
> **All selectors confirmed via live testing (Feb 2026).**

## Architecture Overview

### Design Principles

1. **Page Object Model** — Each LINE Creator Market page maps to a Python class in `automation/`
2. **Real selectors only** — All selectors verified against live site; no guessing
3. **Explicit waits** — Wait for specific elements/states via `human_delay()`, never hard `time.sleep()`
4. **Screenshot on failure** — Every failed operation captures a screenshot for debugging
5. **State persistence** — Session cookies saved to `~/.line-sticker-automation/storage_state.json`

### Module Structure

```
automation/
├── __init__.py                   # Package exports
├── config.py                     # URLs, ALL selectors, timeouts, defaults, categories
├── line_auth.py                  # OAuth login via access.line.me + session persistence
├── line_create_submission.py     # Create draft (single form + confirm dialog)
├── line_upload_images.py         # Per-slot image upload + count change + snap-DOWN
├── line_set_metadata.py          # Tag Settings tab (placeholder — needs more discovery)
├── line_set_price.py             # Price Tier tab
├── line_submit.py                # Consent JS tick + Request button + status check
└── utils.py                      # safe_click, safe_fill, retry, screenshot, progress

scripts/
├── line_uploader.py              # CLI entry point (5-step pipeline)
├── e2e_test.py                   # E2E integration test against real draft
└── debug/                        # Discovery/exploration scripts (5 files)
```

### Pipeline Flow

```
line_uploader.py (CLI)
      │
      ├── Load pack config (title, description, image paths)
      ├── Load submission defaults (from config.DEFAULTS)
      │
      ├── Step 1: line_auth.restore_session()
      │   └── If expired → line_auth.login() → save session
      │
      ├── Step 2: line_create_submission.create()
      │   └── Fills single form → Save → confirm dialog → returns sticker_id
      │
      ├── Step 3: line_upload_images.upload_all()
      │   └── Navigate to /image → set count → upload main+tab+stickers per-slot
      │
      ├── Step 4: line_set_price.set_price()
      │   └── Select price tier on management page
      │
      └── Step 5: line_submit.submit()  (if --submit flag)
          └── JS-tick consent → click Request → verify status
```

---

## Confirmed Selectors Reference

> Source of truth: `automation/config.py`. All confirmed via live DOM inspection.

### Login (access.line.me OAuth)

| Element        | Selector                |
| -------------- | ----------------------- |
| Email input    | `input[name="tid"]`     |
| Password input | `input[name="tpasswd"]` |
| Submit button  | `button.MdBtn01`        |

**Flow**: Navigate to `/signup/line_auth` → redirects to `access.line.me` → submit credentials → browser shows **verification code** → user enters code in LINE mobile app → browser redirects to dashboard.

### Create / Update Form (`/sticker/create` or `/sticker/{id}/update`)

Single-page form with ALL display info fields.

| Element              | Selector                                                                    |
| -------------------- | --------------------------------------------------------------------------- |
| Title (English)      | `input[name="meta[en][title]"]`                                             |
| Description          | `textarea[name="meta[en][description]"]`                                    |
| Copyright            | `input[name="copyright"]`                                                   |
| Sticker type (radio) | `input[name="sticker_type"][value="static"]`                                |
| AI generated (radio) | `input[name="is_ai_generated"][value="true"]`                               |
| Sale region (radio)  | `input[name="area_group"][value="all"]`                                     |
| Auto release (radio) | `input[name="is_auto_release"][value="true"]`                               |
| Style category       | 2nd `<select>` (index 1, no name attr), value e.g. `"1"` = Cute             |
| Character category   | 3rd `<select>` (index 2, no name attr), value e.g. `"10"` = Cats            |
| Save button          | `label.mdBtnLabel:has-text("Save")` (wraps hidden `[data-test="btn-save"]`) |
| Confirm dialog OK    | `.cm-modal[aria-modal="true"] [data-test="dialog-btn-ok"]`                  |
| Campaign popup close | `button.FnCloseDialogBtn`                                                   |

**Unnamed radio groups** (Privacy, Premium, Sticker Arranging, Trial Promotions, Includes Photos) — identified by section order within the form.

### Management Page (`/sticker/{id}`)

Read-only summary page with client-side tabs.

| Element                 | Selector                               |
| ----------------------- | -------------------------------------- |
| Display Information tab | `[data-test="tab-detail-information"]` |
| Sticker Images tab      | `[data-test="tab-image"]`              |
| Tag Settings tab        | `[data-test="tab-tag"]`                |
| Price Tier tab          | `[data-test="tab-price"]`              |
| Status badge            | `[data-test="product-status"]`         |
| Request button          | `[data-test="detail-btn-request"]`     |
| Consent section         | `[data-test="consent-part"]`           |

**Critical**: Request button is DISABLED until ALL image slots are filled.

### Image Edit Page (`/sticker/{id}/image`)

THE upload page — per-slot file inputs.

| Element                | Selector                                                         |
| ---------------------- | ---------------------------------------------------------------- |
| Sticker count select   | `[data-test="select-image-amount"]` (values: 8,16,24,32,40)      |
| Background color       | 2nd `<select>` (no `data-test`)                                  |
| Per-slot file input    | `#upload-file-input-{key}` (hidden, `accept="image/png"`)        |
| Per-slot upload button | `#upload-button-{key}` with `data-test="btn-upload"`             |
| Per-slot delete        | `[data-test="btn-delete"]` (within list item context)            |
| List item              | `[data-test="product-images-list-item"]`                         |
| Image key label        | `[data-test="product-image-key"]` (text: "main","tab","01"-"40") |
| Placeholder            | `[data-test="no-product-image"]`                                 |
| ZIP upload             | `input[name="file"]`                                             |
| Delete All             | `[data-test="delete-all-button"]`                                |
| Back button            | `[data-test="btn-back"]`                                         |

**Upload method**: `page.locator("#upload-file-input-{key}").set_input_files(path)` — confirmed working.

**Count change triggers confirmation dialog** → same OK selector as create form.

### Price Tier Tab

| Element      | Selector                          |
| ------------ | --------------------------------- |
| Price select | `[data-test="select-price-tier"]` |

Option values: `10006`=Rp7,200+, `1`=Rp12,000+, `2`=Rp23,000+, `3`=Rp35,000+, `4`=Rp45,000+, `5`=Rp59,000+

### Consent & Submit

| Element            | Selector                                                         |
| ------------------ | ---------------------------------------------------------------- |
| Consent checkboxes | `[data-test="consent-part"] .mdInputCheck` (2 hidden checkboxes) |

**Must use JS click** (`page.evaluate`) because checkboxes have `class="mdInputCheck"` and are CSS-hidden — Playwright `.click()` fails.

---

## Key Implementation Details

### Sticker Count Snap-DOWN Logic

LINE requires exactly 8, 16, 24, 32, or 40 stickers. ALL slots must be filled for the Request button to enable.

```
10 images → select 8 slots, upload first 8
16 images → select 16 slots, upload all 16
20 images → select 16 slots, upload first 16
 7 images → ERROR (minimum is 8)
```

The upload loop is limited to `target_count` images to prevent uploading to non-existent slots.

### Session Persistence

- Session saved to `~/.line-sticker-automation/storage_state.json` (28 cookies, 2 origins)
- Restored via `browser.new_context(storage_state=path)`
- Validated by checking redirect after navigating to `/my/` dashboard

### Consent Checkboxes

The 2 consent checkboxes ("I Agree" + "Get exclusive news") in `[data-test="consent-part"]` are CSS-hidden and must be clicked via JavaScript:

```python
await page.evaluate("""() => {
    const checkboxes = document.querySelectorAll('[data-test="consent-part"] .mdInputCheck');
    checkboxes.forEach(cb => { if (!cb.checked) cb.click(); });
}""")
```

---

## E2E Test Results

Tested against draft **43200641** with chubby-mochi-cat pack (10 stickers + main + tab):

| Step                                         | Status                    |
| -------------------------------------------- | ------------------------- |
| Session restore                              | PASS                      |
| Delete all images                            | PASS                      |
| Set sticker count (8→16 with confirm dialog) | PASS                      |
| Upload main + tab + 10 sticker images        | PASS (12/18 slots filled) |
| Set price tier Rp23,000+                     | PASS                      |
| Tick 2/2 consent checkboxes via JS           | PASS                      |
| Submit dry-run                               | PASS                      |

---

## Known Limitations

1. **Tag Settings** — The tag editing UI was empty during testing (may only appear after images are uploaded). Needs further exploration.
2. **Verification code** — Login requires manual entry of a verification code in the LINE mobile app. Cannot be automated.
3. **Unnamed radio groups** — Some form radios lack `name` attributes, requiring positional identification.
4. **AI browser automation** — Current approach uses hardcoded selectors. AI-powered fallback (browser-use) can be added later if LINE changes their HTML structure.
