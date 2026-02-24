# Cappy the Chill Capybara Vol.3: Chatty Cappy — DALL-E Generation Prompts

> Use these in ChatGPT UI (Go plan). Two composite sheets, 8 stickers each.
> Generate Sheet 1 first, then Sheet 2 **in the same conversation** for style consistency.
> **IMPORTANT**: Use the SAME conversation as v1/v2 if possible, or re-establish character first.
>
> **KEY DIFFERENCE from v1/v2**: Text will be added AFTER generation via the
> processing pipeline (`sticker_processor.py` text overlay). Do NOT ask DALL-E
> to render text — AI-generated text is unreliable. Generate stickers WITHOUT
> text, then the pipeline adds crisp text from `pack_config.py`.

---

## Step 1: Character Setup Prompt

Paste this first to establish the character before generating:

```
I'm creating a LINE sticker pack called "Cappy the Chill Capybara Vol.3" — this is
the third volume of the Cappy series. 16 stickers total, generated as two 2×4
composite sheets (8 stickers per sheet).

Character — Cappy (SAME as Vol.1 and Vol.2):
- A very round, potato-shaped capybara with chibi proportions
- Warm brown body (#C4956A), soft pink blush on cheeks (#FFB4B4)
- Thick uniform dark brown outline (#4A3728), 3-4px consistent width
- Small round black dot eyes — calm, content, slightly droopy for chill vibes
- Small rounded ears on top of head, short flat nose/snout
- SIGNATURE: A tiny orange (mikan fruit) always sitting on top of his head
- Stubby short limbs, tiny barely-visible tail
- Head is about 50% of total body height

Art style (SAME as Vol.1/Vol.2):
- Kawaii/cute flat-color style — NO gradients, NO realistic shading
- Thick uniform dark brown outlines
- Die-cut sticker style with a thick white outline border around the ENTIRE character
- Clean solid white background
- Simple, round, minimal detail, maximum cuteness
- NO text, NO words, NO letters, NO numbers anywhere in the image
  (text will be added separately in post-processing)

This vol.3 focuses on everyday chat phrases. Each sticker will have text added
later in post-processing, so the character poses and expressions need to clearly
convey the emotion even without text. I'll ask you to generate two sheets. Ready?
```

---

## Step 2: Sheet 1 — Stickers 01-08 (Daily Greetings & Status)

```
Generate stickers 1-8 as a SINGLE image arranged in a 2×4 grid
(2 columns, 4 rows) on a clean white background. Square aspect ratio.

Each sticker must be clearly separated with generous white space between them.
All in the Cappy capybara character described above.

IMPORTANT: Leave clear space at the BOTTOM of each sticker cell for text overlay
that will be added later. Position the character in the upper 70-75% of each cell.

The 8 stickers (left to right, top to bottom):

1. SUP / CASUAL GREETING — Leaning back casually against invisible wall,
   one stubby arm raised in a lazy wave, relaxed posture. Half-lidded chill
   eyes, slight cool smirk, orange balanced perfectly on head, small sparkle
   near waving hand.

2. SAME / RELATABLE — Pointing both stubby arms forward at the viewer,
   leaning in with wide knowing eyes. Emphatic nodding motion lines around
   head, determined agreement expression, orange nodding along on head.

3. NOPE / REFUSAL — Sitting firmly with stubby arms crossed over round body,
   head turned to the side, eyes closed. Big X mark above head, firm closed
   mouth, strong refusal aura lines, orange sitting defiantly on head.

4. LET'S GO / PUMPED UP — Running forward toward viewer, one stubby arm
   pumping in the air, body leaning into the sprint. Fire trail behind feet,
   speed lines, wide determined grin, orange ablaze (tiny flame effect) on
   head, sparkle in eyes.

5. WHY / CONFUSED — Standing still staring blankly forward, stubby arms
   hanging limp at sides, slight head tilt. Three question marks floating
   above head in different sizes, hollow empty eyes, orange tilted askew.

6. FOOD / CRAVING — Standing on tiptoes reaching upward with both stubby
   arms, mouth wide open drooling. Star-shaped sparkle eyes, drool from
   mouth, imaginary bowl of ramen floating above hands, orange bouncing
   excitedly on head.

7. NO MONEY / BROKE — Standing holding an open wallet upside down with both
   stubby arms, shaking it, looking inside desperately. Empty wallet with a
   moth flying out, single tear on cheek, coin with wings flying away,
   orange drooping sadly on head.

8. OMW / ON MY WAY — Riding a tiny scooter at full speed to the right,
   body hunched forward over handlebars. Speed lines trailing behind, dust
   cloud at wheels, determined squinting eyes, orange flapping in the wind
   on head.

Requirements:
- Clean white background between ALL stickers (no overlapping, no touching)
- At least 50px equivalent gap between each sticker
- Each sticker has thick white outline border (die-cut sticker style)
- NO text, NO words, NO letters, NO numbers in any sticker
- Consistent style, proportions, and colors across all 8
- Each character fully contained within its cell (not cut off)
- Leave clear space at bottom of each cell for text to be added later
- Square overall image
```

