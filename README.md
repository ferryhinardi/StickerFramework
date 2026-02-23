# StickerFramework

An end-to-end sticker pack creation framework — from AI ideation through DALL-E generation, image processing, to automated LINE Creator Market upload. Built for creators who want to design, process, and publish kawaii-style sticker packs across multiple platforms.

## Overview

StickerFramework takes a character definition and sticker list from a config file, generates images using DALL-E (via ChatGPT Go plan), processes them through a multi-stage pipeline (splitting, background removal, color normalization, outline generation, platform-specific resizing), and either manually or automatically uploads to LINE Creator Market via Playwright browser automation.

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

# 5. After session saved, run headless with actual submission
python3 scripts/line_uploader.py \
    --pack-dir packs/boba-milo-5/final \
    --title "Boba & Milo Cheerful Otter Duo 5" \
    --description "A fun, caring otter duo for everyday chat" \
    --submit
```

## Features

- **AI Image Generation** — Generates stickers via DALL-E with structured character-consistent prompts (ChatGPT Go plan, $5/month)
- **Composite Sheet Splitting** — Connected-component analysis to split ChatGPT-generated sticker sheets into individual PNGs
- **Background Removal** — Flood-fill corner-based white background removal (preserves interior whites)
- **Die-Cut Outline** — Automatic white outline generation via alpha dilation
- **Multi-Platform Export** — Resizes and optimizes for LINE, WhatsApp, Telegram, iMessage, and print
- **LINE Automation** — Playwright browser automation for LINE Creator Market uploads (login, fill forms, upload images, submit)
- **Print Sheet Generation** — Creates print-ready layouts (US Letter, A4) for physical stickers
- **Telegram Auto-Publish** — Fully automated sticker set creation via Telegram Bot API
- **iMessage Xcode Project** — Generates a complete Xcode Sticker Pack Application structure
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
| 7. Telegram   | `telegram_publisher.py`    | Publish to Telegram (optional)                   | Live sticker set    |
| 8. iMessage   | `prepare_imessage_pack.py` | Generate Xcode project (optional)                | `xcode/`            |

## Supported Platforms

| Platform               | Format | Size      | Max File Size |
| ---------------------- | ------ | --------- | ------------- |
| LINE (stickers)        | PNG    | 370x320   | 1 MB          |
| LINE (main)            | PNG    | 240x240   | 1 MB          |
| LINE (tab)             | PNG    | 96x74     | 1 MB          |
| WhatsApp (Sticker.ly)  | WEBP   | 512x512   | 100 KB        |
| Telegram               | WEBP   | 512x512   | 256 KB        |
| iMessage               | PNG    | 618x618   | 500 KB        |
| Etsy / Gumroad (Print) | PNG    | 2048x2048 | Unlimited     |

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
│   ├── prepare_imessage_pack.py     #   Xcode project generator
│   ├── telegram_publisher.py        #   Telegram Bot API publisher
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
├── templates/                       # Submission defaults
│   └── line_submission_defaults.json
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
├── sticker_pack.png          # Source composite sheet
├── split/                    # Individual stickers from sheet
│   ├── 01_emotion.png
│   └── ...
└── final/                    # Platform-ready outputs
    ├── line/                 # 370x320 PNG
    ├── line_main/            # 240x240 PNG (cover)
    ├── line_tab/             # 96x74 PNG (chat icon)
    ├── whatsapp/             # 512x512 WEBP
    ├── telegram/             # 512x512 WEBP
    ├── imessage_large/       # 618x618 PNG
    └── print_etsy/           # 2048x2048 PNG
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
| [Platform Specs](docs/platform-specs.md)                      | Platform requirements                         |
| [Distribution Guide](docs/guides/distribution_guide.md)       | Multi-platform distribution strategy          |
| [Sticker.ly Guide](docs/guides/stickerly_guide.md)            | WhatsApp upload via Sticker.ly                |

## Requirements

- Python 3.10+
- Playwright + Chromium (for LINE automation)
- OpenAI API key (for DALL-E generation) — or use ChatGPT Go plan ($5/month)
- Telegram Bot Token (optional, for Telegram auto-publishing)
- Docker not required

## Cost Estimate

| Method                | Per Image    | 8-Sticker Pack | Notes                            |
| --------------------- | ------------ | -------------- | -------------------------------- |
| ChatGPT Go plan       | ~$0 marginal | ~$0 marginal   | $5/month, expanded DALL-E access |
| DALL-E API (Standard) | $0.04        | $0.32          | Via OpenAI API directly          |
| DALL-E API (HD)       | $0.08        | $0.64          | Higher quality                   |

## License

Personal use. See distribution packages for licensing details on sticker assets.
