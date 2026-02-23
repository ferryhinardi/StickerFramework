# Migration Guide: StickerFramework Reorganization

> Documents the complete directory restructuring from the original flat layout to the organized target structure. Includes all script import fixes, automation module additions, and pack normalization.

## Migration Date

February 2026

---

## Why Reorganize?

The original StickerFramework repo grew organically — 8 Python scripts, 14 sticker packs, misc assets, and documentation all lived at the root level. This made the repo hard to navigate and understand at a glance.

The new structure separates concerns into clear directories:

- `scripts/` — Pipeline code (generation, processing, splitting, publishing)
- `packs/` — Sticker pack data (kebab-case naming, standardized `final/` layout)
- `automation/` — Playwright browser automation for LINE Creator Market uploads
- `templates/` — Reusable submission defaults
- `docs/` — All documentation
- `reference/` — Non-pipeline assets (screenshots, tax docs, brand kit)

---

## Before (Original Structure)

```
StickerFramework/                          # Everything at root level
├── run_pipeline.py                        # ─┐
├── image_generator.py                     #  │
├── sticker_processor.py                   #  │ 8 Python scripts
├── split_stickers.py                      #  │ mixed with everything
├── pack_config.py                         #  │
├── create_print_sheet.py                  #  │
├── prepare_imessage_pack.py               #  │
├── telegram_publisher.py                  # ─┘
│
├── Boba & Milo – Cheerful Otter Duo/     # ─┐
├── Boba & Milo – Cheerful Otter Duo 2/   #  │
├── Boba & Milo – Cheerful Otter Duo 3/   #  │
├── Boba & Milo – Cheerful Otter Duo 4/   #  │
├── Boba & Milo – Cheerful Otter Duo 5/   #  │ 14 sticker packs
├── chubby mochi cat/                      #  │ with spaces, em-dashes,
├── chubby mochi hamster/                  #  │ mixed naming conventions,
├── chubby mochi hamster 2/                #  │ inconsistent internal layout
├── Corporate Sloth – Tired but Trying/    #  │ (some use line_output/,
├── Jesus Christ – Faith & Peace/          #  │  some use final/)
├── Jesus Christ 1/                        #  │
├── Jesus Christ 2/                        #  │
├── Little Angel – Daily Blessings/        #  │
├── Office Teddy Bear/                     # ─┘
│
├── cartoon faces/                         # ─┐ Misc raw assets
├── stickers/                              #  │ not part of any pack
├── stickers_gen/                          # ─┘
│
├── line creator/                          # Screenshots, tax docs
├── brand_kit.md                           # Visual identity doc
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/                                  # Technical docs
│   ├── README.md
│   ├── architecture.md
│   ├── configuration.md
│   ├── module-reference.md
│   ├── pipeline-guide.md
│   └── platform-specs.md
│
├── guides/                                # Distribution guides
│   ├── distribution_guide.md
│   └── stickerly_guide.md
│
├── __pycache__/
└── .ruff_cache/
```

---

## After (Current Structure)

