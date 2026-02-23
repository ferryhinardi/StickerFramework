# ChatGPT Prompt Templates

> Ready-to-use prompts for generating LINE sticker pack ideas and DALL-E composite sheets.

## How to Use These Prompts

1. Open ChatGPT with the **Go plan** ($5/month — GPT-5.2 Instant + DALL-E access)
2. Copy-paste the relevant prompt below
3. Replace placeholder text in `[BRACKETS]` with your specifics
4. ChatGPT will return structured output you can use directly

### ChatGPT Go Plan Notes

- **Model**: GPT-5.2 Instant (the Go plan does not include Thinking or Pro models)
- **DALL-E**: Image generation included with expanded limits (more than Free, not unlimited)
- **Context window**: 32K tokens — sufficient for ideation + DALL-E generation in one conversation
- **Cost**: $5/month — no per-image API charges when using the ChatGPT UI
- **Limitation**: Response times are not prioritized (same as Free tier). During peak hours, generations may be slower.
- **Ads**: The Go plan may include ads in the interface

All prompts are designed to produce output that fits LINE's metadata constraints:

- Title: max 40 characters
- Description: max 160 characters
- Sticker count: 8 per pack (LINE minimum, fastest to produce)

---

## Prompt 1: Sticker Pack Ideation

Use this to generate a complete sticker pack concept from scratch.

### The Prompt

```
I want to create a LINE sticker pack. Help me design a pack with these constraints:

- Exactly 8 stickers per pack
- Characters should be [STYLE: e.g., "cute/kawaii", "funny/humorous", "cool/trendy"]
- Theme: [THEME: e.g., "two cute otters as a couple", "chubby hamster office worker",
  "angel character with daily blessings"]
- Target audience: [AUDIENCE: e.g., "couples", "office workers", "religious community",
  "friends", "family"]

Please output in this exact format:

**Pack Title**: [title, max 40 characters including spaces]
**Description**: [description, max 160 characters including spaces]
**Style Category**: [one of: Cute, Cool, Natural, Pop, Weird, Other]
**Character Category**: [one of: Characters, Animals, People, Families & Couples, Other]

Stickers:
1. [short_name] -- [emotion/text label] -- [visual description of pose, expression, props]
2. [short_name] -- [emotion/text label] -- [visual description]
3. [short_name] -- [emotion/text label] -- [visual description]
4. [short_name] -- [emotion/text label] -- [visual description]
5. [short_name] -- [emotion/text label] -- [visual description]
6. [short_name] -- [emotion/text label] -- [visual description]
7. [short_name] -- [emotion/text label] -- [visual description]
8. [short_name] -- [emotion/text label] -- [visual description]

Requirements for good sticker concepts:
- Each sticker should express a distinct, commonly-used emotion or reaction
- Stickers should be useful in everyday chat conversations
- Cover a range: greetings, reactions, emotions, farewells
- Avoid niche scenarios that won't get used often
- The short_name should be a 1-2 word snake_case identifier (e.g., good_morning, love_you)
```

### Example Output

For input: Theme = "two cute otters as a couple", Audience = "couples"

```
**Pack Title**: Boba & Milo Cheerful Otter Duo
**Description**: A fun, caring otter duo bringing cheerful energy to
couples and coworkers. Perfect for daily chats, teamwork moments,
and wholesome support.
**Style Category**: Cute
**Character Category**: Families & Couples

Stickers:
1. good_morning -- Good Morning -- Both otters stretching with sleepy eyes, small sun icon
2. love_you -- Love You -- Otters forming a heart shape with their tails, pink cheeks
3. lets_eat -- Let's Eat! -- Otters excitedly sharing a bowl of ramen, chopsticks in paws
4. fighting -- Fighting! -- Otter with determined face and raised fist, sparkle effects
5. miss_you -- Miss You -- Sad otter looking at phone, thought bubble with partner
6. thank_you -- Thank You -- Otter bowing politely with a small gift box
7. good_night -- Good Night -- Both otters cuddling under a blanket, stars and moon
8. bye_bye -- Bye Bye -- Otter waving enthusiastically with both paws
```

---

## Prompt 2: DALL-E Composite Sheet Generation

Use this **immediately after** Prompt 1 in the same conversation. ChatGPT already has context about your sticker concepts.

### The Prompt

```
Now generate all 8 stickers as a SINGLE image arranged in a 2x4 grid
(2 columns, 4 rows) on a clean white background.

Requirements:
- Each sticker is a separate, clearly distinct illustration
- Clean white background between ALL stickers (no overlapping, no touching)
- Generous white space (at least 50px equivalent gap) between each sticker
- Each sticker has a thick white outline border (die-cut sticker style)
- NO text, NO words, NO letters, NO numbers in any sticker
- Kawaii/cute flat-color style with thick uniform black outlines
- Each character should be fully contained within its grid cell (not cut off)
- Consistent art style, proportions, and color palette across all 8 stickers
- Square aspect ratio for the overall image
- Each sticker roughly same size within its cell

Generate based on the 8 sticker descriptions above.
```

### Tips for Better Results

- **Stay in the same conversation** — ChatGPT remembers the sticker descriptions
- **Square aspect ratio** — Say "square" explicitly so DALL-E doesn't crop
- **No text emphasis** — DALL-E sometimes adds text; repeat "NO text" if it happens
- If the first generation isn't perfect, say: "Regenerate with more space between stickers and make sure no stickers are cut off at the edges"

