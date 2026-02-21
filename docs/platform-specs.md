# Platform Specifications

Detailed technical requirements and distribution information for each supported platform.

---

## Platform Comparison

| Platform | Format | Sticker Size | Max File Size | Pack Size | Revenue | Automation |
|----------|--------|-------------|---------------|-----------|---------|------------|
| WhatsApp (Sticker.ly) | WEBP | 512x512 | 100 KB | 3-30 | Free (marketing) | Manual upload |
| Telegram | WEBP | 512x512 | 256 KB | 1-120 | Free (marketing) | Fully automated |
| LINE | PNG | 370x320 | 1 MB | 8-40 | 35-50% revenue | Manual submission |
| iMessage | PNG | 618x618 | 500 KB | 1-unlimited | 70% revenue | Xcode + App Store |
| Etsy | PNG | 2048x2048 | Unlimited | Any | 93.5% revenue | Manual listing |
| Gumroad | PNG | 2048x2048 | Unlimited | Any | 90-95% revenue | Manual listing |

---

## WhatsApp / Sticker.ly

### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | WEBP |
| **Dimensions** | 512x512 pixels |
| **Max File Size** | 100 KB per sticker |
| **Background** | Transparent |
| **Tray Icon** | 96x96 WEBP, <50 KB |
| **Pack Size** | Minimum 3, Maximum 30 stickers |
| **Margin** | 16px margin recommended |

### Processing Notes
- The 100 KB limit is strict -- the processor uses binary search on WebP quality
- Tray icon is auto-generated from the first sticker in the pack
- White outline (die-cut border) is essential for visibility on dark chat backgrounds

### Distribution
- Upload via Sticker.ly app (iOS/Android)
- Manual process: transfer files to phone, upload one-by-one
- Tray icon set separately in the app
- See `guides/stickerly_guide.md` for step-by-step instructions

### Monetization
- Free platform (no direct revenue)
- Use as marketing funnel to drive traffic to paid packs on Etsy/Gumroad
- Add a promo sticker linking to your store

---

## Telegram

### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | WEBP (static), TGS (animated), WEBM (video) |
| **Dimensions** | 512x512 pixels (one side must be exactly 512) |
| **Max File Size** | 256 KB (static), 64 KB (animated), 256 KB (video) |
| **Background** | Transparent |
| **Pack Size** | 1-120 stickers |
| **Set Name** | Must end with `_by_<botname>` |

### Processing Notes
- More generous file size limit (256 KB) than WhatsApp
- Static stickers only -- animated/video stickers not currently supported by the pipeline
- Set names have strict format: alphanumeric + underscores, ending with bot suffix

### Distribution
- **Fully automated** via `telegram_publisher.py`
- Requires a Telegram Bot token from `@BotFather`
- Requires the user's numeric Telegram ID
- Bot creates the sticker set and adds all stickers programmatically

### Automation Details
```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
export TELEGRAM_USER_ID="987654321"

# Run with --telegram flag
python run_pipeline.py --telegram
```

The publisher:
1. Validates bot credentials
2. Creates a new sticker set with the first sticker
3. Adds remaining stickers one-by-one (with rate limit delays)
4. Returns the sticker set URL: `https://t.me/addstickers/<set_name>`

### Monetization
- Free platform (no direct revenue)
- Excellent for brand awareness and community building
- Link to paid packs in set description

---

## LINE Creators Market

### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Sticker Format** | PNG |
| **Sticker Size** | 370x320 pixels (W x H) |
| **Max File Size** | 1 MB per sticker |
| **Main Image** | 240x240 PNG |
| **Tab Image** | 96x74 PNG |
| **Background** | Transparent |
| **Pack Size** | 8, 16, 24, 32, or 40 stickers |
| **Margin** | 10px margin on all sides |

### Processing Notes
- Non-square format (370x320) -- wider than tall
- Specific pack sizes only (multiples of 8, max 40)
- Requires separate main image and tab image
- Strictest margin requirements

