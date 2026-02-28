#!/usr/bin/env python3
"""
ComfyUI Image Generator - Generate sticker images via local ComfyUI API.

Drop-in alternative to image_generator.py (DALL-E 3).
Uses DreamShaper XL Turbo via ComfyUI's REST API for free, unlimited
local generation on Apple Silicon.

Usage:
    # Make sure ComfyUI is running (http://127.0.0.1:8000)
    # Generate a full pack:
    python comfyui_generator.py

    # Generate with specific seed for reproducibility:
    python comfyui_generator.py --seed 42

    # Generate only specific stickers by ID:
    python comfyui_generator.py --only 01_good_morning 05_love

    # Or use as a module:
    from comfyui_generator import ComfyUIStickerGenerator
    gen = ComfyUIStickerGenerator()
    gen.generate_pack(config)
"""

import json
import os
import random
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from text_compositor import composite_text_on_image  # noqa: E402

# Repo root (parent of scripts/)
REPO_ROOT = _SCRIPTS_DIR.parent

# ---------------------------------------------------------------------------
# Default ComfyUI settings (tuned for DreamShaper XL Turbo on Apple Silicon)
# ---------------------------------------------------------------------------
DEFAULT_COMFYUI_URL = "http://127.0.0.1:8000"
DEFAULT_CHECKPOINT = "DreamShaperXL_Turbo_v2_1.safetensors"
DEFAULT_STEPS = 8  # Turbo model works well with 6-10 steps
DEFAULT_CFG = 2.0  # Low CFG for Turbo models
DEFAULT_SAMPLER = "dpmpp_sde"
DEFAULT_SCHEDULER = "karras"
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024


