# Common Error Patterns — StickerFramework

## pack_config.py — Missing Required Keys

| Symptom | Error message | Root cause | Fix |
|---|---|---|---|
| Generation crashes on first sticker | `KeyError: 'blush_color'` | `character` dict missing `blush_color` | Add `"blush_color": "soft pink"` to character |
| Generation crashes on first sticker | `KeyError: 'outline_color'` | `character` dict missing `outline_color` | Add `"outline_color": "black"` to character |
| Generation crashes on first sticker | `KeyError: 'accessory'` | `character` dict uses `accessories` (plural) | Rename to `accessory` (singular) |
| Generation crashes during prompt build | `KeyError: 'extras'` | `style` dict missing `extras` | Add `"extras": "die-cut sticker style..."` to style |

**Required character keys** (all must be present): `name`, `species`, `body_color`, `blush_color`, `outline_color`, `eye_style`, `accessory`, `proportions`

**Required style keys** (all must be present): `outline_type`, `coloring`, `background`, `extras`, `art_style`

## pack_config.py — Wrong Platforms List

| Symptom | Error message | Root cause | Fix |
|---|---|---|---|
| Processing crashes after first sticker's WEBP | `ValueError: Unsupported format: TGS` | `telegram_animated` included in `platforms` list | Remove `telegram_animated` from platforms; use `--telegram-animated` flag instead |
| Processing crashes after first sticker's WEBP | `ValueError: Unsupported format: WEBM` | `telegram_video` included in `platforms` list | Remove `telegram_video` from platforms; use `--telegram-video` flag instead |

**Valid `platforms` list entries** (for `sticker_processor.py`): `line`, `telegram`, `whatsapp`, `imessage_large`, `print_etsy`, `line_main`, `line_tab`

## Missing LINE Cover Images

| Symptom | Root cause | Fix |
|---|---|---|
| `check_line_assets.py` fails on `line_main` or `line_tab` | `--process-only` does not auto-generate cover images | Generate manually with PIL: resize `line/01_happy.png` to 240×240 → `line_main/main.png` and 96×74 → `line_tab/tab.png` |
| LINE upload fails on main image slot | `line_main/` directory empty | See fix above |

## Background Removal

| Symptom | Pattern in output | Root cause |
|---|---|---|
| White box on sticker | `Background removal failed for` | Flood-fill corner heuristic failed on non-white bg |
| Transparent image is all black | `rembg` model output issue | Use `--skip-bg` and verify source image |
| Slow processing | rembg downloading model on first run | Wait for U2Net model download (~170 MB) |

**Fix:** Add `--skip-bg` flag to pipeline command.

## LINE Automation (Playwright)

| Symptom | Pattern in output | Root cause |
|---|---|---|
| `TimeoutError: waiting for selector` | selector not found in time | LINE UI changed or page didn't load |
| `SessionNotFound` | no storage_state.json | First run, or session expired (30-day TTL) |
| Stuck at image upload step | no progress after upload starts | Browser closed mid-session; stale progress |
| 401 Unauthorized | HTTP 401 from LINE | Session token expired |

**Fix order:** `rm -f ~/.line-sticker-automation/progress.json` → Screenshots → fresh session → selector timeout increase.

## Animation / File Size

| Symptom | Root cause | Fix |
|---|---|---|
| TGS file > 64 KB | Complex Lottie preset | Use `pulse` or `bounce` preset |
| WEBM file > 256 KB | Long duration or high frame rate | Reduce `duration_ms` to ≤ 2000 |
| `ffmpeg not found` | FFmpeg not installed | `brew install ffmpeg` |
| `lottie` import error | lottie-python not installed | `pip install lottie` |
| `--telegram-animated` times out | lottie library is slow on first run | Skip TGS for now, re-run separately |

**Note:** Use `python3 scripts/run_pipeline.py --pack ... --telegram-animated` (NOT `animated_converter.py --pack-dir`) to generate a batch of TGS files.

## Image Dimensions

| Symptom | Root cause | Fix |
|---|---|---|
| LINE rejects sticker image | Wrong size (not 370×320) | Rerun `process-pipeline` |
| LINE rejects main image | Wrong size (not 240×240) | Check `line_main/` output |
| LINE rejects tab icon | Wrong size (not 96×74) | Check `line_tab/` output |

## Environment / Setup

| Symptom | Root cause | Fix |
|---|---|---|
| `Set OPENAI_API_KEY` | Missing API key | Add to `.env` |
| `playwright install` needed | Chromium not downloaded | `playwright install chromium` |
| `ModuleNotFoundError` | Missing Python dependency | `pip install -r requirements.txt` |
| `xcodegen not found` | iMessage build tools missing | `brew install xcodegen` |

