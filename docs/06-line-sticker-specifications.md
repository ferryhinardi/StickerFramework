# LINE Sticker Specifications

> Official LINE Creators Market image and metadata requirements for static sticker packs.

This document covers requirements for **static stickers** (the most common type). For animated, custom, message, big, pop-up, and effect stickers, see the [full LINE spec reference](LINE_STICKER_PACK.md).

---

## Required Images

Every static sticker pack submission requires three types of images:

| Image Type     | Quantity             | Dimensions (WxH) | Format | Max Size  |
| -------------- | -------------------- | ---------------- | ------ | --------- |
| Main Image     | 1                    | 240 x 240        | PNG    | 1 MB      |
| Chat Tab Icon  | 1                    | 96 x 74          | PNG    | 1 MB      |
| Sticker Images | 8, 16, 24, 32, or 40 | Up to 370 x 320  | PNG    | 1 MB each |

### Total Files Per Pack

For a pack with **N** stickers: **N + 2** files total (N stickers + 1 main + 1 tab icon).

| Pack Size   | Sticker Images | + Main + Tab | Total Files |
| ----------- | -------------- | ------------ | ----------- |
| 8 stickers  | 8              | 2            | **10**      |
| 16 stickers | 16             | 2            | **18**      |
| 24 stickers | 24             | 2            | **26**      |
| 32 stickers | 32             | 2            | **34**      |
| 40 stickers | 40             | 2            | **42**      |

---

## Dimension Rules

### Sticker Images

- **Maximum width**: 370 px
- **Maximum height**: 320 px
- **Minimum**: 1 px on either dimension
- **Both width and height must be even numbers** (e.g., 370x320, 368x318, 350x300)
- Aspect ratio: wider than tall (370:320 ~ 1.16:1)

### Main Image

- **Exactly** 240 x 240 px (no variation)

### Chat Tab Icon

- **Exactly** 96 x 74 px (no variation)

---

## Technical Requirements

| Requirement   | Value                                      |
| ------------- | ------------------------------------------ |
| File format   | PNG only (`.png` extension)                |
| Color mode    | RGB                                        |
| Resolution    | >= 72 DPI                                  |
| Background    | Transparent (alpha channel required)       |
| Dimensions    | Both width and height must be even numbers |
| Max file size | 1 MB per image                             |
| Max ZIP size  | 60 MB (if uploading as ZIP)                |

### Margin / Padding

- Sticker content should have approximately **10 px of transparent padding** between the content edge and the image boundary
- This ensures the sticker doesn't look "cramped" in chat
- The `sticker_processor.py` handles this automatically by fitting content within 90% of the target dimensions

---

## Text Metadata Limits

| Field               | Max Length     | Required |
| ------------------- | -------------- | -------- |
| Creator Name        | 50 characters  | Yes      |
| Sticker Title       | 40 characters  | Yes      |
| Sticker Description | 160 characters | Yes      |
| Copyright           | 50 characters  | Yes      |

**Important:** Asian characters (CJK) and some special symbols count as **2 characters** each. For example, a Japanese title of 20 characters uses 40 of the 40-character limit.

---

## Content Guidelines

### Recommended

- Stickers that are easy to use in daily conversation
- Clear, instantly understandable expressions and emotions
- Variety across the pack (greetings, reactions, emotions, farewells)
- Good visibility — stickers should be legible even at small chat sizes

### Not Allowed

- Objects or scenery that are difficult to use in conversation context
- Poor visibility (too long/thin, too pale, too small)
- Lack of variety (too many similar expressions)
- Advertising content, corporate logos, product promotions
- Content that offends public order or morality
- Depictions of underage drinking, smoking, or substance use
- Sexual or excessively violent imagery
- Content that promotes nationalism or discrimination
- Content from other messaging apps or services
- Personal data collection or identification requirements

### AI Disclosure

LINE now requires creators to disclose AI usage:

- If AI was used to generate any part of the sticker artwork, select **"AI was used"**
- This is a required field in the submission form

---

## ZIP Upload Structure

When uploading all images as a ZIP file (alternative to individual uploads):

```
sticker_pack.zip
├── main.png          # 240 x 240 main image
├── tab.png           # 96 x 74 chat tab icon
├── 01.png            # Sticker 1
├── 02.png            # Sticker 2
├── 03.png            # Sticker 3
├── 04.png            # Sticker 4
├── 05.png            # Sticker 5
├── 06.png            # Sticker 6
├── 07.png            # Sticker 7
└── 08.png            # Sticker 8
```

- Total ZIP size must not exceed 60 MB
- File names inside ZIP should be simple (no spaces, no special characters)
- Number prefix determines sticker display order

---

## All Sticker Types (Quick Reference)

For completeness, LINE supports 7 sticker types:

