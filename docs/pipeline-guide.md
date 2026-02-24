# Pipeline Guide

Complete guide to running the StickerFramework pipeline.

## Prerequisites

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
| Package | Version | Purpose |
|---------|---------|---------|
| Pillow | >=10.0.0 | Image processing |
| rembg | >=2.0.50 | AI background removal (U2-Net) |
| openai | >=1.0.0 | DALL-E 3 API |
| requests | >=2.31.0 | HTTP client |
| onnxruntime | >=1.16.0 | Neural network inference (rembg dependency) |
| numpy | >=1.24.0 | Array operations |
| scipy | >=1.11.0 | Connected component labeling (split_stickers) |

### 2. Configure API Keys

```bash
# Required for image generation (Stage 1)
export OPENAI_API_KEY="sk-..."

# Required for Telegram publishing (Stage 6)
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_USER_ID="your_numeric_user_id"
```

---

## Running the Full Pipeline

### Default Run (Generate + Process + Package)

```bash
python run_pipeline.py

# Or with a specific pack config:
python run_pipeline.py --pack packs/cappy-capybara-2/pack_config.py
```

This executes stages 1-5:
1. Generates all 24 stickers via DALL-E 3 (HD quality)
2. Processes images (bg removal, outline, resize for all platforms including LINE main/tab)
3. Creates tray icons
4. Generates metadata JSON files
5. Creates print sheets and distribution ZIP

**Estimated time**: ~10 minutes (most time is DALL-E generation with rate limits)
**Estimated cost**: ~$2.70 (HD quality, including ~40% redo rate)

### With Telegram Publishing

```bash
python run_pipeline.py --telegram
```

### With iMessage Xcode Project

```bash
python run_pipeline.py --imessage
```

### With Both

```bash
python run_pipeline.py --telegram --imessage
```

---

## CLI Options Reference

```
python run_pipeline.py [OPTIONS]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--pack <PATH>` | Path to `pack_config.py` file | `scripts/pack_config.py` |
| `--process-only` | Skip generation, use existing raw images | Off |
| `--generate-only` | Only generate images, skip processing | Off |
| `--input <DIR>` | Custom input directory for `--process-only` | None |
| `--skip-bg` | Skip background removal (images already transparent) | Off |
| `--standard` | Use standard quality DALL-E ($0.04/img vs $0.08) | HD |
| `--telegram` | Also publish to Telegram via Bot API | Off |
| `--imessage` | Also generate Xcode project for iMessage | Off |

---

## Common Workflows

### Workflow 1: Generate a New Pack from Scratch

```bash
# Edit pack_config.py with your character and sticker definitions
# Then run:
python run_pipeline.py
```

Output will be in `output/<pack_id>/`.

### Workflow 2: Process Pre-Existing Images

If you already have sticker images (e.g., from ChatGPT image generation or manual creation):

```bash
# Images with backgrounds that need removal
python run_pipeline.py --process-only --input ./my_stickers/

# Images already on transparent backgrounds
python run_pipeline.py --process-only --input ./my_stickers/ --skip-bg
```

### Workflow 3: Split a Sticker Sheet

If you have a single image containing multiple stickers in a grid layout:

```bash
# Split using the default pack (or set STICKER_PACK env var)
python split_stickers.py

# Split a specific pack
STICKER_PACK="Jesus Christ – Faith & Peace" python split_stickers.py

# Then process the split stickers for all platforms
python sticker_processor.py "Jesus Christ – Faith & Peace/split" \
    "Jesus Christ – Faith & Peace/final" \
    whatsapp telegram imessage_large line line_main line_tab print_etsy --skip-bg
```

The `split_stickers.py` script has a built-in pack registry (`PACKS` dict) with per-pack settings including input filename, grid layout, white-background threshold, and sticker names. Select a pack via the `STICKER_PACK` environment variable.

