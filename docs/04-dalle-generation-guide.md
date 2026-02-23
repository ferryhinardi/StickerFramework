# DALL-E Generation Guide

> How to generate high-quality sticker composite sheets using DALL-E via ChatGPT.

## How It Works

We use **ChatGPT Go plan** ($5/month) with its built-in DALL-E to generate a **single composite image** containing all stickers arranged in a grid. This approach is:

- **Faster** — One generation instead of 8 separate API calls
- **Cheapest** — $5/month flat fee covers all generations (no per-image API cost)
- **More consistent** — All stickers generated in one context share the same art style
- **Trade-off** — Less per-sticker control than individual API generation

### ChatGPT Go Plan Specifics

- Uses **GPT-5.2 Instant** model (Thinking and Pro models are not available on Go)
- DALL-E access is **expanded** but not unlimited — you may hit daily limits if generating many packs
- **No priority response times** — during peak hours, image generation may queue
- If you hit the image generation limit, wait a few hours or continue the next day
- The Go plan is sufficient for producing 2-5 sticker packs per day

## Grid Layouts

### 8 Stickers: 2x4 Grid (Recommended)

```
┌──────┬──────┐
│  01  │  02  │
├──────┼──────┤
│  03  │  04  │
├──────┼──────┤
│  05  │  06  │
├──────┼──────┤
│  07  │  08  │
└──────┴──────┘
```

- 2 columns, 4 rows
- Best balance of sticker size vs separation
- Most reliable layout for DALL-E

### 16 Stickers: 4x4 Grid

```
┌────┬────┬────┬────┐
│ 01 │ 02 │ 03 │ 04 │
├────┼────┼────┼────┤
│ 05 │ 06 │ 07 │ 08 │
├────┼────┼────┼────┤
│ 09 │ 10 │ 11 │ 12 │
├────┼────┼────┼────┤
│ 13 │ 14 │ 15 │ 16 │
└────┴────┴────┴────┘
```

- 4 columns, 4 rows
- More crowded — stickers may be smaller or overlap
- Consider generating as two 2x4 sheets instead

### Alternative: Two Separate 2x4 Sheets

For 16 stickers, it's often better to:

1. Generate stickers 1-8 as one 2x4 sheet
2. Generate stickers 9-16 as a second 2x4 sheet (same conversation for style consistency)
3. Process each sheet separately with `split_stickers.py`

---

## Optimal Settings

| Setting            | Recommendation                              |
| ------------------ | ------------------------------------------- |
| ChatGPT plan       | Go ($5/month) — GPT-5.2 Instant with DALL-E |
| Image aspect ratio | Square (explicitly request this)            |
| Background         | Clean white (essential for splitting)       |
| Art style          | Kawaii/cute with thick outlines             |
| Output resolution  | 1024x1024 or 2048x2048 (ChatGPT decides)    |

---

## Common Issues and Solutions

### Issue 1: Stickers Are Overlapping

**Symptoms:** Two or more stickers touch or share borders. The splitting algorithm will merge them into one region.

**Solutions:**

- Add to your prompt: "Leave generous white space (at least 50 pixels) between each sticker"
- Specify the grid explicitly: "2 columns, 4 rows, with clear separation"
- If it persists: "Regenerate with wider gaps between stickers. Each sticker should have a clear white border around it."

### Issue 2: Inconsistent Art Style

**Symptoms:** Some stickers look realistic while others are cartoony, or line thickness varies.

**Solutions:**

