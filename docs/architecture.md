# Architecture

## System Overview

StickerFramework is a modular, pipeline-based system where each stage transforms data and passes results to the next. The pipeline is orchestrated by `run_pipeline.py`, with each major function delegated to a dedicated module.

## Architecture Diagram

```
                        ┌──────────────────┐
                        │   pack_config.py │
                        │                  │
                        │  CHARACTER def   │
                        │  STYLE rules     │
                        │  24 STICKERS     │
                        │  PACK metadata   │
                        └────────┬─────────┘
                                 │
                                 ▼
┌────────────────────────────────────────────────────────────────┐
│                    run_pipeline.py                              │
│                    (Master Orchestrator)                        │
│                                                                │
│  ┌──────────┐   ┌──────────────────┐   ┌───────────────────┐  │
│  │ Stage 1  │   │     Stage 2      │   │     Stage 3       │  │
│  │ Generate │──►│    Process       │──►│   Tray Icons      │  │
│  │          │   │                  │   │                   │  │
│  │ DALL-E 3 │   │ bg removal      │   │ 96x96 icons from  │  │
│  │ API call │   │ color normalize  │   │ first sticker     │  │
│  │          │   │ white outline    │   │                   │  │
│  │ ──► raw/ │   │ multi-platform   │   └───────┬───────────┘  │
│  └──────────┘   │ resize & save    │           │              │
│                 │                  │           ▼              │
│                 │ ──► final/       │   ┌───────────────────┐  │
│                 │   whatsapp/      │   │     Stage 4       │  │
│                 │   telegram/      │   │    Metadata       │  │
│                 │   imessage_large/│   │                   │  │
│                 │   line/          │   │ WhatsApp JSON     │  │
│                 │   print_etsy/    │   │ Telegram JSON     │  │
│                 └──────────────────┘   │ LINE JSON         │  │
│                                        │ Pack summary      │  │
│                                        │                   │  │
│                                        │ ──► metadata/     │  │
│                                        └───────┬───────────┘  │
│                                                │              │
│                                                ▼              │
│  ┌──────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │     Stage 7      │  │    Stage 6     │  │   Stage 5    │  │
│  │    iMessage      │  │   Telegram     │  │   Package    │  │
│  │   (optional)     │  │  (optional)    │  │              │  │
│  │                  │  │                │  │ Print sheets │  │
│  │ Xcode project   │  │ Bot API calls  │  │ Social prev  │  │
│  │ .xcodeproj      │  │ Create set     │  │ Dist ZIP     │  │
│  │ .stickerpack    │  │ Add stickers   │  │              │  │
│  │ Info.plist      │  │                │  │ ──► dist/    │  │
│  │                  │  │                │  │              │  │
│  │ ──► xcode/      │  │ ──► Telegram   │  └──────────────┘  │
│  └──────────────────┘  └────────────────┘                    │
└────────────────────────────────────────────────────────────────┘

Standalone Utility:
┌──────────────────────────────────┐
│ split_stickers.py                │
│                                  │
│ STICKER_PACK env var ──►         │
│ Pack registry (PACKS dict)       │
│ Sheet image ──►                  │
│ Individual PNGs (512x512, no bg) │
│                                  │
│ Then pipe to sticker_processor:  │
│ split/ ──► final/ (7 platforms)  │
└──────────────────────────────────┘
```

## Module Dependency Graph

```
run_pipeline.py
├── image_generator.py      (uses: openai, requests)
├── sticker_processor.py    (uses: Pillow, rembg, onnxruntime)
├── create_print_sheet.py   (uses: Pillow)
├── prepare_imessage_pack.py(uses: Pillow, json, shutil)
├── telegram_publisher.py   (uses: requests)
└── pack_config.py          (pure Python dict definitions)

split_stickers.py           (standalone: Pillow, numpy, scipy)
```

## Data Flow

### Input
The system starts with a `pack_config.py` containing:
1. **CHARACTER** - Species, colors, proportions, accessories
2. **STYLE** - Art direction rules (outline weight, color mode, background)
3. **STICKERS** - List of 24 emotion definitions with pose and prop descriptions
4. **PACK_CONFIG** - Pack metadata (ID, name, publisher, target platforms)

### Processing Pipeline

