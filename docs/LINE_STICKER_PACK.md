# LINE Sticker Pack — Image Upload Requirements

> Reference: [LINE Creators Market Guidelines](https://creator.line.me/en/guideline/sticker/)

This document defines the image specifications for all LINE sticker types so our upload feature can validate and batch-upload every image in a sticker pack.

---

## 1. Sticker Types Overview

| Type              | Sticker Counts       | Sticker Format                | Has Animation?    |
| ----------------- | -------------------- | ----------------------------- | ----------------- |
| Static Stickers   | 8, 16, 24, 32, or 40 | PNG                           | No                |
| Animated Stickers | 8, 16, or 24         | APNG                          | Yes               |
| Custom Stickers   | 8, 16, 24, 32, or 40 | PNG                           | No                |
| Message Stickers  | 8, 16, or 24         | PNG                           | No                |
| Big Stickers      | 8, 16, 24, 32, or 40 | PNG                           | No                |
| Pop-up Stickers   | 8, 16, or 24         | PNG (sticker) + APNG (pop-up) | Yes (pop-up only) |
| Effect Stickers   | 8, 16, or 24         | PNG (sticker) + APNG (effect) | Yes (effect only) |

---

## 2. Required Images Per Pack

Every sticker pack submission requires **three categories** of images. For Pop-up and Effect types, additional animated images are needed.

### 2.1 Common Images (all types)

| Image               | Qty | Size (px) | Format | Max File Size |
| ------------------- | --- | --------- | ------ | ------------- |
| Main Image          | 1   | 240 x 240 | PNG    | 1 MB          |
| Chat Thumbnail Icon | 1   | 96 x 74   | PNG    | 1 MB          |

### 2.2 Sticker Images (per type)

| Type                 | Size (px)                   | Format | Notes                             |
| -------------------- | --------------------------- | ------ | --------------------------------- |
| Static               | Up to 370 x 320             | PNG    | Even-numbered width & height      |
| Animated             | Up to 320 x 270             | APNG   | Width or height must be >= 270 px |
| Custom               | Up to 370 x 320             | PNG    | Same as static                    |
| Message              | Up to 370 x 320             | PNG    | Same as static                    |
| Big                  | Min 80 x 524, Max 396 x 660 | PNG    | Taller portrait orientation       |
| Pop-up (sticker)     | Up to 370 x 320             | PNG    | Displayed in chat                 |
| Pop-up (pop-up anim) | 480 x 480 (max)             | APNG   | Plays across whole chat screen    |
| Effect (sticker)     | Up to 370 x 320             | PNG    | Displayed in chat                 |
| Effect (effect anim) | 480 x 480 (max)             | APNG   | Plays in chat background          |

### 2.3 Total Image Count Per Pack

For a pack with **N** stickers:

| Type                  | Total Files                                                                     |
| --------------------- | ------------------------------------------------------------------------------- |
| Static / Custom / Big | N + 2 (N stickers + main + thumbnail)                                           |
| Animated              | N + 2                                                                           |
| Message               | N + 2                                                                           |
| Pop-up                | (N stickers + N pop-up APNG) + pop-up main APNG + main + thumbnail = **2N + 3** |
| Effect                | (N stickers + N effect APNG) + effect main APNG + main + thumbnail = **2N + 3** |

---

## 3. Global Constraints

| Constraint              | Value                                                                                                                   |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| File format             | PNG (`.png`); animated uses APNG with `.png` extension                                                                  |
| Color mode              | RGB                                                                                                                     |
| Resolution              | >= 72 dpi                                                                                                               |
| Background              | Transparent                                                                                                             |
| Width & height          | Must be even numbers                                                                                                    |
| Max file size per image | 1 MB                                                                                                                    |
| Max ZIP file size       | 60 MB                                                                                                                   |
| Sticker margin          | ~10 px padding between trimmed edge and content (static/custom). Auto-added for message, big, pop-up, and effect types. |

---

## 4. Animation Constraints (Animated / Pop-up / Effect)

| Constraint         | Animated                  | Pop-up / Effect                                                                   |
| ------------------ | ------------------------- | --------------------------------------------------------------------------------- |
| Loops              | 1 -- 4                    | 1 -- 3                                                                            |
| Max playback time  | 4 seconds                 | 3 seconds                                                                         |
| Frames per APNG    | 5 -- 20                   | 5 -- 20                                                                           |
| Min dimension rule | Width or height >= 270 px | One axis exactly 480 px; if width=480, height >= 320; if height=480, width >= 200 |

- All frames must not be identical (causes upload error).
- Use APNG Assembler or equivalent tool; output extension must be `.png`.

---

## 5. Text Metadata

| Field               | Max Length     |
| ------------------- | -------------- |
| Creator Name        | 50 characters  |
| Sticker Title       | 40 characters  |
| Sticker Description | 160 characters |
| Copyright           | 50 characters  |

- Asian characters and some symbols count as **2 characters** each.

---

## 6. ZIP File Structure

When uploading via ZIP, the file must contain all images for the pack. The recommended naming convention:

```
sticker_pack.zip
  ├── main.png              # 240 x 240 main image
  ├── tab.png               # 96 x 74 chat thumbnail icon
  ├── 01.png                # sticker image 1
  ├── 02.png                # sticker image 2
  ├── ...
  ├── {NN}.png              # sticker image N
  │
  │  (Pop-up / Effect only)
  ├── popup_main.png        # 480 x 480 APNG pop-up main  (or effect_main.png)
  ├── popup_01.png          # 480 x 480 APNG pop-up image (or effect_01.png)
  ├── popup_02.png
  └── ...
```

---

## 7. Upload Feature Requirements

Our application should support batch-uploading all images for a sticker pack. The following validations must be enforced **before** upload:

### 7.1 Pre-Upload Validation

1. **Sticker type selection** -- user picks one of the 7 types.
2. **Sticker count selection** -- user picks from allowed counts for the chosen type.
3. **File count validation** -- total files must match expected count (see Section 2.3).
4. **File format validation** -- all files must be `.png`. APNG files are also `.png`.
5. **Dimension validation** -- each image must conform to the size constraints for its role (main, thumbnail, sticker, animation).
6. **Even dimension check** -- width and height must both be even numbers.
7. **File size validation** -- each file <= 1 MB.
8. **Total ZIP size validation** -- combined size of all files <= 60 MB.
9. **Transparent background check** -- verify PNG has alpha channel.
10. **Animation validation** (animated/pop-up/effect):
    - Frame count: 5 -- 20 frames.
    - Not all frames identical.
    - Playback time within limit (4s for animated, 3s for pop-up/effect).

### 7.2 Upload Flow

1. User selects sticker type and count.
2. User uploads images (drag & drop or file picker), assigning each to its role:
   - Main image
   - Chat thumbnail icon
   - Sticker images (ordered 01..N)
   - Pop-up/Effect animation images (if applicable)
   - Pop-up/Effect main animation (if applicable)
3. Client validates all images against rules in Section 7.1.
4. If all pass, bundle into ZIP and upload.
5. Display per-image validation errors inline so user can fix individual files.

### 7.3 Image Role Detection (suggested)

To simplify UX, auto-detect image roles based on dimensions:

| Detected Dimensions                      | Assigned Role                   |
| ---------------------------------------- | ------------------------------- |
| Exactly 240 x 240                        | Main Image                      |
| Exactly 96 x 74                          | Chat Thumbnail Icon             |
| Exactly 480 x 480 (APNG)                 | Pop-up/Effect main animation    |
| <= 480 x 480 (APNG, not 240x240)         | Pop-up/Effect sticker animation |
| <= 370 x 320 (PNG, not 240x240 or 96x74) | Sticker image                   |
| <= 320 x 270 (APNG)                      | Animated sticker image          |
| 80-396 x 524-660                         | Big sticker image               |

Allow manual override for ambiguous cases.

---

## 8. Content Guidelines (for reference)

- No advertising, product release dates, or corporate-logo-only stickers.
- No personal data or ID collection requirements.
- No content from other internet services or messenger apps.
- No content that offends public morality, depicts underage drinking/smoking, sexual/violent imagery, or fuels nationalism.
- Stickers should be easy to use in daily conversation.
- See [LINE Review Process Guidelines](https://creator.line.me/en/review_guideline/) for the full policy.

---

## 9. Reference Links

- [Static Sticker Guidelines](https://creator.line.me/en/guideline/sticker/)
- [Animated Sticker Guidelines](https://creator.line.me/en/guideline/animationsticker/)
- [Custom Sticker Guidelines](https://creator.line.me/en/guideline/customsticker/)
- [Message Sticker Guidelines](https://creator.line.me/en/guideline/messagesticker/)
- [Big Sticker Guidelines](https://creator.line.me/en/guideline/bigsticker/)
- [Pop-up Sticker Guidelines](https://creator.line.me/en/guideline/popupsticker/)
- [Effect Sticker Guidelines](https://creator.line.me/en/guideline/effectsticker/)
- [Review Process Guidelines](https://creator.line.me/en/review_guideline/)