### Distribution
- Submit via LINE Creators Market (https://creator.line.me)
- Manual submission process with review period (1-2 weeks)
- Requires LINE account and creator registration

### Monetization
- Revenue share: 35-50% to creator
- Pricing: Set by LINE (typically $0.99 equivalent)
- Global market with strong presence in Japan, Thailand, Indonesia, Taiwan

### Metadata Generated
```json
{
    "title": "Mochi Emotions Vol. 1",
    "author": "Your Brand Name",
    "sticker_count": 24,
    "format": "PNG",
    "dimensions": "370x320",
    "main_image": "240x240",
    "tab_image": "96x74"
}
```

---

## iMessage (Apple App Store)

### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | PNG (also supports APNG, GIF for animated) |
| **Small Grid** | 300x300 pixels |
| **Medium Grid** | 408x408 pixels |
| **Large Grid** | 618x618 pixels |
| **Max File Size** | 500 KB per sticker |
| **Background** | Transparent |
| **Pack Size** | No strict limit |

### Processing Notes
- Three size tiers based on desired grid layout
- The pipeline defaults to `imessage_large` (618x618) for maximum quality
- Requires an Xcode project structure for App Store submission

### Distribution
- Requires Apple Developer account ($99/year)
- Pipeline generates complete Xcode project structure
- Manual steps: open in Xcode, add icons, configure signing, archive, submit

### Xcode Project Structure (Auto-Generated)
```
<PackName>/
├── <PackName>.xcodeproj/
│   └── project.pbxproj
├── Stickers.xcstickers/
│   ├── iMessage App Icon.stickersiconset/
│   │   └── Contents.json          # Icon size definitions
│   └── Sticker Pack.stickerpack/
│       ├── <sticker_01>.sticker/
│       │   ├── <sticker_01>.png
│       │   └── Contents.json
│       ├── <sticker_02>.sticker/
│       └── ...
└── Info.plist
```

### Required App Icon Sizes
| Size | Scale | Usage |
|------|-------|-------|
| 29x29 | 2x, 3x | Settings |
| 60x45 | 2x, 3x | Messages |
| 67x50 | 2x | iPad |
| 74x55 | 2x | iPad Pro |
| 27x20 | 2x, 3x | Notification |
| 1024x768 | 1x | App Store |

### Monetization
- Revenue share: 70% to developer (Apple takes 30%)
- Pricing: $0.99 recommended for sticker packs
- Global distribution via App Store

---

## Etsy (Digital Download)

### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | PNG (high resolution) |
| **Dimensions** | 2048x2048 pixels |
| **Max File Size** | Unlimited (within Etsy's 20MB listing limit) |
| **Background** | Transparent |
| **Delivery** | Digital download (ZIP file) |

### Processing Notes
- Highest resolution output (2048x2048) for print quality
- Print sheets generated at 300 DPI (US Letter and A4)
- Social preview image (3000x3000) for listing photos

### Distribution Package Contents
```
<pack_id>_distribution.zip
├── stickers/              # Individual high-res PNGs
│   ├── 01_happy.png
│   ├── 02_love.png
│   └── ...
├── print_sheets/
│   ├── sticker_sheet_letter.png  # US Letter (300 DPI)
│   └── sticker_sheet_a4.png      # A4 (300 DPI)
├── README.txt             # Usage instructions
└── LICENSE.txt            # Personal use license
```

### Monetization
- Etsy takes 6.5% transaction fee + $0.20 listing fee
- Recommended pricing: $2.99-$4.99 per pack
- Bundle pricing: 3-pack for $6.99, 5-pack for $9.99
- Commercial license: $14.99 (separate listing)

### Listing Optimization
- Use the generated social preview as the primary listing image
- Include print sheet preview as secondary image
- Tags: "kawaii stickers", "digital stickers", "planner stickers", "cute cat stickers"
- Seasonal packs perform best around holidays

---

## Gumroad (Digital Download)

### Technical Specs
Same as Etsy -- uses the same `print_etsy` output and distribution ZIP.

### Distribution
- Upload the distribution ZIP as the product file
- Use social preview as the product thumbnail
- Set up in minutes (simpler than Etsy)

### Monetization
- Gumroad takes 5-10% fee (based on plan)
- More pricing flexibility than Etsy
- Supports "pay what you want" pricing
- Good for commercial license upsells

---

## Pricing Strategy Summary

| Tier | Platforms | Price | Purpose |
|------|-----------|-------|---------|
| Free | Sticker.ly, Telegram | $0.00 | Marketing, brand awareness |
| Low | LINE, iMessage | $0.99 | Volume sales, platform visibility |
| Mid | Etsy, Gumroad | $2.99-$4.99 | Primary revenue |
| Premium | Etsy, Gumroad (commercial) | $14.99 | Commercial licensing |
| Bundle | Etsy, Gumroad | $6.99-$9.99 | Multi-pack value |

---

## Seasonal Calendar

| Month | Theme | Priority |
|-------|-------|----------|
| January | New Year, Goals | Medium |
| February | Valentine's Day | **High** |
| March | Spring, St. Patrick's | Low |
| April | Easter, Earth Day | Medium |
| May | Mother's Day, Graduation | Medium |
| June | Summer, Pride | Medium |
| July | Beach, Travel | Low |
| August | Back to School | **High** |
| September | Autumn, Coffee | Medium |
| October | Halloween | **High** |
| November | Thanksgiving, Black Friday | Medium |
| December | Christmas, Holidays | **High** |
