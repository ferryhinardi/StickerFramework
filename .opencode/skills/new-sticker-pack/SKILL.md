---
name: new-sticker-pack
description: >
  Scaffolds a complete new sticker pack for this StickerFramework repository.
  Use when the user wants to create a new sticker pack from scratch, define a
  new character, set up a pack directory, or generate a pack_config.py for a
  new theme. Don't use for processing existing images, uploading to platforms,
  or debugging pipeline failures.
---

# Skill: new-sticker-pack

## Purpose
Scaffold a complete new sticker pack: create the directory layout, generate a `pack_config.py` from the user's character/theme description, and validate it is ready for the pipeline.

## Prerequisites
- Working directory is the repository root.
- Python 3.10+ installed (`python3 --version`).
- `.env` file exists with `OPENAI_API_KEY` set (required for generation).

## Steps

### Step 1 — Gather pack parameters
Ask the user for the following if not already provided:
- `pack_id`: kebab-case identifier (e.g., `cappy-capybara-3`). Must match the directory name exactly.
- `pack_name`: Human-readable display name (e.g., `Cappy the Capybara Vol. 3`).
- `publisher`: Brand or creator name.
- Character description: species, body colour, eye style, accessory (singular), proportions.
- Art style: flat vector or painted illustration; outline type; background colour.
- Target platforms: one or more of `line`, `telegram`, `whatsapp`, `imessage_large`, `print_etsy`.
  **Never include `telegram_animated` or `telegram_video` in this list** — these are generated
  separately via `--telegram-animated` / `--telegram-video` flags on `run_pipeline.py`.
- Number of stickers: must be 8, 16, 24, 32, or 40 (LINE constraint).
- Emotion/theme list: user supplies a list of moods or scenes, or accepts the default 8-emotion set.

### Step 2 — Validate pack_id format
Run the validation script to confirm `pack_id` follows naming rules:

```bash
python3 .opencode/skills/new-sticker-pack/scripts/validate_pack_id.py "<pack_id>"
```

If validation fails, prompt the user to correct the name before continuing.

### Step 3 — Create directory layout
Create the standard pack directory tree:

```
packs/<pack_id>/
├── raw/
├── split/
└── final/
    ├── line/
    ├── line_main/
    ├── line_tab/
    ├── whatsapp/
    ├── whatsapp_native/
    ├── telegram/
    ├── telegram_animated/
    ├── telegram_video/
    ├── imessage_large/
    └── print_etsy/
```

Use the scaffold script:

```bash
python3 .opencode/skills/new-sticker-pack/scripts/scaffold_pack.py "<pack_id>"
```

### Step 4 — Generate pack_config.py
Read the asset template at `assets/pack_config_template.py` and fill every `{{PLACEHOLDER}}` with
real values. Write the rendered file to `packs/<pack_id>/pack_config.py`.

**Required `character` keys** — `image_generator.py` will crash with `KeyError` if any are missing:

| Key | Example value |
|---|---|
| `name` | `"Mochi"` |
| `species` | `"hamster"` |
| `body_color` | `"cream white"` |
| `blush_color` | `"soft pink"` |
| `outline_color` | `"black"` |
| `eye_style` | `"large glossy black dot eyes"` |
| `accessory` | `"small pink bow on head"` ← singular string, not a list |
| `proportions` | `"chubby round body, stubby limbs"` |

**Required `style` keys** — all must be present:

| Key | Example value |
|---|---|
| `outline_type` | `"thick uniform black outline, 4px width"` |
| `coloring` | `"flat pastel colors, no gradients"` |
| `background` | `"transparent background"` |
| `extras` | `"die-cut sticker style with white outline border"` |
| `art_style` | `"kawaii flat_vector illustration"` |

Reference `references/sticker-emotions-defaults.md` for a default 8-sticker emotions set to seed
the `stickers` list when the user has not specified individual stickers.

### Step 5 — Validate the config
Confirm the written file is valid Python and has the correct pack_id:

```bash
python3 -c "
import importlib.util
s = importlib.util.spec_from_file_location('c', 'packs/<pack_id>/pack_config.py')
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
print('OK:', m.PACK_CONFIG['pack_id'], '|', len(m.PACK_CONFIG['stickers']), 'stickers')
"
```

### Step 6 — Verify LINE constraints
If `line` is in the target platforms, confirm:
- Sticker count is one of 8, 16, 24, 32, or 40.
- No prohibited keywords in `pack_name` or sticker descriptions. See `references/line-content-policy.md`.

If a violation is found, report the exact field and suggest a replacement before proceeding.

### Step 7 — Confirm and summarise
Print a summary table:

| Field | Value |
|---|---|
| pack_id | `<pack_id>` |
| Directory | `packs/<pack_id>/` |
| Config | `packs/<pack_id>/pack_config.py` |
| Sticker count | `<n>` |
| Platforms | `<platforms>` |

Inform the user of the next command to run (use `env $(...)` pattern, not `export $(...)`:

```bash
env $(python3 -c "
from pathlib import Path
pairs = []
for line in Path('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        pairs.append(f'{k.strip()}={v.strip()}')
print(' '.join(pairs))
") python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --generate-only --standard
```

## Error Handling

| Error | Resolution |
|---|---|
| `pack_id` contains uppercase or spaces | Re-prompt for kebab-case name |
| Directory `packs/<pack_id>` already exists | Ask user to confirm overwrite or choose a new name |
| Sticker count not in 8/16/24/32/40 | Adjust to the nearest valid count and inform user |
| `KeyError: 'blush_color'` during generation | Add missing key to `character` dict in pack_config.py |
| `KeyError: 'extras'` during generation | Add `"extras"` key to `style` dict in pack_config.py |
| `ValueError: Unsupported format: TGS` | Remove `telegram_animated` from `platforms` list |
| Banned keyword detected in metadata | Replace with a compliant alternative from `references/line-content-policy.md` |
