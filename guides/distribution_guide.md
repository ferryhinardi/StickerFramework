# Multi-Platform Distribution Guide

Complete guide for publishing your sticker packs across all money-making platforms.

---

## Platform Overview

| Platform | Revenue | Effort | Automation | Best For |
|---|---|---|---|---|
| **Sticker.ly** | Free (funnel) | Low | Manual only | WhatsApp audience |
| **Telegram** | Free (funnel) | Low | **Fully automated** | Telegram audience |
| **LINE Creators Market** | 35% of sales | Medium | Manual upload | Asian markets |
| **iMessage App Store** | 70-85% of sales | High (first time) | Semi-automated | iOS users |
| **Etsy** | ~88-90% of sales | Medium | Manual listing | Digital sticker buyers |
| **Gumroad** | ~89% of sales | Low | Manual listing | Direct audience |

---

## 1. Telegram (Fully Automated)

### Setup (One-time)
1. Open Telegram, message [@BotFather](https://t.me/BotFather)
2. Send `/newbot` → follow prompts → get your **bot token**
3. Message [@userinfobot](https://t.me/userinfobot) → get your **user ID**
4. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="123456789:ABCdef..."
   export TELEGRAM_USER_ID="987654321"
   ```

### Publish
```bash
# Option A: Via the pipeline
python run_pipeline.py --process-only --telegram

# Option B: Standalone
python telegram_publisher.py \
    pack01_emotions_v1/final/telegram \
    MochiEmotions \
    "Mochi Emotions Vol. 1"
```

### Result
- Pack URL: `https://t.me/addstickers/MochiEmotions_by_YourBot`
- Share this link anywhere for instant installs

---

## 2. Sticker.ly / WhatsApp (Manual)

See [stickerly_guide.md](./stickerly_guide.md) for the full step-by-step process.

**Quick summary**: Transfer WebP files to phone → Open Sticker.ly → Create pack → Add stickers → Fill details → Publish.

---

## 3. LINE Creators Market

### Setup (One-time)
1. Register at [creator.line.me](https://creator.line.me)
2. Fill in creator profile, payment information
3. Verify your account (may take a few days)

### Sticker Requirements
| Item | Spec |
|---|---|
| Main image | 240 x 240 px, PNG |
| Sticker images | Up to 370 x 320 px, PNG, transparent bg |
| Tab image | 96 x 74 px, PNG |
| Stickers per pack | 8, 16, 24, 32, or 40 |
| File size | Max 1MB each |

Your pipeline produces LINE-format files in `<pack_id>/final/line/`.

### Upload Process
1. Go to [LINE Creators Market](https://creator.line.me/en/studio/)
2. Click **"Create New"** → **"Stickers"**
3. Fill in pack details:
   - **Title**: "Mochi Emotions Vol. 1" (in English)
   - **Title (Japanese)**: Use ChatGPT to translate if targeting Japan
   - **Description**: Describe your character and pack theme
   - **Copyright**: Your brand name
4. **Upload sticker images** (drag-and-drop from your `final/line/` folder)
5. **Set main image** (240x240 from your `final/line_main/` or crop from a sticker)
6. **Set tab image** (96x74)
7. **Set price**: LINE Coins 50 (~$0.99), 100 (~$1.49), or 150 (~$1.99)
8. **Submit for review** → Takes 1-7 business days
9. Once approved, your pack appears in the LINE Store

### Tips for LINE
- **Translate to Japanese**: Even basic translation dramatically increases sales
- **Use ChatGPT**: "Translate this sticker pack description to Japanese: ..."
- **Popular in**: Japan, Thailand, Taiwan, Indonesia
- **Revenue**: You receive 35% of sales via bank transfer

---

## 4. iMessage App Store (Apple)

### Setup (One-time)
1. **Apple Developer Program**: Enroll at [developer.apple.com/programs](https://developer.apple.com/programs/enroll/) ($99/year)
2. **Install Xcode** from the Mac App Store
3. **App Store Connect**: Set up at [appstoreconnect.apple.com](https://appstoreconnect.apple.com)
4. Configure banking/tax information for payments

### Create the Xcode Project

```bash
# Option A: Use the pipeline to create project structure
python run_pipeline.py --process-only --imessage

# Option B: Standalone
python prepare_imessage_pack.py --create MochiEmotions pack01_emotions_v1/final/imessage_large
```

### Build and Submit
1. **Open Xcode** → File → New → Project
2. Choose **"Sticker Pack Application"** template
3. Name: "Mochi Emotions" → Bundle ID: `com.yourbrand.mochiemotions`
4. Copy stickers:
   - Drag your processed PNG files from `final/imessage_large/` into the Sticker Pack folder in Xcode
   - Or copy the pre-built `.stickerpack` folder from the pipeline output
5. **Add app icons** (required):
   - Create icons at all required sizes
   - Drop into the "iMessage App Icon" asset catalog
6. **Configure signing**:
   - Select your Apple Developer team
   - Let Xcode manage provisioning profiles
7. **Test on device**:
   - Connect iPhone → Select it as build target → Run
   - Open Messages → Open the sticker browser → Verify your pack works
8. **Archive and submit**:
   - Product → Archive → Distribute → App Store Connect
   - Fill in App Store listing: description, screenshots, keywords
9. **Wait for review** (24-48 hours typically)

### Pricing
- Free or paid ($0.99 - $4.99 typical)
- Apple takes 30% (15% if you qualify for Small Business Program under $1M/year)
- You keep 70-85%

### Tips
- **Keywords matter**: Use all 100 characters for keywords
- **Screenshots**: Show stickers in a real iMessage conversation
- **Description**: Mention "kawaii", "cute", "stickers", "iMessage"
- **Updates**: Release new stickers as app updates to re-engage users

---

## 5. Etsy (Digital Downloads)

### Setup (One-time)
1. Create shop at [etsy.com/sell](https://www.etsy.com/sell)
2. Fill in shop name, payment, billing info
3. Set up your shop policies (digital downloads = no returns needed)

### What to Sell
Your pipeline creates a distribution ZIP in `<pack_id>/dist/` containing:
- Individual high-res PNG stickers
- Print-ready sticker sheets (US Letter + A4)
- README and license files

### Create Listing
1. Go to Shop Manager → Listings → Add a listing
2. **Type**: Digital
3. **Title** (optimized for search):
   ```
   Kawaii Cat Stickers | Cute Mochi Emotions Digital Sticker Pack |
   GoodNotes Stickers | Planner Stickers | Chibi Cat Clipart
   ```
4. **Description**:
   ```
   Adorable kawaii cat "Mochi" emotions sticker pack!

   WHAT'S INCLUDED:
   - 24 individual PNG stickers (transparent background)
   - 2 print-ready sticker sheets (US Letter & A4 @ 300 DPI)
   - High resolution, perfect for digital planners and printing

   PERFECT FOR:
   - GoodNotes, Notability, and other digital planners
   - Printing on sticker paper for journals and scrapbooks
   - Personal social media and messaging

   FORMAT: PNG files with transparent backgrounds
   SIZE: 2048 x 2048 pixels (high resolution)

   LICENSE: Personal use included. Commercial license available separately.

   NOTE: Artwork created with AI assistance and extensively post-processed
   and refined by the artist.
   ```
5. **Tags** (13 max on Etsy):
   ```
   kawaii stickers, cute digital stickers, goodnotes stickers,
   digital planner stickers, kawaii cat stickers, chibi stickers,
   printable stickers, cute clipart, planner clipart,
   kawaii emotions, journal stickers, digital download stickers,
   cute cat stickers
   ```
6. **Upload files**: Your distribution ZIP from `dist/`
7. **Price**: $2.99 - $4.99 for a single pack
8. **Variations** (optional):
   - Personal License: $2.99
   - Commercial License: $14.99

### Bundle Strategy
Create a separate listing for bundles:
- "Mega Bundle: 3 Kawaii Packs (72 stickers)" at $6.99
- "Complete Collection: 5 Packs (120 stickers)" at $9.99
- Bundles have higher perceived value and AOV (average order value)

---

## 6. Gumroad

### Setup (One-time)
1. Create account at [gumroad.com](https://gumroad.com)
2. Set up payment information
3. Create your product page

### Create Product
1. New Product → Digital Product
2. **Name**: "Mochi Emotions Vol. 1 - Kawaii Sticker Pack"
3. **Description**: Similar to Etsy (customize for Gumroad audience)
4. **Upload**: Your distribution ZIP
5. **Pricing tiers**:
   - Personal License: $2.99 (or "pay what you want" minimum $1.99)
   - Commercial License: $14.99
6. **Cover image**: Use the `social_preview.png` from your dist folder
7. **Publish**

### Advantages of Gumroad
- 10% fee (vs Etsy's ~12%)
- No listing fees
- Handles global sales tax automatically
- Great for direct traffic from social media
- Supports memberships/subscriptions for monthly sticker drops

---

## Pricing Quick Reference

| Platform | Recommended Price | Your Take | Notes |
|---|---|---|---|
| Sticker.ly | FREE | $0 | Marketing funnel |
| Telegram | FREE | $0 | Marketing funnel |
| LINE | $0.99 | ~$0.35 | Start low, build reviews |
| iMessage | $0.99 | ~$0.69 | Can raise to $1.99 later |
| Etsy (single) | $2.99 | ~$2.65 | Main digital sales |
| Etsy (bundle) | $6.99 | ~$6.25 | 3-pack bundle |
| Gumroad (single) | $2.99 | ~$2.69 | For direct audience |
| Gumroad (commercial) | $14.99 | ~$13.49 | For businesses |

---

## Launch Checklist

```
[ ] Pipeline produces all platform files correctly
[ ] Test stickers on WhatsApp (via Sticker.ly)
[ ] Telegram pack created and tested
[ ] LINE pack submitted for review
[ ] iMessage app submitted to App Store Connect
[ ] Etsy listing live with correct files, tags, pricing
[ ] Gumroad product page created
[ ] Social media accounts created (Instagram, TikTok, Pinterest)
[ ] First promotional post shared on all channels
[ ] Sticker.ly pack link shared in WhatsApp groups/status
[ ] Telegram pack link shared in relevant groups
```

---

## Monthly Release Calendar

| Month | Pack Theme | Priority |
|---|---|---|
| January | New Year / Winter | Medium |
| February | Valentine's Day | **HIGH** |
| March | Spring / Cherry Blossom | Medium |
| April | Easter | Low |
| May | Mother's Day | Medium |
| June | Summer / Beach | Medium |
| August | Back to School | **HIGH** |
| October | Halloween | **HIGH** |
| November | Thanksgiving | Medium |
| December | Christmas / Holiday | **HIGH** |

Start creating seasonal packs **4-6 weeks before** the holiday for maximum sales.
