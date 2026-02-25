# Chubby Mochi Hamster Vol.2: Study Mode — DALL-E Generation Prompts

> Use these in ChatGPT UI (Go plan). Two composite sheets, 8 stickers each.
> Generate Sheet 1 first, then Sheet 2 **in the same conversation** for style consistency.
> **IMPORTANT**: Use the SAME conversation as Vol.1 if possible, or re-establish character first.
>
> **KEY DIFFERENCE**: Text will be added AFTER generation via the processing pipeline
> (`sticker_processor.py` text overlay). Do NOT ask DALL-E to render text — AI-generated
> text is unreliable. Generate stickers WITHOUT text, then the pipeline adds crisp text
> from `pack_config.py`.

---

## Step 1: Character Setup Prompt

Paste this first to establish the character before generating:

```
I'm creating a LINE sticker pack called "Chubby Mochi Hamster Vol.2: Study Mode" —
this is the second volume of the Mochi Hamster series. 16 stickers total, generated
as two 2×4 composite sheets (8 stickers per sheet).

Character — Mochi Hamster (SAME as Vol.1):
- A cute round chubby hamster, extremely round ball-shaped body
- Warm orange-brown fur (#E8A84C), white belly patch
- Soft pink blush marks on cheeks (#FF9999)
- Thick dark charcoal outlines (#333333), consistent 3-4px width
- Large shiny black round eyes with tiny white highlight dots, expressive
- Small pink nose, large round ears
- Puffed cheek pouches (signature feature)
- Chibi proportions — head is 55% of total body height
- Tiny stubby paws

Art style (SAME as Vol.1):
- Painted illustration style — semi-realistic painting, soft painterly shading
- Warm color palette throughout
- Thick uniform dark charcoal outlines
- Die-cut sticker style with a thick white outline border around the ENTIRE character
- Clean solid white background with no other elements
- Dynamic expressive poses, action effects like motion lines and sweat drops
- Kawaii aesthetic with exaggerated proportions
- NO text, NO words, NO letters, NO numbers anywhere in the image
  (text will be added separately in post-processing)

This vol.2 focuses on study/learning themes. Each sticker will have text added
later in post-processing, so the character poses and expressions need to clearly
convey the emotion even without text. I'll ask you to generate two sheets. Ready?
```

---

## Step 2: Sheet 1 — Stickers 01-08 (Study Actions & States)

```
Generate stickers 1-8 as a SINGLE image arranged in a 2×4 grid
(2 columns, 4 rows) on a clean white background. Square aspect ratio.

Each sticker must be clearly separated with generous white space between them.
All in the Mochi Hamster character described above.

IMPORTANT: Leave clear space at the BOTTOM of each sticker cell for text overlay
that will be added later. Position the character in the upper 70-75% of each cell.

The 8 stickers (left to right, top to bottom):

1. STUDYING HARD — Sitting at a tiny desk, paws holding a pencil, leaning
   over an open book. Stack of books beside desk, focused squinting eyes,
   small reading glasses perched on nose, puffed cheeks showing concentration.

2. BRAIN OVERLOAD — Sitting with paws on head, eyes spiral-dazed, cheeks
   puffed to maximum. Steam coming out of ears, math symbols and letters
   floating around head, dizzy swirl effects, overwhelmed expression.

3. EUREKA / GOT IT — Jumping up with one paw raised high pointing up, wide
   excited eyes, huge grin. Bright lightbulb glowing above head, sparkle
   effects all around, energy lines radiating outward from body.

4. MOTIVATED / LET'S GO — Standing with both paws clenched in fists, powerful
   determined stance, intense focused eyes. Fire aura around body, motion
   lines showing power and energy, determined fierce expression.

5. NEED COFFEE — Slouching forward with half-closed droopy eyes, both paws
   wrapped around a big coffee mug. Steam rising from coffee, dark under-eye
   circles, messy disheveled fur on head, exhausted expression.

6. QUIZ TIME — Sitting upright at full attention, paws gripping pencil tightly,
   wide alert eyes. Paper with checkboxes on desk in front, sweat drop on
   temple, trembling nervous motion lines, anxious excitement.

7. ACED IT — Standing tall holding up a paper with A+ grade, chest puffed out,
   huge proud triumphant grin. Sparkles and stars around the paper, golden
   glow effect, small confetti pieces falling.

8. HELP ME / CONFUSED — Sitting surrounded by open books everywhere, paws
   tangled in fur on head, head tilted to one side. Multiple question marks
   floating above head, tangled scribble lines, bewildered wide eyes.

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

## Step 3: Sheet 2 — Stickers 09-16 (Study Life & Reactions)

**Stay in the same conversation**, then paste:

```
Now generate stickers 9-16 as a second 2×4 grid, same style and character as Sheet 1.

