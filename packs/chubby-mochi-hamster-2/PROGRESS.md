# Chubby Mochi Hamster Vol.2: Study Mode — Production Progress

> **Purpose**: Resume-friendly checklist. If you hit `Request Entity Too Large`,
> just pick up from the next unchecked `[ ]` item.
>
> **Last updated**: 2026-02-25 (Phase 0 generation COMPLETE — 16/16 raw stickers)

---

## Phase 0: Generation — DONE (16/16)

- [x] Character design & pack_config.py (16 study-themed stickers)
- [x] pack_metadata.json created
- [x] DALL-E prompt engineering (`dalle_prompts.md`)
- [x] Generate all 16 individual raw images via ComfyUI (seed 42, DreamShaperXL_Turbo_v2_1)
- [x] Save prompt history (16 `.prompt.txt` files in `raw/`)
- [x] Text composited via Pillow TextCompositor (not AI-generated)

### Raw Sticker Status (16/16 complete)

| # | ID | Status | Size | Notes |
|---|----|--------|------|-------|
| 01 | 01_studying | DONE | 1261KB | seed 42 |
| 02 | 02_brain_full | DONE | 993KB | seed 42 |
| 03 | 03_eureka | DONE | 977KB | seed 42 |
| 04 | 04_lets_go | DONE | 1046KB | seed 42 |
| 05 | 05_need_coffee | DONE | 902KB | seed 42 |
| 06 | 06_quiz_time | DONE | 849KB | seed 42 |
| 07 | 07_aced_it | DONE | 1126KB | seed 42 |
| 08 | 08_help_me | DONE | 1349KB | seed 42 |
| 09 | 09_break_time | DONE | 1168KB | seed 42 |
| 10 | 10_due_tomorrow | DONE | 892KB | seed 42 |
| 11 | 11_good_luck | DONE | 1010KB | seed 42 |
| 12 | 12_so_tired | DONE | 1192KB | seed 42 |
| 13 | 13_you_can_do_it | DONE | 986KB | seed 42 |
| 14 | 14_procrastinating | DONE | 1188KB | seed 42 |
| 15 | 15_group_study | DONE | 1196KB | seed 42 |
| 16 | 16_all_done | DONE | 1022KB | seed 43 |

---

## Known Issues: (ALL RESOLVED)

> All stale split/ and final/ files were cleaned in Phase 3. Raw generation
> completed via ComfyUI in Phase 0. No outstanding issues.

---

## Phase 1: Quality Review (16 stickers) — NEXT UP

Review each of the 16 raw stickers against the character spec in `pack_config.py`.

