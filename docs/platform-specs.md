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

> Source: [LINE Creation Guidelines](https://creator.line.me/en/guideline/sticker/)

LINE Creators Market supports four product types: **Stickers**, **Animated Stickers**, **Emoji**, and **Themes**. Each has distinct image requirements.

### Distribution (All Product Types)
- Submit via LINE Creators Market (https://creator.line.me)
- Manual submission process with review period
- Requires LINE account and creator registration

### Monetization (All Product Types)
- Revenue share: 35-50% to creator
- Pricing: Set by LINE (typically $0.99 equivalent)
- Global market with strong presence in Japan, Thailand, Indonesia, Taiwan

### Text Metadata Limits (All Product Types)

| Field | Max Characters |
|-------|---------------|
| Creator | 50 |
| Title | 40 |
| Description | 160 |
| Copyright | 50 |

- Asian language characters and some symbols count as 2 characters each.

### Content Guidelines (All Product Types)

**Recommended:**
- Content that is easy to use in daily conversation and communication
- Easily understandable expressions, messages, and illustrations

**Not allowed:**
- Objects and scenery that are difficult to use in conversation
- Poor visibility (images too long, full-length illustrations of tall characters)
- Sets that significantly lack variety (purely pale colors, strings of numbers)
- Advertising content, corporate logos, product release dates
- Content that offends public order/morality, suggestive of underage drinking/smoking, sexual/violent imagery, or content that may fuel nationalism
- Content requiring users to provide personal data or IDs for purchase
- Content mentioning internet services, messenger apps, or characters related to such services

---

### 1. Stickers (Static)

> Source: [https://creator.line.me/en/guideline/sticker/](https://creator.line.me/en/guideline/sticker/)

#### Image Requirements

| Image Type | Quantity | Size (W x H) | Format |
|------------|----------|---------------|--------|
| **Main Image** | 1 | 240 x 240 | PNG |
| **Sticker Images** | 8, 16, 24, 32, or 40 | Up to 370 x 320 | PNG |
| **Chat Thumbnail Icon** | 1 | 96 x 74 | PNG |

#### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | PNG |
| **Color Mode** | RGB |
| **Resolution** | At least 72 dpi |
| **Background** | Transparent |
| **Dimensions** | Must have even-numbered height and width |
| **Max File Size** | 1 MB per image |
| **ZIP Upload** | Max 60 MB for all images in a single ZIP |
| **Sticker Margin** | ~10px between trimmed image edge and content |

#### Pack Size Rules
- Select from exactly **8, 16, 24, 32, or 40** stickers (no other counts accepted)
- You can change the count freely before submission on the Manage Stickers page

#### Sticker Margins
- There should be a margin of around **10 pixels** between the trimmed image and the content around it.
- Consider the balance of the stickers when creating designs.

#### Processing Notes
- Non-square format (370x320) -- wider than tall
- Sticker images are resized automatically by LINE, but dimensions must be even numbers
- Main image (240x240) is the pack cover shown in the LINE Store
- Chat thumbnail icon (96x74) is displayed in the chat sticker tray

---

### 2. Animated Stickers (APNG)

> Source: [https://creator.line.me/en/guideline/animationsticker/](https://creator.line.me/en/guideline/animationsticker/)

Includes **pop-up stickers** (animations play across the whole chat screen) and **effect stickers** (animations play in the chat screen background).

#### Image Requirements

| Image Type | Quantity | Size (W x H) | Format |
|------------|----------|---------------|--------|
| **Main Image** | 1 | 240 x 240 | APNG (.png) |
| **Animated Sticker Images** | 8, 16, or 24 | Up to 320 x 270 | APNG (.png) |
| **Chat Thumbnail Icon** | 1 | 96 x 74 | PNG |

#### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | APNG (use `.png` file extension) |
| **Color Mode** | RGB |
| **Background** | Transparent |
| **Max File Size** | 1 MB per image |
| **ZIP Upload** | Max 60 MB for all images in a single ZIP |

#### Animation Specs

| Property | Requirement |
|----------|-------------|
| **Dimensions** | Up to 320 x 270; one side must be at least 270px |
| **Loops** | 1-4 loops per sticker |
| **Total Playback** | Up to 4 seconds per sticker |
| **Frames per APNG** | Between 5 and 20 frames |
| **Height rule** | If height is the longer side, it must be exactly 270px |

#### Animation Notes
- Generate animated sticker images with an APNG creation tool such as APNG Assembler
- The first frame of the APNG is displayed as the static image on LINE STORE and the Sticker Shop
- Repeated identical frames may be combined as a single frame by APNG tools
- Files using the same data for all frames will cause an upload error
- Do not add margins to animated sticker frames
- The small play symbol on the chat thumbnail icon is added automatically -- do not add it yourself

#### Pack Size Rules
- Select from exactly **8, 16, or 24** animated stickers (fewer options than static stickers)

---

### 3. Emoji

> Source: [https://creator.line.me/en/guideline/emoji/](https://creator.line.me/en/guideline/emoji/)

LINE Emoji appear as stickers when sent on their own. When sent alongside text, they appear in-line as part of the user's speech balloon. Also supports **animated emoji** (APNG).

#### Image Requirements

| Image Type | Quantity | Size (W x H) | Format |
|------------|----------|---------------|--------|
| **Chat Thumbnail Icon** | 1 | 96 x 74 | PNG |
| **Emoji Images** | Varies by set type | 180 x 180 | PNG |

#### Set Types

| Set Type | Quantity | Description |
|----------|----------|-------------|
| **Regular Emoji** | 8-40 | Custom emoji only |
| **Letters & Numbers + Regular** | 112-144 | A-Z, a-z, 0-9, symbols (104) + 8-40 regular |
| **Kana + Regular** | 169-201 | Hiragana & Katakana (161) + 8-40 regular |
| **Kana + Letters & Numbers + Regular** | 273-305 | All letter types (265) + 8-40 regular |
| **Letters & Numbers only** | 104 | A-Z, a-z, 0-9, symbols |
| **Kana only** | 161 | Hiragana & Katakana |
| **Kana + Letters & Numbers** | 265 | All letter types combined |

#### Technical Specs

| Property | Requirement |
|----------|-------------|
| **Format** | PNG |
| **Color Mode** | RGB |
| **Resolution** | At least 72 dpi |
| **Background** | Transparent |
| **Max File Size** | 1 MB per image |
| **ZIP Upload** | Max 20 MB for all images in a single ZIP |

#### Emoji Margins
- **No margins recommended** -- make illustrations as large as possible
- If margins are added, ensure images are still clearly visible

#### Emoji Design Tips
- **Thick, dark outlines**: Thin, light-colored outlines may not show up against all backgrounds
- **Stand-alone capable**: Emoji can be sent as stickers when sent alone; design them to work both ways
- **Distinctive expressions**: Emoji appear very small in chat; make each expression large and distinct
- **Keep it simple**: Sparkles, hearts, and motion lines that work in stickers may not register at emoji size
- **Order matters**: Place most frequently used emoji near the top
- **Add variations**: Prevent monotony with a variety of character elements and poses
- **Seamless support**: LINE inserts no space between emoji, enabling seamless illustrations
- **Text emoji margins**: Letter emoji should have margins to prevent clumping against other emoji

#### Filename Convention
- Filenames must use designated numbers: `001.png`, `002.png`, ... up to `305.png`
- Number assignments depend on the selected set type (regular emoji start at 001; letter emoji follow a fixed character mapping)
- See [Set Types and Filenames](https://creator.line.me/en/guideline/emoji/detail/) for the full mapping

---

### 4. Themes

> Source: [https://creator.line.me/en/guideline/theme/](https://creator.line.me/en/guideline/theme/)

Themes customize the entire LINE app appearance: chat backgrounds, menu buttons, passcode screen, profile images, and more.

#### Image Requirements Summary

| Category | Quantity | Description |
|----------|----------|-------------|
| **A. Main Images** | 3 | Store thumbnails (iOS, Android, LINE STORE) |
| **B. Menu Button Images** | 16 | Navigation bar icons (on/off states) |
| **C. Menu Background Images** | 1 | Navigation bar background |
| **D. Passcode Images** | 16 | Passcode digit indicators (4 digits x 2 states x 2 platforms) |
| **E. Profile Images** | 4 | Default profile images (individual + group, iOS + Android) |
| **F. Chat Background Image** | 2 (optional) | Chat screen background (iOS + Android) |
| **Total** | **42 images** | |

#### A. Main Images (3 images)

| Platform | Size (W x H) | Filename |
|----------|---------------|----------|
| iOS | 200 x 284 | `ios_thumbnail.png` |
| Android | 136 x 202 | `android_thumbnail.png` |
| LINE STORE | 198 x 278 | `store_thumbnail.png` |

- Backgrounds **cannot** be transparent; must be non-transparent

#### B. Menu Button Images (16 images)

- Navigation bar icons with on/off states for each platform
- Separate images required for iOS and Android

#### C. Menu Background Images (1 image)

- Background for the navigation/menu bar area

#### D. Passcode Images (16 images)

| Platform | Size (W x H) | States |
|----------|---------------|--------|
| iOS | 120 x 120 | OFF + ON per digit (4 digits) |
| Android | 116 x 116 | OFF + ON per digit (4 digits) |

- Filenames: `i_12.png` through `i_19.png` (iOS), `a_12.png` through `a_19.png` (Android)
- You can display the same image for all 4 digits or a different image for each

#### E. Profile Images (4 images)

| Category | iOS Size | Android Size |
|----------|----------|--------------|
| Individual | 240 x 240 | 247 x 247 |
| Group | 240 x 240 | 247 x 247 |

- Filenames: `i_20.png`, `i_21.png` (iOS), `a_20.png`, `a_21.png` (Android)
- Profile images are cropped into a circle in the app, but when tapped, all four corners are displayed
- Design to fill the entire rectangular space

#### F. Chat Background Image (2 images, optional)

| Platform | Max Size (W x H) | Min Size | Filename |
|----------|-------------------|----------|----------|
| iOS | 1482 x 1334 | 60 x 60 | `i_22.png` |
| Android | 1300 x 1300 | 60 x 60 | `a_22.png` |

- Max file size: 1 MB per image
- Can be any size between the minimum and maximum values
- Both transparent and non-transparent images are supported
- If transparent, the image appears superimposed on the color skin
- iOS: positioned above message input field (640 x 1334 in portrait)
- Android: positioned below message input field (bottom overlaps with input box)

#### Technical Specs (Themes)

| Property | Requirement |
|----------|-------------|
| **Format** | PNG |
| **Color Skin** | Must select a color skin design after uploading images |
| **Background Color** | Configurable per theme to match chat background |

#### Color Skin Settings
- Select a color skin design after uploading theme images
- Download [image templates](https://vos.line-scdn.net/line-creators-market/documents/line_creators_theme_template_v2.psd.zip) (Adobe Photoshop PSD) to compare designs before creating images
- Set a background color for the chat screen that matches your images

#### Theme Review Guidelines
- Themes with poor visibility (icons that are corrupted, difficult to see, or blend with background) will be rejected
- Themes without good overall design balance (no unifying theme, icons with only text) will be rejected
- Images containing only text and no illustrations are not accepted
- Duplicate themes or simple color revisions of existing themes will be rejected

---

### LINE Metadata Generated (by StickerFramework)
```json
{
    "title": "Mochi Emotions Vol. 1",
    "author": "Your Brand Name",
    "description": "Cute chubby cat stickers for daily conversation",
    "copyright": "Your Brand Name",
    "sticker_count": 24,
    "format": "PNG",
    "images": {
        "main_image": "main.png (240x240)",
        "stickers": "01_what.png ... (up to 370x320 each)",
        "chat_thumbnail": "tab.png (96x74)"
    }
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
