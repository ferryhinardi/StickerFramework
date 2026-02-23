# LINE Creator Market Submission Template

> Default form values and step-by-step submission process for LINE sticker packs.

## Overview

The LINE Creator Market submission form has **4 tabs**:

```
┌─────────────────────┬─────────────────┬───────────────┬────────────┐
│ Display Information  │ Sticker Images  │ Tag Settings  │ Price Tier │
└─────────────────────┴─────────────────┴───────────────┴────────────┘
```

This document captures our standard default values for every field. When using the Playwright automation, these values are loaded from `templates/line_submission_defaults.json`.

---

## Tab 1: Display Information

### Sticker Details

| Field                   | Default Value             | Notes                                                           |
| ----------------------- | ------------------------- | --------------------------------------------------------------- |
| Sticker Type            | **Stickers**              | Static stickers (not Animated/Custom/Message/Big/Pop-up/Effect) |
| No. of Stickers per Set | **8**                     | LINE minimum. Set from Manage Stickers page after initial save  |
| Language                | **English**               | Primary language for title and description                      |
| Title                   | _[from ChatGPT ideation]_ | Max 40 characters. Example: "Boba & Milo Cheerful Otter Duo 5"  |
| Sticker Description     | _[from ChatGPT ideation]_ | Max 160 characters                                              |

### Additional Languages (Optional)

Adding extra languages increases discoverability in those regions:

| Language   | When to Add     | Notes                                       |
| ---------- | --------------- | ------------------------------------------- |
| Japanese   | High LINE usage | Translate title + description to Japanese   |
| Thai       | High LINE usage | Translate title + description to Thai       |
| Indonesian | Target market   | Translate title + description to Indonesian |

Each language requires a separate title (40 chars) and description (160 chars).

### Product Details

| Field                        | Default Value                           | Notes                                                             |
| ---------------------------- | --------------------------------------- | ----------------------------------------------------------------- |
| Creator's Name               | **Ferry Hinardi**                       | Locked after first submission. Max 50 characters                  |
| Copyright                    | **FHStudio**                            | Max 50 characters. Your brand/studio name                         |
| Use of AI                    | **AI was used**                         | Required disclosure for AI-generated art                          |
| Style Category               | **Cute**                                | Options: Cute, Cool, Natural, Pop, Weird, Other                   |
| Character Category           | _varies per pack_                       | Options: Characters, Animals, People, Families & Couples, Other   |
| Privacy Setting              | **Show in LINE STORE/Sticker Shop**     | Public visibility. Alt: "Do not show" (private)                   |
| LINE Stickers Premium        | **Join**                                | Earn from Premium subscribers. Eligibility date set after release |
| Sale Region                  | **Distribute in all available regions** | Global distribution. Alt: specific regions only                   |
| Sticker Arranging feature    | **Participate**                         | LINE can rearrange sticker display order                          |
| Sticker trial use promotions | **Participate**                         | Enable free trial promotions                                      |
| Sales settings               | **Start sales automatically**           | Auto-publish after approval. Alt: "Start sales manually"          |

### Character Category Guidelines

Choose based on your pack's characters:

| Characters in Pack         | Recommended Category |
| -------------------------- | -------------------- |
| Animals (single character) | Animals              |
| Animal couple/duo          | Families & Couples   |
| Human characters           | People               |
| Fantasy/abstract           | Characters           |
| Mixed human + animal       | Characters           |
| Office/workplace theme     | People or Characters |
| Religious characters       | Other                |

### License Certificate

| Field                              | Default Value               | Notes                            |
| ---------------------------------- | --------------------------- | -------------------------------- |
| Includes Photos                    | **Does not include photos** | AI-generated art is not photos   |
| License Certificate / Attach Files | _empty_                     | Only needed if using licensed IP |
| Preview URL Link                   | _empty_                     | Optional preview link            |
| Supplementary Notes                | _empty_                     | Optional notes for reviewer      |

---

## Tab 2: Sticker Images

### Upload Order

Upload images in this order:

| #   | Image Type            | Source File                | Dimensions |
| --- | --------------------- | -------------------------- | ---------- |
| 1   | Main Image            | `final/line_main/01_*.png` | 240 x 240  |
| 2   | Tab Image (Chat Icon) | `final/line_tab/01_*.png`  | 96 x 74    |
| 3   | Sticker 01            | `final/line/01_*.png`      | ≤370 x 320 |
| 4   | Sticker 02            | `final/line/02_*.png`      | ≤370 x 320 |
| 5   | Sticker 03            | `final/line/03_*.png`      | ≤370 x 320 |
| 6   | Sticker 04            | `final/line/04_*.png`      | ≤370 x 320 |
| 7   | Sticker 05            | `final/line/05_*.png`      | ≤370 x 320 |
| 8   | Sticker 06            | `final/line/06_*.png`      | ≤370 x 320 |
| 9   | Sticker 07            | `final/line/07_*.png`      | ≤370 x 320 |
| 10  | Sticker 08            | `final/line/08_*.png`      | ≤370 x 320 |

### Upload Methods

**Individual upload:**

- Click the upload zone for each image type
- Select the corresponding file from `final/` directory
- Wait for upload confirmation (thumbnail appears)

**ZIP upload (alternative):**

