# Next Steps After Processing

## Upload to LINE Creator Market

Requires: LINE session (run `--headful` once for interactive login).

```bash
# First run — interactive login (headful + dry-run):
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<Pack Title>" \
    --description "<Pack description>" \
    --headful --dry-run

# Subsequent runs — headless, submit for real:
python3 scripts/line_uploader.py \
    --pack-dir packs/<pack_id>/final \
    --title "<Pack Title>" \
    --description "<Pack description>" \
    --submit
```

## Publish to Telegram (Static)

Requires: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` in `.env`.

```bash
python3 scripts/telegram_publisher.py \
    packs/<pack_id>/final/telegram \
    <BotPackName>_by_<BotUsername> \
    "<Pack Title>"
```

## Publish to Telegram (Animated TGS)

```bash
python3 scripts/telegram_publisher.py \
    packs/<pack_id>/final/telegram_animated \
    <BotPackName>Animated_by_<BotUsername> \
    "<Pack Title> Animated" \
    --format animated
```

## Export for WhatsApp Native

```bash
python3 scripts/whatsapp_exporter.py \
    --pack-dir packs/<pack_id>/final
```

## Build iMessage App

```bash
python3 scripts/imessage_publisher.py \
    --pack-dir packs/<pack_id>/final \
    --dry-run
```
