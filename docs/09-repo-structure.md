# Repository Structure

> Target directory layout for the StickerFramework repository after reorganization.

## Directory Layout

```
StickerFramework/
│
├── scripts/                          # All pipeline scripts
│   ├── run_pipeline.py               # Master orchestrator (7 stages)
│   ├── image_generator.py            # DALL-E 3 image generation
│   ├── sticker_processor.py          # Image processing (bg removal, outline, resize)
│   ├── split_stickers.py             # Composite sheet → individual stickers
│   ├── pack_config.py                # Character/style/pack configuration
│   ├── create_print_sheet.py         # Print-ready layouts and ZIP packages
│   ├── prepare_imessage_pack.py      # iMessage Xcode Sticker Pack generator
│   ├── telegram_publisher.py         # Telegram bot auto-publish
│   ├── line_uploader.py              # NEW: Playwright LINE upload orchestrator
│   └── batch_submit.py              # NEW: Batch process + upload N packs
│
├── automation/                       # NEW: Playwright LINE Creator Market modules
│   ├── __init__.py
│   ├── config.py                     # URLs, selectors, timeouts, defaults
│   ├── line_auth.py                  # Login + session persistence
│   ├── line_create_submission.py     # Create new sticker submission
│   ├── line_upload_images.py         # Upload main + tab + sticker images
│   ├── line_set_metadata.py          # Fill Display Information + Tag Settings
│   ├── line_set_price.py             # Price Tier tab automation
│   └── line_submit.py               # Final review + request submission
│
├── templates/                        # NEW: Reusable templates and defaults
│   ├── chatgpt_ideation_prompt.md    # Copy-paste prompt for ChatGPT ideation
│   ├── chatgpt_dalle_prompt.md       # Copy-paste prompt for DALL-E generation
│   └── line_submission_defaults.json # Default LINE form values (JSON)
│
├── packs/                            # All sticker packs (images mostly gitignored)
│   ├── boba-milo-1/                  # Kebab-case, numbered for series
│   ├── boba-milo-2/
│   ├── boba-milo-3/
│   ├── boba-milo-4/
│   ├── boba-milo-5/
│   ├── chubby-mochi-cat/
│   ├── chubby-mochi-hamster/
│   ├── chubby-mochi-hamster-2/
│   ├── corporate-sloth/
│   ├── jesus-faith-and-peace/
│   ├── jesus-christ-1/
│   ├── jesus-christ-2/
│   ├── little-angel/
│   ├── office-teddy-bear/
│   └── example-pack/                 # Small example committed for reference
│
├── docs/                             # Documentation (10 new + existing)
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
│   ├── architecture.md               # Existing: system design
│   ├── module-reference.md            # Existing: API docs for all modules
│   ├── platform-specs.md             # Existing: multi-platform specs
│   └── configuration.md              # Existing: config reference
│
├── reference/                        # Non-pipeline assets
│   ├── line-creator/                 # LINE Creator Market screenshots, tax docs
│   └── brand_kit.md                  # Visual identity guidelines
│
├── README.md                         # Project overview + quick start
├── requirements.txt                  # Python dependencies (+ playwright)
├── .env.example                      # Environment variable template
└── .gitignore                        # Updated with pack image ignores
```

## Pack Directory Structure

Every sticker pack follows a consistent internal layout:

```
packs/<pack-name>/
├── sticker_pack.png              # Original composite sheet from DALL-E
├── pack_config.json              # Pack metadata (title, description, sticker names)
├── split/                        # Output of split_stickers.py
│   ├── 01_emotion_name.png       # 512x512, transparent background
│   ├── 02_emotion_name.png
│   └── ...
└── final/                        # Output of sticker_processor.py
    ├── line/                     # Sticker images (370x320)
    │   ├── 01_emotion_name.png
    │   └── ...
    ├── line_main/                # Main image (240x240)
    │   └── 01_emotion_name.png   # First sticker used as pack cover
    ├── line_tab/                 # Chat tab icon (96x74)
    │   └── 01_emotion_name.png   # First sticker used as tray icon
    ├── whatsapp/                 # WhatsApp stickers (512x512 WebP)
    ├── telegram/                 # Telegram stickers (512x512 WebP)
    ├── imessage_large/           # iMessage stickers (618x618 PNG)
    └── print_etsy/               # Etsy print-ready (high-res PNG)
```