**Available packs:** `chubby mochi cat`, `chubby mochi hamster 2`, `Little Angel – Daily Blessings`, `Jesus Christ – Faith & Peace`, `Jesus Christ 1`, `Jesus Christ 2`, `Corporate Sloth – Tired but Trying`

The splitter:
1. Removes white background (configurable threshold per pack)
2. Detects individual sticker regions (connected components with row-bucketed sorting)
3. Crops each sticker
4. Resizes to 512x512 with padding
5. Saves as individual transparent PNGs to `<pack_name>/split/`

> **Note**: If stickers are touching in the sheet, the connected-component detection may merge them into one region. In that case, you need to manually sub-split the merged bounding boxes (check for aspect ratios significantly different from ~1:1).

### Workflow 4: Budget-Conscious Generation

```bash
# Use standard quality to halve the cost
python run_pipeline.py --standard
```

| Quality | Per Image | 24 Images | With Redo |
|---------|-----------|-----------|-----------|
| Standard | $0.04 | $0.96 | ~$1.35 |
| HD | $0.08 | $1.92 | ~$2.70 |

### Workflow 5: Iterate on Specific Stickers

1. Run the full pipeline once
2. Review the generated images in `output/<pack_id>/raw/`
3. Delete unsatisfactory stickers
4. Re-run the pipeline -- it will only regenerate missing stickers
5. Process again with `--process-only`

### Workflow 6: Process with Text Overlays

If your `pack_config.py` includes `"text"` fields on individual stickers, use `--pack-config` with the standalone processor:

```bash
# Process raw images and render text on stickers that have a "text" key
python scripts/sticker_processor.py packs/cappy-capybara-2/raw/ \
    packs/cappy-capybara-2/final/ \
    --pack-config packs/cappy-capybara-2/pack_config.py
```

Or via the full pipeline with `--pack`:

```bash
python scripts/run_pipeline.py --pack packs/cappy-capybara-2/pack_config.py --process-only
```

Text is rendered as a **post-processing** step (via PIL) after background removal, color normalization, and white outline — but before platform-specific resize. This ensures crisp text at every output size.

