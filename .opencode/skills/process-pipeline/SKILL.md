---
name: process-pipeline
description: >
  Runs the StickerFramework image processing pipeline on raw sticker images.
  Use when the user wants to process raw PNG images into platform-ready outputs
  (background removal, die-cut outline, resize, format conversion), generate
  animated TGS or video WEBM variants, or produce print sheets and distribution
  ZIPs. Don't use for generating new images via DALL-E, uploading to LINE, or
  publishing to Telegram.
---

# Skill: process-pipeline

## Purpose
Execute the image processing pipeline on an existing pack's raw images, producing platform-ready outputs in `packs/<pack_id>/final/`.

## Prerequisites
- Python 3.10+ with dependencies installed (`pip install -r requirements.txt`).
- Raw source images exist in `packs/<pack_id>/raw/` (PNG format).
- `packs/<pack_id>/pack_config.py` exists and is valid.

## Steps

### Step 1 — Resolve pack_id and paths
Determine `pack_id` from context:
- If the user specifies a pack name, use it directly.
- If a `pack_config.py` path is given, extract `pack_id` from it.
- Otherwise, ask the user which pack to process.

Verify the raw directory exists:

```bash
python3 .github/skills/process-pipeline/scripts/check_inputs.py "<pack_id>"
```

If the script reports missing files, inform the user and stop.

### Step 2 — Choose processing mode

Ask the user (or infer from context) which outputs are needed:

| Mode | Flag | Use when |
|---|---|---|
| Static only (default) | _(none)_ | LINE, WhatsApp, Telegram static |
| Skip background removal | `--skip-bg` | Images already have transparent backgrounds |
| Animated TGS | `--telegram-animated --animation-preset <preset>` | Telegram animated stickers |
| Video WEBM | `--telegram-video` | Telegram video stickers |

Available animation presets: `bounce`, `wiggle`, `pulse`, `spin`, `shake`, `float`, `pop_in`, `slide_in`, `tada`, `heartbeat`.

### Step 3 — Run processing pipeline
Execute from the repo root:

```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only \
    --input packs/<pack_id>/raw
```

If `--skip-bg` is needed:

```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only \
    --input packs/<pack_id>/raw \
    --skip-bg
```

If animated TGS is also needed, append:

```bash
    --telegram-animated --animation-preset bounce
```

### Step 4 — Verify outputs
Run the output checker to confirm all expected platform directories are populated:

```bash
python3 .github/skills/process-pipeline/scripts/check_outputs.py "<pack_id>"
```

The script prints a per-platform summary table. Report any missing outputs to the user.

### Step 5 — Report results
Summarise what was produced:

| Platform | Directory | File count |
|---|---|---|
| LINE stickers | `packs/<pack_id>/final/line/` | `<n>` |
| LINE main image | `packs/<pack_id>/final/line_main/` | 1 |
| LINE tab icon | `packs/<pack_id>/final/line_tab/` | 1 |
| WhatsApp | `packs/<pack_id>/final/whatsapp/` | `<n>` |
| Telegram | `packs/<pack_id>/final/telegram/` | `<n>` |
| iMessage | `packs/<pack_id>/final/imessage_large/` | `<n>` |
| Print | `packs/<pack_id>/final/print_etsy/` | `<n>` |

Inform the user of the next steps. See `references/next-steps.md` for platform-specific follow-up commands.

## Error Handling

| Error | Resolution |
|---|---|
| `Input directory not found` | Confirm raw images are in `packs/<pack_id>/raw/`. Run generation first if needed. |
| `Background removal failed` for an image | Add `--skip-bg` flag to bypass flood-fill and use rembg ML fallback. |
| Animated TGS file exceeds 64 KB limit | Switch to a simpler preset (`pulse` or `bounce`) — avoid `tada` or `heartbeat`. |
| Video WEBM exceeds 256 KB limit | Reduce animation duration in `pack_config.py` sticker `animation.duration_ms`. |
| `FFmpeg not found` | Install FFmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux). |
