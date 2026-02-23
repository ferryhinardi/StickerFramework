#!/usr/bin/env python3
"""
Image Generator - Generate sticker images via OpenAI DALL-E 3 API.

Usage:
    # Generate a full pack:
    export OPENAI_API_KEY="sk-..."
    python image_generator.py

    # Or use as a module:
    from image_generator import StickerGenerator
    gen = StickerGenerator(api_key="sk-...")
    gen.generate_pack(config)
"""

import os
import sys
import time
from pathlib import Path

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Repo root (parent of scripts/)
REPO_ROOT = _SCRIPTS_DIR.parent

import requests

try:
    import openai
except ImportError:
    print("Error: openai package not installed. Run: pip install openai")
    sys.exit(1)


class StickerGenerator:
    """Generate sticker images using OpenAI DALL-E 3 API."""

    def __init__(self, api_key: str | None = None):
        """
        Args:
            api_key: OpenAI API key. Falls back to OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key."
            )
        self.client = openai.OpenAI(api_key=self.api_key)

    def build_prompt(self, character: dict, style: dict, sticker: dict) -> str:
        """
        Build a detailed DALL-E prompt from pack config components.
        The prompt is designed to maintain consistency across all stickers.
        """
        return f"""Generate a single kawaii sticker design with these EXACT specifications:

=== CHARACTER (DO NOT DEVIATE) ===
- Subject: A small, round {character["species"]} character named {character["name"]}
- Body color: {character["body_color"]} solid flat fill
- Cheek blush: Two circular {character["blush_color"]} marks on cheeks
- Eyes: {character["eye_style"]}
- Outline: Thick uniform {character["outline_color"]} outline, {style["outline_type"]}
- Accessory: {character["accessory"]}
- Proportions: {character["proportions"]}

=== THIS STICKER'S EXPRESSION ===
- Emotion: {sticker["emotion"]}
- Pose: {sticker["pose"]}
- Props: {sticker["props"]}

=== MANDATORY STYLE RULES ===
- {style["extras"]}
- {style["background"]}
- {style["coloring"]}
- Thick, uniform outline weight throughout
- Simple, bold, easily readable at small sizes (will be viewed at 512x512 pixels)
- No text or words anywhere in the image
- Centered composition with small padding on all sides
- Single character only, no duplicates, no multiple characters
- Square 1:1 aspect ratio

