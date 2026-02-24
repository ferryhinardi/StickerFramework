# Cappy the Chill Capybara Vol.3: Chatty Cappy — Production Progress

> **Purpose**: Resume-friendly checklist. If you hit `Request Entity Too Large`,
> just pick up from the next unchecked `[ ]` item.
>
> **Last updated**: 2026-02-24 (LINE submitted; Telegram published; WhatsApp APK built; iMessage pending Apple credentials)

---

## Phase 0: Pack Setup (COMPLETE)

- [x] Character design & pack_config.py (16 text stickers, all unique from v1/v2)
- [x] DALL-E prompt engineering (`dalle_prompts.md`)
- [x] Pack metadata (`pack_metadata.json`)
- [x] Production progress tracker (`PROGRESS.md` — this file)

### Sticker List (all 16 — every sticker has text)

| # | ID | Text | Emotion |
|---|-----|------|---------|
| 01 | 01_sup | SUP | Casual Greeting |
| 02 | 02_same | SAME | Relatable / Me Too |
| 03 | 03_nope | NOPE | Refusal / Hard No |
| 04 | 04_lets_go | LET'S GO! | Pumped Up |
| 05 | 05_why | WHY | Confused / Existential |
| 06 | 06_food | FOOD! | Craving Food |
| 07 | 07_no_money | NO MONEY | Broke |
| 08 | 08_on_my_way | OMW! | On My Way |
| 09 | 09_chill | CHILL | Relaxed / Vibing |
| 10 | 10_ugh | UGH | Annoyed / Fed Up |
| 11 | 11_slay | SLAY | Fabulous / Killing It |
| 12 | 12_its_fine | IT'S FINE | Denial |
| 13 | 13_pls | PLS | Begging |
| 14 | 14_wut | WUT | Dumbfounded |
| 15 | 15_ttyl | TTYL | Gotta Go |
| 16 | 16_mood | MOOD | Big Mood |

---

## Phase 1: Image Generation (COMPLETE — ComfyUI)

> Used ComfyUI individual generation (v2 workflow) with DreamShaperXL_Turbo_v2_1.
> Generated in 3 batches due to timeouts: 01-07, 08-14, 15-16. Seed: 42.

### Option B: ComfyUI Individual Generation

- [x] Configure `comfyui_generator.py` for cappy-capybara-3
- [x] Generate all 16 stickers (DreamShaperXL_Turbo_v2_1, 8 steps, CFG 2.0)
- [x] Review each sticker — verify character consistency and pose/prop accuracy
- [x] All 16 PNGs in `raw/` (648KB–1.3MB each)

---

## Phase 2: Split & Rename (SKIPPED — used ComfyUI)

- [ ] Run `split_stickers.py` to split composite sheets into individual PNGs
- [ ] Verify 16 individual PNGs in `split/`
- [ ] Rename to match IDs: `01_sup.png` through `16_mood.png`
- [ ] Move finalized individual PNGs to `raw/` (or confirm already there)

---

## Phase 3: Post-Processing Pipeline (COMPLETE)

### 3A: Background Removal

- [x] Process from `raw/` — remove backgrounds for all 16 stickers
- [x] Verify: all outputs RGBA with transparent backgrounds
- [x] No character parts accidentally removed

### 3B: White Outline Addition (10px)

- [x] White outlines applied (10px, via PIL MaxFilter alpha dilation)
- [x] Outlines clean and consistent across all stickers

### 3C: Color Normalization

- [x] Applied: saturation=1.15, brightness=1.05, contrast=1.05
- [x] Colors vibrant, brown body color warm and consistent

### 3D: Text Overlay

> VOL 3 special step — every sticker gets text overlay from pack_config.py
> Text is rendered AFTER bg-removal + outline, BEFORE resize.
> Pipeline reads `text` field from each sticker in pack_config.py.

- [x] Text overlaid on all 16 stickers
- [x] Text legible at small sizes (especially LINE 370x320)
- [x] Verify text positioning, color (white fill + dark brown stroke), font size
- [x] Check `12_its_fine` uses custom text config (dict form)
- [x] No text clipping or overlap with character artwork

