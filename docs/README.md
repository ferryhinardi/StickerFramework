# StickerFramework

An end-to-end sticker pack creation framework that automates the entire workflow from AI image generation through multi-platform distribution. Built for creators who want to design, process, and publish kawaii-style sticker packs across six major platforms.

## Overview

StickerFramework takes a character definition and sticker list from a single config file, generates images using DALL-E 3, processes them through a multi-stage pipeline (background removal, color normalization, outline generation, platform-specific resizing), and packages the results for distribution across WhatsApp, Telegram, LINE, iMessage, Etsy, and Gumroad.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/ferryhinardi/StickerFramework.git
cd StickerFramework

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# 4. Run the full pipeline
python run_pipeline.py

# 5. Or process existing images (skip generation)
python run_pipeline.py --process-only --input ./stickers --skip-bg
```

## Features

- **AI Image Generation** - Generates stickers via DALL-E 3 with structured character-consistent prompts
- **Sticker Sheet Splitting** - Splits multi-sticker sheet images into individual PNGs with configurable pack profiles
- **Background Removal** - AI-powered bg removal using rembg (U2-Net model)
- **Die-Cut Outline** - Automatic white outline generation for sticker aesthetics
- **Multi-Platform Export** - Automatically resizes and optimizes for 7 platform targets (WhatsApp, Telegram, iMessage, LINE stickers + LINE main + LINE tab, Etsy/print)
- **Print Sheet Generation** - Creates print-ready layouts (US Letter, A4) for physical stickers
- **Telegram Auto-Publish** - Fully automated sticker set creation via Telegram Bot API
- **iMessage Xcode Project** - Generates a complete Xcode Sticker Pack Application structure
- **Distribution Packaging** - Creates ZIP bundles with README and license for digital sales

## Pipeline Stages

| Stage | Description | Output |
|-------|-------------|--------|
| 1. Generate | Create images via DALL-E 3 | `raw/` directory |
| 2. Process | Bg removal, outline, resize per platform | `final/` subdirectories |
| 3. Tray Icons | Create 96x96 pack icons | Tray icon files |
| 4. Metadata | Generate platform JSON metadata | `metadata/` directory |
| 5. Package | Print sheets, social previews, ZIP | `dist/` directory |
| 6. Telegram | Publish to Telegram (optional) | Live sticker set |
| 7. iMessage | Generate Xcode project (optional) | `xcode/` directory |

## Supported Platforms

| Platform | Format | Size | Max File Size |
|----------|--------|------|---------------|
| WhatsApp (Sticker.ly) | WEBP | 512x512 | 100 KB |
| Telegram | WEBP | 512x512 | 256 KB |
| iMessage | PNG | 618x618 | 500 KB |
| LINE (stickers) | PNG | 370x320 | 1000 KB |
| LINE (main image) | PNG | 240x240 | 1000 KB |
| LINE (tab icon) | PNG | 96x74 | 1000 KB |
| Etsy / Gumroad (Print) | PNG | 2048x2048 | Unlimited |

## Project Structure

```
StickerFramework/
├── run_pipeline.py              # Master orchestrator
├── image_generator.py           # DALL-E 3 generation
├── sticker_processor.py         # Image processing pipeline
├── pack_config.py               # Character & sticker definitions
├── split_stickers.py            # Sheet splitter utility
├── create_print_sheet.py        # Print sheet & ZIP generator
├── prepare_imessage_pack.py     # Xcode project generator
├── telegram_publisher.py        # Telegram Bot API publisher
├── requirements.txt             # Python dependencies
├── brand_kit.md                 # Visual identity guidelines
├── docs/                        # Detailed documentation
│   ├── README.md                # This file
│   ├── architecture.md          # System architecture
│   ├── pipeline-guide.md        # Pipeline usage guide
│   ├── module-reference.md      # Module & API reference
│   ├── configuration.md         # Configuration guide
│   └── platform-specs.md        # Platform specifications
├── guides/                      # Distribution & upload guides
│   ├── distribution_guide.md
│   └── stickerly_guide.md
├── stickers/                    # Sample sticker assets
├── chubby mochi cat/            # Mochi cat sticker pack
├── chubby mochi hamster/        # Mochi hamster pack (vol 1)
├── chubby mochi hamster 2/      # Mochi hamster pack (vol 2)
├── Jesus Christ – Faith & Peace/ # Jesus Christ sticker pack
├── Jesus Christ 1/              # Jesus Christ pack (alt version)
├── Jesus Christ 2/              # Jesus Christ pack vol 2
├── Little Angel – Daily Blessings/ # Little Angel sticker pack
├── Corporate Sloth – Tired but Trying/ # Corporate Sloth pack
├── Office Teddy Bear/           # Office Teddy Bear pack
└── output/                      # Pipeline output (gitignored)
```

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, data flow, and module relationships |
| [Pipeline Guide](docs/pipeline-guide.md) | How to run the pipeline with all CLI options |
| [Module Reference](docs/module-reference.md) | Detailed API reference for every module |
| [Configuration](docs/configuration.md) | How to define characters, styles, and sticker packs |
| [Platform Specs](docs/platform-specs.md) | Platform requirements and distribution details |
| [Distribution Guide](guides/distribution_guide.md) | Multi-platform distribution strategy |
| [Sticker.ly Guide](guides/stickerly_guide.md) | Step-by-step Sticker.ly upload instructions |

## Requirements

- Python 3.10+
- OpenAI API key (for DALL-E 3 generation)
- Telegram Bot Token (optional, for auto-publishing)

## Cost Estimate

| Quality | Per Image | 24-Sticker Pack | With ~40% Redo Rate |
|---------|-----------|-----------------|----------------------|
| Standard | $0.04 | $0.96 | ~$1.35 |
| HD | $0.08 | $1.92 | ~$2.70 |

## License

Personal use. See distribution packages for licensing details on sticker assets.