```
StickerFramework/
├── scripts/                               # All pipeline + CLI scripts
│   ├── run_pipeline.py                    #   Master orchestrator
│   ├── image_generator.py                 #   DALL-E generation
│   ├── sticker_processor.py               #   Image processing pipeline
│   ├── split_stickers.py                  #   Composite sheet splitter
│   ├── pack_config.py                     #   Character/style/sticker config
│   ├── create_print_sheet.py              #   Print sheet & ZIP generator
│   ├── prepare_imessage_pack.py           #   Xcode project generator
│   ├── telegram_publisher.py              #   Telegram Bot API publisher
│   └── line_uploader.py                   #   LINE Creator Market CLI (NEW)
│
├── packs/                                 # All sticker packs (kebab-case)
│   ├── boba-milo-1/                       #   Each pack contains:
│   ├── boba-milo-2/                       #     sticker_pack.png  (source sheet)
│   ├── boba-milo-3/                       #     split/            (individual PNGs)
│   ├── boba-milo-4/                       #     final/            (platform outputs)
│   ├── boba-milo-5/                       #       ├── line/       (370x320 PNG)
│   ├── chubby-mochi-cat/                  #       ├── line_main/  (240x240 PNG)
│   ├── chubby-mochi-hamster/              #       ├── line_tab/   (96x74 PNG)
│   ├── chubby-mochi-hamster-2/            #       ├── whatsapp/   (512x512 WEBP)
│   ├── corporate-sloth/                   #       ├── telegram/   (512x512 WEBP)
│   ├── jesus-faith-and-peace/             #       ├── imessage_large/ (618x618 PNG)
│   ├── jesus-christ-1/                    #       └── print_etsy/ (2048x2048 PNG)
│   ├── jesus-christ-2/
│   ├── little-angel/
│   └── office-teddy-bear/
│
├── automation/                            # Playwright browser automation
│   ├── __init__.py                        #   Package exports
│   ├── config.py                          #   URLs, timeouts, defaults
│   ├── utils.py                           #   safe_click, retry, screenshots
│   ├── line_auth.py                       #   Login + session persistence
│   ├── line_create_submission.py          #   Create draft submission
│   ├── line_upload_images.py              #   Upload main/tab/sticker images
│   ├── line_set_metadata.py               #   Display Info + Tag Settings
│   ├── line_set_price.py                  #   Price tier selection
│   └── line_submit.py                     #   Final review + submit
│
├── templates/                             # Reusable templates & defaults
│   └── line_submission_defaults.json      #   LINE submission config
│
├── docs/                                  # All documentation
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
│   ├── 11-migration-guide.md             # This file
│   ├── LINE_STICKER_PACK.md              # Original LINE spec reference
│   ├── README.md
│   ├── architecture.md
│   ├── configuration.md
│   ├── module-reference.md
│   ├── pipeline-guide.md
│   ├── platform-specs.md
│   └── guides/
│       ├── distribution_guide.md
│       └── stickerly_guide.md
│
├── reference/                             # Non-pipeline assets
│   ├── line-creator/                      #   Screenshots, tax PDFs
│   ├── brand_kit.md                       #   Visual identity
│   ├── cartoon-faces/                     #   Raw ChatGPT images
│   ├── stickers/                          #   Older raw stickers
│   └── stickers-gen/                      #   Raw generated images
│
├── README.md                              # Project overview
├── requirements.txt                       # Python deps (incl. playwright)
├── .env.example                           # Environment variable template
└── .gitignore                             # Updated for new paths
```

---

## Complete Move Map

### Scripts (root → scripts/)

| Old Path                   | New Path                           |
| -------------------------- | ---------------------------------- |
| `run_pipeline.py`          | `scripts/run_pipeline.py`          |
| `image_generator.py`       | `scripts/image_generator.py`       |
| `sticker_processor.py`     | `scripts/sticker_processor.py`     |
| `split_stickers.py`        | `scripts/split_stickers.py`        |
| `pack_config.py`           | `scripts/pack_config.py`           |
| `create_print_sheet.py`    | `scripts/create_print_sheet.py`    |
| `prepare_imessage_pack.py` | `scripts/prepare_imessage_pack.py` |
| `telegram_publisher.py`    | `scripts/telegram_publisher.py`    |
| _(new)_                    | `scripts/line_uploader.py`         |

### Sticker Packs (root → packs/, with rename)

| Old Name                              | New Name                        |
| ------------------------------------- | ------------------------------- |
| `Boba & Milo – Cheerful Otter Duo/`   | `packs/boba-milo-1/`            |
| `Boba & Milo – Cheerful Otter Duo 2/` | `packs/boba-milo-2/`            |
| `Boba & Milo – Cheerful Otter Duo 3/` | `packs/boba-milo-3/`            |
| `Boba & Milo – Cheerful Otter Duo 4/` | `packs/boba-milo-4/`            |
| `Boba & Milo – Cheerful Otter Duo 5/` | `packs/boba-milo-5/`            |
| `chubby mochi cat/`                   | `packs/chubby-mochi-cat/`       |
| `chubby mochi hamster/`               | `packs/chubby-mochi-hamster/`   |
| `chubby mochi hamster 2/`             | `packs/chubby-mochi-hamster-2/` |
| `Corporate Sloth – Tired but Trying/` | `packs/corporate-sloth/`        |
| `Jesus Christ – Faith & Peace/`       | `packs/jesus-faith-and-peace/`  |
| `Jesus Christ 1/`                     | `packs/jesus-christ-1/`         |
| `Jesus Christ 2/`                     | `packs/jesus-christ-2/`         |
| `Little Angel – Daily Blessings/`     | `packs/little-angel/`           |
| `Office Teddy Bear/`                  | `packs/office-teddy-bear/`      |