---

## Step 3: Sheet 2 — Stickers 09-16 (Mood Updates & Reactions)

**Stay in the same conversation**, then paste:

```
Now generate stickers 9-16 as a second 2×4 grid, same style and character as Sheet 1.

Again, leave clear space at the BOTTOM of each cell for text overlay.

The 8 stickers (left to right, top to bottom):

9. CHILL / RELAXED — Lying on back floating in a tiny hot spring or puddle,
   stubby arms behind head, eyes closed peacefully. Steam wisps rising,
   serene blissful smile, small musical notes floating, orange floating
   beside in the water, zen ripples.

10. UGH / ANNOYED — Face-palming with one stubby arm covering entire face,
    body slumped forward. Dark annoyed aura cloud behind, visible frustration
    vein on hand, heavy sigh breath cloud, orange wilting on head.

11. SLAY / FABULOUS — Posing dramatically like a runway model, one stubby arm
    on hip, the other flipping imaginary hair, body in sassy S-curve. Sparkles
    and stars all around, confident closed-eye smirk, tiny crown on head next
    to orange, pink glowing aura.

12. IT'S FINE / DENIAL — Sitting in a room surrounded by small flames, holding
    a tiny cup of tea, sipping calmly with eyes closed. Small cartoon flames
    around (this-is-fine meme reference), serene denial smile, sweat drop on
    temple, orange slightly singed on head.

13. PLS / BEGGING — On knees with both stubby arms clasped together in front,
    looking up with huge watery puppy eyes. Giant sparkling teary puppy eyes
    (twice normal size), trembling lower lip, begging sparkles around clasped
    hands, orange wobbling on head.

14. WUT / DUMBFOUNDED — Standing completely frozen mid-step, one foot raised,
    body stiff, eyes wide and vacant like blue-screen. Loading/buffering circle
    spinning above head, completely blank frozen expression, tiny error symbols,
    orange glitching on head.

15. TTYL / GOTTA GO — Peeking from behind a door that is half-closed, only
    half of face and one stubby arm visible, waving goodbye. Small hand wave,
    one visible eye winking, mischievous slight smile, orange peeking from
    behind door too.

16. MOOD / BIG MOOD — Sitting slouched on a tiny couch wrapped in a blanket
    burrito, only face visible, holding a phone up close. Empty snack bags
    around couch, phone screen glowing on face, dead-inside peaceful eyes,
    orange peeking out of blanket on head.

Same requirements as Sheet 1:
- 2×4 grid, square image, clean white background
- Generous spacing, no touching/overlapping
- Die-cut sticker style with white outline border
- NO text anywhere
- Leave space at bottom of each cell for text overlay
- Consistent with Sheet 1's style and proportions
```

---

## Troubleshooting

If results aren't right, try these follow-up prompts:

- **Text appeared**: "Regenerate but remove ALL text, letters, and numbers. The stickers should be purely visual with no written words. Text will be added in post-processing."
- **Stickers overlap**: "Regenerate with MORE space between stickers. Each sticker should be clearly isolated with at least 80px of white space between them."
- **Style inconsistent**: "Make all 8 stickers match the same art style — same outline thickness, same body proportions, same brown color."
- **Character cut off**: "Make sure every sticker's character is FULLY visible within its cell. Nothing should be cropped at the edges."
- **Orange missing**: "Make sure Cappy has the tiny orange (mikan) fruit on his head in every sticker."
- **Style doesn't match v1/v2**: "Match the exact style from Vol.1/Vol.2 — same brown (#C4956A), same outline thickness (#4A3728), same chibi potato proportions."
- **No space for text**: "Position the character in the upper 70-75% of each cell, leaving clear white space at the bottom for text to be added later."

---

## After Generation

1. Download both composite sheet images
2. Save to `packs/cappy-capybara-3/`:
   - Sheet 1 → `composite_sheet_1.png`
   - Sheet 2 → `composite_sheet_2.png`
3. Run the split + process pipeline:
   ```bash
   # Split Sheet 1 (stickers 01-08)
   python scripts/split_stickers.py --pack-dir packs/cappy-capybara-3

   # Process all split stickers (bg removal, outline, text overlay, resize for all platforms)
   python scripts/sticker_processor.py --pack-dir packs/cappy-capybara-3
   ```
4. Run full pipeline (alternative — handles split + process + text + icons):
   ```bash
   python scripts/run_pipeline.py --pack-dir packs/cappy-capybara-3
   ```
5. Run preflight check:
   ```bash
   python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara-3
   ```

### Text Overlay Notes

The text for each sticker is defined in `pack_config.py` under each sticker's
`"text"` field. The processing pipeline reads this and renders bold white text
with dark brown stroke at the bottom of each sticker. This ensures:
- Crisp, readable text (no AI text rendering artifacts)
- Consistent font and positioning across all 16 stickers
- Easy to update text without regenerating images