### Migration from Old Layout

Some older packs use `line_output/` instead of `final/`:

```
# Old layout (to be normalized)
pack-name/
├── sticker_pack.png
├── split/
└── line_output/          # → rename to final/
    ├── main.png          # → move to final/line_main/
    ├── tab.png           # → move to final/line_tab/
    └── line/             # → move to final/line/
```

## Naming Conventions

### Pack Directories

- **Kebab-case**: `boba-milo-1`, `corporate-sloth`, `little-angel`
- **Series numbering**: Append `-N` for sequels: `boba-milo-1`, `boba-milo-2`, etc.
- **No special characters**: No em-dashes, spaces, or unicode

### Sticker Files

- **Zero-padded number prefix**: `01_`, `02_`, ... `16_`
- **Emotion/action suffix**: `01_hello.png`, `02_love.png`, `08_goodbye.png`
- **Underscores** between words: `03_good_morning.png`
- **Lowercase only**: No uppercase in filenames

## What Gets Committed vs Gitignored

### Committed

- `scripts/` — All Python scripts
- `automation/` — All Playwright modules
- `templates/` — Prompt templates and defaults JSON
- `docs/` — All documentation
- `reference/` — Screenshots and brand kit
- `packs/example-pack/` — One small example pack for reference
- `README.md`, `requirements.txt`, `.env.example`, `.gitignore`

### Gitignored

- `packs/*/sticker_pack.png` — Large composite sheets (2-5 MB each)
- `packs/*/split/` — Intermediate split images
- `packs/*/final/` — Processed output images
- `automation/screenshots/` — Failure screenshots
- `automation/.storage_state.json` — Playwright session cookies
- `.env` — Environment variables with credentials
- `__pycache__/`, `.ruff_cache/`, `*.pyc`
- `.DS_Store`

## Environment Variables

| Variable             | Required       | Description                                    |
| -------------------- | -------------- | ---------------------------------------------- |
| `OPENAI_API_KEY`     | For generation | OpenAI API key (DALL-E 3 via API, not ChatGPT) |
| `LINE_EMAIL`         | Optional       | LINE account email (for auto-login)            |
| `LINE_PASSWORD`      | Optional       | LINE account password                          |
| `TELEGRAM_BOT_TOKEN` | For Telegram   | Telegram bot token (from @BotFather)           |
| `STICKER_PACK`       | For split      | Default pack name for `split_stickers.py`      |

`.env.example`:

```bash
# OpenAI (for DALL-E API generation, optional if using ChatGPT UI)
OPENAI_API_KEY=sk-...

# LINE Creator Market (for Playwright automation)
LINE_EMAIL=your-email@example.com
LINE_PASSWORD=your-password

# Telegram (for auto-publish)
TELEGRAM_BOT_TOKEN=123456:ABC-DEF

# Default sticker pack name
STICKER_PACK=boba-milo-5
```

## Setup Instructions

```bash
# Clone the repository
git clone <repo-url>
cd StickerFramework

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser (for LINE upload automation)
playwright install chromium

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Verify installation
python -c "from PIL import Image; print('Pillow OK')"
python -c "import numpy; print('NumPy OK')"
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Requirements

- **Python**: 3.10 or later
- **OS**: macOS, Linux, or Windows
- **Disk space**: ~1 GB for repo + processed images
- **Internet**: Required for ChatGPT/DALL-E generation and LINE upload
- **Docker**: Not required
