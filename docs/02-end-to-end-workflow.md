# End-to-End Workflow

> Complete step-by-step guide from sticker pack idea to published LINE sticker.

## Overview

```
 IDEATION        GENERATION       SPLIT           PROCESS         UPLOAD          REVIEW
 ─────────       ──────────       ─────           ───────         ──────          ──────
 ChatGPT Go   →  DALL-E sheet  →  split_       →  sticker_     →  Playwright  →  LINE
 (GPT-5.2)       composite       stickers.py     processor.py    automation      review
                  (2x4 grid)     (8x 512px)      (LINE specs)    (auto-fill)    (1-7 days)
                                                                                    │
 ~5 min          ~2 min          ~10 sec         ~30 sec         ~2 min          wait
                                                                                    ▼
                                                                              PUBLISHED
```

**Total active time: ~10 minutes per pack.** The rest is waiting for LINE review.

---

## Step 1: Ideation (ChatGPT Go)

**Goal:** Generate a sticker pack concept with title, description, and 8 sticker prompts.

**Subscription:** ChatGPT Go plan ($5/month) — uses GPT-5.2 Instant with expanded DALL-E access.

### What You Do

1. Open ChatGPT (Go plan — GPT-5.2 Instant with DALL-E)
2. Paste the ideation prompt from [ChatGPT Prompt Templates](03-chatgpt-prompt-templates.md)
3. Specify your theme (e.g., "two cute otters as a couple", "office sloth", "angel blessings")
4. ChatGPT returns structured output

### What You Get

| Output             | LINE Constraint                        | Example                                                                      |
| ------------------ | -------------------------------------- | ---------------------------------------------------------------------------- |
| Pack title         | Max 40 characters                      | "Boba & Milo Cheerful Otter Duo"                                             |
| Description        | Max 160 characters                     | "A fun, caring otter duo bringing cheerful energy to couples and coworkers." |
| Style category     | LINE category                          | Cute                                                                         |
| Character category | LINE category                          | Families & Couples                                                           |
| 8 sticker concepts | Each with emotion + visual description | "Good Morning -- Two otters stretching and yawning together"                 |

### Tips

- Ask for exactly **8 stickers** (LINE minimum, fastest to produce)
- Request output in a **numbered list format** for easy reference
- Iterate: ask ChatGPT to replace weak stickers (ones that would be hard to use in chat)
- For sequel packs (e.g., "Boba & Milo 5"), reference the previous pack's emotions to avoid duplicates

### ChatGPT Go Plan Limits

The Go plan ($5/month) provides expanded DALL-E access but not unlimited. Practical limits:

- Comfortably generate **2-5 packs per day** (ideation + DALL-E sheet each)
- If you hit the daily limit, wait until the next day or spread pack creation across days
- Response times are not prioritized — during peak hours, expect slower generations
- For higher volume (10+ packs/day), consider upgrading to Plus ($20/month)

### Example Conversation

```
You: I want to create a LINE sticker pack featuring two cute otters
     as a couple. 8 stickers, kawaii style. Give me title, description,
     and sticker concepts.

ChatGPT: **Pack Title**: Boba & Milo Cheerful Otter Duo
         **Description**: A fun, caring otter duo bringing cheerful
         energy to couples and coworkers. Perfect for daily chats.
         **Style**: Cute
         **Category**: Families & Couples

         1. Good Morning -- Both otters stretching with sleepy eyes
         2. Love You -- Otters forming a heart shape with their tails
         3. Let's Eat! -- Otters sharing a bowl of ramen
         ...
```

---

## Step 2: DALL-E Composite Sheet Generation

**Goal:** Generate a single image containing all 8 stickers arranged in a grid.

### What You Do

1. In the **same ChatGPT conversation**, paste the DALL-E generation prompt from [ChatGPT Prompt Templates](03-chatgpt-prompt-templates.md)
2. ChatGPT generates a composite image via DALL-E
3. **Inspect the result** using the quality checklist from [DALL-E Generation Guide](04-dalle-generation-guide.md)
4. If issues found, ask ChatGPT to regenerate
5. Save the image: right-click → Save Image As

### What You Get

- One large PNG image (typically 1024x1024 or 2048x2048)
- 8 stickers arranged in a 2x4 grid (2 columns, 4 rows)
- White background between stickers
- Each sticker in kawaii/cute style with thick outlines

### Where to Save

```
packs/<pack-name>/sticker_pack.png
```

Example:

```
packs/boba-milo-5/sticker_pack.png
```

### Quick Quality Check

Before proceeding, verify:

- [ ] Exactly 8 distinct stickers visible
- [ ] Clear white space between each sticker
- [ ] No stickers overlapping or cut off at edges
- [ ] No unwanted text or letters in any sticker
- [ ] Consistent art style across all 8 stickers

If any check fails, ask ChatGPT to regenerate. See [DALL-E Generation Guide](04-dalle-generation-guide.md) for detailed troubleshooting.

---