**Check for each sticker:**
- Consistent body color (#E8A84C warm orange-brown)
- Thick dark charcoal outline (#333333)
- Chibi proportions (round ball body, head 55% of body height)
- Puffed cheek pouches, white belly patch
- Large shiny black round eyes with highlight dots
- No AI-generated text/words/letters/numbers (text is composited via Pillow)
- Correct pose & emotion matching the config
- Clean white background (no artifacts)

### Sheet 1 (01-08)

- [ ] **01_studying** — pending review
- [ ] **02_brain_full** — pending review
- [ ] **03_eureka** — pending review
- [ ] **04_lets_go** — pending review
- [ ] **05_need_coffee** — pending review
- [ ] **06_quiz_time** — pending review
- [ ] **07_aced_it** — pending review
- [ ] **08_help_me** — pending review

### Sheet 2 (09-16)

- [ ] **09_break_time** — pending review
- [ ] **10_due_tomorrow** — pending review
- [ ] **11_good_luck** — pending review
- [ ] **12_so_tired** — pending review
- [ ] **13_you_can_do_it** — pending review
- [ ] **14_procrastinating** — pending review
- [ ] **15_group_study** — pending review
- [ ] **16_all_done** — pending review

---

## Phase 2: Re-generate Problematic Stickers

> Pending Phase 1 review results.

---

## Phase 3: Fix Split Directory (Naming & Count) — DONE

> **Decision**: Use `raw/` as the sole source of truth. The 13 misnamed `split/` files
> came from a different composite sheet and are unreliable. Delete all stale files.

- [x] Delete 13 stale files from `split/` (done 2026-02-25)
- [x] Delete stale files from `final/` — all 7 platform subdirs cleaned (done 2026-02-25)
- [x] Delete stale `sticker_pack.png` composite sheet (done 2026-02-25)
- [ ] Will reprocess all 16 stickers from `raw/` in Phase 4
- [ ] Source of truth: `raw/` with exactly 16 correctly-named PNGs:
  ```
  01_studying, 02_brain_full, 03_eureka, 04_lets_go,
  05_need_coffee, 06_quiz_time, 07_aced_it, 08_help_me,
  09_break_time, 10_due_tomorrow, 11_good_luck, 12_so_tired,
  13_you_can_do_it, 14_procrastinating, 15_group_study, 16_all_done
  ```

---

## Phase 4: Post-Processing Pipeline

### 4A: Background Removal

- [ ] Process from `raw/` — all 16 backgrounds removed
- [ ] Verified: all outputs RGBA with transparent backgrounds
- [ ] No character parts accidentally removed

### 4B: White Outline Addition (10px)

- [ ] White outlines applied (10px, via `StickerProcessor(outline_width=10)`)
- [ ] Outlines clean and consistent across all stickers

### 4C: Color Normalization

- [ ] Applied: saturation=1.15, brightness=1.05, contrast=1.05
- [ ] Colors vibrant, orange-brown body color warm and consistent

### 4D: Multi-Platform Resize & Export

- [ ] **LINE** — 16 PNGs, 370x320, max < 1000KB
- [ ] **WhatsApp** — 16 WEBPs, 512x512, max < 100KB
- [ ] **Telegram** — 16 WEBPs, 512x512, max < 256KB
- [ ] **iMessage** — 16 PNGs, 618x618, max < 500KB
- [ ] **Print/Etsy** — 16 PNGs, 2048x2048 (no strict limit)

### 4E: Verify Outputs

- [ ] All 5 platforms have exactly 16 files each
- [ ] No file exceeds its platform size limit
- [ ] Filenames consistent: `01_studying` through `16_all_done` across all platforms

---

## Phase 5: Tray/Tab Icons

- [ ] Choose iconic sticker for tray/tab icons
- [ ] **LINE main** — `final/line_main/main.png` (240x240 PNG)
- [ ] **LINE tab** — `final/line_tab/tab.png` (96x74 PNG)
- [ ] **WhatsApp tray** — `final/whatsapp_tray/tray.webp` (96x96 WEBP, < 50KB)

---

## Phase 6: Pre-flight Checks

- [ ] Run LINE preflight checker
- [ ] Verify no guideline violations (especially rule 3.13)
- [ ] Verify `pack_metadata.json` is complete and accurate
- [ ] Verify sticker_count matches actual file count — 16 = 16

---

## Phase 7: Package for Distribution

### 7A: LINE Creator Market

- [ ] Confirm `final/line/` has exactly 16 PNGs (370x320, RGBA, < 1MB)
- [ ] Confirm main image exists (240x240)
- [ ] Confirm tab image exists (96x74)
- [ ] Dry-run upload — passed all validations
- [ ] Run LINE upload script:
  ```bash
  python scripts/line_uploader.py --pack-dir packs/chubby-mochi-hamster-2
  ```
- [ ] LINE metadata filled (title, description, category, price, copyright)
- [ ] Submitted for review

### 7B: Telegram

- [ ] Confirm `final/telegram/` has 16 WEBPs (512x512, < 256KB)
- [ ] Run Telegram publisher:
  ```bash
  python scripts/telegram_publisher.py --pack-dir packs/chubby-mochi-hamster-2
  ```
- [ ] Set sticker emojis from pack_config.py emoji field

### 7C: WhatsApp (via Sticker.ly)

- [ ] Confirm `final/whatsapp/` has 16 WEBPs (512x512, < 100KB)
- [ ] Confirm tray icon exists (96x96, < 50KB)
- [ ] Upload via Sticker.ly app
- [ ] Pack name, author, tags configured
- [ ] Published

### 7D: iMessage

- [ ] Confirm `final/imessage_large/` has 16 PNGs (618x618, < 500KB)
- [ ] Run iMessage preparer (`scripts/prepare_imessage_pack.py`)
- [ ] Open Xcode project, configure signing, archive & submit

### 7E: Print / Etsy

- [ ] Confirm `final/print_etsy/` has 16 PNGs (2048x2048)
- [ ] Generate print sheets (US Letter + A4 at 300 DPI)
- [ ] Generate social preview (3000x3000)
- [ ] Package as ZIP
- [ ] Create Etsy listing

---

## Phase 8: Final Verification

- [ ] All 5 platforms packaged and ready
- [ ] `pack_metadata.json` updated with submission status for all platforms
- [ ] No temp files or duplicates left behind
- [ ] All filenames consistent across platforms
- [ ] No file exceeds its platform size limit
- [ ] All files committed to git

---

## Quick Reference: File Structure

```
packs/chubby-mochi-hamster-2/
├── pack_config.py          # Character + 16 study-themed sticker definitions
├── pack_metadata.json      # Pack metadata for all platforms
├── dalle_prompts.md        # DALL-E generation prompts
├── PROGRESS.md             # THIS FILE — resume tracker
├── sticker_pack.png        # (DELETED — was stale mismatched composite)
├── raw/                    # Individual ComfyUI outputs (16/16 done)
│   ├── 01_studying.png + .prompt.txt
│   ├── 02_brain_full.png + .prompt.txt
│   ├── ... (all 16 complete)
│   └── 16_all_done.png + .prompt.txt
├── split/                  # CLEANED — empty, will be repopulated in Phase 4
├── final/                  # CLEANED — 7 empty platform subdirs, ready for Phase 4
│   ├── line/
│   ├── line_main/
│   ├── line_tab/
│   ├── whatsapp/
│   ├── telegram/
│   ├── imessage_large/
│   └── print_etsy/
└── dist/                   # Distribution packages (not yet created)
```

## Quick Reference: Commands Cheat Sheet

```bash
# Process all stickers for all platforms (from raw/)
python scripts/sticker_processor.py packs/chubby-mochi-hamster-2/raw \
  packs/chubby-mochi-hamster-2/final \
  line whatsapp telegram imessage_large print_etsy

# Process only LINE
python scripts/sticker_processor.py packs/chubby-mochi-hamster-2/raw \
  packs/chubby-mochi-hamster-2/final line

# Skip bg removal (if already transparent)
python scripts/sticker_processor.py packs/chubby-mochi-hamster-2/raw \
  packs/chubby-mochi-hamster-2/final line --skip-bg

# Preflight check
python scripts/line_preflight_check.py --pack-dir packs/chubby-mochi-hamster-2

# Upload to LINE
python scripts/line_uploader.py --pack-dir packs/chubby-mochi-hamster-2

# Publish to Telegram
python scripts/telegram_publisher.py --pack-dir packs/chubby-mochi-hamster-2

# Create print sheets
python scripts/create_print_sheet.py --pack-dir packs/chubby-mochi-hamster-2
```
