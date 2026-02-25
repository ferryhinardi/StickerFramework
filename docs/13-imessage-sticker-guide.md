# iMessage Sticker Pack Guide — Publishing to the App Store

A top-level reference for building and publishing iMessage sticker packs through StickerFramework. This guide connects the dots between the automated toolchain, Apple's requirements, and the detailed step-by-step submission process.

## Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Toolchain Reference](#toolchain-reference)
- [Current Status — Cappy Vol.3](#current-status--cappy-vol3)
- [What's Blocking](#whats-blocking)
- [After Enrollment — Next Steps](#after-enrollment--next-steps)
- [Related Documentation](#related-documentation)

---

## Overview

iMessage sticker packs are distributed through the Apple App Store as lightweight "Sticker Pack Applications" — Xcode projects that contain only sticker assets and metadata (no Swift/Obj-C code). StickerFramework fully automates the entire pipeline from processed PNG assets to App Store submission.

**Publisher:** BobaStickers
**Copyright:** FHStudio
**Pricing:** $0.99 per pack (Apple takes 30%, developer keeps 70%)

---

## How It Works

```
pack_config.py --> sticker_processor.py --> prepare_imessage_pack.py --> imessage_publisher.py
                                                 |                            |
                                       Xcode project structure        Fastlane automation
                                       (icons, stickers, plist)       (sign -> build -> upload -> submit)
```

1. **Process** — `sticker_processor.py` generates 618x618 transparent PNGs in `final/imessage_large/`
2. **Prepare** — `prepare_imessage_pack.py` creates the full Xcode project structure (`.xcodeproj`, `.xcstickers`, `Info.plist`, app icons)
3. **Publish** — `imessage_publisher.py` runs a 6-step pipeline: generate icons, create xcodegen spec, generate Xcode project, Fastlane match (code signing), build, upload to App Store Connect

---

## Prerequisites

### Software (all installed locally)

| Tool | Version | Status |
|------|---------|--------|
| macOS | 13+ | Installed |
| Xcode | 16.2 | Installed |
| xcodegen | 2.44.1 | Installed |
| Fastlane | 2.232.1 | Installed |
| Python | 3.10+ | Installed |
| Pillow | Latest | Installed |

### Apple Developer Account (NOT YET ENROLLED)

| Requirement | Status |
|-------------|--------|
| Apple Developer Program ($99/year) | **Needed** |
| Apple Team ID | Pending enrollment |
| App-Specific Password (2FA) | Pending enrollment |
| Private Git repo for certificates | Pending setup |
| Bundle ID registration | Pending enrollment |

---

## Quick Start

Once the Apple Developer account is active and credentials are configured:

```bash
# Dry run — generates Xcode project without submitting
python scripts/imessage_publisher.py packs/cappy-capybara-3 --dry-run

# Full pipeline — build and submit to App Store
python scripts/imessage_publisher.py packs/cappy-capybara-3
```

For the complete step-by-step walkthrough, see the [iMessage Submission Guide](guides/imessage_submission_guide.md).

---

## Toolchain Reference

| File | Purpose |
|------|---------|
| `scripts/prepare_imessage_pack.py` | Generates Xcode project structure (stickers, icons, plist) |
| `scripts/imessage_publisher.py` | Full 6-step automation pipeline (icons, xcodegen, build, submit) |
| `templates/imessage_project.yml` | xcodegen project spec template |
| `templates/imessage_metadata.json` | App Store metadata template |
| `fastlane/Appfile` | Apple ID and app identifier config |
| `fastlane/Matchfile` | Code signing repository and type |
| `fastlane/Fastfile` | Build, upload, and release lane definitions |
| `fastlane/Gemfile` | Ruby dependencies for Fastlane |
| `fastlane/metadata/en-US/` | Generated App Store metadata (name, subtitle, description, keywords) |
| `fastlane/screenshots/en-US/` | Generated App Store screenshots (3 device sizes) |

### Fastlane Lanes

```bash
bundle exec fastlane match appstore    # Fetch/create signing certificates
bundle exec fastlane build             # Build .ipa
bundle exec fastlane upload            # Upload to App Store Connect
bundle exec fastlane release           # Full pipeline: match -> build -> upload
```

---

## Current Status — Cappy Vol.3

| Item | Status |
|------|--------|
| Sticker assets processed (618x618 PNG) | 16/16 done |
| Assets location | `packs/cappy-capybara-3/final/imessage_large/` |
| Xcode project structure generator | Built and tested |
| Fastlane configuration | Configured (needs credentials) |
| App Store metadata templates | Generated |
| App Store screenshots | Generated (3 device sizes) |
| Apple Developer enrollment | **Not started** |
| `.env` Apple credentials | **Not configured** |

---

## What's Blocking

**One thing:** Apple Developer Program enrollment ($99/year).

After enrollment, you need to provide 4 values (the automation handles everything else):

| # | What | Where to find it |
|---|------|------------------|
| 1 | **Apple ID email** | The email you enrolled with |
| 2 | **Team ID** | developer.apple.com > Membership Details |
| 3 | **Bundle ID** | You choose (e.g., `com.bobastickers.cappy3`) |
| 4 | **Match Git URL** | A private GitHub repo for certificates |

Optional (recommended with 2FA):

| # | What | Where to find it |
|---|------|------------------|
| 5 | **App-specific password** | appleid.apple.com > App-Specific Passwords |
| 6 | **Match passphrase** | You choose one (save it somewhere safe) |

---

## After Enrollment — Next Steps

1. **Enroll** at [developer.apple.com/programs](https://developer.apple.com/programs/) ($99/year)
2. **Provide the 4 values** listed above — OpenCode will configure `.env` and all Fastlane files
3. **Run dry-run** to verify the Xcode project generates correctly
4. **Run full pipeline** to submit to App Store Connect
5. **Wait for review** (typically 24-48 hours for sticker packs)

The detailed walkthrough for each step is in the [iMessage Submission Guide](guides/imessage_submission_guide.md), sections 2-8.

---

## Related Documentation

| Document | What it covers |
|----------|---------------|
| [iMessage Submission Guide](guides/imessage_submission_guide.md) | Complete step-by-step: enrollment, credentials, code signing, pipeline, troubleshooting, per-pack checklist |
| [Platform Specs — iMessage section](platform-specs.md#imessage-apple-app-store) | Technical specs (image sizes, icon sizes, Xcode structure, Fastlane config, monetization) |
| [Implementation Plan — Phase 1](implementation-plan-phases.md) | Phase 1: iMessage Full Automation (prerequisites, new files, dependencies, verification, risks) |
