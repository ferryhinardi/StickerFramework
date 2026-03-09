# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

StickerFramework is an end-to-end sticker pack creation system for multi-platform distribution. It automates the full workflow from AI generation (DALL-E) through image processing to automated publishing on LINE, Telegram, iMessage, WhatsApp, and print platforms.

The framework has successfully created 14 sticker packs and features sophisticated browser automation (Playwright), multi-stage image processing, and platform-specific optimizations.

## Common Development Commands

### Environment Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium

# Copy environment template
cp .env.example .env
# Then edit .env with your API keys
```

### Image Processing Pipeline
```bash
# Split composite sticker sheet into individual PNGs
STICKER_PACK="pack-name" python3 scripts/split_stickers.py

# Process images for all platforms (from raw/ to final/)
python3 scripts/run_pipeline.py --process-only --input packs/<pack-name>/split --skip-bg

# Full pipeline: generate via DALL-E + process
export OPENAI_API_KEY="sk-..."
python3 scripts/run_pipeline.py

# Use specific pack config
python3 scripts/run_pipeline.py --pack packs/<pack-name>/pack_config.py --process-only
```

### LINE Creator Market Upload
```bash
# First run: headful mode for interactive login (QR/OTP)
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack-name>/final \
    --title "Pack Title" \
    --description "Pack description" \
    --headful --dry-run

# After session saved: headless upload
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack-name>/final \
    --title "Pack Title" \
    --description "Pack description" \
    --submit

# Resume interrupted upload
python3 scripts/line_uploader.py --resume --headful

# Skip pre-flight content check (religious content filter)
python3 scripts/line_uploader.py ... --skip-preflight

# Upload LINE animated stickers (APNG)
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack-name>/final \
    --title "Pack Title" \
    --description "Pack description" \
    --animated --headful
```

### Telegram Publishing
```bash
# Publish static stickers
python3 scripts/telegram_publisher.py --pack-dir packs/<pack-name>/final

# Generate animated TGS stickers (Lottie)
python3 scripts/animated_converter.py \
    --pack-dir packs/<pack-name>/final \
    --format tgs --preset bounce

# Generate video WEBM stickers
python3 scripts/animated_converter.py \
    --pack-dir packs/<pack-name>/final \
    --format webm --preset wiggle

# Publish animated/video sets
python3 scripts/telegram_publisher.py \
    --pack-dir packs/<pack-name>/final \
    --format animated --title "PackNameAnimated"

# Available animation presets:
# bounce, wiggle, pulse, spin, shake, float, pop_in, slide_in, tada, heartbeat
```

### iMessage (Fastlane)
```bash
# Generate Xcode project + build + upload (dry run)
python3 scripts/imessage_publisher.py \
    --pack-dir packs/<pack-name>/final \
    --dry-run

# Full submission to App Store
python3 scripts/imessage_publisher.py \
    --pack-dir packs/<pack-name>/final

# Manual Fastlane lanes
cd fastlane
bundle install
bundle exec fastlane certs           # Sync certificates via match
bundle exec fastlane build           # Build .ipa
bundle exec fastlane upload          # Upload to App Store Connect
bundle exec fastlane publish         # Full pipeline
```

### WhatsApp Native
```bash
# Export pack for WhatsApp Android app
python3 scripts/whatsapp_exporter.py \
    --pack-dir packs/<pack-name>/final

# Export + push to server
python3 scripts/whatsapp_exporter.py \
    --pack-dir packs/<pack-name>/final \
    --server-url https://your-server.com \
    --api-key your-api-key

# Run sticker server locally
docker build -t whatsapp-stickers server/
docker run -p 8000:8000 -v ./packs:/app/sticker_packs whatsapp-stickers

# Build Android app
cd whatsapp-sticker-app
./gradlew assembleRelease
```

### Testing
```bash
# Run E2E test (upload to existing LINE draft)
python3 scripts/e2e_test.py

