# StickerFramework

An end-to-end sticker pack creation framework — from AI ideation through DALL-E generation, image processing, to automated multi-platform publishing. Supports LINE, WhatsApp (Sticker.ly + native Android app), Telegram (static, animated, video), iMessage (Fastlane), Etsy, and Gumroad. Built for creators who want to design, process, and publish kawaii-style sticker packs at scale.

## Overview

StickerFramework takes a character definition and sticker list from a config file, generates images using DALL-E (via ChatGPT Go plan), processes them through a multi-stage pipeline (splitting, background removal, color normalization, outline generation, platform-specific resizing), and publishes to 7+ platforms with varying levels of automation:

- **LINE** — Playwright browser automation for Creator Market uploads
- **Telegram** — Fully automated via Bot API (static WEBP, animated TGS, video WEBM)
- **iMessage** — Xcode project generation + Fastlane App Store submission
- **WhatsApp Native** — Custom Android app with ContentProvider + server API
- **WhatsApp (Sticker.ly)** — Manual upload via Sticker.ly app
- **Etsy / Gumroad** — High-res print-ready exports with distribution ZIPs

**14 sticker packs** have been created with this framework so far.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 2. Copy and fill environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Process existing sticker sheet
STICKER_PACK="Boba & Milo – Cheerful Otter Duo 5" python3 scripts/split_stickers.py
python3 scripts/run_pipeline.py --process-only --input packs/boba-milo-5/split --skip-bg

# 4. Upload to LINE Creator Market (first run — interactive login)
python3 scripts/line_uploader.py \
    --pack-dir packs/boba-milo-5/final \
    --title "Boba & Milo Cheerful Otter Duo 5" \
    --description "A fun, caring otter duo for everyday chat" \
    --headful --dry-run

# 5. Publish to Telegram (static)
python3 scripts/telegram_publisher.py --pack-dir packs/boba-milo-5/final

# 6. Generate animated Telegram stickers
python3 scripts/animated_converter.py --pack-dir packs/boba-milo-5/final \
    --format tgs --preset bounce

# 7. Export for WhatsApp native
python3 scripts/whatsapp_exporter.py --pack-dir packs/boba-milo-5/final

