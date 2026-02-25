"""
Sticker Pack Configuration — Cappy the Chill Capybara Vol.3: Chatty Cappy
=========================================================================
Same beloved Cappy, now with 16 TEXT-BASED chat stickers.
Every sticker features bold, readable text — designed for fast chat replies.

Strategy:
  - VOL 1 = pure emotion stickers (no text)
  - VOL 2 = sassy reply stickers (mixed text/no-text)
  - VOL 3 = ALL text stickers — every single one has a word/phrase
  - Covers everyday phrases not yet in v1/v2: greetings, food talk,
    mood updates, weekend/work transitions, relatable daily moments
  - Text-heavy packs outsell pure-emotion packs 2:1 on LINE (Asian markets)
  - Short 1-3 word phrases for instant readability at small sizes
"""

# =============================================================================
# CHARACTER DEFINITION  (identical to v1/v2 — brand consistency)
# =============================================================================
CHARACTER = {
    "name": "Cappy",
    "species": "round capybara",
    "body_color": "#C4956A",  # warm brown
    "blush_color": "#FFB4B4",  # soft pink
    "outline_color": "#4A3728",  # dark brown
    "eye_style": "small round black dot eyes, calm and content, slightly droopy for chill vibes",
    "accessory": "tiny orange (mikan) sitting on top of head — the iconic capybara meme",
    "proportions": "chibi, very round body like a potato, tiny stubby legs, head is 50% of body height",
    # v2 fields — used by comfyui_generator for character-agnostic prompts
    "body_description": (
        "a single cute round chibi capybara character, warm brown fur, "
        "small round black dot eyes, calm and content expression, "
        "tiny orange mikan fruit sitting on top of head, "
        "very round potato-shaped body, tiny stubby legs, "
        "small rounded ears, short flat snout, "
        "thick dark brown outline, flat colors, no gradients"
    ),
    "features": [
        "small rounded ears on top of head",
        "short flat nose/snout",
        "tiny tail (barely visible)",
        "soft gradient-free flat coloring",
    ],
    # legacy field kept for backward compatibility
    "extra_features": (
        "small rounded ears on top of head, "
        "short flat nose/snout, "
        "tiny tail (barely visible), "
        "soft gradient-free flat coloring"
    ),
}

# =============================================================================
# ART STYLE  (identical to v1/v2 — visual consistency)
# =============================================================================
STYLE = {
    "art_style": "flat_vector",  # v2 field — controls prompt template selection
    "outline_type": "thick uniform dark brown outline, consistent 3-4px width",
    "coloring": "flat colors only, absolutely no gradients, no realistic shading",
    "background": "clean solid white background with no other elements",
    "extras": (
        "die-cut sticker style with a thick white outline border "
        "around the ENTIRE character. "
        "Kawaii aesthetic — simple, round, and expressive. "
        "Minimal detail, maximum cuteness."
    ),
}

