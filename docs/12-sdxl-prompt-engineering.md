# SDXL Prompt Engineering — Cappy the Chill Capybara

A comprehensive record of prompt engineering experiments for generating kawaii capybara stickers using **DreamShaper XL Turbo v2.1** via ComfyUI. This document captures 13+ iterations of prompt refinement, the discoveries made, and the final proven template.

## Table of Contents

- [Setup](#setup)
- [Goal](#goal)
- [Key Visual Requirements](#key-visual-requirements)
- [Final Proven Prompt Template](#final-proven-prompt-template)
- [Optimal Settings](#optimal-settings)
- [Prompt Architecture](#prompt-architecture)
- [Experiment Log](#experiment-log)
- [Core Discoveries](#core-discoveries)
  - [Orange Placement (The Hardest Problem)](#orange-placement-the-hardest-problem)
  - [Expression/Eye Control](#expressioneye-control)
  - [Style and Background](#style-and-background)
  - [Prompt Length Effects](#prompt-length-effects)
- [Negative Prompt Engineering](#negative-prompt-engineering)
- [SDXL Limitations](#sdxl-limitations)
- [Recommendations for Future Packs](#recommendations-for-future-packs)

---

## Setup

| Component | Value |
|-----------|-------|
| Model | DreamShaperXL_Turbo_v2_1.safetensors |
| Backend | ComfyUI (local, Apple Silicon) |
| API URL | `http://127.0.0.1:8000` |
| Resolution | 1024x1024 |
| Sampler | dpmpp_sde / karras |
| Script | `scripts/comfyui_generator.py` |

## Goal

Generate a "Good Morning" sticker (01_good_morning) featuring:
- A cute kawaii capybara (chibi proportions)
- A tiny orange fruit (mikan) sitting on top of its head
- Sleepy/yawning expression (just woke up)
- Pure white background, no border/frame
- Flat vector art style with thick outlines

Once perfected, the prompt template would be applied to all 16 stickers in the pack.

## Key Visual Requirements

| # | Requirement | Difficulty | Status |
|---|-------------|-----------|--------|
| 1 | Orange on HEAD (as fruit, not hat) | EXTREME | Partial -- orange present but hat-shaped |
| 2 | Sleepy/yawning expression | Medium | Solved (attempt #8) |
| 3 | No circular border/frame | Easy | Solved (attempt #5) |
| 4 | No whiskers | Medium | Solved (negative weighting) |
| 5 | Capybara-like (not hamster/cat) | Easy | Solved (species emphasis) |
| 6 | Flat kawaii style | Easy | Solved (style prefix) |
| 7 | Pure white background | Easy | Solved (weighted + negatives) |

## Final Proven Prompt Template

**Best result: Attempt #10, seed 88** -- closed eyes, orange on head, white bg, no frame, no whiskers.

### Positive Prompt

```
kawaii chibi character illustration, flat colors, no gradients, vector art style,
(solid pure white background:1.3), single character centered, masterpiece, best quality,
(closed eyes yawning:1.5), (drowsy sleepy face:1.4),
(cute round chubby round capybara:1.3),
(wearing tiny orange fruit as hat on head:1.4),
warm brown fur, soft pink cheeks, small round ears,
potato-shaped body, tiny stubby legs,
({POSE_DESCRIPTION}:1.2),
flat colors, thick dark outline, simple minimal design, no text, no words, no letters
```

### Negative Prompt

```
text, words, letters, numbers, alphabet, writing, caption, label, watermark, signature, logo,
sticker, die-cut sticker, circular frame, circular border, round frame, badge, emblem, stamp,
die-cut border, sticker outline, white border, cut-out shape, border, frame,
blurry, low quality, low resolution, jpeg artifacts,
realistic, photograph, photorealistic, 3d render, gradient shading,
complex background, detailed background, patterned background,
gray background, beige background, colored background, dark background,
green background, sage background, blue background,
multiple characters, duplicate,
ugly, deformed, disfigured, bad anatomy, bad proportions, extra limbs, extra fingers, mutated,
(whiskers:1.4), cat whiskers, long whiskers, prominent whiskers, facial hair,
cat, feline, hamster, beaver,
holding fruit, carrying orange, orange in hands, orange in paws,
two oranges, multiple oranges, second orange,
large orange, big orange, orange covering head,
floating orange, orange above head, orange in air,
(wide open eyes:1.3), (open eyes:1.2), awake, alert, energetic, staring, surprised look,
tongue out, playful,
orange helmet, orange hat covering head, orange hat with brim, hat brim, cap brim, visor,
knit hat, beanie, winter hat, bucket hat,
nsfw, violence
```

### Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| Steps | 8 | Sweet spot for Turbo model |
| CFG | 2.0 | Low CFG required for Turbo |
| Sampler | dpmpp_sde | Best quality for SDXL Turbo |
| Scheduler | karras | Standard for SDXL |
| Seed | 88 | Best seed found for sticker 01 |

## Prompt Architecture

The prompt is structured in attention-priority order (SDXL pays most attention to early tokens):

```
1. STYLE PREFIX     — Medium/format keywords (highest attention)
2. EMOTION          — Expression tokens with high weight (1.4-1.5)
3. CHARACTER        — Species + signature accessory
4. POSE             — Per-sticker action description
5. STYLE SUFFIX     — Technical reinforcement (lowest attention)
```

Key structural decisions:
- **Emotion BEFORE character** -- ensures sleepy expression isn't lost
- **"character illustration" NOT "sticker"** -- "sticker" triggers circular badge framing
- **Minimal token count** -- SDXL Turbo degrades with long prompts
- **Parenthetical weighting** -- 1.3-1.5 range for critical features

## Experiment Log

| # | Seed | Steps/CFG | Orange | Sleepy Eyes | Yawn | White BG | No Frame | No Whiskers | Key Change |
|---|------|-----------|--------|-------------|------|----------|----------|-------------|------------|
| 1 | 200 | 8/2.0 | beside body | wide open | no | no | circle frame | cat-like | Original prompt |
| 2 | 42 | 8/2.0 | hat+hands | wide open | no | ? | ? | no | Simplified prompt |
| 3 | 42 | 8/2.0 | hands only | wide open | no | ? | ? | no | Further simplified |
| 4 | 100 | 12/3.5 | none | wide open | no | blue | circle | yes | Higher steps/CFG |
| 5 | 55 | 8/2.0 | **on head (hat)** | wide open | no | sage green | **yes** | yes | "wearing...as hat" breakthrough |
| 6 | 55 | 8/2.0 | none | wide open | no | **white** | yes | no | "mikan sitting on" -- failed |
| 7 | 77 | 8/2.0 | **on head (hat)** | wide open | open mouth | **white** | yes | yes | Best pre-eyes-fix |
| 8 | 88 | 8/2.0 | floating | **closed** | **yes** | white | yes | yes | "closed eyes" breakthrough |
| 9 | 88 | 8/2.0 | none | closed | partial | white | yes | yes | "on head" w/o "as hat" = no orange |
| **10** | **88** | **8/2.0** | **on head (hat)** | **closed** | **partial** | **white** | **yes** | **yes** | **BEST OVERALL** |
| 11 | 99 | 8/2.0 | none | closed | big yawn | white | yes | no | "resting on head" = no orange |
| 12a | 88 | 8/2.0 | hat w/ brim | happy | no | white | yes | yes | "round spherical" diluted expression |
| 12b | 100 | 8/2.0 | knit beanie | happy | no | gray | yes | minor | Worst result |
| 12c | 120 | 8/2.0 | bucket hat | happy | no | white | yes | prominent | Full hat + whiskers |
| 12d | 55 | 8/2.0 | bucket hat | squinty | no | white | yes | yes | Textured bucket hat |
| 13a | 88 | 8/2.0 | cap w/ brim | happy | no | white | yes | yes | "as cap" = "as hat" in CLIP |
| 13b | 77 | 8/2.0 | cap w/ brim | happy | happy mouth | white | yes | yes | Confirmed cap = hat |

## Core Discoveries

### Orange Placement (The Hardest Problem)

This was the most challenging aspect of the entire project. SDXL's CLIP text encoder fundamentally struggles with spatial "object A sitting on top of object B" relationships.

**What works:**
- `"wearing tiny orange fruit as hat on head"` -- the ONLY phrasing that reliably places an orange on the capybara's head. SDXL's CLIP encoder needs the "hat" concept to understand head placement.

**What doesn't work (orange disappears entirely):**
- `"small mikan orange fruit sitting on top of head"` (attempt #6)
- `"wearing tiny round orange on head"` without "as hat" (attempt #9)
- `"a small round orange fruit resting on its head"` (attempt #11)

**What partially works (orange present but wrong shape):**
- `"wearing small orange fruit as hat on head"` -- orange present, hat-shaped with brim
- `"wearing small round spherical orange fruit as hat"` -- made it WORSE (knit beanie/bucket hat)
- `"wearing tiny orange fruit as cap on head"` -- "cap" = "hat" in CLIP space

**Root cause:** SDXL's CLIP encoder maps "fruit on head" to the nearest learned concept, which is "hat." The model literally cannot separate "something round sitting on head" from "headwear." Adding adjectives like "round" or "spherical" don't override this -- they just add noise and degrade other prompt elements.

**Accepted compromise:** The orange has a slight brim/hat edge in the best result (attempt #10). This is a minor artifact that can be touched up in post-processing if needed.

### Expression/Eye Control

**Breakthrough: Binary states over gradients.**

SDXL Turbo understands "closed eyes" far better than "half-closed droopy eyes." Across attempts #1-#7, every variation of "half-closed," "droopy," "sleepy-looking" eyes resulted in wide-open eyes.

| Phrasing | Result |
|----------|--------|
| `half-closed droopy eyes` | Wide open eyes (7 consecutive failures) |
| `sleepy eyes` | Wide open eyes |
| `(closed eyes yawning:1.5)` | **Closed eyes** (works reliably) |

Key technique: **Weight the expression at 1.5** and place it BEFORE the character description. SDXL's attention mechanism prioritizes earlier tokens, so emotion tokens must come before species/body tokens.

Additional reinforcement via negatives:
```
(wide open eyes:1.3), (open eyes:1.2), awake, alert, energetic, staring
```

### Style and Background

**"sticker" is a trap word.** Including "sticker" in the positive prompt triggers SDXL to render a circular badge/die-cut frame around the character (attempts #1, #4). Replacing with "character illustration" completely eliminates this.

**Background color control** requires both positive emphasis and negative blocking:
- Positive: `(solid pure white background:1.3)`
- Negative: `green background, sage background, blue background, gray background, beige background, colored background, dark background`

Without the negative list, SDXL defaults to sage green or soft blue backgrounds for "cute animal" subjects.

### Prompt Length Effects

**SDXL Turbo is extremely sensitive to prompt length.** Attempt #12 proved this definitively:

- Attempt #10 prompt (shorter): closed eyes, sleepy face -- correct expression
- Attempt #12 prompt (added "round spherical"): happy face, no sleepiness -- expression completely regressed

Adding just 2 extra tokens ("round spherical") to the orange description diluted attention away from the expression tokens `(closed eyes yawning:1.5)`. The model has a finite attention budget, and every token competes.

**Rule of thumb:** Keep the positive prompt under ~80 tokens. Front-load the most important features. Cut ruthlessly.

## Negative Prompt Engineering

The negative prompt grew organically through 13 iterations. Key categories:

| Category | Tokens | Why Needed |
|----------|--------|------------|
| Text/watermarks | text, words, letters, watermark, logo | SDXL often adds text artifacts |
| Frame/border | sticker, die-cut sticker, circular frame, badge | Prevents sticker-shaped framing |
| Realism | realistic, photograph, 3d render | Keeps flat art style |
| Background | green/sage/blue/gray background | Forces white bg |
| Wrong species | cat, feline, hamster, beaver | Prevents species drift |
| Whiskers | (whiskers:1.4), cat whiskers | Capybaras don't have prominent whiskers |
| Orange misplacement | holding fruit, orange in hands, floating orange | Prevents wrong orange position |
| Hat artifacts | hat brim, visor, knit hat, beanie, bucket hat | Reduces hat-like features on orange |
| Expression | (wide open eyes:1.3), awake, alert | Prevents sleepy->happy regression |

**Weighted negatives** (parenthetical emphasis) are essential for persistent problems like whiskers and open eyes. Standard negatives weren't strong enough.

## SDXL Limitations

Limitations discovered during this project that apply broadly:

1. **Poor spatial reasoning** -- SDXL cannot reliably place one object on top of another unless the combination maps to a known concept (e.g., "hat on head"). "Fruit sitting on head" is not a strong enough concept in CLIP's training data.

2. **Binary > gradient for features** -- "closed eyes" works, "half-closed eyes" doesn't. SDXL understands discrete states better than continuous ones.

3. **Attention is zero-sum** -- Adding tokens to describe feature A degrades feature B. Prompt engineering is fundamentally about budget allocation.

4. **Turbo models need low CFG** -- CFG 2.0 with 8 steps is the sweet spot. Higher CFG (3.5) and steps (12) caused regression, not improvement.

5. **Seed sensitivity is extreme** -- The same prompt produces dramatically different results across seeds. Seed 88 was the "golden seed" for this character; seed 99 produced a completely different style.

6. **"sticker" triggers framing** -- The word "sticker" in SDXL prompts activates the "sticker = die-cut badge" concept, adding unwanted circular frames.

## Recommendations for Future Packs

1. **Start with the proven template** -- Use the prompt architecture (style > emotion > character > pose > style suffix) as a starting point.

2. **Test 4-5 seeds early** -- Seeds 42, 55, 77, 88, 100 gave a good spread of variation. Find your "golden seed" early.

3. **Keep prompts short** -- Under 80 tokens positive. Front-load what matters.

4. **Use binary descriptors** -- "closed eyes" not "half-closed eyes." "open mouth" not "slightly open mouth."

5. **Build negatives incrementally** -- Start with the base negative set, then add specific negatives as problems appear.

6. **For complex spatial requirements (object on object)** -- Consider DALL-E 3 instead. It handles spatial relationships ("orange sitting on head") vastly better than SDXL. The `dalle_prompts.md` file contains pre-written prompts as a fallback.

7. **For head accessories that aren't hats** -- This remains an unsolved problem in SDXL. The workaround is to use "as hat" and accept minor hat artifacts, or composite in post-processing.