# 8. Build iMessage app + submit via Fastlane
python3 scripts/imessage_publisher.py --pack-dir packs/boba-milo-5/final
```

## Features

- **AI Image Generation** — Generates stickers via DALL-E with structured character-consistent prompts (ChatGPT Go plan, $5/month)
- **Composite Sheet Splitting** — Connected-component analysis to split ChatGPT-generated sticker sheets into individual PNGs
- **Background Removal** — Flood-fill corner-based white background removal (preserves interior whites)
- **Die-Cut Outline** — Automatic white outline generation via alpha dilation
- **Multi-Platform Export** — Resizes and optimizes for LINE, WhatsApp, Telegram, iMessage, and print
- **LINE Automation** — Playwright browser automation for LINE Creator Market uploads (login, fill forms, upload images, submit)
- **Telegram Auto-Publish** — Fully automated sticker set creation via Telegram Bot API (static, animated TGS, video WEBM)
- **Telegram Animations** — Convert static stickers to animated TGS (Lottie) and video WEBM (VP9) with 10+ presets (bounce, wiggle, pulse, spin, etc.)
- **iMessage Fastlane** — Xcode project generation via `xcodegen` + automated App Store submission via Fastlane (match, build, deliver)
- **WhatsApp Native** — Custom Android app with ContentProvider integration + FastAPI server for direct WhatsApp sticker pack installation
- **WhatsApp Sticker.ly** — Export optimized WEBP stickers for manual Sticker.ly upload
- **Print Sheet Generation** — Creates print-ready layouts (US Letter, A4) for physical stickers
- **Progress Recovery** — LINE upload automation saves progress after each step; resume on failure

## Pipeline Stages

| Stage         | Script                     | Description                                      | Output              |
| ------------- | -------------------------- | ------------------------------------------------ | ------------------- |
| 0. Split      | `split_stickers.py`        | Split composite sheet into individual PNGs       | `split/`            |
| 1. Generate   | `image_generator.py`       | Create images via DALL-E 3 (or use split output) | `raw/`              |
| 2. Process    | `sticker_processor.py`     | Bg removal, outline, resize per platform         | `final/`            |
| 3. Tray Icons | `run_pipeline.py`          | Create 96x96 / 96x74 pack icons                  | Tray/tab icon files |
| 4. Metadata   | `run_pipeline.py`          | Generate platform JSON metadata                  | `metadata/`         |
| 5. Package    | `create_print_sheet.py`    | Print sheets, social previews, ZIP               | `dist/`             |
| 6. Upload     | `line_uploader.py`         | Automated LINE Creator Market submission         | Live on LINE        |
| 7. Telegram   | `telegram_publisher.py`    | Publish static stickers to Telegram              | Live sticker set    |
| 8. Animate    | `animated_converter.py`    | Convert to TGS (Lottie) or WEBM (VP9 video)     | `telegram_animated/` or `telegram_video/` |
| 9. iMessage   | `imessage_publisher.py`    | Xcode project + Fastlane App Store submission    | `.ipa` + App Store  |
| 10. WhatsApp  | `whatsapp_exporter.py`     | Native WhatsApp pack export + server push        | `whatsapp_native/`  |

## Supported Platforms

| Platform               | Format | Size      | Max File Size | Automation |
| ---------------------- | ------ | --------- | ------------- | ---------- |
| LINE (stickers)        | PNG    | 370x320   | 1 MB          | Playwright browser |
| LINE (main)            | PNG    | 240x240   | 1 MB          | Playwright browser |
| LINE (tab)             | PNG    | 96x74     | 1 MB          | Playwright browser |
| WhatsApp (Sticker.ly)  | WEBP   | 512x512   | 100 KB        | Manual upload |
| WhatsApp (Native)      | WEBP   | 512x512   | 100 KB        | Android app + server |
| Telegram (static)      | WEBP   | 512x512   | 256 KB        | Bot API |
| Telegram (animated)    | TGS    | 512x512   | 64 KB         | Bot API |
| Telegram (video)       | WEBM   | 512x512   | 256 KB        | Bot API |
| iMessage               | PNG    | 618x618   | 500 KB        | Fastlane |
| Etsy / Gumroad (Print) | PNG    | 2048x2048 | Unlimited     | Manual listing |

## Project Structure

```
StickerFramework/
├── scripts/                         # Pipeline + CLI scripts
│   ├── run_pipeline.py              #   Master pipeline orchestrator
│   ├── image_generator.py           #   DALL-E image generation
│   ├── sticker_processor.py         #   Multi-platform image processing
│   ├── split_stickers.py            #   Composite sheet → individual PNGs
│   ├── pack_config.py               #   Character/style/sticker definitions
│   ├── create_print_sheet.py        #   Print sheets & distribution ZIP
│   ├── prepare_imessage_pack.py     #   Xcode project generator (legacy)
│   ├── imessage_publisher.py        #   iMessage Fastlane publisher
│   ├── telegram_publisher.py        #   Telegram Bot API publisher
│   ├── animated_converter.py        #   TGS/WEBM animated sticker converter
│   ├── animation_presets.py         #   Lottie animation preset definitions
│   ├── whatsapp_exporter.py         #   WhatsApp native pack exporter
│   └── line_uploader.py             #   LINE Creator Market upload CLI
│
├── automation/                      # Playwright browser automation
│   ├── config.py                    #   URLs, timeouts, submission defaults
│   ├── utils.py                     #   safe_click, retry, screenshot helpers
│   ├── line_auth.py                 #   Login + session persistence
│   ├── line_create_submission.py    #   Create draft submission
│   ├── line_upload_images.py        #   Upload main/tab/sticker images
│   ├── line_set_metadata.py         #   Display Information + Tag Settings
│   ├── line_set_price.py            #   Price tier selection
│   └── line_submit.py               #   Final review and submit
│
├── fastlane/                        # iMessage App Store automation
│   ├── Appfile                      #   App identifier + Apple ID
│   ├── Matchfile                    #   Code signing config
│   ├── Fastfile                     #   Lane definitions (build, upload, release)
│   ├── Gemfile                      #   Ruby dependencies
│   ├── Pluginfile                   #   Fastlane plugins
│   └── metadata/en-US/              #   App Store metadata templates
│
├── server/                          # WhatsApp sticker server
│   ├── whatsapp_api.py              #   FastAPI server for sticker delivery
│   ├── Dockerfile                   #   Container deployment
│   ├── .dockerignore                #   Docker build exclusions
│   └── requirements.txt             #   Python dependencies
│
├── whatsapp-sticker-app/            # WhatsApp Android sticker app
│   ├── app/src/main/
│   │   ├── java/.../stickers/       #   ContentProvider, activities, adapters
│   │   ├── res/                     #   Layouts, strings, styles
│   │   └── AndroidManifest.xml
│   ├── build.gradle.kts
│   └── settings.gradle.kts
│
├── templates/                       # Config templates
│   ├── line_submission_defaults.json
│   ├── imessage_metadata.json       #   iMessage app metadata template
│   └── imessage_project.yml         #   xcodegen project spec template
│
├── packs/                           # 14 sticker packs (kebab-case)
│   ├── boba-milo-1/ ... boba-milo-5/
│   ├── chubby-mochi-cat/
│   ├── chubby-mochi-hamster/
│   ├── chubby-mochi-hamster-2/
│   ├── corporate-sloth/
│   ├── jesus-faith-and-peace/
│   ├── jesus-christ-1/
│   ├── jesus-christ-2/
│   ├── little-angel/
│   └── office-teddy-bear/
│
├── docs/                            # Documentation (20+ files)
│   ├── 01-project-overview.md
│   ├── 02-end-to-end-workflow.md
│   ├── 03-chatgpt-prompt-templates.md
│   ├── 04-dalle-generation-guide.md
│   ├── 05-image-processing-pipeline.md
│   ├── 06-line-sticker-specifications.md
│   ├── 07-line-submission-template.md
│   ├── 08-browser-automation-design.md
│   ├── 09-repo-structure.md
│   ├── 10-troubleshooting-faq.md
│   ├── 11-migration-guide.md
│   ├── platform-specs.md
│   ├── implementation-plan-phases.md
│   └── guides/
│
├── reference/                       # Non-pipeline assets
│   ├── line-creator/                #   LINE screenshots, tax PDFs
│   ├── brand_kit.md
│   ├── cartoon-faces/
│   ├── stickers/
│   └── stickers-gen/
│
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