# Run text compositor tests
python3 scripts/test_text_compositor.py
```

## Architecture Overview

### Core Pipeline Stages

The `scripts/run_pipeline.py` orchestrator drives the entire workflow:

1. **Generation** (`image_generator.py`, `comfyui_generator.py`)
   - Creates stickers via DALL-E 3 API or ComfyUI
   - Reads character/style/emotion definitions from `pack_config.py`
   - Outputs to `packs/<name>/raw/`

2. **Splitting** (`split_stickers.py`)
   - Uses connected-component analysis to split composite sheets
   - Handles ChatGPT-generated multi-sticker images
   - Outputs to `packs/<name>/split/`

3. **Processing** (`sticker_processor.py`)
   - Flood-fill corner-based background removal (preserves interior whites)
   - Die-cut white outline generation via alpha dilation
   - Multi-platform resizing (LINE: 370x320, WhatsApp: 512x512, etc.)
   - Format conversion (PNG → WEBP)
   - Outputs to `packs/<name>/final/<platform>/`

4. **Animation** (`animated_converter.py`, `animation_presets.py`)
   - Converts static PNGs to animated TGS (Lottie), video WEBM (VP9), or APNG (LINE animated)
   - 10+ animation presets (bounce, wiggle, pulse, spin, etc.)
   - Respects platform size limits (TGS: 64KB, WEBM: 256KB, APNG: 300KB target / 1MB hard limit)

5. **Metadata** (`run_pipeline.py::stage_metadata`)
   - Generates platform-specific JSON: `whatsapp_contents.json`, `telegram_emojis.json`, `line_metadata.json`, `line_animated_metadata.json`

6. **Distribution** (`create_print_sheet.py`)
   - Creates print sheets (US Letter, A4) for physical stickers
   - Generates social preview images
   - Packages into distribution ZIPs

### LINE Browser Automation

The `automation/` module implements a stateful, resumable Playwright automation:

- **`line_auth.py`**: OAuth login with session persistence (`~/.line-sticker-automation/storage_state.json`)
- **`line_create_submission.py`**: Creates draft, fills display info (title, description, AI usage, categories, copyright)
- **`line_upload_images.py`**: Uploads main image (240x240), tab icon (96x74), and 8 stickers (370x320)
- **`line_animated_upload.py`**: Uploads animated APNG main image, tab icon, and 8/16/24 animated stickers (320x270)
- **`line_set_metadata.py`**: Sets display information and tag settings with emoji auto-assignment
- **`line_set_price.py`**: Selects price tier (default: Rp23.000+)
- **`line_submit.py`**: Final review and submission to LINE Creator Market

Progress is saved after each step to `~/.line-sticker-automation/progress.json` for resumability.

### Pack Configuration System

Every pack is driven by a `pack_config.py` (or `packs/<name>/pack_config.py`):

```python
PACK_CONFIG = {
    "pack_id": "pack-name",
    "pack_name": "Display Name",
    "publisher": "Your Brand",
    "character": {...},      # name, species, body_color, eye_style, proportions
    "style": {...},          # outline_type, coloring, background, art_style
    "platforms": [...],      # "line", "whatsapp", "telegram", "imessage", "print"
    "stickers": [
        {
            "id": "01_happy",
            "emotion": "Happy",
            "pose": "Jumping with arms raised",
            "props": "Sparkle effects",
            "emoji": "😊",
            "animation": {"type": "bounce", "duration_ms": 2000}
        },
        ...
    ]
}
```

The config drives prompt generation, file naming, metadata, and animation hints.

### Directory Structure Conventions

```
packs/<pack-name>/
├── sticker_pack.png              # Source composite sheet (if applicable)
├── split/                        # Individual PNGs from sheet splitter
├── raw/                          # DALL-E generated images (pre-processing)
├── final/                        # Platform-ready outputs
│   ├── line/                     # 370x320 PNG
│   ├── line_main/                # 240x240 PNG (cover)
│   ├── line_tab/                 # 96x74 PNG (chat icon)
│   ├── line_animated/            # 320x270 APNG (animated stickers)
│   ├── line_animated_main/       # 240x240 APNG (animated cover)
│   ├── line_animated_tab/        # 96x74 APNG (animated chat icon)
│   ├── whatsapp/                 # 512x512 WEBP (Sticker.ly)
│   ├── whatsapp_native/          # 512x512 WEBP + contents.json
│   ├── telegram/                 # 512x512 WEBP
│   ├── telegram_animated/        # 512x512 TGS
│   ├── telegram_video/           # 512x512 WEBM
│   ├── imessage_large/           # 618x618 PNG
│   └── print_etsy/               # 2048x2048 PNG
├── metadata/                     # Platform metadata JSON
└── dist/                         # Print sheets, previews, ZIPs
```

### Key Technical Constraints

**LINE Creator Market**:
- Static stickers only: 8, 16, 24, 32, or 40 per set
- Sticker dimensions: 370x320px PNG, max 1MB
- Main image: 240x240px PNG
- Tab icon: 96x74px PNG
- Animated stickers (APNG): 8, 16, or 24 per set
- Animated sticker dimensions: 320x270px APNG (.png extension), max 1MB
- Animation: 5-20 frames, 1-4 seconds, 1-4 loops per APNG
- Guideline 3.13: Religious content (including Jesus, Mary, crosses) is prohibited and will cause instant rejection
- Pre-flight check: `line_preflight_check.py` scans metadata for banned keywords before upload

**Telegram**:
- Static (WEBP): 512x512, max 256KB
- Animated (TGS): 512x512, max 64KB, 3-second Lottie
- Video (WEBM): 512x512, max 256KB, 3-second VP9

**WhatsApp**:
- Sticker.ly: 512x512 WEBP, max 100KB (manual upload)
- Native: 512x512 WEBP via ContentProvider + FastAPI server
- Tray icon: 96x96 WEBP

**iMessage**:
- Sticker size: 618x618 PNG, max 500KB
- Xcode project generated via `xcodegen`
- Fastlane automation: `match` (code signing) → `gym` (build) → `deliver` (upload)

### Image Processing Implementation Details

**Background Removal** (`sticker_processor.py`):
- Flood-fill from all four corners to detect white background
- Preserves interior whites (eyes, clothing details)
- Falls back to rembg ML model if flood-fill fails

**Outline Generation**:
- Binary dilation on alpha channel to expand edges by 10px
- Composite white outline behind original image
- Creates die-cut sticker appearance

**Platform Resizing**:
- Maintains aspect ratio, adds transparent padding to square canvas
- Platform-specific dimensions defined in `automation/config.py` and `platform-specs.md`

### Content Policy Enforcement

The `line_preflight_check.py` module enforces LINE's guideline 3.13:

- Scans `metadata/pack_summary.json` for banned keywords: "jesus", "christ", "mary", "cross", "faith", "peace", "angel", "bible", "god"
- Blocks upload if religious theme detected
- Can be bypassed with `--skip-preflight` (not recommended)

**Historical context**: 5 packs were created before this check was added (`jesus-faith-and-peace`, `jesus-christ-1`, `jesus-christ-2`, `little-angel`). These packs are rejected by LINE but remain in the repo as examples.

### Environment Variables

See `.env.example` for full reference. Critical vars:

- `OPENAI_API_KEY`: DALL-E API access (or use ChatGPT Go plan)
- `LINE_EMAIL`, `LINE_PASSWORD`: LINE Creator Market credentials
- `TELEGRAM_BOT_TOKEN`: Telegram Bot API token
- `APPLE_ID`, `APPLE_TEAM_ID`, `APPLE_APP_SPECIFIC_PASSWORD`: iMessage/Fastlane
- `MATCH_GIT_URL`, `MATCH_PASSWORD`: Fastlane match code signing
- `WHATSAPP_SERVER_URL`, `WHATSAPP_SERVER_API_KEY`: WhatsApp server
- `STICKER_PACK`: Default pack name for `split_stickers.py`

### Documentation

Extensive documentation in `docs/`:

- `01-project-overview.md` to `11-migration-guide.md`: Comprehensive guides
- `platform-specs.md`: Platform requirements reference
- `guides/distribution_guide.md`: Multi-platform publishing strategy
- `guides/stickerly_guide.md`: Manual WhatsApp upload via Sticker.ly

### Existing Sticker Packs

14 packs under `packs/`:
- `boba-milo-1` through `boba-milo-5`: Otter duo
- `chubby-mochi-cat`, `chubby-mochi-hamster`, `chubby-mochi-hamster-2`: Kawaii animals
- `corporate-sloth`, `office-teddy-bear`: Office themes
- `jesus-faith-and-peace`, `jesus-christ-1`, `jesus-christ-2`, `little-angel`: Religious (LINE-rejected)
- `CappyCapybara`: Example pack in root

Each pack follows the standard directory layout above.

## Development Guidelines

- **Session management**: LINE automation saves session to `~/.line-sticker-automation/`. First run requires `--headful` for manual login.
- **Progress resumability**: `line_uploader.py --resume` continues from last completed step.
- **Screenshots**: Automation captures screenshots to `automation/screenshots/` for debugging.
- **Pack naming**: Use kebab-case for pack directories (e.g., `boba-milo-5`, `chubby-mochi-cat`).
- **Image quality**: Use `--standard` for DALL-E to save cost ($0.04 vs $0.08 per image).
- **Animation presets**: Defined in `animation_presets.py`. Each preset returns a Lottie JSON template.
- **Server deployment**: WhatsApp server can be deployed via Docker (`server/Dockerfile`).
- **Android builds**: WhatsApp app uses Kotlin + Gradle 8.0+.

## Key Files to Modify

- **`scripts/pack_config.py`**: Default pack configuration (character, style, stickers)
- **`automation/config.py`**: LINE URLs, selectors, timeouts, default submission values
- **`animation_presets.py`**: Lottie animation templates
- **`templates/line_submission_defaults.json`**: LINE form defaults
- **`templates/imessage_metadata.json`**: iMessage app metadata template
- **`server/whatsapp_api.py`**: FastAPI endpoints for WhatsApp sticker server

## Troubleshooting

- **LINE upload stuck**: Check `automation/screenshots/` for visual debugging
- **Session expired**: Delete `~/.line-sticker-automation/storage_state.json` and rerun with `--headful`
- **Playwright timeout**: Increase `PAGE_LOAD_TIMEOUT` in `automation/config.py`
- **Background removal failed**: Use `--skip-bg` to bypass flood-fill
- **Religious content blocked**: Use `--skip-preflight` to bypass (not recommended for actual submission)
- **Animation size too large**: Use simpler presets (e.g., `pulse` instead of `tada`)
- **iMessage build fails**: Verify Fastlane match git repo is configured and certificates are valid
- **WhatsApp Android build fails**: Check `local.properties` for valid Android SDK path

## External Dependencies

- Python 3.10+
- Playwright + Chromium (LINE automation)
- FFmpeg with VP9 support (video stickers)
- Fastlane + xcodegen (iMessage)
- Docker (WhatsApp server)
- Android SDK + Gradle (WhatsApp app)
- Ruby (Fastlane dependency)

## Repository Structure Reference

- `scripts/`: All CLI entry points and pipeline stages
- `automation/`: Playwright browser automation for LINE
- `fastlane/`: iMessage App Store automation (Fastfile, Matchfile, metadata)
- `server/`: WhatsApp sticker FastAPI server
- `whatsapp-sticker-app/`: WhatsApp Android sticker app (Kotlin + Gradle)
- `templates/`: JSON/YAML templates for config defaults
- `packs/`: 14 existing sticker packs (kebab-case names)
- `docs/`: 20+ documentation files
- `reference/`: Non-pipeline assets (brand kit, samples, screenshots)
- `fonts/`: Custom fonts for text compositor
