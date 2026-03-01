# Common Error Patterns — StickerFramework

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

**Fix order:** Screenshots → fresh session → selector timeout increase.

## Animation / File Size

| Symptom | Root cause | Fix |
|---|---|---|
| TGS file > 64 KB | Complex Lottie preset | Use `pulse` or `bounce` preset |
| WEBM file > 256 KB | Long duration or high frame rate | Reduce `duration_ms` to ≤ 2000 |
| `ffmpeg not found` | FFmpeg not installed | `brew install ffmpeg` |
| `lottie` import error | lottie-python not installed | `pip install lottie` |

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