### Standard Pack Layout

Every pack under `packs/` follows this structure:

```
packs/<pack-name>/
├── sticker_pack.png              # Source composite sheet
├── split/                        # Individual stickers from sheet
│   ├── 01_emotion.png
│   └── ...
└── final/                        # Platform-ready outputs
    ├── line/                     # 370x320 PNG
    ├── line_main/                # 240x240 PNG (cover)
    ├── line_tab/                 # 96x74 PNG (chat icon)
    ├── whatsapp/                 # 512x512 WEBP (Sticker.ly)
    ├── whatsapp_native/          # 512x512 WEBP (Android app)
    ├── whatsapp_native_tray/     # 96x96 WEBP (tray icon)
    ├── telegram/                 # 512x512 WEBP (static)
    ├── telegram_animated/        # 512x512 TGS (Lottie animation)
    ├── telegram_video/           # 512x512 WEBM (VP9 video)
    ├── imessage_large/           # 618x618 PNG
    └── print_etsy/               # 2048x2048 PNG
```

## LINE Upload Automation

The `line_uploader.py` CLI automates the entire LINE Creator Market submission:

```bash
# Step 1: First run — headful mode for interactive login (QR code / OTP)
python3 scripts/line_uploader.py \
    --pack-dir packs/boba-milo-5/final \
    --title "Boba & Milo Cheerful Otter Duo 5" \
    --description "A fun, caring otter duo" \
    --headful --dry-run

# Step 2: After session saved — headless upload + submit
python3 scripts/line_uploader.py \
    --pack-dir packs/boba-milo-5/final \
    --title "Boba & Milo Cheerful Otter Duo 5" \
    --description "A fun, caring otter duo" \
    --submit

# Resume from last progress (if interrupted)
python3 scripts/line_uploader.py --resume --headful
```

### Automation Steps

1. **Authenticate** — Restore saved session or interactive login via QR code
2. **Create Submission** — Navigate to create page, select sticker type, save draft
3. **Fill Display Info** — Title, description, AI usage, categories, copyright
4. **Upload Images** — Main image (240x240), tab icon (96x74), 8 sticker PNGs (370x320)
5. **Tag Settings** — Auto-assign emoji tags based on sticker name keywords
6. **Set Price** — Select price tier (+23,000 IDR default)
7. **Submit** — Click "Request" for review (only with `--submit` flag)

### LINE Account Details

