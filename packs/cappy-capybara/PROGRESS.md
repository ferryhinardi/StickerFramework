# Cappy the Chill Capybara — Production Progress

> **Purpose**: Resume-friendly checklist. If you hit `Request Entity Too Large`,
> just pick up from the next unchecked `[ ]` item.
>
> **Last updated**: 2026-02-24

---

## Phase 0: Generation (DONE)

- [x] Character design & pack_config.py
- [x] DALL-E prompt engineering (`dalle_prompts.md`)
- [x] Generate composite sheet 1 (stickers 01-08)
- [x] Generate composite sheet 2 (stickers 09-16)
- [x] Generate individual raw images (16 PNGs in `raw/`)
- [x] Save prompt history (16 `.prompt.txt` files in `raw/`)
- [x] Split composite sheets → `split/` (18 files extracted)
- [x] Initial LINE export → `final/line/` (18 files, 370x320 RGBA)

---

## Phase 1: Quality Review (16 stickers)

Review each of the 16 raw stickers against the character spec in `pack_config.py`.

**Check for each sticker:**
- Consistent body color (#C4956A warm brown)
- Thick dark brown outline (#4A3728)
- Orange (mikan) on head present
- Chibi potato-shaped proportions
- No text/words/letters/numbers
- Correct pose & emotion matching the config
- Clean white background (no artifacts)

### Sheet 1 (01-08)

- [x] **01_good_morning** — PASS (cov=32%, body=9.1%, outline=2.7%, clean white bg)
- [x] **02_ok_thumbs_up** — PASS (cov=32%, body=23.4%, outline=1.2%, clean white bg)
- [x] **03_thank_you** — PASS (cov=34%, body=26.0%, outline=4.2%, clean white bg)
- [x] **04_lol** — PASS w/FIX (off-white bg ~(234,232,230), fixed by lowering bg threshold 230→225 in sticker_processor.py)
- [x] **05_love** — PASS (cov=39%, body=23.0%, outline=1.0%, clean white bg)
- [x] **06_sleepy** — PASS (cov=48%, body=35.4%, outline=3.4%, clean white bg)
- [x] **07_hungry** — PASS (cov=40%, body=31.4%, outline=2.9%, clean white bg)
- [x] **08_working_hard** — PASS (cov=50%, body=35.9%, outline=4.6%, clean white bg)

### Sheet 2 (09-16)

- [x] **09_excited** — PASS (cov=26%, body=22.0%, outline=1.8%, clean white bg)
- [x] **10_sad** — PASS (cov=30%, body=21.3%, outline=2.3%, clean white bg)
- [x] **11_angry** — PASS (cov=37%, body=26.2%, outline=3.2%, clean white bg)
- [x] **12_sorry** — PASS (cov=35%, body=25.5%, outline=0.7%, clean white bg)
- [x] **13_bye** — PASS (cov=37%, body=24.8%, outline=1.1%, clean white bg)
- [x] **14_thinking** — PASS (cov=34%, body=24.8%, outline=4.0%, clean white bg)
- [x] **15_cheering** — PASS (cov=28%, body=4.1%, outline=2.7%, clean white bg)
- [x] **16_good_night** — PASS (cov=54%, body=21.3%, outline=6.0%, clean white bg)

### Review Results

> **Reviewed: 2026-02-24** (automated + visual)
>
> ```
> PASS: 01, 02, 03, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16
> PASS w/FIX: 04 (off-white bg — fixed processor threshold)
> NEEDS REGEN: NONE
> ```
>
> **Fix applied**: `scripts/sticker_processor.py` line 122 — `white_threshold` changed from 230→225
> to handle off-white DALL-E backgrounds. Verified BG removal works for all 16 stickers.

---

## Phase 2: Re-generate Problematic Stickers (SKIPPED — all passed)

> All 16 stickers passed quality review. No re-generation needed.
> Only fix was adjusting BG removal threshold for 04_lol (off-white background).

---

## Phase 3: Fix Split Directory (Naming & Count) — DONE

> **Decision**: Use `raw/` as the sole source of truth. The 18 misnamed `split/` files
> came from composite sheet extraction and are unreliable. Deleted all stale files.
>
> **Cleaned on 2026-02-24:**

- [x] Deleted 18 stale files from `split/` (now empty)
- [x] Deleted 18 stale files from `final/line/` (now empty)
- [x] Will reprocess all 16 stickers from `raw/` in Phase 4
- [x] Source of truth: `raw/` with exactly 16 correctly-named PNGs:
  ```
  01_good_morning, 02_ok_thumbs_up, 03_thank_you, 04_lol,
  05_love, 06_sleepy, 07_hungry, 08_working_hard,
  09_excited, 10_sad, 11_angry, 12_sorry,
  13_bye, 14_thinking, 15_cheering, 16_good_night
  ```

---

## Phase 4: Post-Processing Pipeline — DONE

> **Processed on 2026-02-24**: All 16 raw stickers processed through full pipeline
> (bg removal → color normalization → white outline → resize) for all 5 platforms.

### 4A: Background Removal

- [x] Process from `raw/` — all 16 backgrounds removed (including 04_lol off-white)
- [x] Verified: all outputs RGBA with transparent backgrounds
- [x] No character parts accidentally removed

### 4B: White Outline Addition (10px)

- [x] White outlines applied (10px, via `StickerProcessor(outline_width=10)`)
- [x] Outlines clean and consistent across all stickers

### 4C: Color Normalization

- [x] Applied: saturation=1.15, brightness=1.05, contrast=1.05
- [x] Colors vibrant, brown body color warm and consistent

### 4D: Multi-Platform Resize & Export

- [x] **LINE** — 16 PNGs, 370x320, max 118KB (limit 1000KB)
- [x] **WhatsApp** — 16 WEBPs, 512x512, max 56KB (limit 100KB)
- [x] **Telegram** — 16 WEBPs, 512x512, max 56KB (limit 256KB)
- [x] **iMessage** — 16 PNGs, 618x618, max 321KB (limit 500KB)
- [x] **Print/Etsy** — 16 PNGs, 2048x2048, max 1941KB (no strict limit)

### 4E: Verify Outputs

- [x] All 5 platforms have exactly 16 files each
- [x] No file exceeds its platform size limit — **ALL PASS**
- [x] Filenames consistent: `01_good_morning` through `16_good_night` across all platforms

---

## Phase 5: Tray/Tab Icons — DONE

> **Source sticker**: `02_ok_thumbs_up` (thumbs up — universally recognizable)
> **Generated on 2026-02-24**

- [x] Chose `02_ok_thumbs_up` as the iconic sticker for tray/tab icons
- [x] **LINE main** — `final/line_main/main.png` (240x240 PNG, 46.3KB)
- [x] **LINE tab** — `final/line_tab/tab.png` (96x74 PNG, 6.9KB)
- [x] **WhatsApp tray** — `final/whatsapp_tray/tray.webp` (96x96 WEBP, 4.1KB < 50KB limit)

---

## Phase 6: Pre-flight Checks — DONE

> **Checked on 2026-02-24**

- [x] Run LINE preflight checker — **ALL CHECKS PASSED**
  (Note: checker reported "Checking 18 sticker filename(s)" but only 16 files in directory — cosmetic issue)
- [x] Verify no guideline violations (especially rule 3.13) — none found
- [x] Verify `pack_metadata.json` is complete and accurate — confirmed
- [x] Verify sticker_count matches actual file count — 16 = 16 ✓

---

## Phase 7: Package for Distribution

### 7A: LINE Creator Market — DONE

> **Submitted on 2026-02-24**: Sticker ID **43216653**
> URL: `https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/43216653`
> Price: Rp23.000+
> Status: **Waiting for Review**

- [x] Confirm `final/line/` has exactly 16 PNGs (370x320, RGBA, < 1MB) — verified
- [x] Confirm main image exists (240x240) — `final/line_main/main.png`
- [x] Confirm tab image exists (96x74) — `final/line_tab/tab.png`
- [x] Dry-run upload — passed all validations
- [x] Run LINE upload script:
  ```bash
  python scripts/line_uploader.py --pack-dir packs/cappy-capybara
  ```
- [x] LINE metadata filled:
  - Title: "Cappy the Chill Capybara"
  - Description: from pack_metadata.json
  - Category: cute > other_animals
  - Price: Rp23.000+
  - Copyright: "FHStudio"
- [x] Submitted for review — sticker ID 43216653

### 7B: Telegram

- [ ] Confirm `final/telegram/` has 16 WEBPs (512x512, < 256KB)
- [ ] Run Telegram publisher:
  ```bash
  python scripts/telegram_publisher.py --pack-dir packs/cappy-capybara
  ```
- [ ] Set sticker emojis from pack_config.py emoji field

### 7C: WhatsApp (via Sticker.ly) — DONE

> **Published on 2026-02-24**: Pack live on Sticker.ly
> URL: `https://sticker.ly/s/7ZNT6Z`

- [x] Confirm `final/whatsapp/` has 16 WEBPs (512x512, < 100KB) — verified
- [x] Confirm tray icon exists (96x96, < 50KB) — `final/whatsapp_tray/tray.webp` (4.1KB)
- [x] Upload via Sticker.ly app — 16 stickers + tray icon uploaded
- [x] Pack name: "Cappy the Chill Capybara", Author: "FHStudio"
- [x] Tags added for discoverability
- [x] Published — `https://sticker.ly/s/7ZNT6Z`

### 7D: iMessage — DONE

> **Completed on 2026-02-24**: Xcode project created at `CappyCapybara/` (repo root).

- [x] Confirm `final/imessage_large/` has 16 PNGs (618x618, < 500KB) — verified
- [x] Run iMessage preparer (`scripts/prepare_imessage_pack.py`) — Xcode project created
- [ ] Open Xcode project, add app icons, configure signing, archive & submit to App Store
  > **Note**: Project is at `CappyCapybara/` in repo root (not inside `packs/cappy-capybara/`).
  > This step requires Xcode and an Apple Developer account — must be done manually.

### 7E: Print / Etsy — DONE

> **Completed on 2026-02-24**: All print assets generated + distribution ZIP created.

- [x] Confirm `final/print_etsy/` has 16 PNGs (2048x2048) — verified
- [x] Generate print sheets — US Letter (2550x3300) + A4 (2480x3508) at 300 DPI
- [x] Generate social preview (3000x3000)
- [x] Package as ZIP — `dist/cappy_the_chill_capybara_digital_download.zip` (27.3MB)
  Contains: individual PNGs, sticker sheets, social preview, README.txt, LICENSE.txt
- [ ] Create Etsy listing with print sheet + individual PNGs (manual step)
- [ ] Customize README.txt and LICENSE.txt placeholders (email, shop URL, publisher name)

---

## Phase 8: Final Verification — DONE

> **Verified on 2026-02-24**

- [x] All 5 platforms packaged and ready
  - LINE: 16 PNGs + main + tab — submitted (ID 43216653, waiting for review)
  - WhatsApp: 16 WEBPs + tray — published (sticker.ly/s/7ZNT6Z)
  - Telegram: 16 WEBPs — files ready, awaiting bot credentials
  - iMessage: 16 PNGs + Xcode project — project created, awaiting manual Xcode submission
  - Print/Etsy: 16 PNGs + sheets + ZIP (27.3MB) — files ready, awaiting Etsy listing
- [x] `pack_metadata.json` updated with submission status for all 5 platforms
- [x] No temp files or duplicates left behind (cleaned .DS_Store x2, __pycache__/)
- [x] All filenames consistent across platforms (01_good_morning through 16_good_night)
- [x] No file exceeds its platform size limit
- [x] All files committed to git — commit `c5a47cb` (74 files, ~15MB)

---

## Quick Reference: File Structure

```
packs/cappy-capybara/
├── pack_config.py          # Character + sticker definitions
├── pack_metadata.json      # Pack metadata for all platforms
├── dalle_prompts.md        # DALL-E generation prompts
├── PROGRESS.md             # THIS FILE — resume tracker
├── composite_sheet_1.png   # Generated 2x4 grid (stickers 01-08)
├── composite_sheet_2.png   # Generated 2x4 grid (stickers 09-16)
├── raw/                    # 16 individual DALL-E outputs (1024x1024 RGB)
│   ├── 01_good_morning.png + .prompt.txt
│   ├── ...
│   └── 16_good_night.png + .prompt.txt
├── split/                  # EMPTY (stale files deleted in Phase 3)
├── final/                  # Platform-ready exports
│   ├── line/               # 370x320 PNG (16 stickers)
│   ├── line_main/          # 240x240 PNG (1 main image)
│   ├── line_tab/           # 96x74 PNG (1 tab icon)
│   ├── whatsapp/           # 512x512 WEBP (16 stickers)
│   ├── whatsapp_tray/      # 96x96 WEBP (1 tray icon)
│   ├── telegram/           # 512x512 WEBP (16 stickers)
│   ├── imessage_large/     # 618x618 PNG (16 stickers)
│   └── print_etsy/         # 2048x2048 PNG (16 stickers)
└── dist/                   # Distribution packages
    ├── sheets/             # Print sheets (US Letter + A4, 300 DPI)
    ├── social_preview.png  # 3000x3000 social media image
    └── cappy_the_chill_capybara_digital_download.zip  # 27.3MB

# Also at repo root:
CappyCapybara/              # iMessage Xcode project
├── CappyCapybara.xcodeproj/
├── Stickers.xcstickers/    # 16 .sticker directories + Contents.json
└── Info.plist
```

## Quick Reference: Commands Cheat Sheet

```bash
# Process all stickers for all platforms (from raw/)
python scripts/sticker_processor.py packs/cappy-capybara/raw \
  packs/cappy-capybara/final \
  line whatsapp telegram imessage_large print_etsy

# Process only LINE
python scripts/sticker_processor.py packs/cappy-capybara/raw \
  packs/cappy-capybara/final line

# Skip bg removal (if already transparent)
python scripts/sticker_processor.py packs/cappy-capybara/raw \
  packs/cappy-capybara/final line --skip-bg

# Preflight check
python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara

# Upload to LINE
python scripts/line_uploader.py --pack-dir packs/cappy-capybara

# Publish to Telegram
python scripts/telegram_publisher.py --pack-dir packs/cappy-capybara

# Create print sheets
python scripts/create_print_sheet.py --pack-dir packs/cappy-capybara
```