class ComfyUIStickerGenerator:
    """Generate sticker images using local ComfyUI API."""

    def __init__(
        self,
        comfyui_url: str = DEFAULT_COMFYUI_URL,
        checkpoint: str = DEFAULT_CHECKPOINT,
        steps: int = DEFAULT_STEPS,
        cfg: float = DEFAULT_CFG,
        sampler: str = DEFAULT_SAMPLER,
        scheduler: str = DEFAULT_SCHEDULER,
    ):
        self.comfyui_url = comfyui_url.rstrip("/")
        self.checkpoint = checkpoint
        self.steps = steps
        self.cfg = cfg
        self.sampler = sampler
        self.scheduler = scheduler

        # Verify ComfyUI is reachable
        try:
            req = urllib.request.Request(f"{self.comfyui_url}/prompt")
            resp = urllib.request.urlopen(req, timeout=5)
            resp.read()
        except Exception as e:
            raise ConnectionError(
                f"Cannot connect to ComfyUI at {self.comfyui_url}. "
                f"Make sure ComfyUI is running.\n  Error: {e}"
            )

    @staticmethod
    def _extract_text_content(sticker: dict) -> str | None:
        """
        Extract the display text from a sticker's config.

        Handles both forms:
          - Simple:  "text": "NOTED!"
          - Full:    "text": {"content": "NOTED!", "position": "top", ...}

        Returns the text string, or None if no text is configured.
        """
        text_field = sticker.get("text")
        if text_field is None:
            return None
        if isinstance(text_field, str):
            return text_field
        if isinstance(text_field, dict):
            return text_field.get("content")
        return None

    @staticmethod
    def _get_art_style(style: dict) -> str:
        """Return the art_style string, defaulting to 'flat_vector'."""
        return style.get("art_style", "flat_vector")

    @staticmethod
    def _get_body_description(character: dict) -> str:
        """
        Return the full SDXL body description for the character.

        Uses v2 ``body_description`` field if present, otherwise falls back
        to the original hardcoded capybara description for backward
        compatibility with cappy-capybara packs.
        """
        if character.get("body_description"):
            return character["body_description"]

        # Legacy fallback — original capybara description
        return (
            f"cute round chubby {character.get('species', 'character')}, "
            "wearing tiny orange fruit as hat on head, "
            "warm brown fur, soft pink cheeks, "
            "small round ears, potato-shaped body, tiny stubby legs"
        )

    def build_prompt(
        self,
        character: dict,
        style: dict,
        sticker: dict,
        emoji_mode: bool = False,
    ) -> str:
        """
        Build a Stable Diffusion prompt from pack config components.
        Optimized for SDXL sticker generation.

        Text is NEVER included in the SDXL prompt — it is always composited
        in post-processing via TextCompositor.  The prompt focuses purely
        on character, pose, and art style.

        Prompt structure (SDXL attention order):
        1. Style/medium keywords (highest weight) — varies by art_style
        2. Subject + body description (character-agnostic)
        3. Pose/action for this specific sticker
        4. Style reinforcement suffix — ALWAYS includes anti-text tokens

        Args:
            emoji_mode: When True, switches to face close-up framing and
                boosted emotion weight for 180×180 LINE Emoji generation.
        """
        art_style = self._get_art_style(style)
        body_desc = self._get_body_description(character)

        # ------------------------------------------------------------------
        # 1. Style prefix — determined by art_style and emoji_mode
        # ------------------------------------------------------------------
        if emoji_mode:
            # Emoji mode: face/head close-up, fill the frame, bold expression
            if art_style == "painted_illustration":
                style_prefix = (
                    "kawaii emoji design, cute chibi face icon, "
                    "single expression, centered face close-up, "
                    "(large head fills frame:1.3), "
                    "digital anime art, thick black outlines, clean lineart, "
                    "(solid pure white background:1.3), "
                    "bold expressive face, masterpiece, best quality"
                )
            else:
                style_prefix = (
                    "kawaii emoji icon, cute chibi face, "
                    "single expression, centered face close-up, "
                    "(large head fills frame:1.3), "
                    "flat colors, no gradients, vector art style, "
                    "(solid pure white background:1.3), "
                    "masterpiece, best quality"
                )
        else:
            # Standard sticker mode (full body)
            if art_style == "painted_illustration":
                style_prefix = (
                    "kawaii chibi sticker design, cute cartoon illustration, "
                    "digital anime art, thick black outlines, clean lineart, "
                    "(solid pure white background:1.3), "
                    "single character centered, large head small body, "
                    "dynamic expressive pose, masterpiece, best quality"
                )
            else:
                # Default: flat_vector (original capybara/mochi style)
                style_prefix = (
                    "kawaii chibi character illustration, flat colors, no gradients, "
                    "vector art style, (solid pure white background:1.3), "
                    "single character centered, masterpiece, best quality"
                )

        # ------------------------------------------------------------------
        # 2. Emotion + character (character-agnostic via body_description)
        #    Emoji mode: boosted emotion weight (1.6 vs 1.5)
        # ------------------------------------------------------------------
        emotion_tag = sticker.get("emotion", "")
        props_tag = sticker.get("props", "")

        emotion_weight = 1.6 if emoji_mode else 1.5
        char_desc = f"({emotion_tag}:{emotion_weight}), ({body_desc}:1.3)"

        # ------------------------------------------------------------------
        # 3. This sticker's specific pose + props
        # ------------------------------------------------------------------
        sticker_desc = f"({sticker['pose']}:1.2)"
        if props_tag:
            sticker_desc += f", ({props_tag}:1.1)"

        # ------------------------------------------------------------------
        # 4. Style reinforcement suffix — ALWAYS anti-text
        #    Text is handled exclusively by TextCompositor in post-processing.
        # ------------------------------------------------------------------
        if emoji_mode:
            # Emoji suffix: emphasize close-up face, bold expression
            if art_style == "painted_illustration":
                style_suffix = (
                    "thick dark outlines, clean lineart, "
                    "(bold expressive face:1.2), exaggerated expression, "
                    "soft cel shading, warm color palette, "
                    "no text, no words, no letters, no writing"
                )
            else:
                style_suffix = (
                    "flat colors, thick dark outline, "
                    "(bold expressive face:1.2), exaggerated expression, "
                    "no text, no words, no letters, no writing"
                )
        else:
            # Standard sticker suffix
            if art_style == "painted_illustration":
                style_suffix = (
                    "thick dark outlines, clean lineart, expressive face, "
                    "soft cel shading, warm color palette, action effects, "
                    "dynamic composition, "
                    "no text, no words, no letters, no writing"
                )
            else:
                style_suffix = (
                    "flat colors, thick dark outline, simple minimal design, "
                    "no text, no words, no letters, no writing"
                )

        # Assemble
        parts = [style_prefix, char_desc, sticker_desc, style_suffix]
        return ", ".join(parts)

    def build_negative_prompt(
        self, art_style: str = "flat_vector", emoji_mode: bool = False
    ) -> str:
        """
        Standard negative prompt for sticker generation.

        Anti-text tokens are ALWAYS included — text is never generated by
        SDXL; it is composited in post-processing.

        For ``painted_illustration`` style, anti-gradient and anti-realistic
        tokens are removed (those qualities are desired).

        Args:
            emoji_mode: When True, adds anti-full-body tokens to force
                face/head close-up composition for 180×180 emoji images.
        """
        # Anti-text tokens — always present (text is post-processed, not SDXL)
        anti_text = "text, words, letters, numbers, alphabet, writing, caption, label, "

        # Core quality negatives (always present)
        core_negatives = (
            "watermark, signature, logo, "
            "sticker, die-cut sticker, circular frame, circular border, round frame, "
            "badge, emblem, stamp, die-cut border, sticker outline, "
            "white border, cut-out shape, border, frame, "
            "blurry, low quality, low resolution, jpeg artifacts, "
            "multiple characters, duplicate, "
            "ugly, deformed, disfigured, bad anatomy, bad proportions, "
            "extra limbs, extra fingers, mutated, "
            "nsfw, violence"
        )

        # Background negatives (always present)
        bg_negatives = (
            "complex background, detailed background, patterned background, "
            "gray background, beige background, colored background, dark background, "
            "green background, sage background, blue background"
        )

        if art_style == "painted_illustration":
            # Painted style wants cartoon/anime shading, NOT photorealism
            # Block realistic fur textures, photo-like rendering, lifelike animals
            style_negatives = (
                "realistic, photorealistic, photograph, 3d render, "
                "real animal, real photo, lifelike, hyperrealistic, "
                "raw photo, dslr, film grain, fur texture, detailed fur, "
                "skin texture, skin pores"
            )
        else:
            # Flat vector blocks all realistic/gradient/shading elements
            style_negatives = (
                "realistic, photograph, photorealistic, 3d render, gradient shading"
            )

        # Emoji mode: force close-up by blocking full body generation
        emoji_negatives = ""
        if emoji_mode:
            emoji_negatives = (
                ", full body, legs, feet, standing pose, sitting pose, "
                "wide shot, far away, tiny character, small character, "
                "full figure, distant view"
            )

        return f"{anti_text}{core_negatives}, {bg_negatives}, {style_negatives}{emoji_negatives}"

    def _build_workflow(
        self,
        positive_prompt: str,
        negative_prompt: str,
        seed: int,
        filename_prefix: str,
    ) -> dict:
        """Build a ComfyUI API workflow dict."""
        return {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": self.checkpoint},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": positive_prompt,
                    "clip": [
                        "1",
                        1,
                    ],  # CheckpointLoader output: [0]=MODEL, [1]=CLIP, [2]=VAE
                },
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "text": negative_prompt,
                    "clip": ["1", 1],
                },
            },
            "4": {
                "class_type": "EmptyLatentImage",
                "inputs": {
                    "width": DEFAULT_WIDTH,
                    "height": DEFAULT_HEIGHT,
                    "batch_size": 1,
                },
            },
            "5": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "latent_image": ["4", 0],
                    "seed": seed,
                    "steps": self.steps,
                    "cfg": self.cfg,
                    "sampler_name": self.sampler,
                    "scheduler": self.scheduler,
                    "denoise": 1.0,
                },
            },
            "6": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2],
                },
            },
            "7": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["6", 0],
                    "filename_prefix": filename_prefix,
                },
            },
        }

    def _queue_prompt(self, workflow: dict) -> str:
        """Send a workflow to ComfyUI and return the prompt_id."""
        data = json.dumps({"prompt": workflow}).encode("utf-8")
        req = urllib.request.Request(
            f"{self.comfyui_url}/prompt",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read())

        if result.get("node_errors"):
            raise RuntimeError(
                f"ComfyUI validation errors: {json.dumps(result['node_errors'], indent=2)}"
            )

        return result["prompt_id"]

    def _wait_for_completion(
        self, prompt_id: str, timeout: int = 600, poll_interval: float = 5.0
    ) -> dict:
        """Poll ComfyUI history until the prompt completes or fails."""
        start = time.time()
        while time.time() - start < timeout:
            try:
                req = urllib.request.Request(f"{self.comfyui_url}/history/{prompt_id}")
                resp = urllib.request.urlopen(req, timeout=10)
                history = json.loads(resp.read())

                if prompt_id in history:
                    info = history[prompt_id]
                    status = info.get("status", {}).get("status_str", "unknown")

                    if status == "success":
                        return info
                    elif status == "error":
                        # Extract error details
                        messages = info.get("status", {}).get("messages", [])
                        for msg_type, msg_data in messages:
                            if msg_type == "execution_error":
                                raise RuntimeError(
                                    f"ComfyUI execution error on node "
                                    f"'{msg_data.get('node_type', '?')}': "
                                    f"{msg_data.get('exception_message', 'Unknown error')}"
                                )
                        raise RuntimeError(f"ComfyUI execution failed: {status}")
            except urllib.error.URLError:
                pass  # Server busy, retry

            time.sleep(poll_interval)

        raise TimeoutError(
            f"ComfyUI generation timed out after {timeout}s for prompt {prompt_id}"
        )

    def _copy_output(
        self, history_info: dict, output_path: Path, filename_prefix: str = ""
    ) -> Path | None:
        """Copy generated image from ComfyUI output dir to target path."""
        comfyui_output = Path.home() / "Documents" / "ComfyUI" / "output"

        # Method 1: Use history API output info
        outputs = history_info.get("outputs", {})
        for node_id, node_output in outputs.items():
            images = node_output.get("images", [])
            for img_info in images:
                filename = img_info.get("filename")
                subfolder = img_info.get("subfolder", "")
                if filename:
                    src = (
                        comfyui_output / subfolder / filename
                        if subfolder
                        else comfyui_output / filename
                    )

                    if src.exists():
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src, output_path)
                        return output_path

        # Method 2: Fallback — search by filename prefix in ComfyUI output dir
        if filename_prefix and comfyui_output.exists():
            matches = sorted(
                comfyui_output.glob(f"{filename_prefix}*.png"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
            if matches:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(matches[0], output_path)
                print(f"    (found via fallback: {matches[0].name})")
                return output_path

        return None

    def generate_sticker(
        self,
        character: dict,
        style: dict,
        sticker: dict,
        output_dir: str,
        seed: int | None = None,
        max_retries: int = 2,
        text_defaults: dict | None = None,
        emoji_mode: bool = False,
    ) -> Path | None:
        """
        Generate a single sticker image via ComfyUI.

        Args:
            character: Character definition dict
            style: Style definition dict
            sticker: Single sticker definition (id, emotion, pose, props, emoji)
            output_dir: Directory to save generated images
            seed: Random seed (None for random)
            max_retries: Number of retries on failure
            text_defaults: Pack-level text_defaults for TextCompositor
            emoji_mode: When True, uses face close-up prompts for emoji

        Returns:
            Path to saved image, or None on failure
        """
        text_config = sticker.get("text")  # dict, str, or None
        text_content = self._extract_text_content(sticker)
        has_text = text_content is not None
        art_style = self._get_art_style(style)

        positive_prompt = self.build_prompt(
            character, style, sticker, emoji_mode=emoji_mode
        )
        negative_prompt = self.build_negative_prompt(
            art_style=art_style, emoji_mode=emoji_mode
        )
        output_path = Path(output_dir) / f"{sticker['id']}.png"

        if seed is None:
            seed = random.randint(0, 2**32 - 1)

        text_info = f' text="{text_content}"' if has_text else ""
        print(
            f"  Generating: {sticker['id']} ({sticker['emotion']}{text_info}) [seed={seed}]..."
        )

        for attempt in range(max_retries):
            try:
                # Use a unique prefix to avoid filename collisions
                prefix = f"sticker_{sticker['id']}_{seed}"

                workflow = self._build_workflow(
                    positive_prompt=positive_prompt,
                    negative_prompt=negative_prompt,
                    seed=seed,
                    filename_prefix=prefix,
                )

                # Queue and wait
                prompt_id = self._queue_prompt(workflow)
                history = self._wait_for_completion(prompt_id)

                # Copy output to pack directory
                result_path = self._copy_output(
                    history, output_path, filename_prefix=prefix
                )

                if result_path:
                    # ----- Text compositing (post-processing) -----
                    if has_text and text_config:
                        try:
                            composite_text_on_image(
                                image_path=result_path,
                                text_config=text_config,
                                defaults=text_defaults,
                                output_path=result_path,  # overwrite in place
                            )
                            print(f'    Text composited: "{text_content}"')
                        except Exception as te:
                            print(f"    Warning: text compositing failed: {te}")
                            # Image is still saved without text — non-fatal

                    # Save prompt for reference
                    prompt_file = output_path.with_suffix(".prompt.txt")
                    with open(prompt_file, "w") as f:
                        f.write(f"=== Positive Prompt ===\n{positive_prompt}\n\n")
                        f.write(f"=== Negative Prompt ===\n{negative_prompt}\n\n")
                        f.write(f"=== Text Overlay ===\n")
                        if has_text:
                            f.write(f"Content: {text_content}\n")
                            f.write(f"Config: {text_config}\n")
                            f.write(f"Defaults: {text_defaults}\n")
                            f.write(f"Method: Pillow TextCompositor (post-process)\n")
                        else:
                            f.write(f"None (no text configured for this sticker)\n")
                        f.write(f"\n=== Settings ===\n")
                        f.write(f"Art style: {art_style}\n")
                        f.write(f"Emoji mode: {emoji_mode}\n")
                        f.write(f"Checkpoint: {self.checkpoint}\n")
                        f.write(f"Seed: {seed}\n")
                        f.write(f"Steps: {self.steps}\n")
                        f.write(f"CFG: {self.cfg}\n")
                        f.write(f"Sampler: {self.sampler}\n")
                        f.write(f"Scheduler: {self.scheduler}\n")
                        f.write(f"Size: {DEFAULT_WIDTH}x{DEFAULT_HEIGHT}\n")

                    size_kb = result_path.stat().st_size / 1024
                    print(f"    Saved: {output_path.name} ({size_kb:.0f}KB)")
                    return result_path
                else:
                    print(
                        f"    Warning: Generation succeeded but output file not found"
                    )
                    if attempt < max_retries - 1:
                        seed = random.randint(0, 2**32 - 1)

            except (RuntimeError, TimeoutError) as e:
                print(f"    Error (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    seed = random.randint(0, 2**32 - 1)
                    time.sleep(2)

            except Exception as e:
                print(f"    Unexpected error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        print(f"    FAILED after {max_retries} attempts: {sticker['id']}")
        return None

    def generate_pack(
        self,
        config: dict,
        seed: int | None = None,
        only: list[str] | None = None,
    ) -> list[Path]:
        """
        Generate all stickers in a pack configuration.

        Args:
            config: Full pack config dict (from pack_config.py)
            seed: Base seed (each sticker gets seed+index for reproducibility)
            only: If set, only generate stickers with these IDs

        Returns:
            List of paths to successfully generated images

        Cost: FREE (local generation)
        """
        output_dir = str(REPO_ROOT / "packs" / config["pack_id"] / "raw")
        stickers = config["stickers"]
        text_defaults = config.get("text_defaults")
        art_style = self._get_art_style(config.get("style", {}))
        emoji_mode = config.get("product_type") == "line_emoji"

        if only:
            stickers = [s for s in stickers if s["id"] in only]
            if not stickers:
                print(f"No stickers matched IDs: {only}")
                return []

        total = len(stickers)
        base_seed = seed if seed is not None else random.randint(0, 2**32 - 1)

        print(f"\n{'=' * 60}")
        print(f"Generating pack: {config['pack_name']}")
        print(f"Generator: ComfyUI (local) — {self.checkpoint}")
        print(f"Art style: {art_style}")
        if emoji_mode:
            print(f"Mode: EMOJI (face close-up, boosted emotion)")
        print(f"Stickers: {total}")
        print(f"Base seed: {base_seed}")
        print(f"Steps: {self.steps} | CFG: {self.cfg} | Sampler: {self.sampler}")
        if text_defaults:
            print(f"Text defaults: {text_defaults}")
        print(f"Cost: FREE")
        print(f"Output: {output_dir}/")
        print(f"{'=' * 60}\n")

        results = []
        failed = []
        skipped = 0

        for i, sticker in enumerate(stickers):
            sticker_seed = base_seed + i
            # Skip already-generated images
            existing = Path(output_dir) / f"{sticker['id']}.png"
            if existing.exists():
                skipped += 1
                print(f"[{i + 1}/{total}] Skipping {sticker['id']} (already exists)")
                results.append(existing)
                continue

            print(f"[{i + 1}/{total}]", end="")
            path = self.generate_sticker(
                character=config["character"],
                style=config["style"],
                sticker=sticker,
                output_dir=output_dir,
                seed=sticker_seed,
                text_defaults=text_defaults,
                emoji_mode=emoji_mode,
            )

            if path:
                results.append(path)
            else:
                failed.append(sticker["id"])

        # Summary
        print(f"\n{'=' * 60}")
        print(f"Generation complete: {len(results)}/{total} successful")
        if skipped:
            print(f"Skipped (already existed): {skipped}")
        if failed:
            print(f"Failed: {', '.join(failed)}")
            print("Re-run with --only flag to retry failed stickers.")
        print(f"Output directory: {output_dir}/")
        print(f"{'=' * 60}")

        return results


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
def _load_pack_config(pack_dir: str | None = None) -> dict:
    """Load PACK_CONFIG from a pack directory or fall back to scripts/pack_config.py."""
    if pack_dir:
        pack_path = Path(pack_dir).resolve()
        if not pack_path.exists():
            # Try as pack_id under packs/
            pack_path = REPO_ROOT / "packs" / pack_dir
        if not pack_path.exists():
            print(f"ERROR: Pack directory not found: {pack_dir}")
            sys.exit(1)
        config_file = pack_path / "pack_config.py"
        if not config_file.exists():
            print(f"ERROR: No pack_config.py found in {pack_path}")
            sys.exit(1)
        # Add pack dir to path so we can import it
        sys.path.insert(0, str(pack_path))
        import importlib

        mod = importlib.import_module("pack_config")
        sys.path.pop(0)
        return mod.PACK_CONFIG
    else:
        # Use STICKER_PACK env var or fall back to scripts/pack_config.py
        pack_id = os.environ.get("STICKER_PACK")
        if pack_id:
            return _load_pack_config(pack_id)
        from pack_config import PACK_CONFIG

        return PACK_CONFIG


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate sticker images via local ComfyUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all stickers in the pack:
  python comfyui_generator.py

  # Generate with a fixed seed for reproducibility:
  python comfyui_generator.py --seed 42

  # Regenerate only specific stickers:
  python comfyui_generator.py --only 01_good_morning 05_love

  # Use a different ComfyUI URL:
  python comfyui_generator.py --url http://127.0.0.1:8188

  # Use custom model settings:
  python comfyui_generator.py --steps 12 --cfg 3.0
""",
    )
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_COMFYUI_URL,
        help=f"ComfyUI server URL (default: {DEFAULT_COMFYUI_URL})",
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=DEFAULT_CHECKPOINT,
        help=f"Model checkpoint name (default: {DEFAULT_CHECKPOINT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Base random seed for reproducibility",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=DEFAULT_STEPS,
        help=f"Sampling steps (default: {DEFAULT_STEPS})",
    )
    parser.add_argument(
        "--cfg",
        type=float,
        default=DEFAULT_CFG,
        help=f"CFG scale (default: {DEFAULT_CFG})",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Only generate stickers with these IDs (e.g., 01_good_morning 05_love)",
    )
    parser.add_argument(
        "--pack",
        type=str,
        default=None,
        help="Pack directory or pack_id (e.g., cappy-capybara). "
        "Also reads STICKER_PACK env var.",
    )
    args = parser.parse_args()

    config = _load_pack_config(args.pack)

    try:
        generator = ComfyUIStickerGenerator(
            comfyui_url=args.url,
            checkpoint=args.checkpoint,
            steps=args.steps,
            cfg=args.cfg,
        )
    except ConnectionError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    generator.generate_pack(config, seed=args.seed, only=args.only)