# =============================================================================
# PACK: Cappy the Chill Capybara Vol.3 — Chatty Cappy (16 stickers)
#
# Theme rationale:
#   v1 covered basic emotions (happy, sad, angry, love, sleepy, etc.)
#   v2 covered sassy reactions (OMG, BRB, Noted, Side-eye, etc.)
#   v3 covers DAILY CHAT PHRASES — things you say all the time in casual
#   conversation. Every sticker has text. Short, punchy, universal.
#
# Avoided concepts (already in v1/v2):
#   v1: good morning, ok, thank you, lol, love, sleepy, hungry, working,
#       excited, sad, angry, sorry, bye, thinking, cheering, good night
#   v2: omg, no way, noted, brb, wait what, lmao, yay, help, dead tired,
#       jealous, judging, hug, oops, deal with it, fighting, miss you
# =============================================================================
PACK_CONFIG = {
    "pack_id": "cappy-capybara-3",
    "pack_name": "Cappy the Chill Capybara Vol.3",
    "publisher": "BobaStickers",
    "character": CHARACTER,
    "style": STYLE,
    "text_defaults": {  # v2 field — pack-level Pillow text styling for all-text pack
        "font_size": "auto",
        "color": "#FFFFFF",
        "stroke_color": "#4A3728",
        "stroke_width": 8,
        "position": "bottom",
    },
    # -----------------------------------------------------------------
    # TEXT OVERLAY — every sticker in this pack has text
    #
    # Simple form:  "text": "WORD"       — white fill, dark brown stroke, bottom
    # Full form:    "text": { "content": "WORD", "position": "top", ... }
    # -----------------------------------------------------------------
    "stickers": [
        # --- Sheet 1: Stickers 01-08  (Daily Greetings & Status) ---
        {
            "id": "01_sup",
            "emotion": "Casual Greeting / Hey",
            "pose": "Leaning back casually against invisible wall, one stubby arm raised in a lazy wave, relaxed posture",
            "props": "Half-lidded chill eyes, slight cool smirk, orange balanced perfectly on head, small sparkle near waving hand",
            "emoji": "\U0001f44b",
            "text": "SUP",
        },
        {
            "id": "02_same",
            "emotion": "Relatable / Me Too",
            "pose": "Pointing both stubby arms forward at the viewer, leaning in with wide knowing eyes",
            "props": "Emphatic nodding motion lines around head, determined agreement expression, orange nodding along on head",
            "emoji": "\U0001f64f",
            "text": "SAME",
        },
        {
            "id": "03_nope",
            "emotion": "Refusal / Hard No",
            "pose": "Sitting firmly with stubby arms crossed over round body, head turned to the side, eyes closed",
            "props": "Big X mark above head, firm closed mouth, strong refusal aura lines, orange sitting defiantly on head",
            "emoji": "\U0001f645",
            "text": "NOPE",
        },
        {
            "id": "04_lets_go",
            "emotion": "Pumped Up / Let's Do This",
            "pose": "Running forward toward viewer, one stubby arm pumping in the air, body leaning into the sprint",
            "props": "Fire trail behind feet, speed lines, wide determined grin, orange ablaze (tiny flame effect) on head, sparkle in eyes",
            "emoji": "\U0001f525",
            "text": "LET'S GO!",
        },
        {
            "id": "05_why",
            "emotion": "Confused / Existential Why",
            "pose": "Standing still staring blankly forward, stubby arms hanging limp at sides, slight head tilt",
            "props": "Three question marks floating above head in different sizes, hollow empty eyes, orange tilted askew on head",
            "emoji": "\U0001f615",
            "text": "WHY",
        },
        {
            "id": "06_food",
            "emotion": "Craving Food / Hungry Excited",
            "pose": "Standing on tiptoes reaching upward with both stubby arms, mouth wide open drooling",
            "props": "Star-shaped sparkle eyes, drool waterfall from mouth, imaginary bowl of ramen floating above hands, orange bouncing excitedly on head",
            "emoji": "\U0001f35c",
            "text": "FOOD!",
        },
        {
            "id": "07_no_money",
            "emotion": "Broke / No Budget",
            "pose": "Standing holding an open wallet upside down with both stubby arms, shaking it, looking inside desperately",
            "props": "Empty wallet with a moth flying out, single tear on cheek, coin with wings flying away, orange drooping sadly on head",
            "emoji": "\U0001f4b8",
            "text": "NO MONEY",
        },
        {
            "id": "08_on_my_way",
            "emotion": "Coming / Almost There",
            "pose": "Riding a tiny scooter at full speed to the right, body hunched forward over handlebars",
            "props": "Speed lines trailing behind, dust cloud at wheels, determined squinting eyes, orange flapping in the wind on head, motion blur on legs",
            "emoji": "\U0001f6f5",
            "text": "OMW!",
        },
        # --- Sheet 2: Stickers 09-16  (Mood Updates & Reactions) ---
        {
            "id": "09_chill",
            "emotion": "Relaxed / Vibing",
            "pose": "Lying on back floating in a tiny hot spring or puddle, stubby arms behind head, eyes closed peacefully",
            "props": "Steam wisps rising, serene blissful smile, small musical notes floating, orange floating beside in the water, zen ripples",
            "emoji": "\u2728",
            "text": "CHILL",
        },
        {
            "id": "10_ugh",
            "emotion": "Annoyed / Fed Up",
            "pose": "Face-palming with one stubby arm covering entire face, body slumped forward",
            "props": "Dark annoyed aura cloud behind, visible frustration vein on hand, heavy sigh breath cloud, orange wilting on head",
            "emoji": "\U0001f624",
            "text": "UGH",
        },
        {
            "id": "11_slay",
            "emotion": "Fabulous / Killing It",
            "pose": "Posing dramatically like a runway model, one stubby arm on hip, the other flipping imaginary hair, body in sassy S-curve",
            "props": "Sparkles and stars all around, confident closed-eye smirk, tiny crown on head next to orange, pink glowing aura",
            "emoji": "\U0001f485",
            "text": "SLAY",
        },
        {
            "id": "12_its_fine",
            "emotion": "Everything Is Fine / Denial",
            "pose": "Sitting in a room surrounded by small flames, holding a tiny cup of tea, sipping calmly with eyes closed",
            "props": "Small cartoon flames around (this-is-fine meme), serene denial smile, sweat drop on temple, orange slightly singed on head",
            "emoji": "\U0001f525",
            "text": {
                "content": "IT'S FINE",
                "position": "bottom",
                "color": "#FFFFFF",
                "stroke_color": "#4A3728",
            },
        },
        {
            "id": "13_pls",
            "emotion": "Begging / Pretty Please",
            "pose": "On knees with both stubby arms clasped together in front, looking up with huge watery puppy eyes",
            "props": "Giant sparkling teary puppy eyes (twice normal size), trembling lower lip, begging sparkles around clasped hands, orange wobbling on head",
            "emoji": "\U0001f97a",
            "text": "PLS",
        },
        {
            "id": "14_wut",
            "emotion": "Dumbfounded / Processing",
            "pose": "Standing completely frozen mid-step, one foot raised, body stiff, eyes wide and vacant like blue-screen",
            "props": "Loading/buffering circle spinning above head, completely blank frozen expression, tiny error symbols, orange glitching on head",
            "emoji": "\U0001f9d0",
            "text": "WUT",
        },
        {
            "id": "15_ttyl",
            "emotion": "Gotta Go / Talk Later",
            "pose": "Peeking from behind a door that is half-closed, only half of face and one stubby arm visible, waving goodbye",
            "props": "Small hand wave, one visible eye winking, mischievous slight smile, orange peeking from behind door too",
            "emoji": "\U0001f44b",
            "text": "TTYL",
        },
        {
            "id": "16_mood",
            "emotion": "Big Mood / That's So Me",
            "pose": "Sitting slouched on a tiny couch wrapped in a blanket burrito, only face visible, holding a phone up close",
            "props": "Empty snack bags around couch, phone screen glowing on face, dead-inside peaceful eyes, orange peeking out of blanket on head",
            "emoji": "\U0001f6cb\ufe0f",
            "text": "MOOD",
        },
    ],
    "platforms": [
        "line",
        "telegram",
        "whatsapp",
        "imessage_large",
        "print_etsy",
    ],
}