### Misc Assets (root → reference/)

| Old Path         | New Path                   |
| ---------------- | -------------------------- |
| `line creator/`  | `reference/line-creator/`  |
| `brand_kit.md`   | `reference/brand_kit.md`   |
| `cartoon faces/` | `reference/cartoon-faces/` |
| `stickers/`      | `reference/stickers/`      |
| `stickers_gen/`  | `reference/stickers-gen/`  |

### Guides (root → docs/guides/)

| Old Path                       | New Path                            |
| ------------------------------ | ----------------------------------- |
| `guides/distribution_guide.md` | `docs/guides/distribution_guide.md` |
| `guides/stickerly_guide.md`    | `docs/guides/stickerly_guide.md`    |

---

## Naming Convention Changes

### Pack Directories

| Convention         | Old                            | New                              |
| ------------------ | ------------------------------ | -------------------------------- |
| Case               | Mixed (PascalCase, lowercase)  | All lowercase                    |
| Word separator     | Spaces, em-dashes (–)          | Hyphens (-)                      |
| Series numbering   | Suffix (" 2", " 3") or in name | Always `-N` suffix               |
| Special characters | Em-dashes, ampersands          | None                             |
| Subtitles          | Full subtitle in name          | Removed (tracked in pack_config) |

### Misc Asset Directories

| Old              | New                        | Change                |
| ---------------- | -------------------------- | --------------------- |
| `line creator/`  | `reference/line-creator/`  | Spaces → hyphens      |
| `cartoon faces/` | `reference/cartoon-faces/` | Spaces → hyphens      |
| `stickers_gen/`  | `reference/stickers-gen/`  | Underscores → hyphens |

---

## Script Import Fixes

When scripts moved from root to `scripts/`, inter-script imports like `from pack_config import PACK_CONFIG` broke because Python's import resolver looks in the current working directory, not the script's directory.

### Fix Applied

Each script that imports siblings now has a `sys.path` preamble:

```python
from pathlib import Path
import sys

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

REPO_ROOT = _SCRIPTS_DIR.parent
```

This ensures imports work regardless of where you run the script from.

### Path References Updated

All hard-coded paths like `os.path.join(pack_id, "raw")` were updated to use `REPO_ROOT`:

```python
# Before (assumed CWD = repo root)
raw_dir = os.path.join(pack_id, "raw")

# After (works from any CWD)
raw_dir = str(REPO_ROOT / "packs" / pack_id / "raw")
```

**Scripts updated:** `run_pipeline.py`, `image_generator.py`, `telegram_publisher.py`, `split_stickers.py`

### split_stickers.py PACKS Dictionary

Each pack entry gained a `pack_dir` key mapping display names to kebab-case directory names:

```python
# Before
"Boba & Milo – Cheerful Otter Duo 5": {
    "input_file": "sticker_pack.png",
    ...
}
input_path = os.path.join(os.path.dirname(__file__), pack_name, pack["input_file"])

# After
"Boba & Milo – Cheerful Otter Duo 5": {
    "pack_dir": "boba-milo-5",
    "input_file": "sticker_pack.png",
    ...
}
pack_dir = REPO_ROOT / "packs" / pack["pack_dir"]
input_path = str(pack_dir / pack["input_file"])
```

---

## Pack Normalization

Three older packs used a non-standard `line_output/` directory instead of the standard `final/` layout:

| Pack                 | Old Layout                                     | New Layout (added)                                   |
| -------------------- | ---------------------------------------------- | ---------------------------------------------------- |
| chubby-mochi-cat     | `line_output/stickers/`, `main.png`, `tab.png` | `final/line/`, `final/line_main/`, `final/line_tab/` |
| chubby-mochi-hamster | `line_output/line/`, `main.png`, `tab.png`     | `final/line/`, `final/line_main/`, `final/line_tab/` |
| office-teddy-bear    | `line_output/line/`, `main.png`, `tab.png`     | `final/line/`, `final/line_main/`, `final/line_tab/` |

