# iMessage Sticker Pack Submission Guide

A practical end-to-end guide for submitting Cappy the Chill Capybara sticker
packs to the App Store via iMessage. This covers everything from Apple Developer
enrollment to final App Store review.

---

## TL;DR -- What I (OpenCode) Need From You

Once you have your Apple Developer account, come back and give me these
**4 values**. I will handle the rest (configure env, run the pipeline, submit).

| # | What | Where to find it | Example |
|---|------|-------------------|---------|
| 1 | **Apple ID email** | The email you enrolled with | `bobastickers.shop@gmail.com` |
| 2 | **Team ID** | developer.apple.com > Account > Membership Details | `A1B2C3D4E5` (10 chars) |
| 3 | **Bundle ID** | You choose it (I'll register it for you if needed) | `com.bobastickers.cappy2` |
| 4 | **Match Git URL** | A private GitHub repo you create for certificates | `git@github.com:ferryhinardi/fastlane-certs.git` |

Optional (needed if you have 2FA, which you should):

| # | What | Where to find it |
|---|------|-------------------|
| 5 | **App-specific password** | appleid.apple.com > Sign-In and Security > App-Specific Passwords |
| 6 | **Match passphrase** | You choose one (first time only, save it somewhere safe) |

That is literally it. Everything else -- Xcode project generation, icons,
screenshots, metadata, code signing, build, upload, submission -- is automated.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Apple Developer Program Enrollment](#2-apple-developer-program-enrollment)
3. [After Enrollment -- Step by Step](#3-after-enrollment----step-by-step)
4. [Credential Setup (Details)](#4-credential-setup-details)
5. [Environment Configuration](#5-environment-configuration)
6. [Code Signing with Fastlane Match](#6-code-signing-with-fastlane-match)
7. [Running the Pipeline](#7-running-the-pipeline)
8. [App Store Connect Manual Steps](#8-app-store-connect-manual-steps)
9. [Review Guidelines for Sticker Packs](#9-review-guidelines-for-sticker-packs)
10. [Troubleshooting](#10-troubleshooting)
11. [Per-Pack Checklist](#11-per-pack-checklist)

---

## 1. Prerequisites

### Software

| Tool | Install | Verify |
|------|---------|--------|
| macOS 13+ | Required | `sw_vers` |
| Xcode 15+ | Mac App Store | `xcodebuild -version` |
| Xcode CLI Tools | `xcode-select --install` | `xcode-select -p` |
| Fastlane | `brew install fastlane` | `fastlane --version` |
| xcodegen | `brew install xcodegen` | `xcodegen --version` |
| Python 3.10+ | Already installed | `python3 --version` |
| Pillow | `pip install Pillow` | `python3 -c "import PIL"` |

### Sticker Assets

Before starting, make sure your pack has processed iMessage stickers:

```
packs/<pack>/final/imessage_large/*.png   (618x618 px, transparent PNG)
```

If not, run the processor first:

```bash
python scripts/sticker_processor.py packs/<pack>/raw/ packs/<pack>/final/ \
  --pack-config packs/<pack>/pack_config.py
```

---

## 2. Apple Developer Program Enrollment

**Cost: $99 USD/year**

This is the single biggest blocker. Without an active Apple Developer Program
membership, you cannot submit apps to the App Store.

### Steps

1. Go to https://developer.apple.com/programs/enroll/
2. Sign in with your Apple ID (or create one)
3. Enroll as an **Individual** (simplest for indie sticker publishing)
   - You will need: legal name, address, phone number
   - For organizations: requires a D-U-N-S number (takes 1-2 weeks)
4. Pay the $99 annual fee
5. Wait for Apple to process (usually 24-48 hours, sometimes faster)

### What You Get

- **Team ID** (10-character alphanumeric, e.g., `A1B2C3D4E5`)
- Access to **App Store Connect** (https://appstoreconnect.apple.com)
- Ability to create **App IDs**, provisioning profiles, and certificates
- Access to **TestFlight** for beta testing

### Finding Your Team ID

After enrollment is complete:

1. Go to https://developer.apple.com/account
2. Click **Membership Details** (or look in the sidebar)
3. Your **Team ID** is listed there (10 characters)

---

## 3. After Enrollment -- Step by Step

You just paid $99 and Apple has activated your Developer account. Here is
exactly what to do next, in order. This should take about 15-20 minutes.

### Step 1: Confirm your Team ID

1. Go to https://developer.apple.com/account
2. In the sidebar (or under "Membership Details"), find **Team ID**
3. Copy it -- it looks like `A1B2C3D4E5` (10 characters)
4. Save it somewhere (you will give this to me)

### Step 2: Register your Bundle IDs

You need TWO App IDs for each sticker pack (one for the container app, one
for the sticker extension).

1. Go to https://developer.apple.com/account/resources/identifiers/list
2. Click the **+** button (top-left, blue circle)
3. Select **App IDs** > continue > select **App** > continue
4. Fill in:
   - **Description**: `Cappy Vol.2 Stickers`
   - **Bundle ID**: select **Explicit**, enter `com.bobastickers.cappy2`
   - Under Capabilities: no special capabilities needed
5. Click **Continue** > **Register**
6. **Repeat** for the extension:
   - **Description**: `Cappy Vol.2 Sticker Extension`
   - **Bundle ID**: `com.bobastickers.cappy2.StickerPackExtension`

### Step 3: Create a private Git repo for certificates

Fastlane Match stores signing certificates in a private repo.

1. Go to https://github.com/new
2. **Repository name**: `fastlane-certs`
3. **Visibility**: **Private** (critical -- this will hold signing certs)
4. Leave everything else default, click **Create repository**
5. Copy the repo URL: `https://github.com/ferryhinardi/fastlane-certs.git`

### Step 4: Generate an App-Specific Password (for 2FA)

If your Apple ID has two-factor authentication (it should):

1. Go to https://appleid.apple.com
2. Sign in > **Sign-In and Security** > **App-Specific Passwords**
3. Click **Generate** or the **+** button
4. Label: `Fastlane`
5. Copy the generated password (format: `xxxx-xxxx-xxxx-xxxx`)
6. Save it securely

### Step 5: Come back and give me these values

| # | What | What you just got |
|---|------|-------------------|
| 1 | **Apple ID email** | The email you used to enroll |
| 2 | **Team ID** | From Step 1 above |
| 3 | **Bundle ID** | `com.bobastickers.cappy2` (or whatever you chose) |
| 4 | **Match Git URL** | `https://github.com/<you>/fastlane-certs.git` |
| 5 | **App-specific password** | From Step 4 above |
| 6 | **Match passphrase** | Choose any strong password (I will use it to encrypt certs) |

Paste these into the chat and I will configure the environment, run the
pipeline, and submit to the App Store.

### What happens after you give me the values

1. I set the env vars in `.env`
2. I run `fastlane match appstore` to create signing certificates
3. I run `imessage_publisher.py` with `--skip-submit` first (dry check)
4. You verify metadata/screenshots in App Store Connect
5. I run the full publish to submit for Apple's review
6. Apple reviews (24-48h typical, up to 7 days for first submission)
7. Once approved, the sticker pack goes live on the App Store

---

## 4. Credential Setup (Details)

You need four pieces of information. Here is where to find each:

### APPLE_ID

Your Apple ID email address (the one you enrolled with).

```
Example: bobastickers.shop@gmail.com
```

### APPLE_TEAM_ID

The 10-character Team ID from your Apple Developer membership page.

```
Example: A1B2C3D4E5
```

### BUNDLE_ID

A reverse-DNS identifier for your app. You choose this, but it must be unique
across the entire App Store.

**Recommended convention:**

```
com.bobastickers.cappy              (Vol.1)
com.bobastickers.cappy2             (Vol.2)
com.bobastickers.cappy3             (Vol.3)
```

You must register this Bundle ID in Apple Developer portal:

1. Go to https://developer.apple.com/account/resources/identifiers/list
2. Click the **+** button
3. Select **App IDs** > **App**
4. Enter a description (e.g., "Cappy Vol.2 Stickers")
5. Set Bundle ID to **Explicit** and enter your chosen ID
6. Under **Capabilities**, ensure **iMessage** (or Sticker Packs) is not needed
   as a separate entitlement -- iMessage sticker packs work automatically
7. Click **Continue** > **Register**

**Important:** You also need a second App ID for the StickerPackExtension:

```
com.bobastickers.cappy2.StickerPackExtension
```

Register this the same way (the Matchfile handles both automatically).

### MATCH_GIT_URL

Fastlane Match stores your code signing certificates and provisioning profiles
in a **private Git repo**. You need to create one:

1. Create a **private** GitHub repo (e.g., `ferryhinardi/fastlane-certs`)
2. The URL will be: `https://github.com/ferryhinardi/fastlane-certs.git`
   - Or SSH: `git@github.com:ferryhinardi/fastlane-certs.git`
3. Match will automatically populate this repo when you first run `fastlane certs`

**Security:** This repo contains your signing certificates. Keep it private and
never make it public.

---

## 5. Environment Configuration

### Option A: .env file (recommended)

Create or update `.env` in the repo root:

```bash
# Apple Developer credentials for iMessage submission
APPLE_ID=bobastickers.shop@gmail.com
APPLE_TEAM_ID=A1B2C3D4E5
BUNDLE_ID=com.bobastickers.cappy2
MATCH_GIT_URL=https://github.com/ferryhinardi/fastlane-certs.git
```

Then source it before running:

```bash
export $(grep -v '^#' .env | xargs)
```

### Option B: Shell exports

```bash
export APPLE_ID="bobastickers.shop@gmail.com"
export APPLE_TEAM_ID="A1B2C3D4E5"
export BUNDLE_ID="com.bobastickers.cappy2"
export MATCH_GIT_URL="https://github.com/ferryhinardi/fastlane-certs.git"
```

### Verify Environment

```bash
echo "APPLE_ID=$APPLE_ID"
echo "APPLE_TEAM_ID=$APPLE_TEAM_ID"
echo "BUNDLE_ID=$BUNDLE_ID"
echo "MATCH_GIT_URL=$MATCH_GIT_URL"
```

All four must be non-empty before proceeding.

---

## 6. Code Signing with Fastlane Match

Match manages your certificates and provisioning profiles automatically using
a private Git repo as storage.

### First-Time Setup

The very first time, Match needs to create certificates:

```bash
# This creates App Store distribution cert + provisioning profiles
# and stores them in your MATCH_GIT_URL repo
fastlane match appstore
```

Match will prompt for:
- **Passphrase**: Choose a strong password to encrypt the certificates in Git.
  You will need this passphrase on every new machine. Store it securely.
- **Apple ID password** / **App-specific password**: If you have 2FA enabled
  (you should), generate an app-specific password at https://appleid.apple.com
  under Security > App-Specific Passwords.

### Subsequent Runs

After initial setup, the `certs` lane uses `readonly: true` to just fetch
existing certs without creating new ones:

```bash
fastlane certs
```

### App-Specific Password for CI / Automation

If you have two-factor authentication on your Apple ID (recommended):

1. Go to https://appleid.apple.com
2. Sign in > Security > App-Specific Passwords
3. Generate a password (label it "Fastlane")
4. Set it as an environment variable:

```bash
export FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
```

---

## 7. Running the Pipeline

### Step-by-Step Automated Pipeline

Our `imessage_publisher.py` script handles 6 steps automatically:

```
Step 1/6  Generate Xcode project structure (sticker assets + Info.plist)
Step 2/6  Generate .xcodeproj via xcodegen from template
Step 3/6  Generate all 9 required app icon sizes
Step 4/6  Populate Fastlane metadata from pack config
Step 5/6  Generate App Store screenshots (3 device sizes)
Step 6/6  Run Fastlane (match certs -> gym build -> deliver upload -> submit)
```

### Dry Run First (Recommended)

Always do a dry run to verify everything before the real submission:

```bash
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py \
  --dry-run
```

This generates the Xcode project, icons, metadata, and screenshots without
invoking Fastlane. Check the output in:

```
packs/cappy-capybara-2/imessage_build/
fastlane/metadata/en-US/
fastlane/screenshots/en-US/
```

### Upload Without Submitting for Review

Good for verifying everything looks right in App Store Connect before
submitting for Apple's review:

```bash
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py \
  --skip-submit
```

Then log into App Store Connect to verify metadata, screenshots, and binary
before manually submitting for review.

### Full Publish (Build + Upload + Submit for Review)

```bash
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py
```

### Custom Icon

By default, the first sticker in the pack is used as the app icon. To use a
custom icon:

```bash
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py \
  --icon path/to/custom_icon.png
```

---

## 8. App Store Connect Manual Steps

Some things are best verified manually in App Store Connect before your
first submission.

### First-Time App Creation

If the automated pipeline did not create the app record in App Store Connect,
do it manually:

1. Go to https://appstoreconnect.apple.com/apps
2. Click **+** > **New App**
3. Fill in:
   - **Platform**: iOS
   - **Name**: "Cappy The Chill Capybara Vol.2 Stickers"
   - **Primary Language**: English (U.S.)
   - **Bundle ID**: Select `com.bobastickers.cappy2`
   - **SKU**: `cappy-capybara-vol2` (any unique string)
4. Click **Create**

### Required Fields to Verify

Before submission, check these in App Store Connect:

| Field | Value |
|-------|-------|
| **Name** | Cappy The Chill Capybara Vol.2 Stickers |
| **Subtitle** | Cute sticker pack for iMessage |
| **Category** | Stickers |
| **Price** | Free (tier 0) -- standard for sticker packs |
| **Privacy Policy URL** | Required -- even for sticker packs |
| **Support URL** | Required |
| **Age Rating** | Fill out questionnaire (all "None" for stickers) |
| **Copyright** | FHStudio |

### Privacy Policy

Apple requires a privacy policy URL even for simple sticker packs. Options:

1. **Host a simple page** on your domain
2. **Use GitHub Pages**: Create a `privacy.md` in a public repo
3. **Free generators**: Sites like privacypolicygenerator.info

The policy can be minimal since sticker packs collect no data:

> "This app does not collect, store, or transmit any personal data.
> The app is a sticker pack for iMessage and has no server-side component."

Update the URLs in `templates/imessage_metadata.json` once you have them:

```json
{
  "privacy_url": "https://bobastickers.github.io/privacy",
  "support_url": "https://bobastickers.github.io/support"
}
```

### Screenshots

The pipeline generates screenshots automatically (gradient background with
sticker grid). If you want custom screenshots:

1. Place them in `fastlane/screenshots/en-US/`
2. Follow the naming convention:
   - `iPhone_6.7_01.png` (1290x2796)
   - `iPhone_6.5_01.png` (1284x2778)
   - `iPad_12.9_01.png` (2048x2732)
3. You can add multiple screenshots: `_01.png`, `_02.png`, etc.

---

## 9. Review Guidelines for Sticker Packs

Apple reviews sticker packs. Common rejection reasons and how to avoid them:

### Content Rules

- No violence, hate speech, or sexually explicit content
- No copyrighted characters (no Mickey Mouse, no Pokemon, etc.)
- No real people without permission
- Must be "clearly different" from existing sticker packs on the store
- **AI-generated content**: Apple currently allows AI-generated art but may
  require disclosure. Be transparent in your description if asked.

### Technical Requirements

- **Sticker sizes**: Small (100x100), Medium (136x136), or Large (206x206)
  at 3x resolution. Our pipeline uses Large (618x618 at 3x = 206x206 pt).
- **Format**: PNG with transparency
- **File size**: Each sticker must be under 500 KB
- **Animated stickers**: APNG format, under 500 KB, max 16 frames
- **Pack size**: Minimum 3 stickers, recommended 16-40

### Metadata Requirements

- **App Name**: Max 30 characters
- **Subtitle**: Max 30 characters
- **Keywords**: Max 100 characters total, comma-separated
- **Description**: 10-4000 characters
- **What's New**: Required for updates

### Common Rejection Reasons

1. **Missing privacy policy URL** -- Even sticker packs need one
2. **Misleading screenshots** -- Screenshots must represent actual content
3. **Insufficient content** -- At least 3 unique stickers
4. **App name too similar** to existing apps
5. **Broken or placeholder URLs** in metadata

### Review Timeline

- Typical review: 24-48 hours
- First submission may take longer (up to 7 days)
- Rejections come with specific feedback -- fix and resubmit

---

## 10. Troubleshooting

### "No matching provisioning profiles found"

```bash
# Nuke and recreate certificates
fastlane match nuke appstore
fastlane match appstore
```

### "xcodegen not found"

```bash
brew install xcodegen
```

### "Code signing error" during build

1. Verify BUNDLE_ID matches what you registered in Apple Developer portal
2. Verify both App IDs exist:
   - `com.bobastickers.cappy2`
   - `com.bobastickers.cappy2.StickerPackExtension`
3. Re-run `fastlane match appstore` to regenerate profiles

### "APPLE_TEAM_ID environment variable not set"

```bash
export APPLE_TEAM_ID="YOUR_TEAM_ID"
# or source your .env
```

### "Deliver: App not found in App Store Connect"

Create the app manually in App Store Connect first (see Section 8), then
re-run the upload.

### Screenshots rejected

- Ensure exact pixel dimensions match required sizes
- No alpha/transparency in screenshots (PNG must be RGB, not RGBA)
- No device frames required for sticker pack screenshots

### "This bundle is invalid" error

- Check that the deployment target in `templates/imessage_project.yml`
  matches or is below the minimum supported iOS version
- Current setting: iOS 16.0

---

## 11. Per-Pack Checklist

Use this checklist for each pack you submit:

```
Pre-submission:
[ ] Apple Developer Program membership active
[ ] All 4 env vars set (APPLE_ID, APPLE_TEAM_ID, BUNDLE_ID, MATCH_GIT_URL)
[ ] App ID registered in Apple Developer portal (main + StickerPackExtension)
[ ] Stickers processed to final/imessage_large/ (618x618 PNG)
[ ] Dry run completed successfully
[ ] Privacy policy URL live and accessible
[ ] Support URL live and accessible

Build & Upload:
[ ] Ran imessage_publisher.py with --skip-submit first
[ ] Verified app record exists in App Store Connect
[ ] Verified metadata in App Store Connect (name, description, keywords)
[ ] Verified screenshots look correct
[ ] Verified app icon renders correctly
[ ] Filled out age rating questionnaire (all "None")
[ ] Set copyright to "FHStudio"

Submission:
[ ] Ran full publish (or manually clicked Submit for Review)
[ ] Received confirmation email from Apple

Post-submission:
[ ] Monitor App Store Connect for review status
[ ] If rejected, read feedback and fix issues
[ ] Update pack_metadata.json status to "submitted" / "approved" / "live"
```

---

## Quick Reference: Commands

```bash
# Dry run (verify everything, no submission)
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py --dry-run

# Upload only (build + upload, no review submission)
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py --skip-submit

# Full pipeline (build + upload + submit for review)
python scripts/imessage_publisher.py packs/cappy-capybara-2 \
  --pack-config packs/cappy-capybara-2/pack_config.py

# Sync certificates only
fastlane certs

# Manual Fastlane lanes
fastlane build project:packs/cappy-capybara-2/imessage_build/CappyTheChillCapybaraVol.2/CappyTheChillCapybaraVol.2.xcodeproj
fastlane upload
fastlane submit
```

---

## Cost Summary

| Item | Cost | Frequency |
|------|------|-----------|
| Apple Developer Program | $99 | Annual |
| App Store listing | Free | Per app |
| Sticker pack price to users | Free (recommended) | -- |

Total upfront cost: **$99** for the first year. This covers unlimited app
submissions across all your sticker packs.

---

## Files Referenced

| File | Purpose |
|------|---------|
| `scripts/imessage_publisher.py` | Main automation script (667 lines) |
| `fastlane/Appfile` | Apple credentials config |
| `fastlane/Fastfile` | Build/upload/submit lanes |
| `fastlane/Matchfile` | Code signing config |
| `templates/imessage_project.yml` | Xcode project template |
| `templates/imessage_metadata.json` | App Store metadata template |
| `fastlane/metadata/en-US/*.txt` | Generated metadata files |
| `fastlane/screenshots/en-US/*.png` | Generated screenshots |
