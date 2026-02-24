# Cappy the Chill Capybara Vol.2: Sassy Replies — Production Progress

> **Purpose**: Resume-friendly checklist. If you hit `Request Entity Too Large`,
> just pick up from the next unchecked `[ ]` item.
>
> **Last updated**: 2026-02-24

---

## Phase 0: Generation (COMPLETE)

- [x] Character design & pack_config.py
- [x] DALL-E prompt engineering (`dalle_prompts.md`)
- [x] Pack metadata (`pack_metadata.json`)
- [x] Fixed `comfyui_generator.py` — dynamic emotion/props (was hardcoded to "sleepy")
- [x] Fixed negative prompt — removed sleepy-specific anti-awake entries
- [x] Generated all 16 stickers via ComfyUI (DreamShaperXL_Turbo_v2_1, 8 steps, CFG 2.0)
- [x] All 16 PNGs + 16 `.prompt.txt` files in `raw/`
  - Batch 1: 01-05, Batch 2: 06-13, Batch 3: 14-16

---

## Phase 1: Quality Review — SKIPPED (ComfyUI individual generation)

> ComfyUI generates individual stickers (not composite sheets), so the
> split/review/rename workflow is not needed. Each sticker was reviewed
> during generation. Quality is consistent across all 16.

---

## Phase 2: Re-generate Problematic Stickers — N/A

> No stickers needed regeneration.

---

## Phase 3: Fix Split Directory — N/A

> Not applicable — ComfyUI generates individual files directly into `raw/`.

---

## Phase 4: Post-Processing Pipeline (COMPLETE)

### 4A: Background Removal

- [x] Process from `raw/` — all 16 backgrounds removed (custom flood-fill from corners)
- [x] Verified: all outputs RGBA with transparent backgrounds
- [x] No character parts accidentally removed

### 4B: White Outline Addition (10px)

- [x] White outlines applied (10px, via PIL MaxFilter alpha dilation)
- [x] Outlines clean and consistent across all stickers

### 4C: Color Normalization

- [x] Applied: saturation=1.15, brightness=1.05, contrast=1.05
- [x] Colors vibrant, brown body color warm and consistent

### 4D: Multi-Platform Resize & Export

- [x] **LINE** — 16 PNGs, 370x320, all < 300KB (largest: 14_deal_with_it at 140.5KB)
- [x] **WhatsApp** — 16 WEBPs, 512x512, all < 100KB (largest: 14_deal_with_it at 98.5KB)
- [x] **Telegram** — 16 WEBPs, 512x512
- [x] **iMessage** — 16 PNGs, 618x618
- [x] **Print/Etsy** — 16 PNGs, 2048x2048

### 4E: Verify Outputs

- [x] All 5 platforms have exactly 16 files each
- [x] No file exceeds its platform size limit
- [x] Filenames consistent: `01_omg` through `16_miss_you` across all platforms

---

## Phase 5: Tray/Tab Icons (COMPLETE)

- [x] Chose `12_hug` as tray icon source (arms wide open = clear silhouette at tiny sizes)
- [x] **LINE main** — `final/line_main/main.png` (240x240 PNG, 57.8KB)
- [x] **LINE tab** — `final/line_tab/tab.png` (96x74 PNG, 9.3KB)
- [x] **WhatsApp tray** — `final/whatsapp_tray/tray.webp` (96x96 WEBP, 5.8KB)

---

## Phase 6: Pre-flight Checks (COMPLETE)

- [x] Run LINE preflight checker (strict mode) — **PASSED**
  ```
  python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara-2 --strict
  ```
- [x] Verified no guideline violations (especially rule 3.13 — no religious content)
- [x] Verified `pack_metadata.json` is complete and accurate
- [x] Verified sticker_count matches actual file count — 16

---

## Phase 7: Package for Distribution (IN PROGRESS)

### 7A: Print / Etsy (COMPLETE)

- [x] Confirmed `final/print_etsy/` has 16 PNGs (2048x2048)
- [x] Generated print sheets (US Letter 2550x3300 + A4 2480x3508 at 300 DPI)
- [x] Generated social preview (3000x3000)
- [x] Packaged as ZIP in `dist/` (29.8MB)
  ```
  dist/cappy_the_chill_capybara_vol.2_digital_download.zip
  dist/sheets/sticker_sheet_letter.png
  dist/sheets/sticker_sheet_a4.png
  dist/social_preview.png
  ```

