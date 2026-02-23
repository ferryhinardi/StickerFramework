# Cappy the Chill Capybara — DALL-E Generation Prompts

> Use these in ChatGPT UI (Go plan). Two composite sheets, 8 stickers each.
> Generate Sheet 1 first, then Sheet 2 **in the same conversation** for style consistency.

---

## Step 1: Character Setup Prompt

Paste this first to establish the character before generating:

```
I'm creating a LINE sticker pack called "Cappy the Chill Capybara" — 16 stickers
total, generated as two 2×4 composite sheets (8 stickers per sheet).

Character — Cappy:
- A very round, potato-shaped capybara with chibi proportions
- Warm brown body (#C4956A), soft pink blush on cheeks (#FFB4B4)
- Thick uniform dark brown outline (#4A3728), 3-4px consistent width
- Small round black dot eyes — calm, content, slightly droopy for chill vibes
- Small rounded ears on top of head, short flat nose/snout
- SIGNATURE: A tiny orange (mikan fruit) always sitting on top of his head
- Stubby short limbs, tiny barely-visible tail
- Head is about 50% of total body height

Art style:
- Kawaii/cute flat-color style — NO gradients, NO realistic shading
- Thick uniform dark brown outlines
- Die-cut sticker style with a thick white outline border around the ENTIRE character
- Clean solid white background
- Simple, round, minimal detail, maximum cuteness
- NO text, NO words, NO letters, NO numbers anywhere

I'll ask you to generate two sheets. Ready?
```

---

## Step 2: Sheet 1 — Stickers 01-08

```
Generate stickers 1-8 as a SINGLE image arranged in a 2×4 grid
(2 columns, 4 rows) on a clean white background. Square aspect ratio.

Each sticker must be clearly separated with generous white space between them.
All in the Cappy capybara character described above.

The 8 stickers (left to right, top to bottom):

1. GOOD MORNING — Sitting up sleepily, one stubby arm rubbing eye, small yawn.
   Small sun icon in top-right corner. Orange slightly tilted on head.

2. OK / THUMBS UP — Standing facing forward, one arm giving thumbs up, confident lean.
   Sparkle near thumb, cheerful closed-eye smile.

3. THANK YOU — Bowing forward at 45 degrees, both arms pressed together in front.
   Small sparkles around head, peaceful closed eyes, orange wobbling on head.

4. LOL / LAUGHING — Leaning back, body shaking, one arm on belly.
   Eyes squeezed shut in joy, wide open laughing mouth, single tear of joy,
   orange bouncing off head slightly.

5. LOVE — Both arms hugging a large pink heart against round body.
   Eyes closed blissfully, pink blush extra visible, small floating hearts above.

6. SLEEPY — Lying on side curled up, eyes closed, one arm under cheek.
   Three Zzz bubbles floating up, small pillow under head,
   orange rolled off and sitting next to head.

7. HUNGRY — Standing with both arms reaching forward, mouth open drooling.
   Single drool drop from mouth, eyes sparkling, small steam/aroma lines.

8. WORKING HARD — Sitting at a tiny laptop, arms typing, focused squinting.
   Small sweat drop on temple, steam from coffee cup beside laptop,
   orange balanced on head.

Requirements:
- Clean white background between ALL stickers (no overlapping, no touching)
- At least 50px equivalent gap between each sticker
- Each sticker has thick white outline border (die-cut sticker style)
- NO text, NO words, NO letters, NO numbers in any sticker
- Consistent style, proportions, and colors across all 8
- Each character fully contained within its cell (not cut off)
- Square overall image
```

---

## Step 3: Sheet 2 — Stickers 09-16

**Stay in the same conversation**, then paste:

```
Now generate stickers 9-16 as a second 2×4 grid, same style and character as Sheet 1.

The 8 stickers (left to right, top to bottom):

9. EXCITED / YAY — Jumping with both arms thrown up, feet off ground.
   Star sparkles around body, wide open happy mouth,
   orange flying up above head.

10. SAD — Sitting hunched over, head down, ears drooping slightly.
    Single large blue teardrop on cheek, small rain cloud above head,
    orange sitting sadly on head.

11. ANGRY / FRUSTRATED — Standing with arms at sides clenched, leaning forward,
    cheeks puffed red. Steam lines from head, anger vein mark on forehead,
    orange trembling on head.

12. SORRY — Deep bow with body bent forward, arms at sides,
    looking up with guilty puppy eyes. Large sweat drop on head,
    wavy guilt lines, orange about to fall off head.

13. BYE BYE — Walking away to the right, looking back over shoulder,
    one arm waving. Small motion lines near feet, gentle smile,
    orange secure on head.

14. THINKING / HMM — Standing with one arm on chin, looking upward to right.
    Three thought-bubble dots floating above, one eyebrow raised,
    orange tilted on head.

15. CHEERING / YOU CAN DO IT — Standing on tippy-toes, both arms pumping in air.
    Determined bright eyes, sparkle effects, motion lines showing energy,
    orange bouncing on head.

16. GOOD NIGHT — Lying in a tiny round bed, eyes peacefully closed,
    blanket pulled up to chin. Small crescent moon and stars above,
    orange on the bedside table, serene expression.

Same requirements as Sheet 1:
- 2×4 grid, square image, clean white background
- Generous spacing, no touching/overlapping
- Die-cut sticker style with white outline border
- NO text anywhere
- Consistent with Sheet 1's style and proportions
```

---

## Troubleshooting

If results aren't right, try these follow-up prompts:

- **Text appeared**: "Regenerate but remove ALL text, letters, and numbers. The stickers should be purely visual with no written words."
- **Stickers overlap**: "Regenerate with MORE space between stickers. Each sticker should be clearly isolated with at least 80px of white space between them."
- **Style inconsistent**: "Make all 8 stickers match the same art style — same outline thickness, same body proportions, same brown color."
- **Character cut off**: "Make sure every sticker's character is FULLY visible within its cell. Nothing should be cropped at the edges."
- **Orange missing**: "Make sure Cappy has the tiny orange (mikan) fruit on his head in every sticker."

---

## After Generation

1. Download both composite sheet images
2. Save to `packs/cappy-capybara/`:
   - Sheet 1 → `composite_sheet_1.png`
   - Sheet 2 → `composite_sheet_2.png`
3. Run the split + process pipeline:
   ```bash
   # Split Sheet 1 (stickers 01-08)
   STICKER_PACK="Cappy the Chill Capybara (Sheet 1)" python scripts/split_stickers.py

   # Split Sheet 2 (stickers 09-16)
   STICKER_PACK="Cappy the Chill Capybara (Sheet 2)" python scripts/split_stickers.py

   # Process all 16 split stickers (bg removal, outline, resize for LINE)
   STICKER_PACK="cappy-capybara" python scripts/sticker_processor.py
   ```
4. Run preflight check:
   ```bash
   python scripts/line_preflight_check.py --pack-dir packs/cappy-capybara
   ```