See [Configuration Guide — Text Overlay](configuration.md#text-overlay) for the full text config schema.

### Workflow 7: Telegram-Only Publish

If you have already-processed stickers and just want to publish to Telegram:

```python
from telegram_publisher import TelegramStickerPublisher
from pack_config import PACK_CONFIG

publisher = TelegramStickerPublisher(bot_token="YOUR_TOKEN")
publisher.create_sticker_set(
    user_id=YOUR_USER_ID,
    name="pack01_emotions_v1",
    title="Mochi Emotions Vol. 1",
    sticker_paths=["path/to/sticker1.webp", ...],
    emojis_list=["😊", "❤️", ...],
)
```

---

## Pipeline Output Reference

After a full pipeline run, the output directory contains:

```
output/<pack_id>/
├── raw/                         # Generated DALL-E images
│   ├── 01_happy.png             # 1024x1024 raw images
│   ├── 01_happy_prompt.txt      # Generation prompt + revised prompt
│   └── ...                      # (24 images + 24 prompt files)
├── final/                       # Processed platform-ready stickers
│   ├── whatsapp/                # 512x512 WEBP, <100KB
│   ├── telegram/                # 512x512 WEBP, <256KB
│   ├── imessage_large/          # 618x618 PNG, <500KB
│   ├── line/                    # 370x320 PNG, <1000KB
│   ├── line_main/               # 240x240 PNG, <1000KB (LINE store cover)
│   ├── line_tab/                # 96x74 PNG, <1000KB (LINE chat tray icon)
│   └── print_etsy/              # 2048x2048 PNG, high-res
├── metadata/
│   ├── whatsapp_pack.json       # WhatsApp/Sticker.ly metadata
│   ├── telegram_pack.json       # Telegram sticker set config
│   ├── line_pack.json           # LINE Creators Market metadata
│   └── pack_summary.json        # Human-readable summary
├── dist/
│   ├── sticker_sheet_letter.png # US Letter print layout (300 DPI)
│   ├── sticker_sheet_a4.png     # A4 print layout (300 DPI)
│   ├── social_preview.png       # 3000x3000 preview for Etsy/IG
│   └── pack01_emotions_v1_distribution.zip
└── xcode/                       # (if --imessage was used)
    └── MochiEmotionsVol1/
        ├── MochiEmotionsVol1.xcodeproj/
        ├── Stickers.xcstickers/
        └── Info.plist
```

For packs processed via `split_stickers.py` + `sticker_processor.py`, the output lives directly in the pack folder:

```
<Pack Name>/
├── sticker_pack.png             # Original sheet image
├── split/                       # Individual split stickers (512x512 PNG)
│   ├── 01_sticker_name.png
│   └── ...
└── final/                       # Processed platform-ready stickers
    ├── whatsapp/                # 512x512 WEBP, <100KB
    ├── telegram/                # 512x512 WEBP, <256KB
    ├── imessage_large/          # 618x618 PNG, <500KB
    ├── line/                    # 370x320 PNG, <1000KB
    ├── line_main/               # 240x240 PNG (LINE store cover)
    ├── line_tab/                # 96x74 PNG (LINE chat tray icon)
    └── print_etsy/              # 2048x2048 PNG, high-res
```
output/pack01_emotions_v1/
├── raw/                         # Generated DALL-E images
│   ├── 01_happy.png             # 1024x1024 raw images
│   ├── 01_happy_prompt.txt      # Generation prompt + revised prompt
│   └── ...                      # (24 images + 24 prompt files)
├── final/                       # Processed platform-ready stickers
│   ├── whatsapp/                # 512x512 WEBP, <100KB
│   ├── telegram/                # 512x512 WEBP, <256KB
│   ├── imessage_large/          # 618x618 PNG, <500KB
│   ├── line/                    # 370x320 PNG, <1000KB
│   └── print_etsy/              # 2048x2048 PNG, high-res
├── metadata/
│   ├── whatsapp_pack.json       # WhatsApp/Sticker.ly metadata
│   ├── telegram_pack.json       # Telegram sticker set config
│   ├── line_pack.json           # LINE Creators Market metadata
│   └── pack_summary.json        # Human-readable summary
├── dist/
│   ├── sticker_sheet_letter.png # US Letter print layout (300 DPI)
│   ├── sticker_sheet_a4.png     # A4 print layout (300 DPI)
│   ├── social_preview.png       # 3000x3000 preview for Etsy/IG
│   └── pack01_emotions_v1_distribution.zip
└── xcode/                       # (if --imessage was used)
    └── MochiEmotionsVol1/
        ├── MochiEmotionsVol1.xcodeproj/
        ├── Stickers.xcstickers/
        └── Info.plist
```

---

## Troubleshooting

### DALL-E Content Policy Rejection
Some emotion prompts (e.g., "angry" or "crying") may trigger content policy filters. The pipeline handles this gracefully -- it logs the rejection and moves to the next sticker. Rerun to retry, or modify the sticker description in `pack_config.py`.

### WebP File Size Too Large
If a sticker exceeds the platform's WebP file size limit, the processor uses binary search on quality settings. If it still can't fit, check that the source image isn't unusually complex.

### rembg First-Run Download
The first time `rembg` runs, it downloads the U2-Net model (~170MB). Ensure you have internet connectivity for the initial run.

### Rate Limiting
DALL-E 3 has rate limits. The pipeline includes a configurable delay between requests (default 12 seconds). If you hit rate limits, increase the delay in `run_pipeline.py`.

### Telegram Bot Permissions
The Telegram bot must be able to create sticker sets. Ensure:
1. The bot token is from `@BotFather`
2. You've started a conversation with the bot
3. The `user_id` is correct (use `@userinfobot` to find yours)