- Bundle all images into a ZIP file (see [LINE Specs](06-line-sticker-specifications.md#zip-upload-structure))
- Upload the single ZIP file
- LINE extracts and assigns images based on filenames

### Image Selection Tips

- **Main image**: Use the most recognizable/iconic sticker (usually the first one, or the "hello/greeting" sticker)
- **Tab icon**: Use the same sticker as main image (scaled down), or choose one with the simplest design for legibility at 96x74

---

## Tab 3: Tag Settings

### What Tags Are

Tags are emoji-based search labels that help users find your stickers when typing in chat. Each sticker can have 1-3 emoji tags.

### Tagging Strategy

Map each sticker's emotion to relevant LINE emoji categories:

| Sticker Emotion    | Recommended Tags           |
| ------------------ | -------------------------- |
| Hello / Greeting   | Waving hand, Smile         |
| Love / Heart       | Heart, Smiling with hearts |
| Thank you          | Folded hands, Smile        |
| Sorry              | Bowing, Crying face        |
| Good morning       | Sun, Yawning               |
| Good night         | Moon, Sleeping             |
| Angry              | Angry face, Pouting        |
| Sad                | Crying, Broken heart       |
| Excited / Fighting | Flexed bicep, Fire         |
| Eating             | Fork and knife, Yummy      |
| Bye bye            | Waving hand                |
| Laugh / LOL        | Laughing with tears        |
| Surprise           | Open mouth, Exclamation    |
| Celebrate          | Party popper, Confetti     |

### Automation Approach

The Playwright automation can auto-assign tags based on sticker `short_name` from the pack config:

1. Parse the sticker name (e.g., `01_good_morning`)
2. Look up emotion keywords → emoji mapping
3. Click the corresponding emoji tags in the Tag Settings UI

---

## Tab 4: Price Tier

### Available Tiers

| Tier       | Price (IDR) | Price (USD) | Price (JPY) |
| ---------- | ----------- | ----------- | ----------- |
| **Tier 1** | **+23,000** | ~$1.49      | ~120        |
| Tier 2     | +46,000     | ~$2.99      | ~250        |
| Tier 3     | +69,000     | ~$4.49      | ~370        |

### Recommended Default

**+23,000 IDR** (Tier 1, lowest price)

Rationale:

- Maximizes download volume at the lowest barrier
- LINE Premium subscribers get stickers for free (you earn per usage)
- Revenue comes from volume, not per-pack price
- Lower price = more likely to be featured by LINE

### Revenue Split

| Party                                 | Share   |
| ------------------------------------- | ------- |
| Creator                               | **35%** |
| LINE                                  | 30%     |
| Platform fees (App Store/Google Play) | 30%     |
| Payment processing                    | 5%      |

At Tier 1 (+23,000 IDR):

- Creator earns: ~8,050 IDR per sale (~$0.52)
- Monthly potential at 100 sales: ~805,000 IDR (~$52)

### Special Low-Cost Option

LINE offers a special reduced pricing option when ALL conditions are met:

- Sticker type: Stickers (static)
- Number of stickers per set: 8
- Sale region: **Indonesia only**

This may offer a lower price point for the Indonesian market.

---

## Submission Flow (Step by Step)

### 1. Create New Submission

1. Go to [LINE Creator Market](https://creator.line.me)
2. Navigate to **My Page** → **Stickers**
3. Click **New Submission**
4. Select **Stickers** as the type
5. Click **Save** (creates draft with default settings)

### 2. Fill Display Information

1. Enter **Title** and **Description** (from ChatGPT ideation)
2. Set **Use of AI** → "AI was used"
3. Set **Style Category** → Cute (or appropriate)
4. Set **Character Category** → (based on pack content)
5. Verify all other fields match defaults above
6. Click **Save**

### 3. Upload Sticker Images

1. Click **Sticker Images** tab
2. Upload **Main Image** (240x240)
3. Upload **Tab Image** (96x74)
4. Upload all **8 sticker images** (≤370x320)
5. Verify all thumbnails appear correctly
6. Click **Save**

### 4. Set Tags

1. Click **Tag Settings** tab
2. For each sticker, click the sticker thumbnail
3. Select 1-3 relevant emoji tags
4. Repeat for all 8 stickers
5. Click **Save**

### 5. Set Price

1. Click **Price Tier** tab
2. Select **+23,000 IDR**
3. Click **Save**

### 6. Submit for Review

1. Review all tabs — ensure no warnings or errors
2. Click **Preview** to verify how stickers will look
3. Click **Request** to submit for review
4. Confirm the submission dialog

---

## Post-Submission

### Review Timeline

| Status         | Description                         | Expected Duration     |
| -------------- | ----------------------------------- | --------------------- |
| Editing        | Draft, not yet submitted            | N/A                   |
| Pending Review | Submitted, in LINE's queue          | 1-7 business days     |
| Approved       | Passed review, live (if auto-sales) | Immediate             |
| Rejected       | Failed review, needs fixes          | Read rejection reason |

### Daily Submission Limit

- **30 submissions per day** (shown as "Requests Remaining Today: X/30")
- Rejections do NOT count against this limit
- Re-submissions after fixing rejections count as new submissions

### Checking Status

1. Go to [Sticker Management](https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/?status=all)
2. Filter by status if needed
3. Click on a pack to see details or rejection reason

### After Approval

- Store link: `https://line.me/S/sticker/<sticker-id>`
- Creator page: `https://line.me/S/shop/sticker/author/5964498`
- Share the store link on social media to drive sales