- Creator ID: 5964498
- URL path: `LQu3ADYzrcqp2KCs`
- Copyright: FHStudio
- Default price: +23,000 IDR
- Sticker type: Static, 8 per set

## Telegram Animated & Video Stickers

Convert static stickers to animated TGS (Lottie) or video WEBM (VP9) formats using `animated_converter.py`, then publish via `telegram_publisher.py`.

```bash
# Generate animated TGS stickers with bounce preset
python3 scripts/animated_converter.py \
    --pack-dir packs/boba-milo-5/final \
    --format tgs --preset bounce

# Generate video WEBM stickers with wiggle preset
python3 scripts/animated_converter.py \
    --pack-dir packs/boba-milo-5/final \
    --format webm --preset wiggle

# Publish animated sticker set to Telegram
python3 scripts/telegram_publisher.py \
    --pack-dir packs/boba-milo-5/final \
    --format animated --title "BobaAndMilo5Animated"

# Publish video sticker set to Telegram
python3 scripts/telegram_publisher.py \
    --pack-dir packs/boba-milo-5/final \
    --format video --title "BobaAndMilo5Video"
```

### Animation Presets

| Preset    | Effect                        | Best For          |
| --------- | ----------------------------- | ----------------- |
| bounce    | Vertical bounce with squash   | Energetic emotes  |
| wiggle    | Side-to-side rotation         | Playful greetings |
| pulse     | Scale up/down breathing       | Love/heart emotes |
| spin      | Full 360-degree rotation      | Celebration       |
| shake     | Horizontal vibration          | Surprise/anger    |
| float     | Gentle up-down drift          | Dreamy/calm       |
| pop_in    | Scale from 0 to 100%          | Entrances         |
| slide_in  | Slide from off-screen         | Arrivals          |
| tada      | Scale + rotation flourish     | Announcements     |
| heartbeat | Double-pulse rhythm           | Love/affection    |

### Format Limits

| Format | Max Size | Max Duration | Codec   |
| ------ | -------- | ------------ | ------- |
| TGS    | 64 KB    | 3 seconds    | Lottie  |
| WEBM   | 256 KB   | 3 seconds    | VP9     |

## iMessage Fastlane Automation

The `imessage_publisher.py` generates an Xcode project and submits to the App Store via Fastlane:

```bash
# Generate Xcode project + build + upload (dry run)
python3 scripts/imessage_publisher.py \
    --pack-dir packs/boba-milo-5/final \
    --dry-run

# Full submission
python3 scripts/imessage_publisher.py \
    --pack-dir packs/boba-milo-5/final
```

### What It Does

1. **Generate Assets** — Creates iMessage-sized PNGs (618x618), app icons with gradient backgrounds, and App Store screenshots
2. **Create Xcode Project** — Uses `xcodegen` to generate an iMessage sticker pack `.xcodeproj` from a YAML spec
3. **Build & Sign** — Fastlane `match` handles certificates and provisioning profiles, then builds the `.ipa`
4. **Upload** — Fastlane `deliver` uploads the build + metadata + screenshots to App Store Connect

### Fastlane Lanes

| Lane       | Description                                  |
| ---------- | -------------------------------------------- |
| `certs`    | Fetch/create signing certificates via match  |
| `build`    | Build the iMessage extension `.ipa`          |
| `upload`   | Upload build + metadata to App Store Connect |
| `release`  | Full pipeline: certs + build + upload        |

### Prerequisites

- Apple Developer Account ($99/year)
- Fastlane installed (`gem install fastlane`)
- `xcodegen` installed (`brew install xcodegen`)
- Match git repo configured for code signing

## WhatsApp Native Sticker Integration

Export sticker packs for direct installation via a custom Android app with ContentProvider, or serve them via a FastAPI server.

```bash
# Export pack in WhatsApp-native format
python3 scripts/whatsapp_exporter.py \
    --pack-dir packs/boba-milo-5/final

# Export and push to server
python3 scripts/whatsapp_exporter.py \
    --pack-dir packs/boba-milo-5/final \
    --server-url https://your-server.com \
    --api-key your-api-key

# Run the sticker server locally
docker build -t whatsapp-stickers server/
docker run -p 8000:8000 -v ./packs:/app/sticker_packs whatsapp-stickers
```

### Architecture

