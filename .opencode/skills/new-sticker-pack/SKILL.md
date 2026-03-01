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
- Character description: species, body colour, eye style, accessories, proportions.
- Art style: flat vector or painted illustration; outline type; background colour.
- Target platforms: one or more of `line`, `telegram`, `whatsapp`, `imessage`, `print`.
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
Read the asset template at `assets/pack_config_template.py` and fill it with the values collected in Step 1.

Write the rendered file to `packs/<pack_id>/pack_config.py`.

Reference `references/sticker-emotions-defaults.md` for a default 8-sticker emotions set to seed the `stickers` list when the user has not specified individual stickers.

### Step 5 — Verify LINE constraints
If `line` is in the target platforms, confirm:
- Sticker count is one of 8, 16, 24, 32, or 40.
- No prohibited keywords in `pack_name` or sticker descriptions. See `references/line-content-policy.md` for the banned keyword list.

If a violation is found, report the exact field and suggest a replacement before proceeding.

### Step 6 — Confirm and summarise
Print a summary table:

| Field | Value |
|---|---|
| pack_id | `<pack_id>` |
| Directory | `packs/<pack_id>/` |
| Config | `packs/<pack_id>/pack_config.py` |
| Sticker count | `<n>` |
| Platforms | `<platforms>` |

Inform the user of the next command to run:

```bash
python3 scripts/run_pipeline.py \
    --pack packs/<pack_id>/pack_config.py \
    --process-only --input packs/<pack_id>/raw
```

Or, to generate images via DALL-E first:

```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/run_pipeline.py --pack packs/<pack_id>/pack_config.py
```

## Error Handling

| Error | Resolution |
|---|---|
| `pack_id` contains uppercase or spaces | Re-prompt for kebab-case name |
| Directory `packs/<pack_id>` already exists | Ask user to confirm overwrite or choose a new name |
| Sticker count not in 8/16/24/32/40 | Adjust to the nearest valid count and inform user |
| Banned keyword detected in metadata | Replace with a compliant alternative from `references/line-content-policy.md` |