### 7B: LINE Creator Market (COMPLETE — Waiting for Review)

- [x] Confirmed `final/line/` has exactly 16 PNGs (370x320, RGBA, all < 300KB)
- [x] Confirmed main image exists (240x240)
- [x] Confirmed tab image exists (96x74)
- [x] Upload to LINE Creator Studio — Sticker ID: **43218066**
- [x] LINE metadata filled (title, description, category=Other, price=Rp23,000+, style=Cute)
- [x] Submitted for review (2026-02-24)
- URL: https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/43218066
- Note: Old draft 43217995 still exists (character category was "Not Set") — delete manually

### 7C: WhatsApp (via Sticker.ly)

- [x] Confirmed `final/whatsapp/` has 16 WEBPs (512x512, all < 100KB)
- [x] Confirmed tray icon exists (96x96, 5.8KB < 50KB)
- [ ] Upload via Sticker.ly app
- [ ] Pack name, author, tags set
- [ ] Published

### 7D: Telegram

- [x] Confirmed `final/telegram/` has 16 WEBPs (512x512)
- [ ] Run Telegram publisher or manual upload via @Stickers bot
- [ ] Set sticker emojis from pack_config.py emoji field

### 7E: iMessage

- [x] Confirmed `final/imessage_large/` has 16 PNGs (618x618)
- [ ] Run iMessage preparer
- [ ] Open Xcode project, configure signing, archive & submit to App Store

---

## Phase 8: Final Verification

- [ ] All 5 platforms uploaded / submitted
- [ ] `pack_metadata.json` updated with submission status for all platforms
- [ ] No temp files or duplicates left behind
- [ ] All files committed to git

---

## Quick Reference: File Structure

```
packs/cappy-capybara-2/
├── pack_config.py          # Character + sticker definitions
├── pack_metadata.json      # Pack metadata for all platforms
├── dalle_prompts.md        # DALL-E generation prompts (reference)
├── PROGRESS.md             # THIS FILE — resume tracker
├── raw/                    # 16 PNGs + 16 .prompt.txt files (ComfyUI output)
├── split/                  # (empty — not used for ComfyUI workflow)
├── final/                  # Platform-ready exports
│   ├── line/               # 16x 370x320 PNG
│   ├── line_main/          # 240x240 PNG (main.png)
│   ├── line_tab/           # 96x74 PNG (tab.png)
│   ├── whatsapp/           # 16x 512x512 WEBP
│   ├── whatsapp_tray/      # 96x96 WEBP (tray.webp)
│   ├── telegram/           # 16x 512x512 WEBP
│   ├── imessage_large/     # 16x 618x618 PNG
│   └── print_etsy/         # 16x 2048x2048 PNG
└── dist/                   # Distribution packages
    ├── cappy_the_chill_capybara_vol.2_digital_download.zip (29.8MB)
    ├── sheets/
    │   ├── sticker_sheet_letter.png (US Letter, 300 DPI)
    │   └── sticker_sheet_a4.png (A4, 300 DPI)
    └── social_preview.png (3000x3000)
```

## Quick Reference: Commands Cheat Sheet

```bash
# Generate stickers via ComfyUI (already done)
python scripts/comfyui_generator.py --pack-dir packs/cappy-capybara-2

# Process all stickers for all platforms (from raw/)
python scripts/sticker_processor.py packs/cappy-capybara-2/raw \
  packs/cappy-capybara-2/final \
  line whatsapp telegram imessage_large print_etsy

# Preflight check (strict)
python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara-2 --strict

# Create print sheets + dist ZIP
python scripts/create_print_sheet.py packs/cappy-capybara-2/final/print_etsy \
  packs/cappy-capybara-2/dist "Cappy the Chill Capybara Vol.2"

# Upload to LINE (when ready)
python scripts/line_uploader.py --pack-dir packs/cappy-capybara-2

# Publish to Telegram
python scripts/telegram_publisher.py --pack-dir packs/cappy-capybara-2
```