### 3E: Multi-Platform Resize & Export

- [x] **LINE** — 16 PNGs, 370x320, all < 300KB (largest: 167KB)
- [x] **WhatsApp** — 16 WEBPs, 512x512, all < 100KB (largest: 69KB)
- [x] **Telegram** — 16 WEBPs, 512x512
- [x] **iMessage** — 16 PNGs, 618x618
- [x] **Print/Etsy** — 16 PNGs, 2048x2048

### 3F: Verify Outputs

- [x] All 5 platforms have exactly 16 files each
- [x] No file exceeds its platform size limit
- [x] Filenames consistent: `01_sup` through `16_mood` across all platforms
- [x] Text readable on all platforms at target resolution

---

## Phase 4: Tray/Tab Icons (COMPLETE)

- [x] Choose best sticker for tray icon — `01_sup` (waving pose, clear silhouette)
- [x] **LINE main** — `final/line_main/main.png` (240x240 PNG, 42.8KB)
- [x] **LINE tab** — `final/line_tab/tab.png` (96x74 PNG, 6.5KB)
- [x] **WhatsApp tray** — `final/whatsapp_tray/tray_icon.webp` (96x96 WEBP, 4.0KB)

---

## Phase 5: Pre-flight Checks (COMPLETE)

- [x] Run LINE preflight checker (strict mode) — PASSED
  ```
  python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara-3 --strict
  ```
- [x] Verify no guideline violations (especially rule 3.13 — no religious content)
- [x] Verify `pack_metadata.json` is complete and accurate
- [x] Verify sticker_count matches actual file count — 16
- [x] Verify all text is appropriate (no profanity, slang that could be misread)

---

## Phase 6: Package for Distribution (LINE submitted; Telegram published; WhatsApp APK built; iMessage needs Apple credentials)

### 6A: Print / Etsy (COMPLETE)

- [x] Confirmed `final/print_etsy/` has 16 PNGs (2048x2048)
- [x] Generate print sheets (US Letter 2550x3300 + A4 2480x3508 at 300 DPI)
- [x] Generate social preview (3000x3000)
- [x] Package as ZIP in `dist/` — `cappy_the_chill_capybara_vol.3_digital_download.zip` (32.6MB)

### 6B: LINE Creator Market (COMPLETE — Waiting for Review)

- [x] Confirmed `final/line/` has exactly 16 PNGs (370x320, RGBA, all < 300KB)
- [x] Confirmed main image exists (240x240)
- [x] Confirmed tab image exists (96x74)
- [x] Upload to LINE Creator Studio
- [x] LINE metadata filled (title, description, category, price, style)
- [x] AI usage disclosed (LINE requirement)
- [x] Submitted for review
- [x] Sticker ID: **43221908**
- [x] Status: **Waiting for Review** (submitted 2026-02-24)
- [x] URL: https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/43221908

### 6C: WhatsApp (via Android App) — APK BUILT

> **Method**: Custom Android app (`whatsapp-sticker-app/`) with WhatsApp ContentProvider integration.
> VOL 3 stickers bundled into app assets. Also supports dynamic loading from server.
> APK: `whatsapp-sticker-app/app/build/outputs/apk/debug/app-debug.apk` (7.8MB)

- [x] Confirmed `final/whatsapp/` has 16 WEBPs (512x512, all < 100KB)
- [x] Confirmed tray icon exists (96x96, < 50KB)
- [x] VOL 3 stickers copied to `whatsapp-sticker-app/app/src/main/assets/cappy-capybara-3/`
- [x] `contents.json` updated with VOL 3 pack entry and emoji mappings
- [x] Fixed StickerContentProvider — loads from assets + cache, supports refresh
- [x] Fixed StickerPackLoader — added saveToCache() for persistence
- [x] Fixed StickerPackListActivity — downloads stickers after server fetch
- [x] APK builds successfully (`./gradlew assembleDebug`)
- [ ] Install APK on Android device/emulator
- [ ] Verify VOL 2 + VOL 3 both appear in sticker list
- [ ] Tap "Add to WhatsApp" — verify stickers load in WhatsApp

