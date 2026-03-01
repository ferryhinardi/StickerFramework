---
name: line-upload
description: >
  Uploads a processed sticker pack to LINE Creator Market using Playwright
  browser automation. Use when the user wants to submit stickers to LINE,
  resume an interrupted upload, handle LINE login/session, set metadata,
  upload images, set price tier, or submit for review. Don't use for image
  processing, Telegram publishing, or packs that contain religious content.
---

# Skill: line-upload

## Purpose
Upload a fully processed sticker pack to LINE Creator Market: authenticate,
create submission, upload images, set metadata + price, and optionally submit
for review.

## Prerequisites
- Processed images exist in `packs/<pack_id>/final/line/`, `line_main/`, `line_tab/`.
- `LINE_EMAIL` and `LINE_PASSWORD` set in `.env` (or interactive login available).
- Playwright installed: `playwright install chromium`.
- For first run: a display is available (headful mode required for QR/OTP login).

## Steps

### Step 1 — Pre-flight content check
Run the content gate before touching the browser. This prevents wasting time
uploading a pack that LINE will reject.

```bash
python3 scripts/line_preflight_check.py \
    --pack-dir packs/<pack_id>/final \
    --title "<title>" \
    --description "<description>"
```

If the check fails, report the exact banned keyword and field to the user.
Do **not** proceed unless the user passes `--skip-preflight` explicitly.
See `references/line-content-policy.md` for the full banned-keyword list.

### Step 2 — Verify image assets
Run the asset checker to confirm all required LINE images are present and
within spec before launching the browser:

```bash
python3 .github/skills/line-upload/scripts/check_line_assets.py "<pack_id>"
```

Fix any reported errors before continuing.

### Step 3 — Determine login mode
Check whether a saved session exists:

```bash
ls ~/.line-sticker-automation/storage_state.json 2>/dev/null \
  && echo "SESSION EXISTS" || echo "NO SESSION"
```

- **Session exists** → proceed headless (Step 4a).
- **No session** → must run headful for interactive login (Step 4b).

### Step 4a — Upload headless (session exists)

Dry-run first to confirm everything looks correct:

```bash
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<title>" \
    --description "<description>" \
    --dry-run
```

If dry-run passes, run the real upload:

```bash
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<title>" \
    --description "<description>" \
    --submit
```

### Step 4b — Upload headful (first login)

```bash
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<title>" \
    --description "<description>" \
    --headful --dry-run
```

Instruct the user to complete the QR code or OTP login in the browser window.
Session is saved automatically to `~/.line-sticker-automation/storage_state.json`.
After login succeeds, rerun without `--headful` for the actual submission.

### Step 5 — Resume interrupted upload
If a previous upload was interrupted, check for saved progress:

```bash
cat ~/.line-sticker-automation/progress.json 2>/dev/null
```

If progress exists, resume from the last completed step:

```bash
python3 scripts/line_uploader.py --resume --headful
```

### Step 6 — Confirm submission
After a successful run, inform the user:
- Submission is under LINE review (typically 3–7 business days).
- Review status is visible at: `https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/`
- Screenshots of each automation step are saved to `automation/screenshots/`.

## Error Handling

| Error | Resolution |
|---|---|
| Pre-flight banned keyword detected | Fix the title/description, or use `--skip-preflight` (not recommended) |
| `Session expired` / 401 on LINE | Delete `~/.line-sticker-automation/storage_state.json` and rerun with `--headful` |
| `Playwright timeout` on selector | Increase `SELECTOR_TIMEOUT` in `automation/config.py`; check `automation/screenshots/` for visual state |
| Sticker image dimension mismatch | Rerun `process-pipeline` skill; LINE requires exactly 370×320 px |
| Main image size wrong | Must be 240×240 px PNG — check `packs/<pack_id>/final/line_main/` |
| Tab icon size wrong | Must be 96×74 px PNG — check `packs/<pack_id>/final/line_tab/` |
| Upload stuck at image step | Delete `~/.line-sticker-automation/progress.json` and restart |
| Religious content rejection after submission | Pack was submitted before pre-flight was added; LINE rejects automatically |
