---
name: debug-pipeline
description: >
  Diagnoses and fixes failures in the StickerFramework pipeline. Use when
  images fail background removal, the LINE upload gets stuck, Playwright
  timeouts occur, animation files are too large, the processing pipeline
  crashes, or sticker outputs are wrong dimensions. Don't use for creating
  new packs, running normal processing, or publishing to platforms.
---

# Skill: debug-pipeline

## Purpose
Systematically diagnose the most common StickerFramework failures and produce
a concrete fix for each one.

## Steps

### Step 1 — Identify failure category
Ask the user to describe the error, or scan recent output for known patterns.
Then read `references/error-patterns.md` to map the symptom to a root cause.

Run the diagnostic script to collect a snapshot of the current state:

```bash
python3 .opencode/skills/debug-pipeline/scripts/diagnose.py "<pack_id>"
```

### Step 2 — Apply the matched fix

Navigate to the matching section below based on the diagnosed category.

---

#### Category A — Background removal failure
**Symptom:** `Background removal failed` in pipeline output, or sticker has
white box instead of transparent background.

**Fix:** Bypass flood-fill and use the rembg ML fallback:
```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only --input packs/<pack_id>/raw \
    --skip-bg
```
If rembg also fails, ensure `rembg` is installed:
```bash
pip install rembg
```

---

#### Category B — Playwright / LINE automation timeout
**Symptom:** `TimeoutError` in `automation/`, upload appears stuck.

**Fix steps:**
1. Check screenshots for visual state:
   ```bash
   ls -lt automation/screenshots/ | head -10
   open automation/screenshots/<latest>.png
   ```
2. If the page shows a CAPTCHA or unexpected modal, the session may be stale:
   ```bash
   rm ~/.line-sticker-automation/storage_state.json
   python3 scripts/line_uploader.py --pack-dir packs/<pack_id>/final \
       --title "<title>" --description "<desc>" --headful --dry-run
   ```
3. If selectors are broken (LINE UI changed), increase timeout:
   Edit `automation/config.py` → raise `SELECTOR_TIMEOUT` from `10_000` to `20_000`.

---

#### Category C — Animation file too large
**Symptom:** TGS file exceeds 64 KB limit, or WEBM exceeds 256 KB.

**Fix:** Switch to a simpler preset or shorter duration.
```bash
# TGS — use pulse (lightest preset)
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only --telegram-animated --animation-preset pulse

# WEBM — reduce duration in pack_config.py
# Edit: "animation": {"duration_ms": 1500}  (was 3000)
```

---

#### Category D — Wrong output dimensions
**Symptom:** LINE rejects images; dimensions don't match spec.

**Fix:** Confirm `sticker_processor.py` platform specs and reprocess:
```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only --input packs/<pack_id>/raw
```
See `references/platform-specs.md` for required dimensions per platform.

---

#### Category E — LINE session expired
**Symptom:** `SessionNotFound` or HTTP 401 when starting upload.

**Fix:**
```bash
rm -f ~/.line-sticker-automation/storage_state.json
rm -f ~/.line-sticker-automation/progress.json
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<title>" --description "<desc>" \
    --headful --dry-run
```

---

#### Category F — Missing environment variables
**Symptom:** `ERROR: Set OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN not set`, etc.

**Fix:** Check `.env` against the template:
```bash
diff .env.example .env | grep "^<"
```
Copy missing keys from `.env.example` and fill in real values.

### Step 3 — Verify fix
After applying the fix, rerun the relevant check script:

```bash
# For processing issues:
python3 .opencode/skills/process-pipeline/scripts/check_outputs.py "<pack_id>"

# For LINE assets:
python3 .opencode/skills/line-upload/scripts/check_line_assets.py "<pack_id>"
```

Report the result to the user.

## Error Handling

| Diagnostic script fails | Ensure `pack_id` is correct and `packs/<pack_id>/` exists |
| Unknown error pattern | Check `references/error-patterns.md` for additional patterns; share the full traceback |
