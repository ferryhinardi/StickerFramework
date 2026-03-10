# LINE Sticker Market Insights & Strategy Guide

> Research compiled from LINE Messaging API sticker reference and LINE Store marketplace analysis (March 2026).

## Executive Summary

Analysis of the LINE sticker ecosystem reveals clear patterns that can dramatically improve sticker pack success. The market strongly favors **animated stickers**, **cute animal characters**, **couple/romance themes**, and **series-based publishing strategies**. This document provides actionable insights for the StickerFramework pipeline.

---

## 1. Official LINE Messaging API Sticker Catalog

The LINE Messaging API provides 15 official sticker packages that bots can send for free. These represent LINE's view of "essential" sticker communication patterns:

### Package Summary

| Package ID | Title | Count | Theme |
|-----------|-------|-------|-------|
| 446 | Moon: Special Edition | 40 | Solo character, emotions |
| 789 | Sally: Special Edition | 40 | Solo character, emotions |
| 1070 | Moon: Special Edition | 40 | Regional variant |
| 6136 | LINE Characters: Making Amends | 24 | Apology/manners |
| 6325-6370 | Brown and Cony Fun Size Pack | 24 | Couple/romance (4 regional variants) |
| 6632 | LINE Characters: Making Amends | 24 | Apology/manners (variant) |
| 8515-8525 | LINE Characters: Pretty Phrases | 24 | Polite conversational phrases (3 variants) |
| 11537 | Brown & Cony & Sally: Animated | 40 | Animated trio |
| 11538 | CHOCO & Friends: Animated | 40 | Animated ensemble |
| 11539 | UNIVERSTAR BT21: Animated | 40 | Animated IP collab |

### Key Takeaways from Official Catalog

1. **Two standard sizes dominate**: 24 stickers (utility/themed) and 40 stickers (character showcase)
2. **Regional localization is a first-class strategy**: Same content published as separate packages for different markets (Japan, Thailand, Taiwan, Indonesia, etc.)
3. **Conversation utility drives selection**: Apology, polite phrases, and emotional expressions are considered essential
4. **Character pairs outperform solos**: Brown & Cony (couple) has 4x more package variants than solo characters

---

## 2. Marketplace Trends (LINE Store Analysis)

### What's Selling: Top Sticker Patterns

#### Format Popularity (Most to Least)
1. **Animation & Sound** - Premium tier, highest engagement
2. **Animation only** - ~70% of top sellers are animated
3. **Pop-Up Stickers** - Full-screen animated stickers
4. **Static Stickers** - Still viable but declining in top charts
5. **Custom/Name Stickers** - Personalization is a growing niche
6. **Message Stickers** - Customizable text overlays

**Critical Insight**: 11 out of 12 top creators' stickers are animated. Animation is no longer optional for competitive packs.

#### Theme/Category Rankings (by marketplace representation)

| Rank | Theme | Examples | Market Share |
|------|-------|----------|-------------|
| 1 | **Couples/Romance** | Milk & Mocha, Bobo & Lola, Brown & Cony, I LOVE U | ~35% of top sellers |
| 2 | **Cute Animals** | Bears, cats, hamsters, capybara, dinosaurs | ~25% of top sellers |
| 3 | **Meme/Humor** | Bocil MEME MODE, silly calico cat memes, Greensock | ~15% of top sellers |
| 4 | **Cute Girl Characters** | Olivia Chan, TuaGom, Syalala-chan | ~10% of top sellers |
| 5 | **Polite/Greetings** | Pretty Phrases, seasonal greetings | ~10% of top sellers |
| 6 | **IP/Brand Collabs** | Disney, Sanrio, BT21, Pokemon | ~5% of top sellers |

#### Most Popular Animal Characters
1. Bears (Milk & Mocha, Brown, Bobo)
2. Cats (calico memes, orange cat, ugly black cat)
3. Rabbits (Cony, various kawaii bunnies)
4. Dogs (Corgi, Beagle, trending in new releases)
5. Hamsters (Rocky, kawaii hamster series)
6. Capybara (Pipi capybara, trending)
7. Dinosaurs (dino in love, BabyDino)

---

## 3. Successful Creator Strategies