```
User's Phone                    Your Server
┌─────────────┐                ┌──────────────┐
│ WhatsApp    │ ←── intent ──→ │ Sticker App  │
│             │                │ (ContentProv)│
└─────────────┘                └──────┬───────┘
                                      │ HTTP
                                ┌─────▼──────┐
                                │ FastAPI     │
                                │ Server      │
                                └─────────────┘
```

### ContentProvider URIs

| URI Pattern                                         | Returns             |
| --------------------------------------------------- | ------------------- |
| `content://<authority>/metadata`                     | All pack metadata   |
| `content://<authority>/metadata/<pack_id>`           | Single pack info    |
| `content://<authority>/stickers/<pack_id>`           | Sticker list        |
| `content://<authority>/stickers_asset/<pack>/<file>` | Sticker image bytes |

### Server API Endpoints

| Endpoint                        | Method | Description              |
| ------------------------------- | ------ | ------------------------ |
| `/health`                       | GET    | Health check             |
| `/packs`                        | GET    | List all sticker packs   |
| `/packs/{pack_id}`              | GET    | Get pack metadata        |
| `/packs/{pack_id}/stickers`     | GET    | List stickers in pack    |
| `/stickers/{pack_id}/{file}`    | GET    | Serve sticker image      |
| `/upload`                       | POST   | Upload new sticker pack  |

## Documentation

| Document                                                      | Description                                   |
| ------------------------------------------------------------- | --------------------------------------------- |
| [Project Overview](docs/01-project-overview.md)               | Goals, architecture, cost model               |
| [End-to-End Workflow](docs/02-end-to-end-workflow.md)         | Complete flow from idea to published stickers |
| [ChatGPT Prompts](docs/03-chatgpt-prompt-templates.md)        | Prompt templates for ideation and DALL-E      |
| [DALL-E Guide](docs/04-dalle-generation-guide.md)             | Image generation with ChatGPT Go plan         |
| [Processing Pipeline](docs/05-image-processing-pipeline.md)   | Split, background removal, resize pipeline    |
| [LINE Specifications](docs/06-line-sticker-specifications.md) | LINE image specs and requirements             |
| [LINE Submission](docs/07-line-submission-template.md)        | Step-by-step manual submission guide          |
| [Automation Design](docs/08-browser-automation-design.md)     | Playwright automation architecture            |
| [Repo Structure](docs/09-repo-structure.md)                   | Directory layout explanation                  |
| [Troubleshooting](docs/10-troubleshooting-faq.md)             | Common issues and fixes                       |
| [Migration Guide](docs/11-migration-guide.md)                 | Restructure from flat layout                  |
| [Architecture](docs/architecture.md)                          | System design and module relationships        |
| [Pipeline Guide](docs/pipeline-guide.md)                      | Pipeline CLI options                          |
| [Module Reference](docs/module-reference.md)                  | Detailed API reference                        |
| [Configuration](docs/configuration.md)                        | Character/style/pack config                   |
| [Platform Specs](docs/platform-specs.md)                      | Platform requirements and format specifications |
| [Implementation Plan](docs/implementation-plan-phases.md)     | Multi-platform automation implementation reference |
| [Distribution Guide](docs/guides/distribution_guide.md)       | Multi-platform distribution strategy          |
| [Sticker.ly Guide](docs/guides/stickerly_guide.md)            | WhatsApp upload via Sticker.ly                |

## Requirements

- Python 3.10+
- Playwright + Chromium (for LINE automation)
- OpenAI API key (for DALL-E generation) — or use ChatGPT Go plan ($5/month)
- Telegram Bot Token (optional, for Telegram auto-publishing)
- FFmpeg with VP9 support (optional, for WEBM video sticker conversion)
- Fastlane + xcodegen (optional, for iMessage App Store submission)
- Apple Developer Account (optional, $99/year for iMessage)
- Docker (optional, for WhatsApp sticker server deployment)
- Android SDK + Gradle (optional, for building WhatsApp sticker app)

## Cost Estimate

| Method                | Per Image    | 8-Sticker Pack | Notes                            |
| --------------------- | ------------ | -------------- | -------------------------------- |
| ChatGPT Go plan       | ~$0 marginal | ~$0 marginal   | $5/month, expanded DALL-E access |
| DALL-E API (Standard) | $0.04        | $0.32          | Via OpenAI API directly          |
| DALL-E API (HD)       | $0.08        | $0.64          | Higher quality                   |

## License

Personal use. See distribution packages for licensing details on sticker assets.