---

## Prompt 3: Sequel Pack (Same Characters, New Emotions)

Use this when creating Pack 2, 3, 4, etc. of the same character series.

### The Prompt

```
I want to create a sequel sticker pack for my existing series:
"[SERIES NAME]" (this will be pack #[N] in the series).

The characters are: [BRIEF CHARACTER DESCRIPTION from previous packs]
Art style: [STYLE DESCRIPTION: e.g., "kawaii, thick outlines, flat colors,
chibi proportions"]

Previous packs already covered these emotions (DO NOT repeat):
- Pack 1: good_morning, love_you, lets_eat, fighting, miss_you, thank_you,
  good_night, bye_bye
- Pack 2: sorry, surprise, angry, hungry, celebrate, study, exercise, lazy
[Add more packs if applicable]

Create 8 NEW sticker concepts that:
- Feature the same characters in the same art style
- Express different emotions/reactions not covered above
- Are useful in everyday chat conversations
- [OPTIONAL THEME: e.g., "Ramadan-themed", "holiday season", "work from home"]

Output in the same format:
**Pack Title**: [series name + number, max 40 chars]
**Description**: [max 160 chars, different from previous packs]
...
```

### Example: Creating "Boba & Milo 5" (Ramadan Theme)

```
Series: "Boba & Milo Cheerful Otter Duo" (pack #5)
Characters: Two cute otters, Boba (slightly rounder) and Milo (taller)
Art style: Kawaii, thick outlines, flat colors, pastel tones
Theme: Ramadan activities and greetings

Previous emotions covered: [list from packs 1-4]
```

---

## Prompt 4: Seasonal/Holiday Pack

Use this for themed packs tied to specific holidays or events.

### The Prompt

```
Create a [HOLIDAY/SEASON]-themed LINE sticker pack with these constraints:

- Exactly 8 stickers
- Characters: [CHARACTER DESCRIPTION or "create new characters"]
- Holiday/Season: [e.g., "Ramadan", "Christmas", "Valentine's Day",
  "Chinese New Year", "Back to School", "Summer Vacation"]
- Art style: Kawaii/cute with thick outlines, flat colors
- Each sticker should reference a specific [HOLIDAY] activity or greeting
- Stickers should still be useful in everyday chat (not too niche)

Output format:
**Pack Title**: [title, max 40 chars, include holiday reference]
**Description**: [max 160 chars]
**Style Category**: Cute
**Character Category**: [appropriate category]

Stickers:
1-8: [same format as Prompt 1]

Holiday-specific sticker ideas to consider:
- Holiday-specific greetings
- Traditional activities
- Food/feast related
- Counting down / anticipation
- Celebration / party
- Gift giving
- Family/togetherness
- Post-holiday (back to normal)
```

### Seasonal Calendar

| Month   | Holiday/Event              | Target Audience   |
| ------- | -------------------------- | ----------------- |
| Jan     | New Year, Chinese New Year | General, Asian    |
| Feb     | Valentine's Day            | Couples           |
| Mar-Apr | Ramadan (varies)           | Muslim community  |
| Apr     | Easter, Eid                | Religious         |
| May     | Mother's Day               | Family            |
| Jun     | Father's Day, Summer       | Family, General   |
| Jul-Aug | Summer Vacation            | General           |
| Sep     | Back to School             | Students, Parents |
| Oct     | Halloween                  | General           |
| Nov     | Thanksgiving               | Western           |
| Dec     | Christmas, Year-End        | General           |

---

## Prompt 5: Batch Ideation (Multiple Packs at Once)

Use this when you want to plan several packs in one session.

### The Prompt

```
I want to create [N] different LINE sticker packs to publish this week.
Each pack should have a different theme and character.

For each pack, provide:
- Pack title (max 40 characters)
- Short description (max 160 characters)
- Style category (Cute/Cool/Pop/etc.)
- Character category
- Brief character concept (1 sentence)
- List of 8 sticker emotions/reactions

Requirements:
- Each pack should target a different audience
- Mix of animals, people, and fantasy characters
- All in kawaii/cute style
- Variety in themes: everyday life, work, romance, humor, inspirational

Output as a numbered list of packs.
```

---

## Quality Checklist for ChatGPT Output

Before proceeding to DALL-E generation, verify:

- [ ] Title is under 40 characters (count spaces)
- [ ] Description is under 160 characters (count spaces)
- [ ] Exactly 8 sticker concepts listed
- [ ] Each sticker has a distinct emotion (no duplicates like "happy" and "joyful")
- [ ] Good coverage: at least 1 greeting, 1 reaction, 1 emotion, 1 farewell
- [ ] All stickers would be useful in everyday chat (not too niche)
- [ ] Short names are snake_case and unique
- [ ] Style/character categories match LINE's options
- [ ] For sequels: no emotions repeated from previous packs

## Tips for Consistent Quality

1. **Be specific about art style** — "kawaii with thick black outlines and flat colors" gives much better results than just "cute"
2. **Name your characters** — Having names (Boba & Milo, Mochi, etc.) helps ChatGPT maintain consistency across packs
3. **Reference existing packs** — When making sequels, briefly describe what previous packs looked like
4. **Ask for revisions** — If a sticker concept is weak, say "Replace sticker #5 with something more universally useful"
5. **Save the conversation** — You'll reference it when using Prompt 2 for DALL-E generation