Again, leave clear space at the BOTTOM of each cell for text overlay.

The 8 stickers (left to right, top to bottom):

9. BREAK TIME — Leaning back in chair with paws behind head, eyes closed
   peacefully, satisfied relaxed smile. Clock showing break time on desk,
   snack or drink on desk, relaxation wave lines around body.

10. DUE TOMORROW / PANIC — Eyes popping out of head, paws on cheeks in
    classic horror/scream pose, body stiff and trembling. Calendar page
    showing deadline in background, alarm bells ringing above, lightning
    bolt shock lines, extreme panic expression.

11. GOOD LUCK — Both paws giving enthusiastic double thumbs up, warm
    cheerful encouraging smile, slight forward lean toward viewer. Four-leaf
    clover floating nearby, sparkle effects, warm golden glow around body.

12. SO TIRED / DEAD — Face-planted flat on an open book, body completely
    limp and deflated like a pancake. Tiny ghost/soul floating out of body
    upward, X eyes or closed exhausted eyes, book used as pillow.

13. YOU GOT THIS / CHEER — Holding tiny pom-poms in both paws, jumping
    mid-air with legs spread apart, big wide open mouth cheering. Star burst
    effect behind, exclamation energy marks, energetic motion lines.

14. PROCRASTINATING — Lying on belly scrolling a tiny phone, half-lidded
    relaxed guilty eyes, open textbook completely ignored beside. Thought
    bubble showing phone screen, books gathering dust, guilty pleasure
    expression.

15. GROUP STUDY — Waving one paw invitingly toward viewer, other paw
    pointing to an empty chair beside. Small table with books set up,
    extra empty chair, warm welcoming smile, friendly inviting pose.

16. ALL DONE / FINISHED — Both paws thrown up high in celebration, eyes
    closed with huge relieved triumphant smile. Completed checklist with
    all checkmarks floating nearby, sparkle burst effects, weight-lifted
    relief effect lines radiating outward.

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
- **Style inconsistent**: "Make all 8 stickers match the same art style — same outline thickness, same body proportions, same warm orange-brown color (#E8A84C)."
- **Character cut off**: "Make sure every sticker's character is FULLY visible within its cell. Nothing should be cropped at the edges."
- **Cheek pouches missing**: "Make sure the hamster has VISIBLE puffed cheek pouches in every sticker — this is a signature feature."
- **Style doesn't match Vol.1**: "Match the exact style from Vol.1 — same orange-brown (#E8A84C), same charcoal outlines (#333333), same chibi round proportions, same painted illustration style."
- **No space for text**: "Position the character in the upper 70-75% of each cell, leaving clear white space at the bottom for text to be added later."
- **Eyes wrong**: "The hamster should have LARGE shiny black round eyes with tiny white highlight dots — expressive and cute."

---

## After Generation

1. Download both composite sheet images
2. Save to `packs/chubby-mochi-hamster-2/`:
   - Sheet 1 → `composite_sheet_1.png`
   - Sheet 2 → `composite_sheet_2.png`
3. Run the split + process pipeline:
   ```bash
   # Split Sheet 1 (stickers 01-08)
   python scripts/split_stickers.py --pack-dir packs/chubby-mochi-hamster-2

   # Process all split stickers (bg removal, outline, text overlay, resize for all platforms)
   python scripts/sticker_processor.py --pack-dir packs/chubby-mochi-hamster-2
   ```
4. Run full pipeline (alternative — handles split + process + text + icons):
   ```bash
   python scripts/run_pipeline.py --pack-dir packs/chubby-mochi-hamster-2
   ```
5. Run preflight check:
   ```bash
   python scripts/line_preflight_check.py --pack-dir packs/chubby-mochi-hamster-2
   ```

### Text Overlay Notes

The text for each sticker is defined in `pack_config.py` under each sticker's
`"text"` field. The processing pipeline reads this and renders bold text with
dark stroke at the bottom of each sticker. This ensures:
- Crisp, readable text (no AI text rendering artifacts)
- Consistent font (FredokaOne-Regular) and positioning across all 16 stickers
- Easy to update text without regenerating images
- Per-sticker text colors defined in config (e.g., #5588CC for "STUDYING", #FF5566 for "BRAIN FULL")