## Step 3: Split Composite Sheet

**Goal:** Split the composite sheet into 8 individual 512x512 PNG files.

### Prerequisites

- Composite sheet saved at `packs/<pack-name>/sticker_pack.png`
- Pack registered in `split_stickers.py` PACKS dictionary (see [Image Processing Pipeline](05-image-processing-pipeline.md))

### Command

```bash
STICKER_PACK="boba-milo-5" python split_stickers.py
```

### What Happens

1. White background pixels are detected and made transparent (threshold-based)
2. Connected-component analysis (`scipy.ndimage.label`) finds individual sticker regions
3. Bounding boxes are extracted, filtered by minimum size
4. Stickers are sorted in reading order (top-left to bottom-right, row by row)
5. Each sticker is cropped, padded, and resized to **512x512** on a transparent canvas

### Output

```
packs/boba-milo-5/split/
├── 01_good_morning.png       # 512x512, transparent background
├── 02_love_you.png
├── 03_lets_eat.png
├── 04_fighting.png
├── 05_miss_you.png
├── 06_thank_you.png
├── 07_good_night.png
└── 08_bye_bye.png
```

### Verify

```bash
ls -la packs/boba-milo-5/split/
# Should show exactly 8 PNG files
# Each ~80-300 KB, 512x512 pixels
```

Open a few images to confirm:

- Each contains a single sticker (not merged)
- Transparent background (no white remnants)
- Sticker content is centered and not cropped

