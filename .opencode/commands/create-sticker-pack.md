---
description: Create a complete sticker pack end-to-end from a topic — scaffold, generate images via DALL-E, process for all platforms, and publish to LINE and Telegram. Usage: /create-sticker-pack <topic>
agent: build
---

You are running the StickerFramework end-to-end pipeline.

The user's sticker topic is: **$ARGUMENTS**

Read the project structure overview:
!`find packs -maxdepth 1 -type d | sort | tail -5`

Read the existing pack config as a concrete example:
@scripts/pack_config.py

---

## Your job

Execute all phases below in order. Use the TodoWrite tool to track every phase before starting. Mark each todo completed immediately when done. Only stop at an explicit **[STOP]** marker.

---

## Phase 1 — Derive pack parameters from the topic

From the topic "$ARGUMENTS", infer:

1. `PACK_ID` — kebab-case, max 64 chars. Example: "chubby office capybara" → `chubby-office-capybara`.
2. `PACK_NAME` — Human display title, max 40 chars.
3. `publisher` — Read from AGENTS.md or use "StickerFramework".
4. `character` — Infer species, body color, eye style, accessories, proportions from the topic. If the topic is abstract (food, objects, phrases), skip character fields and use the topic directly as the visual subject.
5. `art_style` — Default to `flat_vector`.
6. `sticker_count` — Default 8 (LINE-compliant).
7. `platforms` — Default `["line", "telegram", "whatsapp", "telegram_animated", "imessage_large", "print_etsy"]`.
8. `animation_preset` — Default `bounce`.
9. `quality` — Default `standard`.

**Important:** Store the derived `PACK_ID` and `PACK_NAME` as concrete string values you will substitute literally into every subsequent bash command and file path. Never pass `<pack_id>` or `<pack_name>` as literal text — always substitute the real value.

Read the LINE content policy before finalising any names or descriptions:
@.opencode/skills/new-sticker-pack/references/line-content-policy.md

If the topic matches any banned keyword, append a disclaimer in your plan and ask the user:
**[STOP]** Topic may violate LINE guideline 3.13. Confirm you want to skip LINE publishing, or provide a revised topic.

---

## Phase 2 — Scaffold

Read the full scaffolding skill:
@.opencode/skills/new-sticker-pack/SKILL.md

1. Validate the pack_id (substitute your real PACK_ID value, e.g. `chubby-couple-mochi-hamster`):
```bash
python3 .opencode/skills/new-sticker-pack/scripts/validate_pack_id.py "PACK_ID"
```
If it fails, auto-correct (fix casing/special chars) and retry once. If still failing: **[STOP]** Report the conflict to the user.

2. Create the directory layout:
```bash
python3 .opencode/skills/new-sticker-pack/scripts/scaffold_pack.py "PACK_ID"
```

3. Write `packs/PACK_ID/pack_config.py` — use the template structure from:
@.opencode/skills/new-sticker-pack/assets/pack_config_template.py

Fill every `{{PLACEHOLDER}}` with the inferred values from Phase 1. For the stickers list, adapt the default emotion set from:
@.opencode/skills/new-sticker-pack/references/sticker-emotions-defaults.md

Rewrite each sticker's `pose` and `props` to fit the character/topic while keeping emotion IDs and emoji unchanged.

4. Verify the config is valid Python (substitute your real PACK_ID):
```bash
python3 -c "
import importlib.util, sys
s = importlib.util.spec_from_file_location('c', 'packs/PACK_ID/pack_config.py')
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
print('OK:', m.PACK_CONFIG['pack_id'])
"
```

---

## Phase 3 — Generate images

1. Check for OPENAI_API_KEY:
```bash
python3 -c "
import os, sys
from pathlib import Path
for line in Path('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip())
key = os.environ.get('OPENAI_API_KEY', '')
if not key or not key.startswith('sk-'):
    print('MISSING')
    sys.exit(1)
print('SET')
"
```
If output is `MISSING`: **[STOP]** Ask the user to add `OPENAI_API_KEY=sk-...` to `.env`.

2. Run DALL-E generation (substitute your real PACK_ID):
```bash
python3 -c "
import os
from pathlib import Path
for line in Path('.env').read_text().splitlines():
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, _, v = line.partition('=')
        os.environ[k.strip()] = v.strip()
" && \
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
    --pack packs/PACK_ID/pack_config.py \
    --generate-only \
    --standard
```

3. Report how many images landed:
```bash
ls packs/PACK_ID/raw/*.png 2>/dev/null | wc -l | tr -d ' '
```

---

## Phase 4 — Process images

Read the processing skill:
@.opencode/skills/process-pipeline/SKILL.md

1. Ensure required dependencies are installed:
```bash
pip install -q rembg lottie 2>&1 | tail -3
```

2. Verify inputs exist (substitute your real PACK_ID):
```bash
python3 .opencode/skills/process-pipeline/scripts/check_inputs.py "PACK_ID"
```