- Keep all sticker descriptions in a **single prompt** (don't split across messages)
- Be explicit about style: "All 8 stickers must use the same art style: thick uniform black outlines, flat colors without gradients, chibi proportions"
- For sequel packs: upload a reference image from a previous pack and say "Match this exact art style"

### Issue 3: Unwanted Text in Stickers

**Symptoms:** DALL-E adds words, letters, or numbers inside sticker illustrations.

**Solutions:**

- Include in every prompt: "NO text, NO words, NO letters, NO numbers in any sticker"
- If text still appears: "Remove all text from the stickers. The stickers should be purely visual with no writing."
- As a last resort: manually remove text in an image editor, or regenerate

### Issue 4: Wrong Number of Stickers

**Symptoms:** DALL-E generates 6, 7, 9, or 10 stickers instead of exactly 8.

**Solutions:**

- Be explicit: "Generate exactly 8 stickers, no more, no less"
- Specify the grid: "2 columns by 4 rows = 8 stickers total"
- Count them in the prompt: "Sticker 1:... Sticker 2:... ... Sticker 8:..."
- If wrong count: "That has [N] stickers. I need exactly 8. Please regenerate with 2 columns and 4 rows."

### Issue 5: Stickers Cut Off at Edges

**Symptoms:** Characters at the edges of the image are partially cropped.

**Solutions:**

- Request: "Each sticker should be fully contained within its grid cell with padding around edges"
- Add: "No part of any sticker should touch the image border"
- Switch to "wide" or "square" aspect ratio if available

### Issue 6: Non-White Background

**Symptoms:** Background is colored, gradient, or has patterns instead of pure white.

**Solutions:**

- Explicitly state: "Clean, pure white (#FFFFFF) background between all stickers"
- If it generates a colored bg: "Regenerate with a plain white background. No patterns, no gradients, no colored background."
- Minor background issues can be handled by `split_stickers.py`'s threshold parameter

---

## Quality Checklist Before Splitting

Inspect the generated composite sheet and verify all items:

- [ ] **Correct count**: Exactly 8 (or 16) distinct stickers visible
- [ ] **Clear separation**: White space visible between every pair of adjacent stickers
- [ ] **No overlap**: No sticker touches or overlaps with another
- [ ] **No cut-off**: All characters fully contained (no parts missing at edges)
- [ ] **No text**: Zero words, letters, or numbers in any sticker
- [ ] **Consistent style**: Same line thickness, color palette, and proportions across all stickers
- [ ] **White background**: Pure white between stickers (not colored or gradient)
- [ ] **Distinct emotions**: Each sticker clearly shows a different emotion or action

### Scoring

- **8/8 checks pass**: Proceed to splitting
- **6-7/8 checks pass**: Minor issues — try regeneration or accept and adjust threshold in splitting
- **5 or fewer pass**: Regenerate — ask ChatGPT to fix specific issues

---

## Saving the Image

1. In ChatGPT, right-click the generated image → **Save Image As**
2. Save as PNG (not JPEG — we need transparency support later)
3. Save to: `packs/<pack-name>/sticker_pack.png`
4. File size should be 1-5 MB

```bash
# Verify the saved image
ls -la packs/<pack-name>/sticker_pack.png
# Should show 1-5 MB file size

# Check dimensions (requires ImageMagick)
identify packs/<pack-name>/sticker_pack.png
# Typically 1024x1024 or 2048x2048
```

---

## Advanced Tips

### Maintaining Style Across Series

When creating Pack 2, 3, 4, etc.:

1. **Upload a reference** — Save one sticker from the previous pack and upload it to the new ChatGPT conversation
2. **Describe the style** — "Match this exact art style: thick black outlines, flat colors, pastel tones, chibi proportions"
3. **Name the characters** — "The characters are Boba (round otter) and Milo (taller otter)"

### Cost Analysis

| Method                                | Cost              | Best For                                   |
| ------------------------------------- | ----------------- | ------------------------------------------ |
| **ChatGPT Go plan**                   | **$5/month flat** | Interactive generation, 2-5 packs/day      |
| ChatGPT Plus plan                     | $20/month flat    | Higher limits, priority response times     |
| DALL-E API (via `image_generator.py`) | $0.04-0.08/image  | Batch generation (10+ packs/day), scripted |

The **Go plan at $5/month is the most cost-effective** for sticker production. At 5 packs/week (20/month), the cost is effectively $0.25 per pack — cheaper than any API approach.

### When to Use the API Instead

| Use ChatGPT Go (recommended) | Use DALL-E API                     |
| ---------------------------- | ---------------------------------- |
| Interactive, iterate quickly | Batch generation (10+ packs/day)   |
| Need conversation context    | Scripted pipeline (no manual save) |
| $5/month flat fee            | $0.04-0.08 per generation          |
| Manual save required         | Auto-saves to disk                 |
| 2-5 packs/day comfortably    | Unlimited (budget permitting)      |