=== TECHNICAL ===
- High contrast, vibrant but soft pastel kawaii color palette
- Professional sticker quality, clean vector-like appearance
- Output should look like a professional die-cut sticker product"""

    def generate_sticker(
        self,
        character: dict,
        style: dict,
        sticker: dict,
        output_dir: str,
        size: str = "1024x1024",
        quality: str = "hd",
        max_retries: int = 3,
    ) -> Path | None:
        """
        Generate a single sticker image via DALL-E 3.

        Args:
            character: Character definition dict
            style: Style definition dict
            sticker: Single sticker definition (id, emotion, pose, props, emoji)
            output_dir: Directory to save raw generated images
            size: DALL-E output size (1024x1024 recommended)
            quality: "hd" for higher detail, "standard" for faster/cheaper
            max_retries: Number of retries on failure

        Returns:
            Path to saved image, or None on failure
        """
        prompt = self.build_prompt(character, style, sticker)
        output_path = Path(output_dir) / f"{sticker['id']}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"  Generating: {sticker['id']} ({sticker['emotion']})...")

        for attempt in range(max_retries):
            try:
                response = self.client.images.generate(
                    model="dall-e-3",
                    prompt=prompt,
                    size=size,
                    quality=quality,
                    n=1,
                    response_format="url",
                )

                image_url = response.data[0].url
                revised_prompt = response.data[0].revised_prompt

                # Download the image
                img_response = requests.get(image_url, timeout=60)
                img_response.raise_for_status()

                with open(output_path, "wb") as f:
                    f.write(img_response.content)

                # Save the prompts for reference / debugging
                prompt_file = output_path.with_suffix(".prompt.txt")
                with open(prompt_file, "w") as f:
                    f.write(f"=== Original Prompt ===\n{prompt}\n\n")
                    f.write(f"=== DALL-E Revised Prompt ===\n{revised_prompt}\n")

                size_kb = output_path.stat().st_size / 1024
                print(f"    Saved: {output_path.name} ({size_kb:.0f}KB)")
                return output_path

            except openai.RateLimitError:
                wait = 60 * (attempt + 1)
                print(
                    f"    Rate limited. Waiting {wait}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait)

            except openai.BadRequestError as e:
                print(f"    Bad request (content policy?): {e}")
                # Save the failed prompt for debugging
                fail_file = output_path.with_suffix(".failed.txt")
                with open(fail_file, "w") as f:
                    f.write(f"Error: {e}\n\nPrompt:\n{prompt}")
                return None

            except requests.RequestException as e:
                print(f"    Download error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

            except Exception as e:
                print(f"    Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

        print(f"    FAILED after {max_retries} attempts: {sticker['id']}")
        return None

    def generate_pack(
        self,
        config: dict,
        delay_between: float = 3.0,
        quality: str = "hd",
    ) -> list[Path]:
        """
        Generate all stickers in a pack configuration.

        Args:
            config: Full pack config dict (from pack_config.py)
            delay_between: Seconds to wait between API calls (rate limit safety)
            quality: "hd" ($0.08/image) or "standard" ($0.04/image)

        Returns:
            List of paths to successfully generated images

        Cost estimate:
            - HD quality, 1024x1024: $0.080 per image
            - Standard quality: $0.040 per image
            - 24 stickers HD: $1.92
            - With ~40% redo rate: ~$2.70
        """
        output_dir = str(REPO_ROOT / "packs" / config["pack_id"] / "raw")
        stickers = config["stickers"]
        total = len(stickers)

        print(f"\n{'=' * 60}")
        print(f"Generating pack: {config['pack_name']}")
        print(f"Stickers: {total}")
        print(f"Quality: {quality}")
        print(f"Est. cost: ${total * (0.08 if quality == 'hd' else 0.04):.2f}")
        print(f"Output: {output_dir}/")
        print(f"{'=' * 60}\n")

        results = []
        failed = []

        for i, sticker in enumerate(stickers):
            print(f"[{i + 1}/{total}]", end="")
            path = self.generate_sticker(
                character=config["character"],
                style=config["style"],
                sticker=sticker,
                output_dir=output_dir,
                quality=quality,
            )

            if path:
                results.append(path)
            else:
                failed.append(sticker["id"])

            # Rate limit safety delay
            if i < total - 1:
                time.sleep(delay_between)

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Generation complete: {len(results)}/{total} successful")
        if failed:
            print(f"Failed: {', '.join(failed)}")
            print("Re-run with only failed stickers or adjust prompts.")
        print(f"Output directory: {output_dir}/")
        print(f"{'=' * 60}")

        return results

    def generate_reference_sheet(
        self,
        character: dict,
        output_path: str = "reference_sheet.png",
    ) -> Path | None:
        """
        Generate a character reference sheet for consistency checking.
        Use this before generating a pack to establish the character look.
        """
        prompt = f"""Create a character reference sheet for a kawaii mascot character:

CHARACTER: A small round {character["species"]} named {character["name"]}
COLORS: Body is {character["body_color"]} solid flat fill, cheeks have {character["blush_color"]} circular blush marks, outline is {character["outline_color"]}
EYES: {character["eye_style"]}
PROPORTIONS: {character["proportions"]}
SIGNATURE: Always has {character["accessory"]}
STYLE: Flat colors, thick uniform outline, NO gradients, NO realistic shading

Show the character in 6 poses on a clean white background:
1. Front view standing neutral
2. 3/4 view waving hello
3. Side view walking
4. Sitting down
5. Back view looking over shoulder
6. Close-up face showing detail

Label each pose. Character reference sheet layout, clean organized grid, white background."""

        print("Generating reference sheet...")
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",
                quality="hd",
                n=1,
                response_format="url",
            )

            img_response = requests.get(response.data[0].url, timeout=60)
            img_response.raise_for_status()

            with open(output_path, "wb") as f:
                f.write(img_response.content)

            print(f"Reference sheet saved: {output_path}")
            return Path(output_path)

        except Exception as e:
            print(f"Error generating reference sheet: {e}")
            return None


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    from pack_config import PACK_CONFIG

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Set OPENAI_API_KEY environment variable")
        print("  export OPENAI_API_KEY='sk-...'")
        sys.exit(1)

    generator = StickerGenerator(api_key=api_key)

    # Generate reference sheet first (optional but recommended)
    if "--ref" in sys.argv:
        generator.generate_reference_sheet(
            character=PACK_CONFIG["character"],
            output_path=os.path.join(PACK_CONFIG["pack_id"], "reference_sheet.png"),
        )
        print()

    # Generate the full pack
    quality = "standard" if "--standard" in sys.argv else "hd"
    generator.generate_pack(PACK_CONFIG, quality=quality)
