---
name: telegram-publish
description: >
  Publishes a processed sticker pack to Telegram as a sticker set using the
  Telegram Bot API. Use when the user wants to create or update a Telegram
  sticker set, publish static WebP stickers, animated TGS stickers, or video
  WEBM stickers to Telegram. Don't use for LINE uploads, image processing, or
  packs that haven't been processed yet.
---

# Skill: telegram-publish

## Purpose
Publish a processed sticker pack to Telegram via the Bot API, creating a new
sticker set in the user's Telegram account.

## Prerequisites
- Processed sticker images exist in the appropriate `final/` subdirectory.
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` set in `.env`.
- Pack name (Telegram set name) follows the required format: alphanumeric + underscores, ends with `_by_<botname>`.

## Steps

### Step 1 — Verify environment
Check that Telegram credentials are configured:

```bash
python3 .github/skills/telegram-publish/scripts/check_telegram_env.py
```

If credentials are missing, instruct the user:
1. Message `@BotFather` on Telegram → `/newbot` → copy the token.
2. Message `@userinfobot` on Telegram → copy the numeric user ID.
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_USER_ID=987654321
   ```

### Step 2 — Determine format and source directory

Ask the user which format to publish (or infer from context):

| Format | Source directory | Flag |
|---|---|---|
| Static (default) | `packs/<pack_id>/final/telegram/` | _(none)_ |
| Animated TGS | `packs/<pack_id>/final/telegram_animated/` | `--format animated` |
| Video WEBM | `packs/<pack_id>/final/telegram_video/` | `--format video` |

Verify the source directory contains files:

```bash
python3 .github/skills/telegram-publish/scripts/check_telegram_assets.py \
    "<pack_id>" "<format>"
```

### Step 3 — Compose the sticker set name
Telegram set names must:
- Be 5–64 characters.
- Contain only `a-z`, `0-9`, `_`.
- End with `_by_<bot_username>` (Telegram enforces this).

Derive a default suggestion: `<pack_id_underscored>_by_<botname>`

Confirm with the user before proceeding.

### Step 4 — Publish sticker set

Static:
```bash
python3 scripts/telegram_publisher.py \
    packs/<pack_id>/final/telegram \
    "<set_name>" \
    "<Pack Title>"
```

Animated:
```bash
python3 scripts/telegram_publisher.py \
    packs/<pack_id>/final/telegram_animated \
    "<set_name>" \
    "<Pack Title>" \
    --format animated
```

Video:
```bash
python3 scripts/telegram_publisher.py \
    packs/<pack_id>/final/telegram_video \
    "<set_name>" \
    "<Pack Title>" \
    --format video
```

### Step 5 — Confirm and share link
On success, the sticker set is immediately available. Provide the user with
the direct link:

```
https://t.me/addstickers/<set_name>
```

## Error Handling

| Error | Resolution |
|---|---|
| `TELEGRAM_BOT_TOKEN not set` | Add token to `.env` — see Step 1 |
| `TELEGRAM_USER_ID not set` | Add user ID to `.env` — see Step 1 |
| `STICKER_SET_INVALID` | Set name format is wrong — must end with `_by_<botname>` |
| `STICKER_SET_NAME_OCCUPIED` | Choose a different set name |
| Animated TGS exceeds 64 KB | Reprocess with a simpler animation preset (`pulse` or `bounce`) |
| Video WEBM exceeds 256 KB | Reduce `duration_ms` in `pack_config.py` and rerun `process-pipeline` |
| Static WebP exceeds 256 KB | Reprocess images — check `sticker_processor.py` quality settings |