If stickers are merged or missing, see [Troubleshooting](10-troubleshooting-faq.md#image-processing-issues).

---

## Step 4: Process for LINE Specs

**Goal:** Resize and optimize the split stickers for LINE's exact requirements.

### Command

```bash
python sticker_processor.py \
    packs/boba-milo-5/split \
    packs/boba-milo-5/final \
    line line_main line_tab \
    --skip-bg
```

The `--skip-bg` flag skips background removal (already done during splitting).

### What Happens

For each sticker image:

1. **Color normalization** — Adjusts saturation (1.15x), brightness (1.05x), contrast (1.05x) for consistency
2. **White outline** — Adds a 10px die-cut border via alpha channel dilation (MaxFilter)
3. **Resize** — Fits within 90% of target dimensions, centered on transparent canvas:
   - `line`: 370x320 (sticker images)
   - `line_main`: 240x240 (pack main image)
   - `line_tab`: 96x74 (chat tab/tray icon)
4. **Save optimized** — PNG with `optimize=True`, color quantization fallback if over 1MB

### Output

```
packs/boba-milo-5/final/
├── line/                         # 8 sticker images for LINE
│   ├── 01_good_morning.png       # 370x320 (or smaller, even dimensions)
│   ├── 02_love_you.png
│   └── ... (8 files)
├── line_main/                    # Main image (pack cover)
│   └── 01_good_morning.png       # 240x240 (first sticker used)
└── line_tab/                     # Chat tab icon
    └── 01_good_morning.png       # 96x74 (first sticker used)
```

### Verify

```bash
# Check file count
ls packs/boba-milo-5/final/line/ | wc -l       # Should be 8
ls packs/boba-milo-5/final/line_main/ | wc -l   # Should be 1 (or 8)
ls packs/boba-milo-5/final/line_tab/ | wc -l    # Should be 1 (or 8)

# Check dimensions (requires ImageMagick)
identify packs/boba-milo-5/final/line/01_good_morning.png
# → 370x320 (or similar, both dimensions even)

# Check file sizes (all must be < 1MB)
ls -la packs/boba-milo-5/final/line/
```

All images must pass:

- [x] PNG format with transparent background
- [x] Even-numbered width and height
- [x] Stickers: width <= 370, height <= 320
- [x] Main: exactly 240x240
- [x] Tab: exactly 96x74
- [x] Each file < 1MB

See [LINE Sticker Specifications](06-line-sticker-specifications.md) for the full requirements.

---

## Step 5: Upload to LINE Creator Market

**Goal:** Create a new sticker submission and upload all images.

### Option A: Automated (Playwright)

```bash
python line_uploader.py \
    --pack-dir packs/boba-milo-5/final \
    --title "Boba & Milo Cheerful Otter Duo 5" \
    --description "A fun, caring otter duo bringing cheerful energy to couples and coworkers." \
    --style-category cute \
    --character-category "families-couples" \
    --price-tier 23000 \
    --headful
```

**First run:** The browser opens and waits for you to log in to LINE (QR code scan). Session is saved for subsequent runs.

**What the automation does:**

1. Opens LINE Creator Market (creator.line.me)
2. Restores saved session (or waits for manual login)
3. Creates a new sticker submission
4. Fills Display Information tab (title, description, AI disclosure, categories, etc.)
5. Navigates to Sticker Images tab and uploads:
   - Main image (from `final/line_main/`)
   - Tab image (from `final/line_tab/`)
   - 8 sticker images (from `final/line/`)
6. Sets Tag Settings (emoji tags based on sticker emotions)
7. Sets Price Tier (+23,000 IDR)
8. Saves the submission (draft)

Add `--submit` to also click the "Request" button to submit for review.
Add `--dry-run` to fill everything without saving.

See [Browser Automation Design](08-browser-automation-design.md) for architecture details.

### Option B: Manual Upload

If automation is not set up or fails:

1. Go to [LINE Creator Market](https://creator.line.me)
2. Click **New Submission** → select **Stickers**
3. Fill the **Display Information** tab using defaults from [Submission Template](07-line-submission-template.md)
4. Click **Save**
5. Navigate to **Sticker Images** tab
6. Upload:
   - **Main Image**: `final/line_main/01_*.png` (240x240)
   - **Tab Image**: `final/line_tab/01_*.png` (96x74)
   - **Sticker Images 01-08**: All files from `final/line/` (370x320)
7. Go to **Tag Settings** → assign emoji tags to each sticker
8. Go to **Price Tier** → select +23,000 IDR
9. Click **Request** to submit for review

---

## Step 6: Wait for Review

**Goal:** LINE reviews and approves (or rejects) your sticker pack.

### Timeline

- **Typical review**: 1-7 business days
- **Fast reviews**: Sometimes within 24 hours
- **Slow reviews**: Up to 2 weeks during holidays or high volume

### Check Status

1. Go to [LINE Creator Market Dashboard](https://creator.line.me/my/LQu3ADYzrcqp2KCs/sticker/?status=all)
2. Find your pack in the list
3. Status will be one of:
   - **Editing** — Not yet submitted
   - **Pending review** — Submitted, waiting for LINE
   - **Approved** — Ready for sale (auto-starts if configured)
   - **Rejected** — Needs fixes (see rejection reason)

### If Rejected

1. Read the rejection reason on the dashboard
2. Common reasons and fixes are in [Troubleshooting](10-troubleshooting-faq.md#line-creator-market-rejection-reasons)
3. Fix the issues, re-upload images, and re-submit
4. Rejection does NOT count against your daily submission limit (30/day)

### After Approval

If **Sales settings** is "Start sales automatically":

- Stickers go live immediately after approval
- Store link appears on the dashboard
- Share link: `https://line.me/S/sticker/<sticker-id>`

If **Sales settings** is "Start sales manually":

- Click "Start Sales" on the dashboard when ready

---

## Complete Example: "Boba & Milo 5"

Here's the actual workflow used to create sticker pack ID 43198882:

### 1. Ideation

```
ChatGPT prompt: "Create 8 stickers for a Ramadan-themed sequel of the
Boba & Milo otter duo series. Kawaii style. Include typical Ramadan
greetings and activities."

Output:
  Title: Boba & Milo Cheerful Otter Duo 5
  Description: A fun, caring otter duo bringing cheerful energy to
  couples and coworkers. Perfect for daily chats, teamwork moments,
  and wholesome support.
  Stickers: marhaban_ya_ramadan, sahur_time, ...
```

### 2. Generation

- DALL-E generated a 2x4 composite sheet with 8 Ramadan-themed otter stickers
- Saved to: `packs/boba-milo-5/sticker_pack.png`

### 3. Split

```bash
STICKER_PACK="boba-milo-5" python split_stickers.py
# Output: packs/boba-milo-5/split/ (8 files)
```

### 4. Process

```bash
python sticker_processor.py \
    packs/boba-milo-5/split packs/boba-milo-5/final \
    line line_main line_tab --skip-bg
# Output: packs/boba-milo-5/final/{line,line_main,line_tab}/
```

### 5. Upload

Submitted through LINE Creator Market:

- Sticker ID: 43198882
- Status: Editing (images pending upload at time of screenshot)
- Creator URL: https://line.me/S/shop/sticker/author/5964498

### 6. Review

- Submitted for review
- Expected approval: 1-7 business days
- Auto-sales enabled: will go live immediately after approval

---

## Time Investment Summary

| Step               | Time (first pack) | Time (repeat) | Notes                        |
| ------------------ | ----------------- | ------------- | ---------------------------- |
| Ideation           | 5 min             | 3 min         | Faster with prompt templates |
| Generation         | 2-5 min           | 2 min         | Regeneration adds time       |
| Splitting          | 10 sec            | 10 sec        | Fully automated              |
| Processing         | 30 sec            | 30 sec        | Fully automated              |
| Upload (auto)      | 2 min             | 2 min         | Playwright fills everything  |
| Upload (manual)    | 15 min            | 10 min        | Tedious form-filling         |
| Review             | 1-7 days          | 1-7 days      | Out of your control          |
| **Total (auto)**   | **~10 min**       | **~8 min**    |                              |
| **Total (manual)** | **~25 min**       | **~18 min**   |                              |

At the automated rate, you can produce **6-8 packs per hour** of active work, limited mainly by ChatGPT/DALL-E generation quality and the daily submission limit of 30.