```
pack_config.py ──► image_generator.py ──► raw PNG files (1024x1024)
                                              │
                                              ▼
                                     sticker_processor.py
                                              │
                            ┌─────────────────┼─────────────────────┐
                            │                 │                     │
                            ▼                 ▼                     ▼
                     remove_background  normalize_colors    add_white_outline
                     (rembg / U2-Net)   (sat/bright/contrast) (alpha dilation)
                            │                 │                     │
                            └─────────────────┼─────────────────────┘
                                              │
                                              ▼
                                     resize_to_spec() per platform
                                              │
                     ┌─────────┬───────────┬───┴────┬──────────┬──────────┬─────────┐
                     ▼         ▼           ▼        ▼          ▼          ▼         ▼
                whatsapp/  telegram/  imessage/   line/    line_main/ line_tab/ print_etsy/
                512x512    512x512    618x618   370x320   240x240    96x74    2048x2048
                WEBP       WEBP       PNG       PNG       PNG        PNG      PNG
                <100KB     <256KB     <500KB    <1000KB   <1000KB    <1000KB  unlimited
```

### Output Directory Structure

Each pipeline run creates a self-contained output directory:

```
output/<pack_id>/
├── raw/                    # Stage 1 output
│   ├── 01_happy.png
│   ├── 01_happy_prompt.txt # Original + revised prompts
│   ├── 02_love.png
│   └── ...
├── final/                  # Stage 2 output
│   ├── whatsapp/
│   │   ├── 01_happy.webp
│   │   └── ...
│   ├── telegram/
│   │   ├── 01_happy.webp
│   │   └── ...
│   ├── imessage_large/
│   │   ├── 01_happy.png
│   │   └── ...
│   ├── line/
│   │   ├── 01_happy.png
│   │   └── ...
│   └── print_etsy/
│       ├── 01_happy.png
│       └── ...
├── metadata/               # Stage 4 output
│   ├── whatsapp_pack.json
│   ├── telegram_pack.json
│   ├── line_pack.json
│   └── pack_summary.json
├── dist/                   # Stage 5 output
│   ├── sticker_sheet_letter.png
│   ├── sticker_sheet_a4.png
│   ├── social_preview.png
│   └── <pack_id>_distribution.zip
└── xcode/                  # Stage 7 output (optional)
    └── <PackName>/
        ├── <PackName>.xcodeproj/
        ├── Stickers.xcstickers/
        └── Info.plist
```

## Key Design Decisions

### 1. Config-Driven Generation
All character and sticker definitions live in `pack_config.py`. This makes it trivial to create new packs by duplicating and modifying the config while reusing the entire pipeline.

### 2. Modular Pipeline Stages
Each stage is independently runnable. You can:
- Skip generation to process existing images (`--process-only`)
- Skip processing to only generate (`--generate-only`)
- Skip background removal for pre-transparent images (`--skip-bg`)
- Selectively enable Telegram or iMessage stages

### 3. Platform-Aware Processing
The `sticker_processor.py` uses a spec-driven approach. Each platform has defined dimensions, format, and file size limits. The processor handles format-specific optimization (e.g., binary search for WebP quality to fit size constraints).

### 4. Copyright Strengthening
The white outline (alpha dilation) and color normalization steps are documented as "meaningful post-processing" that strengthens copyright claims on AI-generated artwork, since the transformative processing adds creative choices made by the human operator.

### 5. Cost Optimization
DALL-E 3 costs are managed through:
- Standard vs HD quality selection (`--standard` flag)
- Rate limit handling with configurable delays
- Prompt + revised prompt logging for debugging without regenerating

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | For generation | OpenAI API key for DALL-E 3 |
| `TELEGRAM_BOT_TOKEN` | For Telegram publish | Bot token from @BotFather |
| `TELEGRAM_USER_ID` | For Telegram publish | Your Telegram user ID |
| `STICKER_PACK` | For split_stickers | Name of pack to split (default: `Jesus Christ – Faith & Peace`) |

## Error Handling Strategy

- **Rate Limiting**: Configurable delays between API calls (default 12s for DALL-E 3)
- **Retry Logic**: Up to 3 retries for generation failures with exponential backoff
- **Content Policy**: Catches and logs DALL-E content policy rejections gracefully
- **File Size Optimization**: Binary search on WebP quality to meet platform size limits
- **Graceful Degradation**: Individual sticker failures don't halt the batch
