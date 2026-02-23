# Project Overview

> LINE Sticker Automation — From idea to published sticker pack in minutes.

## What Is This?

An end-to-end automation pipeline for creating and publishing LINE sticker packs. Starting from a single ChatGPT conversation, this project takes you through AI-generated sticker art, automated image processing, and hands-free upload to the LINE Creators Market.

The typical manual workflow (ideation, generation, image editing, resizing, form-filling, uploading) takes ~45 minutes per pack. This pipeline reduces human input to ~5 minutes — the rest is automated.

## The Problem

The LINE Creators Market has no public API for sticker submission. Each pack requires:

- 8 sticker images resized to 370x320 with transparent backgrounds
- 1 main image at exactly 240x240
- 1 chat tab icon at exactly 96x74
- Filling ~15 form fields across 4 tabs (Display Information, Sticker Images, Tag Settings, Price Tier)
- Uploading each image individually through a web UI

At volume (5+ packs per week), this becomes a significant time sink with high error potential.

## The Solution

| Stage         | Tool                            | Automation Level               |
| ------------- | ------------------------------- | ------------------------------ |
| 1. Ideation   | ChatGPT Go (GPT-5.2 Instant)    | Semi-auto (copy-paste prompts) |
| 2. Generation | DALL-E via ChatGPT Go           | Semi-auto (single prompt)      |
| 3. Splitting  | `split_stickers.py`             | Fully automated                |
| 4. Processing | `sticker_processor.py`          | Fully automated                |
| 5. Upload     | Playwright (`line_uploader.py`) | Fully automated                |
| 6. Review     | LINE Creators Market            | Manual (1-7 days)              |

## Tech Stack

- **Python 3.10+** — Pipeline language
- **Pillow** — Image manipulation (resize, outline, color normalize)
- **NumPy + SciPy** — Connected-component analysis for sticker splitting
- **Playwright** — Browser automation for LINE Creator Market
- **ChatGPT Go plan** (GPT-5.2 Instant + DALL-E) — AI sticker ideation & generation ($5/month)
- **rembg** — AI-powered background removal (U2-Net model)

## Key Features

- Reusable ChatGPT prompt templates for consistent sticker pack ideation
- Composite sheet splitting via connected-component analysis (no manual cropping)
- Multi-platform image processing (LINE, WhatsApp, Telegram, iMessage, Etsy)
- LINE-spec validation (dimensions, format, file size, transparency)
- Browser automation for the complete LINE submission flow (create, fill, upload, submit)
- Batch support for processing and uploading multiple packs
- Session persistence for LINE login (no re-auth on every run)
- Dry-run mode for testing without actual submission

## Documentation Index

| #   | Document                                                         | Description                                        |
| --- | ---------------------------------------------------------------- | -------------------------------------------------- |
| 01  | [Project Overview](01-project-overview.md)                       | This document                                      |
| 02  | [End-to-End Workflow](02-end-to-end-workflow.md)                 | Step-by-step from idea to published pack           |
| 03  | [ChatGPT Prompt Templates](03-chatgpt-prompt-templates.md)       | Copy-paste prompts for ideation and generation     |
| 04  | [DALL-E Generation Guide](04-dalle-generation-guide.md)          | Getting good composite sheets from DALL-E          |
| 05  | [Image Processing Pipeline](05-image-processing-pipeline.md)     | split_stickers.py + sticker_processor.py reference |
| 06  | [LINE Sticker Specifications](06-line-sticker-specifications.md) | Official LINE image and metadata requirements      |
| 07  | [LINE Submission Template](07-line-submission-template.md)       | Default form values for every submission           |
| 08  | [Browser Automation Design](08-browser-automation-design.md)     | Playwright architecture and module design          |
| 09  | [Repository Structure](09-repo-structure.md)                     | Directory layout and conventions                   |
| 10  | [Troubleshooting & FAQ](10-troubleshooting-faq.md)               | Common issues and solutions                        |

## Quick Start

```bash
# 1. Clone and set up
git clone <repo-url>
cd StickerFramework
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 2. Generate stickers via ChatGPT (see docs 03 + 04)
# Save composite sheet as: packs/<pack-name>/sticker_pack.png

# 3. Split composite into individual stickers
STICKER_PACK="pack-name" python split_stickers.py

# 4. Process for LINE specs
python sticker_processor.py packs/<pack-name>/split packs/<pack-name>/final \
    line line_main line_tab --skip-bg

# 5. Upload to LINE Creator Market
python line_uploader.py \
    --pack-dir packs/<pack-name>/final \
    --title "Pack Title" \
    --description "Pack description" \
    --headful
```

See [End-to-End Workflow](02-end-to-end-workflow.md) for the complete guide.