### 6D: Telegram (COMPLETE — Published)

- [x] Confirmed `final/telegram/` has 16 WEBPs (512x512)
- [x] Set TELEGRAM_BOT_TOKEN and TELEGRAM_USER_ID in .env
- [x] Run Telegram publisher with --pack-config for emoji mapping
- [x] Pack name: **CappyChillV3_by_BobaStickersBot**
- [x] URL: https://t.me/addstickers/CappyChillV3_by_BobaStickersBot
- [x] Published: 2026-02-24

### 6E: iMessage — PENDING APPLE DEVELOPER CREDENTIALS

> **Requires**: Xcode + Apple developer account + signing credentials.
> Env vars needed: APPLE_ID, APPLE_TEAM_ID, APPLE_APP_SPECIFIC_PASSWORD,
> MATCH_GIT_URL, MATCH_PASSWORD, BUNDLE_ID_PREFIX.

- [x] Confirmed `final/imessage_large/` has 16 PNGs (618x618)
- [ ] Configure Apple developer credentials in .env
- [ ] Run iMessage preparer
- [ ] Open Xcode project, configure signing, archive & submit to App Store

---

## Phase 7: Final Verification (PARTIAL — blocked on device testing + iMessage)

- [ ] All 5 platforms uploaded / submitted
  - [x] LINE — submitted (sticker ID 43221908, waiting for review)
  - [x] Print/Etsy — dist ZIP ready (32.6MB)
  - [x] WhatsApp — APK built, needs install + device test
  - [x] Telegram — published (https://t.me/addstickers/CappyChillV3_by_BobaStickersBot)
  - [ ] iMessage — pending Apple developer credentials
- [x] `pack_metadata.json` updated with LINE submission status and sticker ID
- [x] No temp files or duplicates left behind
- [x] All files committed to git

---

## Quick Reference: File Structure

```
packs/cappy-capybara-3/
├── pack_config.py          # Character + sticker definitions (all 16 with text)
├── pack_metadata.json      # Pack metadata for all platforms
├── dalle_prompts.md        # DALL-E generation prompts (2 sheets)
├── PROGRESS.md             # THIS FILE — resume tracker
├── raw/                    # Source PNGs (from DALL-E or ComfyUI)
├── split/                  # Individual stickers (DALL-E workflow only)
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
    ├── cappy_the_chill_capybara_vol.3_digital_download.zip
    ├── sheets/
    │   ├── sticker_sheet_letter.png (US Letter, 300 DPI)
    │   └── sticker_sheet_a4.png (A4, 300 DPI)
    └── social_preview.png (3000x3000)
```

## Quick Reference: Commands Cheat Sheet

```bash
# Option A: Generate stickers via ComfyUI
python scripts/comfyui_generator.py --pack-dir packs/cappy-capybara-3

# Option B: Split DALL-E composite sheets
python scripts/split_stickers.py packs/cappy-capybara-3/raw/sheet1.png \
  packs/cappy-capybara-3/split --cols 4 --rows 2
python scripts/split_stickers.py packs/cappy-capybara-3/raw/sheet2.png \
  packs/cappy-capybara-3/split --cols 4 --rows 2

# Process all stickers for all platforms (from raw/)
python scripts/sticker_processor.py packs/cappy-capybara-3/raw \
  packs/cappy-capybara-3/final \
  line whatsapp telegram imessage_large print_etsy

# Preflight check (strict)
python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara-3 --strict

# Create print sheets + dist ZIP
python scripts/create_print_sheet.py packs/cappy-capybara-3/final/print_etsy \
  packs/cappy-capybara-3/dist "Cappy the Chill Capybara Vol.3"

# Upload to LINE
python scripts/line_uploader.py --pack-dir packs/cappy-capybara-3

# Publish to Telegram
python scripts/telegram_publisher.py --pack-dir packs/cappy-capybara-3
```