### Series-Based Publishing
Top creators build empires through sequential packs:
- **Milk & Mocha**: 7+ packs (Unstoppable Lovers, Custom Stickers, etc.)
- **Bobo & Lola**: 3+ packs (Lovely, Viral Couple, Cute Couple)
- **small eyes by Shiochan**: 11 packs in the series
- **Cute Duduu**: 5+ packs
- **Brown & Cony**: 4+ official packs

**Strategy**: Launch a character, build audience, then release sequel packs. Each pack reinforces the character brand. Our framework should support rapid sequel generation from established `pack_config.py` definitions.

### Regional Targeting
- Indonesian market shows the strongest engagement for creators' stickers
- Thai market is second largest for LINE stickers
- Localized text/greetings in stickers dramatically improves regional sales
- Same pack can be published as regional variants with different language titles

### Pricing Tiers
- Official packs: Free to Rp12,000-23,000 (Indonesian Rupiah)
- Creators' packs: Typically Rp12,000 for static, higher for animated
- Custom/Name stickers command premium pricing

---

## 4. Actionable Improvements for StickerFramework

### 4.1 Animation Support (HIGH PRIORITY)

**Current State**: Framework supports TGS (Lottie) and WEBM (VP9) for Telegram only.

**Recommended Changes**:
- Add LINE APNG (Animated PNG) generation to the pipeline
- LINE animated stickers: 320x270px APNG, max 300KB, 1-4 seconds
- Implement animation presets optimized for LINE's APNG format
- Priority presets: bounce, wiggle, pulse (most versatile for emotions)

### 4.2 Couple/Pair Character System (HIGH PRIORITY)

**Current State**: Pack configs define a single character.

**Recommended Changes**:
- Extend `pack_config.py` to support dual characters (primary + secondary)
- Add relationship-type field: `couple`, `friends`, `rivals`, `family`
- Generate interaction poses between two characters (hugging, high-five, arguing, etc.)
- Template sticker concepts for couple packs:
  - Shared emotions (both happy, both sad)
  - Complementary emotions (one comforting the other)
  - Interaction stickers (hugging, kissing, playing)
  - Individual reactions (for when used solo in chat)

```python
# Proposed pack_config.py extension
PACK_CONFIG = {
    "characters": [
        {"name": "Mocha", "role": "primary", "species": "bear", ...},
        {"name": "Milk", "role": "secondary", "species": "bear", ...}
    ],
    "relationship": "couple",
    "interaction_stickers": [
        {"id": "01_hug", "type": "interaction", "pose": "hugging each other"},
        {"id": "02_happy_together", "type": "shared_emotion", "emotion": "happy"},
        ...
    ]
}
```

### 4.3 Emotion/Conversation Coverage Matrix (MEDIUM PRIORITY)

Based on the official API stickers and marketplace trends, every successful pack covers these core conversation needs:

**Essential Emotion Set (minimum 8 for a viable pack)**:
1. Happy/Excited (jumping, sparkles)
2. Love/Heart (heart eyes, blowing kiss)
3. Sad/Crying (tears, droopy)
4. Angry/Frustrated (red face, steam)
5. Laughing/LOL (rolling, tears of joy)
6. Surprised/Shocked (wide eyes, jaw drop)
7. Sleepy/Tired (yawning, zzz)
8. Thumbs up/OK (approval gesture)

**Extended Emotion Set (for 24-40 sticker packs)**:
9. Thank you/Grateful
10. Sorry/Apologetic (bowing, sweating)
11. Confused/Thinking
12. Proud/Accomplished
13. Shy/Blushing
14. Eating/Hungry
15. Dancing/Celebrating
16. Waving hello/goodbye
17. Sick/Unwell
18. Working/Busy
19. Waiting/Bored
20. Praying/Hoping
21. Cool/Sunglasses
22. Scared/Hiding
23. Encouraging/Fighting!
24. Goodnight/Sweet dreams

**Recommendation**: Add an emotion coverage validator to the pipeline that checks if a pack config covers the essential set.

### 4.4 Visual Style Recommendations (MEDIUM PRIORITY)

Analysis of top sellers reveals these design principles:

