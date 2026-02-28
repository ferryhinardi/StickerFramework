# Sticker.ly Upload Guide

Complete step-by-step guide for publishing sticker packs on Sticker.ly for WhatsApp.

> **Important**: Sticker.ly has **NO API** and **NO creator monetization**. All uploads must be done manually through the mobile app. Use Sticker.ly as a **free marketing funnel** to drive users to your paid platforms (Etsy, Gumroad, iMessage, LINE).

---

## Pre-requisites

1. **Install Sticker.ly** from [App Store](https://apps.apple.com/app/sticker-ly/id1448282073) or [Google Play](https://play.google.com/store/apps/details?id=com.snowcorp.stickerly.android)
2. **Create an account** using your brand email
3. **Prepare your sticker files**: 512x512 WebP, transparent background, <100KB each
4. **Transfer files to your phone**:
   - **Mac to iPhone**: Use AirDrop (fastest)
   - **Any to Android**: Use Google Drive, email, or USB cable
   - **Any to iPhone**: Use Files app with iCloud Drive

---

## File Requirements

| Requirement | Specification |
|---|---|
| **Format** | WebP (PNG also accepted, auto-converted) |
| **Dimensions** | 512 x 512 pixels |
| **Max file size** | 100 KB per sticker |
| **Background** | Transparent |
| **Min per pack** | 3 stickers |
| **Max per pack** | 30 stickers |
| **Tray icon** | 96 x 96 pixels |

Your pipeline already produces these files in `<pack_id>/final/whatsapp/`.

---

## Transfer Files to Phone (Mac to iPhone via AirDrop)

1. Open Finder on your Mac
2. Navigate to `<pack_id>/final/whatsapp/`
3. Select all `.webp` files + `tray_icon.webp`
4. Right-click → Share → AirDrop → Select your iPhone
5. On iPhone, accept the transfer → files save to the Files app

**Alternative**: Email yourself a ZIP of the files and unzip on your phone.

---

## Step-by-Step Upload Process

### Step 1: Open Sticker.ly
- Open the app and sign in to your account

### Step 2: Start Creating
- Tap the **"+" button** at the bottom center of the screen
- Select **"WhatsApp Stickers"** as the sticker type

### Step 3: Add Stickers
- Tap **"Add Sticker"** (or the "+" icon in the pack editor)
- Navigate to your transferred files in the photo library or Files app
- Select a sticker image
- The editor will show your image — crop/adjust if needed (your images are already correctly sized, so just confirm)
- Tap **"Done"** or **"Save"**
- **Repeat for each sticker** (3-30 stickers per pack)

### Step 4: Set Tray Icon
- Tap the **tray icon area** (small square at the top/side of the pack)
- Select your 96x96 tray icon image
- This appears as the pack thumbnail in WhatsApp

### Step 5: Fill Pack Details
- **Pack Name**: `Mochi Emotions Vol. 1` (or your character name + theme)
- **Author/Creator Name**: Your brand name
- **Tags** (add as many as possible for discoverability):
  ```
  kawaii, cute, cat, mochi, emotions, stickers, anime, chibi,
  happy, sad, love, funny, reaction, daily, whatsapp stickers,
  cute cat, kawaii cat, emoji, expression
  ```

### Step 6: Add a Promo Sticker (Marketing Funnel)
- Create one sticker that subtly promotes your paid platforms:
  - Example: Your character holding a small sign or next to text saying:
    - "More packs at etsy.com/shop/YourShop"
    - "Premium packs: gumroad.com/yourbrand"
  - Keep it tasteful — overly promotional stickers may get reported
- Add this as one of the stickers in the pack

### Step 7: Publish
- Tap **"Publish"** or **"Save and Publish"**
- Your pack enters a brief review (usually **under 24 hours**)
- You'll receive a notification when approved

### Step 8: Share Your Pack
- Once approved, you get a shareable link: `https://sticker.ly/s/XXXXXX`
- Share this link on:
  - Your social media (Instagram, Twitter, TikTok)
  - WhatsApp status and groups
  - Reddit (r/stickers, r/whatsapp, r/kawaii)
  - Your Etsy/Gumroad product descriptions

---

## Tips for Going Viral on Sticker.ly

1. **Trending tags**: Check what tags popular packs use and include them
2. **Pack series**: Upload multiple packs (Emotions, Daily Life, Food) to build your profile
3. **Seasonal packs**: Holiday-themed packs get extra visibility during events
4. **Cross-promote**: Link your Sticker.ly packs from your other social media
5. **Engage**: Follow other creators, like their packs, build community
6. **Quality over quantity**: Ensure every sticker is clean and expressive
7. **Consistent character**: Using the same recognizable character across packs builds a following

---

## Automated Upload via Android Emulator

While Sticker.ly has no API, we've built a full automation pipeline using an
Android emulator + uiautomator2 to drive the Sticker.ly app programmatically.

### Prerequisites

```bash
# Install Python dependency
pip install uiautomator2

# Verify Android SDK and emulator are set up
adb version
emulator -list-avds   # Should show Medium_Phone_API_36.1
```

### First-Time Setup (Interactive Login)

```bash
# Start emulator with GUI, log in to Google, save snapshot
python3 scripts/stickerly_uploader.py --setup-only --headful
```

This will:
1. Launch the emulator with a visible window
2. Prompt you to install Sticker.ly from Play Store (if needed)
3. Prompt you to log in via Google
4. Save an AVD snapshot so future runs skip login

### Single Pack Upload

```bash
# Headless upload (after first-time setup)
python3 scripts/stickerly_uploader.py \
    --pack-dir packs/chubby-mochi-panda/final/whatsapp

# Dry run (skip final publish tap)
python3 scripts/stickerly_uploader.py \
    --pack-dir packs/chubby-mochi-panda/final/whatsapp --dry-run
```

### Batch Upload (All Packs)

```bash
# Upload all packs with final/whatsapp/ directories
python3 scripts/stickerly_uploader.py --batch

# Batch dry run
python3 scripts/stickerly_uploader.py --batch --dry-run
```

### Resume Interrupted Upload

```bash
python3 scripts/stickerly_uploader.py --resume
```

Progress is saved after each step to `~/.stickerly-automation/progress.json`.

### CLI Options

| Flag | Description |
|------|-------------|
| `--pack-dir` | Path to pack's `final/whatsapp/` directory |
| `--pack-config` | Path to `pack_config.py` (auto-detected) |
| `--batch` | Upload all packs with WhatsApp stickers |
| `--headful` | Show emulator GUI (required first time) |
| `--dry-run` | Skip the final publish step |
| `--resume` | Resume from saved progress |
| `--setup-only` | Only log in, don't upload |
| `--no-stop` | Keep emulator running after upload |

### How It Works

The automation uses a 4-step pipeline per pack:

1. **Push files** — ADB pushes WEBP stickers to emulator storage
2. **Create pack** — Taps Create, selects WhatsApp Stickers, adds each sticker via file picker
3. **Set metadata** — Fills pack name, author, tags
4. **Publish** — Taps Publish, captures share link

### Troubleshooting

| Issue | Solution |
|---|---|
| Session expired | Run with `--headful` to log in again |
| Selector not found | Sticker.ly UI may have changed; inspect with `uiautomator2 weditor` |
| Emulator won't start | Check `emulator -list-avds` and `adb devices` |
| Screenshots | Saved to `automation/stickerly/screenshots/` on any failure |

### Updating UI Selectors

If Sticker.ly updates their app UI, selectors in
`automation/stickerly/config.py` may need updating. To inspect the current UI:

```bash
# Start emulator and open Sticker.ly
python3 -c "
from automation.stickerly.emulator import EmulatorManager
em = EmulatorManager(); em.start(headless=False)
"

# In another terminal, dump UI hierarchy
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml
```

---

## Manual Upload (Fallback)

If automation is not set up, you can still upload manually:

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Images not showing in camera roll | Use Files app instead; or save WebP files as PNG first |
| Pack rejected | Check for copyrighted content, offensive material, or excessive branding |
| Images look blurry | Ensure source is exactly 512x512, not upscaled from smaller |
| File too large | Re-run pipeline with lower WebP quality; check size is <100KB |
| Can't add to WhatsApp | Make sure WhatsApp is installed and updated; restart phone |