The old `line_output/` directories were preserved (not deleted) for reference. The new `final/` directories contain copies of the same files in the standardized layout that `line_uploader.py` expects.

---

## Files Created

### New Files

| File                                      | Purpose                                          |
| ----------------------------------------- | ------------------------------------------------ |
| `automation/__init__.py`                  | Package init with public API exports             |
| `automation/config.py`                    | URLs, timeouts, submission defaults              |
| `automation/utils.py`                     | safe_click, safe_fill, retry, screenshot helpers |
| `automation/line_auth.py`                 | Login + session persistence via storage_state()  |
| `automation/line_create_submission.py`    | Create new sticker submission draft              |
| `automation/line_upload_images.py`        | Upload main/tab/sticker images                   |
| `automation/line_set_metadata.py`         | Fill Display Information + Tag Settings tabs     |
| `automation/line_set_price.py`            | Select price tier                                |
| `automation/line_submit.py`               | Final review and submit for review               |
| `scripts/line_uploader.py`                | CLI entry point for LINE upload automation       |
| `templates/line_submission_defaults.json` | Default values for LINE submissions              |
| `.env.example`                            | Environment variable template                    |

### Documentation Created (10 files, 3,298 lines)

| File                                     | Lines | Description                            |
| ---------------------------------------- | ----- | -------------------------------------- |
| `docs/01-project-overview.md`            | ~180  | Project goals, architecture, cost      |
| `docs/02-end-to-end-workflow.md`         | ~350  | Complete workflow from idea to upload  |
| `docs/03-chatgpt-prompt-templates.md`    | ~300  | ChatGPT prompts for ideation/DALL-E    |
| `docs/04-dalle-generation-guide.md`      | ~280  | DALL-E generation with ChatGPT Go plan |
| `docs/05-image-processing-pipeline.md`   | ~320  | Split, bg removal, resize pipeline     |
| `docs/06-line-sticker-specifications.md` | ~250  | LINE image specs and requirements      |
| `docs/07-line-submission-template.md`    | ~200  | Step-by-step LINE submission guide     |
| `docs/08-browser-automation-design.md`   | ~833  | Playwright automation architecture     |
| `docs/09-repo-structure.md`              | ~220  | Directory layout explanation           |
| `docs/10-troubleshooting-faq.md`         | ~200  | Common issues and fixes                |

---

## .gitignore Updates

Added patterns for:

- `packs/*/sticker_pack.png` — Large composite sheets
- `packs/*/split/` — Intermediate split images
- `packs/*/final/` — Processed output images
- `automation/screenshots/` — Failure screenshots
- `automation/.storage_state.json` — Playwright session cookies
- `reference/` large binary assets
- `__pycache__/`, `.ruff_cache/`, `*.pyc`

---

## Standard Pack Layout

After normalization, every pack under `packs/` follows this structure:

```
packs/<pack-name>/
├── sticker_pack.png          # Source composite sheet (from ChatGPT/DALL-E)
├── split/                    # Individual stickers extracted from sheet
│   ├── 01_emotion_name.png
│   ├── 02_emotion_name.png
│   └── ...
└── final/                    # Platform-ready outputs
    ├── line/                 # 370x320 PNG (≤1MB each)
    │   ├── 01_emotion_name.png
    │   └── ...
    ├── line_main/            # 240x240 PNG (cover image)
    │   └── main.png
    ├── line_tab/             # 96x74 PNG (chat tab icon)
    │   └── tab.png
    ├── whatsapp/             # 512x512 WEBP (≤100KB each)
    ├── telegram/             # 512x512 WEBP (≤256KB each)
    ├── imessage_large/       # 618x618 PNG (≤500KB each)
    └── print_etsy/           # 2048x2048 PNG (high-res for print)
```

The `line_uploader.py` CLI expects `--pack-dir` to point to the `final/` directory.

---

## Rollback

If anything goes wrong, use git to restore the previous state:

```bash
git checkout HEAD -- .
```

Or to see what changed:

```bash
git status
git diff --name-status
```