**What Works**:
- **Chibi/SD proportions**: 1:1 to 1:1.5 head-to-body ratio (oversized head)
- **Minimal line work**: Clean outlines, not overly detailed
- **Bright, saturated colors**: Pastel backgrounds, vivid character colors
- **Exaggerated expressions**: Eyes 2-3x normal size for emotions
- **White outline/die-cut effect**: Creates sticker feel (already implemented)
- **Simple backgrounds**: Transparent or solid color, never complex scenes
- **Props for context**: Simple icons (hearts, stars, sparkles, sweat drops, anger veins)

**What Doesn't Work**:
- Photorealistic style (too detailed for small sticker size)
- Complex multi-character scenes (hard to read at 370x320)
- Dark/muted color palettes (low visibility in chat)
- Text-heavy stickers without universal appeal
- Religious or politically sensitive content (LINE guideline 3.13)

### 4.5 Pack Size Strategy (MEDIUM PRIORITY)

**Recommended approach based on market data**:
- **Launch pack**: 8 stickers (minimum viable, test market)
- **Standard pack**: 24 stickers (sweet spot for creators)
- **Premium pack**: 40 stickers (for established characters with proven audience)

**Our current default of 8 stickers is correct for initial launches** but we should plan for 24-sticker expansion packs as a standard follow-up.

### 4.6 Localization Support (LOW PRIORITY)

**Current State**: Packs are English-only.

**Recommended Changes**:
- Add `localization` field to pack_config.py for multi-language titles
- Priority markets: Indonesian (id), Thai (th), Japanese (ja), Traditional Chinese (zh_TW)
- Text stickers should have localized variants
- Metadata generation should output per-language LINE submission data

### 4.7 Meme Sticker Template System (LOW PRIORITY)

Growing trend of meme-style stickers suggests adding:
- Templates for reaction-meme style stickers
- Bold text overlay capability (already partially supported via text compositor)
- "Caption this" style sticker generator
- Trending meme format references for DALL-E prompts

---

## 5. Competitive Landscape Summary

### What Top Creators Do Differently

| Aspect | Average Creator | Top Creator |
|--------|----------------|-------------|
| Animation | Static only | Animation + Sound |
| Pack frequency | 1-2 packs total | 5-10+ packs per character |
| Character design | Generic kawaii | Distinctive, memorable silhouette |
| Emotion range | 4-6 emotions | 20+ emotions + situational |
| Localization | Single language | 3-5 languages |
| Series planning | Ad hoc | Planned seasonal/thematic releases |
| Social media | None | Instagram/Twitter character accounts |

### Market Gaps We Can Fill

1. **Capybara stickers** - Trending animal character with limited quality packs (our CappyCapybara pack is well-positioned)
2. **Work/Office stickers** - Limited animated options (our corporate-sloth and office-teddy-bear can be expanded)
3. **Food/Boba stickers** - Boba culture is huge in Southeast Asia (our boba-milo series aligns)
4. **Otter stickers** - Underrepresented despite being popular in Japanese kawaii culture

---

## 6. Recommended Next Steps

### Immediate (Next Pack)
1. Prioritize animated sticker generation for LINE (APNG support)
2. Create a couple/pair character pack (highest market demand)
3. Use 24-sticker pack size for next launch
4. Target Indonesian market with localized title

### Short-term (Next 3 Packs)
5. Build sequel packs for best-performing existing characters
6. Implement emotion coverage validator in pipeline
7. Add meme sticker template support

### Long-term (Framework Improvements)
8. APNG generation pipeline for LINE animated stickers
9. Multi-character interaction pose system
10. Regional variant auto-generation
11. Analytics integration to track which sticker emotions are most used

---

## Appendix: LINE Sticker Format Reference

| Format | Dimensions | Max Size | Duration | Notes |
|--------|-----------|----------|----------|-------|
| Static | 370x320 PNG | 1MB | - | Transparent BG required |
| Animated (APNG) | 320x270 APNG | 300KB | 1-4s | Loop or play once |
| Pop-up | 320x270 APNG | 2.5MB | 1-5s | Full-screen effect |
| Custom/Name | 370x320 PNG | 1MB | - | Text replacement areas |
| Message | 370x320 PNG | 1MB | - | Editable text overlay |
| Sound | 370x320 PNG + MP3 | 1MB+300KB | - | Audio plays on send |

> **Source**: LINE Creators Market documentation + LINE Messaging API sticker list
> **Last Updated**: March 2026