| Type       | Counts        | Sticker Size        | Format   | Animated? |
| ---------- | ------------- | ------------------- | -------- | --------- |
| **Static** | 8/16/24/32/40 | ≤370x320            | PNG      | No        |
| Animated   | 8/16/24       | ≤320x270            | APNG     | Yes       |
| Custom     | 8/16/24/32/40 | ≤370x320            | PNG      | No        |
| Message    | 8/16/24       | ≤370x320            | PNG      | No        |
| Big        | 8/16/24/32/40 | 80-396 x 524-660    | PNG      | No        |
| Pop-up     | 8/16/24       | ≤370x320 + ≤480x480 | PNG+APNG | Partial   |
| Effect     | 8/16/24       | ≤370x320 + ≤480x480 | PNG+APNG | Partial   |

This project focuses on **Static** stickers. See [LINE_STICKER_PACK.md](LINE_STICKER_PACK.md) for detailed specs on all types.

---

## Pre-Submission Checklist

Verify all items before uploading to LINE Creator Market:

### Images

- [ ] Correct sticker count: exactly 8, 16, 24, 32, or 40 sticker images
- [ ] All sticker images: width ≤ 370, height ≤ 320, both even numbers
- [ ] Main image: exactly 240 x 240 px
- [ ] Tab icon: exactly 96 x 74 px
- [ ] All files are PNG format with `.png` extension
- [ ] All files have transparent background (alpha channel)
- [ ] Each file is under 1 MB
- [ ] ~10 px transparent margin around sticker content
- [ ] Stickers have clear visibility (not too pale or too thin)

### Metadata

- [ ] Title: ≤ 40 characters
- [ ] Description: ≤ 160 characters
- [ ] Copyright: ≤ 50 characters
- [ ] Creator name: ≤ 50 characters
- [ ] AI disclosure set correctly

### Content

- [ ] Each sticker expresses a distinct emotion or action
- [ ] No text violating LINE content guidelines
- [ ] No advertising or corporate logos
- [ ] No content from other messaging platforms
- [ ] Stickers are useful in everyday conversation

### Guideline 3.13 — Religious Content (CRITICAL)

LINE explicitly prohibits "images designed to solicit or spread religion, or with strong religious components." This applies to **all** elements of a submission: sticker images, main image, tab image, title, description, and tags.

**Run the automated pre-flight check before submitting:**
```bash
python scripts/line_preflight_check.py --pack-dir packs/<pack-name>
```

The following will trigger a 3.13 rejection:

#### Visual Elements — NOT ALLOWED
- [ ] No religious buildings (mosques, churches, temples, synagogues)
- [ ] No religious symbols (crescent moon in religious context, cross, Star of David, Om, etc.)
- [ ] No prayer gestures or religious poses (hands together in prayer, prostration, etc.)
- [ ] No religious clothing/accessories (prayer caps, prayer beads, prayer mats, rosaries, etc.)
- [ ] No religious furniture or objects (altars, pulpits, menorahs, etc.)

#### Text — NOT ALLOWED
- [ ] No religious greetings (Marhaban ya Ramadan, Merry Christmas in religious context, etc.)
- [ ] No religious phrases (Alhamdulillah, Hallelujah, Amen, etc.)
- [ ] No religious practice references (sahur, iftar/berbuka, tarawih, Lent, etc.)
- [ ] No religious holiday names (Ramadan, Eid, Easter, Diwali, Vesak, Hanukkah, etc.)
- [ ] No prayer or worship references (doa, pray, worship, etc.)

#### Metadata — NOT ALLOWED
- [ ] Pack title must not contain religious references
- [ ] Pack description must not contain religious references
- [ ] Tags/keywords must not contain religious terms

#### Submission Timing
- [ ] Do NOT submit religious and non-religious packs simultaneously from the same account
- [ ] Religious-themed packs flagged in one submission may cause concurrent submissions to be rejected

> **Note:** Packs with religious themes should use `pack_metadata.json` with `platforms.line.enabled: false` and distribute on other platforms only (Telegram, WhatsApp, iMessage, Stickerly, Etsy).

---

## Reference Links

- [Static Sticker Guidelines](https://creator.line.me/en/guideline/sticker/)
- [Animated Sticker Guidelines](https://creator.line.me/en/guideline/animationsticker/)
- [Custom Sticker Guidelines](https://creator.line.me/en/guideline/customsticker/)
- [Message Sticker Guidelines](https://creator.line.me/en/guideline/messagesticker/)
- [Big Sticker Guidelines](https://creator.line.me/en/guideline/bigsticker/)
- [Pop-up Sticker Guidelines](https://creator.line.me/en/guideline/popupsticker/)
- [Effect Sticker Guidelines](https://creator.line.me/en/guideline/effectsticker/)
- [Review Process Guidelines](https://creator.line.me/en/review_guideline/)
