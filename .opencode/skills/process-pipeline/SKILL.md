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
python3 .opencode/skills/process-pipeline/scripts/check_inputs.py "<pack_id>"
```

If the script reports missing files, inform the user and stop.

### Step 2 — Choose processing mode

Determine which outputs are needed (infer from context or ask the user):

| Mode | When to use | Step |
|---|---|---|
| Static only (default) | LINE, WhatsApp, Telegram static | Step 3 |
| Skip background removal | Images already have transparent BGs | Step 3 with `--skip-bg` |
| LINE cover images | Always required for LINE upload | Step 3b (always run after static) |
| Animated TGS | Telegram animated stickers | Step 3c (separate call) |
| Video WEBM | Telegram video stickers | Step 3d (separate call) |

> **Important**: `--telegram-animated` and `--telegram-video` must each be run as
> **separate** `run_pipeline.py` invocations. Do not combine them with the static run.

### Step 3 — Run static processing pipeline
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

### Step 3b — Generate LINE cover images (line_main / line_tab)
`run_pipeline.py` does **not** auto-generate `line_main/` or `line_tab/`. Generate them
from the first sticker after static processing completes:

```bash
python3 - <<'EOF'
from PIL import Image
import pathlib, shutil

pack_id = "<pack_id>"
src = sorted(pathlib.Path(f"packs/{pack_id}/final/line").glob("*.png"))[0]

# Main image: 240x240
out_main = pathlib.Path(f"packs/{pack_id}/final/line_main")
out_main.mkdir(parents=True, exist_ok=True)
img = Image.open(src).convert("RGBA")
img.thumbnail((240, 240), Image.LANCZOS)
canvas = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
canvas.paste(img, ((240 - img.width) // 2, (240 - img.height) // 2))
canvas.save(out_main / "main.png")

# Tab icon: 96x74
out_tab = pathlib.Path(f"packs/{pack_id}/final/line_tab")
out_tab.mkdir(parents=True, exist_ok=True)
img2 = Image.open(src).convert("RGBA")
img2.thumbnail((96, 74), Image.LANCZOS)
canvas2 = Image.new("RGBA", (96, 74), (0, 0, 0, 0))
canvas2.paste(img2, ((96 - img2.width) // 2, (74 - img2.height) // 2))
canvas2.save(out_tab / "tab.png")

print("Done: line_main/main.png and line_tab/tab.png")
EOF
```

### Step 3c — Generate animated TGS (if requested)
Animated TGS must be run as a **separate** pipeline call — do **not** append
`--telegram-animated` to the static pipeline call above:

```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only \
    --input packs/<pack_id>/raw \
    --telegram-animated \
    --animation-preset bounce
```

Available presets: `bounce`, `wiggle`, `pulse`, `spin`, `shake`, `float`, `pop_in`, `slide_in`, `tada`, `heartbeat`.
Prefer `bounce` or `pulse` to stay under the 64 KB TGS limit.

### Step 3d — Generate video WEBM (if requested)
Similarly, video WEBM is a separate pipeline call:

```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only \
    --input packs/<pack_id>/raw \
    --telegram-video
```

### Step 4 — Verify outputs
Run the output checker to confirm all expected platform directories are populated:

```bash
python3 .opencode/skills/process-pipeline/scripts/check_outputs.py "<pack_id>"
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
| `ValueError: Unsupported format: TGS` | Do not include `telegram_animated` in the `platforms` list in `pack_config.py`. Run TGS via Step 3c instead. |
| Animated TGS file exceeds 64 KB limit | Switch to a simpler preset (`pulse` or `bounce`) — avoid `tada` or `heartbeat`. |
| Video WEBM exceeds 256 KB limit | Reduce animation duration in `pack_config.py` sticker `animation.duration_ms`. |
| `FFmpeg not found` | Install FFmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux). |
| `line_main/` or `line_tab/` missing | Run Step 3b — these are not auto-generated by `run_pipeline.py`. |