3. Run the pipeline (substitute your real PACK_ID):
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
    --pack packs/PACK_ID/pack_config.py \
    --process-only \
    --input packs/PACK_ID/raw
```
If any output contains "Background removal failed", rerun with `--skip-bg`:
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
    --pack packs/PACK_ID/pack_config.py \
    --process-only \
    --input packs/PACK_ID/raw \
    --skip-bg
```

4. Generate animated TGS:
```bash
python3 scripts/animated_converter.py \
    --pack-dir packs/PACK_ID/final \
    --format tgs --preset bounce
```

5. Verify all outputs (substitute your real PACK_ID):
```bash
python3 .opencode/skills/process-pipeline/scripts/check_outputs.py "PACK_ID"
```
On failure, run diagnostics:
```bash
python3 .opencode/skills/debug-pipeline/scripts/diagnose.py "PACK_ID"
```
Apply the matching fix from:
@.opencode/skills/debug-pipeline/references/error-patterns.md

Retry once. If still failing: **[STOP]** Show the full error output.

---

## Phase 5 — Publish to LINE

Read the LINE upload skill:
@.opencode/skills/line-upload/SKILL.md

Skip this phase if LINE was excluded from platforms.

1. Clear any stale upload progress from previous runs:
```bash
rm -f ~/.line-sticker-automation/progress.json
echo "Progress cleared"
```

2. Pre-flight check (substitute your real PACK_ID and PACK_NAME):
```bash
python3 scripts/line_preflight_check.py \
    --pack-dir packs/PACK_ID/final \
    --title "PACK_NAME" \
    --description "Cute sticker pack"
```
If it reports violations: **[STOP]** Report the banned keyword and field. Do not proceed.

3. Verify LINE assets (substitute your real PACK_ID):
```bash
python3 .opencode/skills/line-upload/scripts/check_line_assets.py "PACK_ID"
```
On failure, rerun processing (Phase 4) then retry.

4. Check for saved session:
```bash
ls ~/.line-sticker-automation/storage_state.json 2>/dev/null && echo SESSION_EXISTS || echo NO_SESSION
```

5. If `SESSION_EXISTS`: run the upload (substitute your real PACK_ID and PACK_NAME):
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
") python3 scripts/line_uploader.py \
    --pack-dir packs/PACK_ID/final \
    --title "PACK_NAME" \
    --description "Cute sticker pack" \
    --submit
```

6. If `NO_SESSION`:
**[STOP]** No LINE session found. Ask the user to run this once in their terminal to log in:
```bash
python3 scripts/line_uploader.py \
    --pack-dir packs/PACK_ID/final \
    --title "PACK_NAME" \
    --description "Cute sticker pack" \
    --headful --dry-run
```
After completing the QR/OTP login, re-run `/create-sticker-pack $ARGUMENTS` — the upload will proceed automatically.

---

## Phase 6 — Publish to Telegram

Read the Telegram skill:
@.opencode/skills/telegram-publish/SKILL.md

Skip this phase if Telegram was excluded from platforms.

1. Verify credentials and assets (substitute your real PACK_ID):
```bash
python3 .opencode/skills/telegram-publish/scripts/check_telegram_assets.py "PACK_ID" static
```
If credentials are missing: **[STOP]** Ask the user to add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` to `.env`.

2. Derive set name — replace `-` with `_` in PACK_ID, append `_by_<bot_username>`.
   Read the bot username from `.env`:
```bash
grep TELEGRAM_BOT_USERNAME .env 2>/dev/null | cut -d= -f2
```
If not found, use `StickerBot` as a placeholder and inform the user.

3. Publish static stickers (substitute your real PACK_ID, SET_NAME, PACK_NAME):
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
") python3 scripts/telegram_publisher.py \
    packs/PACK_ID/final/telegram \
    "SET_NAME" \
    "PACK_NAME"
```

4. Check animated assets:
```bash
python3 .opencode/skills/telegram-publish/scripts/check_telegram_assets.py "PACK_ID" animated
```
If assets exist, publish animated set:
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
") python3 scripts/telegram_publisher.py \
    packs/PACK_ID/final/telegram_animated \
    "SET_NAME_anim" \
    "PACK_NAME Animated" \
    --format animated
```

---

## Phase 7 — Summary

Print this completion table (fill in actual values):

```
╔══════════════════════════════════════════════════════════╗
║  STICKER PACK COMPLETE                                   ║
╠══════════════════════════════════════════════════════════╣
║  Topic      : $ARGUMENTS
║  Pack ID    : PACK_ID                                    ║
║  Directory  : packs/PACK_ID/                             ║
╠══════════════════════════════════════════════════════════╣
║  Scaffold   : ✓                                          ║
║  Generation : ✓  N images                               ║
║  Processing : ✓  all platforms                          ║
║  LINE       : ✓ submitted / ⏸ needs login / ⏭ skipped  ║
║  Telegram   : ✓ t.me/addstickers/SET_NAME               ║
╚══════════════════════════════════════════════════════════╝
```

Mark all todos as completed.
