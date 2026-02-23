# Troubleshooting & FAQ

> Common issues, LINE rejection reasons, and debugging guide.

---

## Image Processing Issues

### split_stickers.py finds wrong number of stickers

**Symptoms:** Script detects 6, 7, 9, or 10 regions instead of 8.

**Causes & Solutions:**

| Cause                         | Solution                                                                  |
| ----------------------------- | ------------------------------------------------------------------------- |
| Stickers touching/overlapping | Lower `threshold` (e.g., 230 instead of 240) to remove more border pixels |
| Background not fully white    | Lower `threshold` to be more aggressive                                   |
| `grid_rows` mismatch          | Count actual rows in the composite sheet and update PACKS config          |
| Noise regions detected        | Increase `min_size` filter to ignore small artifacts                      |
| Sticker too faint/pale        | Increase contrast of the source image before splitting                    |

```bash
# Quick test: try different thresholds
STICKER_PACK="my-pack" THRESHOLD=230 python split_stickers.py
```

### Two stickers merged into one region

**Cause:** Connected-component analysis treats touching regions as a single object.

**Solutions:**

1. Best fix: Regenerate the composite with more spacing (see [DALL-E Guide](04-dalle-generation-guide.md#issue-1-stickers-are-overlapping))
2. Workaround: Open the composite in an image editor (GIMP, Photoshop) and add white pixels between the touching stickers
3. Lower the threshold to erode the border between them

### Output stickers have wrong dimensions

**Cause:** `split_stickers.py` outputs 512x512, then `sticker_processor.py` resizes to LINE specs.

**Check:**

```bash
# Verify split output (should be 512x512)
identify packs/<pack>/split/01_*.png

# Verify final output (should be ≤370x320, even dimensions)
identify packs/<pack>/final/line/01_*.png
```

If dimensions are wrong in `final/`, check that you passed the correct platform IDs: `line line_main line_tab`.

### File size exceeds 1 MB

**Cause:** Complex sticker with many colors, large outline, or high-resolution source.

**Solutions:**

1. `sticker_processor.py` auto-quantizes colors as a fallback — check if the optimized file is still over 1 MB
2. Reduce outline width: edit `StickerProcessor(outline_width=8)` (default is 10)
3. Simplify the source image (fewer gradient colors)
4. Use PNG optimization tools: `pngquant --quality=65-80 file.png`

### White outline is too thick or too thin

**Adjustment:** Edit the outline width in `sticker_processor.py`:

```python
# Default: 10px outline
processor = StickerProcessor(outline_width=10)

# Thinner outline (for small or detailed stickers)
processor = StickerProcessor(outline_width=6)

# Thicker outline (for simple/bold stickers)
processor = StickerProcessor(outline_width=14)
```

### Background removal leaves artifacts

**Cause:** `rembg` (U2-Net) struggles with certain image types.

**Solutions:**

1. Use `--skip-bg` flag if the composite already has clean white background
2. `split_stickers.py` handles white background removal via threshold — this is usually sufficient
3. For stubborn artifacts: manually clean up in GIMP/Photoshop before processing

---

## LINE Creator Market Rejection Reasons

### "Images have poor visibility"

**Meaning:** Stickers are too thin, too pale, or hard to see at small sizes.

**Fixes:**

- Add thicker white outline (increase `outline_width` to 12-14)
- Increase contrast in color normalization
- Ensure ~10px transparent margin around sticker content
- Avoid very pale pastel colors that blend with white backgrounds
- Test: view stickers at 96x74 (tab icon size) — if you can't tell what it is, LINE won't approve it

### "Lack of variety"

**Meaning:** Too many stickers look similar or express the same emotion.

**Fixes:**

- Ensure each sticker has a visually distinct pose, expression, and props
- Avoid multiple "happy" variants — differentiate with context (happy eating, happy celebrating, happy greeting)
- Add variety in: body position, facial expression, accessories, background elements
- Review your pack side by side — if any two look swappable, redesign one

### "Content policy violation"

**Meaning:** Content violates LINE's guidelines.

**Common triggers and fixes:**

| Trigger                            | Fix                                          |
| ---------------------------------- | -------------------------------------------- |
| Text resembling advertising        | Remove any product names or promotional text |
| Corporate logos                    | Remove logos, use generic designs            |
| References to other messaging apps | Remove WhatsApp/Telegram/iMessage references |
| Violent or sexual content          | Redesign with family-friendly imagery        |
| Real person likeness               | Use cartoon/abstract characters instead      |

### "Images do not meet specifications"

**Meaning:** Technical image requirements not met.

**Checklist:**

- [ ] All images are PNG format (`.png` extension)
- [ ] All images have transparent background (alpha channel)
- [ ] Width and height are both even numbers
- [ ] Sticker images: width ≤ 370, height ≤ 320
- [ ] Main image: exactly 240 x 240
- [ ] Tab image: exactly 96 x 74
- [ ] Each file under 1 MB
- [ ] Resolution ≥ 72 DPI

```bash
# Verify all requirements at once
for f in packs/<pack>/final/line/*.png; do
    size=$(stat -f%z "$f")
    dims=$(identify -format "%wx%h" "$f")
    w=$(echo $dims | cut -dx -f1)
    h=$(echo $dims | cut -dx -f2)
    even_w=$((w % 2))
    even_h=$((h % 2))
    echo "$f: ${dims} ${size}B even_w=$even_w even_h=$even_h"
done
```

### "Cannot be used easily in conversation"

**Meaning:** Stickers show objects/scenery that don't fit in a chat context.

**Fixes:**

- Each sticker should clearly express an emotion, reaction, or greeting
- Characters should have visible facial expressions
- Avoid landscape/scenery-only stickers
- Avoid abstract patterns without clear emotional context
- Test: for each sticker, can you name when you'd send it in a conversation?

---

## Browser Automation Issues

### Playwright can't find login elements

**Cause:** LINE may have updated their UI, changing HTML structure and selectors.

**Solutions:**

1. Run `playwright codegen creator.line.me` to discover new selectors
2. Update selectors in `automation/config.py`
3. Use headful mode to see what the page looks like: `--headful`
4. Check if the page uses iframes: `page.frames` may reveal hidden content

### Session cookies expired

**Symptoms:** Automation redirects to login page instead of dashboard.

**Solutions:**

1. Delete saved session: `rm ~/.line-sticker-automation/storage_state.json`
2. Run with `--headful` to trigger manual re-login
3. Session is automatically saved after successful login

### Upload fails mid-way

**Symptoms:** Some images uploaded, others didn't.

**Solutions:**

1. Use `--resume` flag to continue from the last completed step
2. Check `automation/screenshots/` for failure screenshots
3. Verify image files are valid PNGs and meet specs before uploading
4. Try uploading one by one in headful mode to identify the failing image

### Playwright is blocked/detected as bot

**Symptoms:** Page shows CAPTCHA, blank content, or "Access Denied."

**Solutions:**

1. Use headful mode (non-headless): `--headful`
2. Install and enable `playwright-stealth`: `pip install playwright-stealth`
3. Add random delays between actions (see `human_delay()` in automation design)
4. Avoid running too many submissions in quick succession
5. Use a real browser profile (pass `user_data_dir` to Playwright)

### Save button doesn't work / form validation error

**Symptoms:** Clicking Save triggers a validation error on the page.

**Solutions:**

1. Take a screenshot to see the error message
2. Common causes: empty required field, title too long, description too long
3. Verify metadata lengths: title ≤ 40 chars, description ≤ 160 chars, copyright ≤ 50 chars
4. Check the automation filled all required fields (not just the ones with defaults)

---

## ChatGPT / DALL-E Issues

### DALL-E generates wrong number of stickers in sheet

**Solutions:**

- Be explicit: "exactly 8 stickers in a 2 column by 4 row grid"
- Count them in the prompt: "Sticker 1:... Sticker 2:... ... Sticker 8:..."
- If it generates wrong count: "That has [N] stickers. Please regenerate with exactly 8 in a 2x4 grid."

### Art style inconsistent across stickers

**Solutions:**

- Generate all stickers in a **single** DALL-E request (one prompt, one image)
- Be specific about style: "thick uniform black outlines, flat colors without gradients"
- For sequels: upload a reference image from a previous pack
- Avoid vague style descriptions like "cute" — instead use "kawaii chibi style with thick outlines, flat pastel colors, large head-to-body ratio"

### DALL-E adds text/words to stickers

**Solutions:**

- Include: "NO text, NO words, NO letters, NO numbers in any sticker"
- If text still appears, try: "The stickers should be purely visual illustrations with zero written text or characters"
- Some DALL-E models are more prone to adding text — regenerate if needed
- As last resort: manually edit out text in an image editor

### ChatGPT won't generate the image

**Causes:** Content policy, rate limiting, Go plan daily limit, or model limitation.

**Solutions:**

- Rephrase any potentially sensitive content in the prompt
- Wait a few minutes and try again (rate limiting)
- If you've hit the Go plan's daily DALL-E limit, wait until the next day or upgrade to Plus ($20/month) for higher limits
- If a specific sticker concept is blocked, replace it with a safer alternative
- Try a different phrasing: instead of specific emotion names, describe the visual scene

---

## Frequently Asked Questions

### Can I use this for animated stickers?

Not currently. This project focuses on **static stickers** only. Animated stickers require:

- APNG format with specific frame requirements (5-20 frames)
- Different dimension constraints (≤320x270)
- Animation timing rules (≤4 seconds, 1-4 loops)

Adding animated sticker support is a potential future enhancement.

### Can I sell on multiple platforms besides LINE?

Yes. The `sticker_processor.py` supports multiple platforms:

- **WhatsApp** (via Sticker.ly): 512x512 WebP
- **Telegram**: 512x512 WebP (auto-publish via bot API)
- **iMessage**: 300/408/618 PNG (Xcode project generation)
- **Etsy**: 3000x3000 print-ready PNG

Process for all platforms:

```bash
python sticker_processor.py input/ output/ \
    line line_main line_tab whatsapp telegram imessage_large print_etsy --skip-bg
```

### What's the revenue potential?

Realistic estimates at Tier 1 pricing (+23,000 IDR):

| Scenario                    | Monthly Sales | Monthly Revenue (IDR) | Monthly Revenue (USD) |
| --------------------------- | ------------- | --------------------- | --------------------- |
| 1 pack, minimal promotion   | 10-50         | 80k-400k              | $5-26                 |
| 5 packs, moderate promotion | 50-200        | 400k-1.6M             | $26-104               |
| 20+ packs, active promotion | 200-1000      | 1.6M-8M               | $104-520              |

Key factors: pack quality, niche targeting, promotion effort, seasonal timing, and LINE Premium subscriber base.

### Do I need to disclose AI usage?

**Yes.** LINE requires creators to select "AI was used" or "AI was not used" on every submission. Since this pipeline uses DALL-E for generation, always select "AI was used." This is handled automatically by the submission template defaults.

### How many packs can I submit per day?

LINE allows **30 submissions per day** (shown on the dashboard). This includes new submissions and re-submissions. Rejections don't count against the limit.

At automated rates (~8 min per pack), you could theoretically submit all 30 in under 4 hours of active work.

### Is there a review queue priority?

No official priority system. LINE reviews submissions in the order received. However:

- High-quality packs with diverse stickers tend to pass faster
- Packs with issues may be queued for manual review (slower)
- Holiday periods may slow down reviews

### Can I change the price after publishing?

LINE does not allow price changes after a sticker pack is published. Choose your price tier carefully before submission. You can use different tiers for different packs.

### What happens if my pack is rejected?

1. You receive an email with the rejection reason
2. The pack status changes to "Rejected" on the dashboard
3. Click the pack to see the specific reason
4. Fix the issues (edit images, change metadata)
5. Re-submit for review
6. Repeat until approved
7. There's no penalty for rejections

### How do I delete a published sticker pack?

1. Go to the sticker management page on LINE Creator Market
2. Click the pack you want to remove
3. Click "Stop Sales" to remove from the LINE Store
4. The pack remains on your dashboard but is no longer available for purchase
5. Existing buyers keep their downloaded stickers
