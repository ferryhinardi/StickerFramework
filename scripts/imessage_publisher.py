#!/usr/bin/env python3
"""
iMessage Sticker Pack Publisher - Full App Store automation via Fastlane.

Orchestrates the complete pipeline:
    prepare Xcode project (existing) → generate xcodegen YAML → xcodegen generate
    → generate app icons → populate fastlane metadata → generate screenshots
    → fastlane publish

Prerequisites:
    - macOS with Xcode 15+ installed
    - Apple Developer Program membership
    - Fastlane installed (brew install fastlane)
    - xcodegen installed (brew install xcodegen)
    - Environment variables set:
        APPLE_ID, APPLE_TEAM_ID, BUNDLE_ID, MATCH_GIT_URL

Usage:
    python imessage_publisher.py <pack_dir> [--dry-run] [--skip-submit]

    # Example:
    python imessage_publisher.py pack01_emotions_v1 --dry-run
"""

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# Repo root (parent of scripts/)
REPO_ROOT = _SCRIPTS_DIR.parent

from prepare_imessage_pack import create_xcode_project


def _load_pack_config(config_path: str) -> dict:
    """Dynamically import PACK_CONFIG from an arbitrary pack_config.py path."""
    path = Path(config_path).resolve()
    spec = importlib.util.spec_from_file_location("pack_config_dynamic", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PACK_CONFIG


# =============================================================================
# ICON SIZES REQUIRED FOR iMESSAGE STICKER APPS
# =============================================================================
# (width, height, scale, idiom, [platform])
ICON_SPECS = [
    (60, 45, 2, "iphone", None),  # 120x90
    (60, 45, 3, "iphone", None),  # 180x135
    (67, 50, 2, "ipad", None),  # 134x100
    (74, 55, 2, "ipad", None),  # 148x110
    (27, 20, 2, "universal", "ios"),  # 54x40
    (27, 20, 3, "universal", "ios"),  # 81x60
    (32, 24, 2, "universal", "ios"),  # 64x48
    (32, 24, 3, "universal", "ios"),  # 96x72
    (1024, 768, 1, "ios-marketing", None),  # 1024x768
]

# App Store screenshot sizes (width x height in pixels)
SCREENSHOT_SIZES = {
    "iPhone_6.7": (1290, 2796),  # iPhone 14 Pro Max / 15 Pro Max
    "iPhone_6.5": (1284, 2778),  # iPhone 14 Plus / 13 Pro Max
    "iPad_12.9": (2048, 2732),  # iPad Pro 12.9"
}


class IMessagePublisher:
    """Automate iMessage sticker pack building and App Store submission."""

    def __init__(
        self,
        pack_dir: str,
        pack_config: dict | None = None,
        dry_run: bool = False,
    ):
        """
        Args:
            pack_dir: Path to the pack output directory (contains final/ subdir).
            pack_config: Pack configuration dict. Falls back to importing PACK_CONFIG.
            dry_run: If True, prepare everything but don't invoke Fastlane.
        """
        self.pack_dir = Path(pack_dir).resolve()
        self.dry_run = dry_run

        # Load pack config
        if pack_config:
            self.config = pack_config
        else:
            try:
                from pack_config import PACK_CONFIG

                self.config = PACK_CONFIG
            except ImportError:
                raise RuntimeError(
                    "No pack_config provided and could not import PACK_CONFIG "
                    "from pack_config.py"
                )

        self.pack_name = self.config["pack_name"]
        # Sanitize for use as Xcode project name (alphanumeric + spaces)
        self.project_name = self.pack_name.replace("_", " ").title().replace(" ", "")
        self.character_name = self.config.get("character_name", self.pack_name)
        self.sticker_count = len(self.config.get("stickers", []))

        # Paths
        self.sticker_dir = self._find_sticker_dir()
        self.build_dir = self.pack_dir / "imessage_build"
        self.project_dir = self.build_dir / self.project_name
        self.fastlane_dir = REPO_ROOT / "fastlane"
        self.templates_dir = REPO_ROOT / "templates"

        # Environment
        self.team_id = os.environ.get("APPLE_TEAM_ID", "")
        self.bundle_id = os.environ.get(
            "BUNDLE_ID", f"com.yourbrand.{self.project_name.lower()}"
        )
        self.bundle_id_prefix = (
            self.bundle_id.rsplit(".", 1)[0]
            if "." in self.bundle_id
            else "com.yourbrand"
        )

    def _find_sticker_dir(self) -> Path:
        """Locate the processed iMessage sticker images directory."""
        # Try common paths in order of preference
        candidates = [
            self.pack_dir / "final" / "imessage_large",
            self.pack_dir / "final" / "imessage_medium",
            self.pack_dir / "final" / "imessage_small",
            self.pack_dir / "final" / "imessage",
            self.pack_dir / "final",
            self.pack_dir,
        ]
        for candidate in candidates:
            if candidate.is_dir() and list(candidate.glob("*.png")):
                return candidate

        raise FileNotFoundError(
            f"No PNG sticker files found in any expected subdirectory of {self.pack_dir}"
        )

    # =========================================================================
    # STEP 1: Generate Xcode project structure
    # =========================================================================
    def generate_xcode_project(self) -> Path:
        """Create the Xcode project structure using existing prepare_imessage_pack."""
        print("\n[Step 1/6] Generating Xcode project structure...")
        self.build_dir.mkdir(parents=True, exist_ok=True)

        project_dir = create_xcode_project(
            project_name=self.project_name,
            sticker_dir=str(self.sticker_dir),
            bundle_id_prefix=self.bundle_id_prefix,
            output_dir=str(self.build_dir),
        )
        self.project_dir = Path(project_dir)
        return self.project_dir

    # =========================================================================
    # STEP 2: Generate xcodegen YAML and run xcodegen
    # =========================================================================
    def generate_xcode_project_file(self) -> Path:
        """Generate a real .xcodeproj using xcodegen from the YAML template."""
        print("\n[Step 2/6] Generating Xcode project file via xcodegen...")
        template_path = self.templates_dir / "imessage_project.yml"

        if not template_path.exists():
            raise FileNotFoundError(f"xcodegen template not found: {template_path}")

        # Read and fill template
        template = template_path.read_text()
        yaml_content = (
            template.replace("{{PROJECT_NAME}}", self.project_name)
            .replace("{{BUNDLE_ID_PREFIX}}", self.bundle_id_prefix)
            .replace("{{TEAM_ID}}", self.team_id)
            .replace("{{BUNDLE_ID}}", self.bundle_id)
        )

        # Write filled YAML into the project directory
        project_yml = self.project_dir / "project.yml"
        project_yml.write_text(yaml_content)
        print(f"  Generated xcodegen spec: {project_yml}")

        # Run xcodegen
        try:
            result = subprocess.run(
                ["xcodegen", "generate", "--spec", str(project_yml)],
                cwd=str(self.project_dir),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print(f"  xcodegen stderr: {result.stderr}")
                raise RuntimeError(f"xcodegen failed (exit {result.returncode})")
            print(
                f"  xcodegen succeeded: {self.project_dir / (self.project_name + '.xcodeproj')}"
            )
        except FileNotFoundError:
            print("  WARNING: xcodegen not found. Install with: brew install xcodegen")
            print(
                "  Skipping .xcodeproj generation — manual Xcode setup will be needed."
            )

        return project_yml

    # =========================================================================
    # STEP 3: Generate app icons
    # =========================================================================
    def generate_app_icons(self, icon_source: str | Path | None = None) -> int:
        """
        Generate all required iMessage app icon sizes from a source image.

        Args:
            icon_source: Path to source image. Defaults to first sticker in pack.

        Returns:
            Number of icon sizes generated.
        """
        print("\n[Step 3/6] Generating app icons...")
        iconset_dir = (
            self.project_dir
            / "Stickers.xcstickers"
            / "iMessage App Icon.stickersiconset"
        )
        iconset_dir.mkdir(parents=True, exist_ok=True)

        # Find source image
        if icon_source:
            source_path = Path(icon_source)
        else:
            pngs = sorted(self.sticker_dir.glob("*.png"))
            if not pngs:
                print("  WARNING: No PNG stickers found for icon generation.")
                return 0
            source_path = pngs[0]

        print(f"  Source image: {source_path.name}")

        # Open and prepare the source image
        img = Image.open(source_path).convert("RGBA")

        # Generate each required icon size
        images_entries = []
        count = 0

        for width, height, scale, idiom, platform in ICON_SPECS:
            actual_w = width * scale
            actual_h = height * scale
            filename = f"icon_{actual_w}x{actual_h}.png"

            # Resize: fit the sticker into the icon dimensions, centered on white bg
            icon = self._create_icon(img, actual_w, actual_h)
            icon.save(iconset_dir / filename, "PNG")

            entry = {
                "filename": filename,
                "idiom": idiom,
                "scale": f"{scale}x",
                "size": f"{width}x{height}",
            }
            if platform:
                entry["platform"] = platform

            images_entries.append(entry)
            count += 1

        # Write Contents.json
        contents = {
            "images": images_entries,
            "info": {"author": "xcode", "version": 1},
        }
        with open(iconset_dir / "Contents.json", "w") as f:
            json.dump(contents, f, indent=2)

        print(f"  Generated {count} icon sizes in {iconset_dir.name}")
        return count

    @staticmethod
    def _create_icon(source: Image.Image, target_w: int, target_h: int) -> Image.Image:
        """
        Create an icon by fitting the source image into the target dimensions.

        Centers the sticker on a white background with padding.
        """
        # Create white background
        icon = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))

        # Calculate size with 10% padding
        padding = 0.1
        available_w = int(target_w * (1 - 2 * padding))
        available_h = int(target_h * (1 - 2 * padding))

        # Maintain aspect ratio
        src_w, src_h = source.size
        ratio = min(available_w / src_w, available_h / src_h)
        new_w = int(src_w * ratio)
        new_h = int(src_h * ratio)

        # Resize with high quality
        resized = source.resize((new_w, new_h), Image.LANCZOS)

        # Center on background
        offset_x = (target_w - new_w) // 2
        offset_y = (target_h - new_h) // 2
        icon.paste(resized, (offset_x, offset_y), resized)

        return icon

    # =========================================================================
    # STEP 4: Populate Fastlane metadata
    # =========================================================================
    def populate_metadata(self) -> None:
        """Fill fastlane/metadata/ template files from pack config."""
        print("\n[Step 4/6] Populating Fastlane metadata...")
        metadata_dir = self.fastlane_dir / "metadata" / "en-US"
        metadata_dir.mkdir(parents=True, exist_ok=True)

        # Load the metadata template
        template_path = self.templates_dir / "imessage_metadata.json"
        if template_path.exists():
            with open(template_path) as f:
                meta_template = json.load(f)
        else:
            meta_template = {}
            print(f"  WARNING: Metadata template not found at {template_path}")

        # Substitution values
        subs = {
            "{pack_name}": self.pack_name.replace("_", " ").title(),
            "{character_name}": self.character_name,
            "{sticker_count}": str(self.sticker_count),
        }

        def apply_subs(text: str) -> str:
            for key, val in subs.items():
                text = text.replace(key, val)
            return text

        # Map template keys to metadata files
        file_mapping = {
            "app_name": "name.txt",
            "subtitle": "subtitle.txt",
            "description": "description.txt",
            "keywords": "keywords.txt",
            "privacy_url": "privacy_url.txt",
            "support_url": "support_url.txt",
        }

        for key, filename in file_mapping.items():
            value = meta_template.get(key, "")
            if value:
                value = apply_subs(value)
                filepath = metadata_dir / filename
                filepath.write_text(value)
                print(f"  Wrote {filename}: {value[:60]}...")

        # Release notes
        release_notes_path = metadata_dir / "release_notes.txt"
        release_notes_path.write_text(
            f"Initial release with {self.sticker_count} stickers."
        )
        print(f"  Wrote release_notes.txt")

        print(f"  Metadata populated in {metadata_dir}")

    # =========================================================================
    # STEP 5: Generate App Store screenshots
    # =========================================================================
    def generate_screenshots(self, max_stickers_per_row: int = 4) -> int:
        """
        Generate App Store screenshot composites showing stickers in a grid.

        Creates screenshots for each required device size with stickers arranged
        in a grid on a gradient background.

        Returns:
            Number of screenshots generated.
        """
        print("\n[Step 5/6] Generating App Store screenshots...")
        screenshots_dir = self.fastlane_dir / "screenshots" / "en-US"
        screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Gather sticker images
        pngs = sorted(self.sticker_dir.glob("*.png"))
        if not pngs:
            print("  WARNING: No stickers found for screenshots.")
            return 0

        # Use up to 12 stickers for the grid
        sticker_images = []
        for png in pngs[:12]:
            sticker_images.append(Image.open(png).convert("RGBA"))

        count = 0
        for device_name, (screen_w, screen_h) in SCREENSHOT_SIZES.items():
            screenshot = self._create_screenshot_composite(
                sticker_images, screen_w, screen_h, max_stickers_per_row
            )
            filename = f"{device_name}_01.png"
            screenshot.save(screenshots_dir / filename, "PNG")
            print(f"  Generated {filename} ({screen_w}x{screen_h})")
            count += 1

        # Close opened images
        for img in sticker_images:
            img.close()

        print(f"  {count} screenshots saved to {screenshots_dir}")
        return count

    def _create_screenshot_composite(
        self,
        stickers: list[Image.Image],
        width: int,
        height: int,
        max_per_row: int,
    ) -> Image.Image:
        """Create a screenshot composite with stickers in a grid layout."""
        # Create gradient background (light purple to light blue) using numpy
        import numpy as np

        arr = np.zeros((height, width, 3), dtype=np.uint8)
        ratios = np.linspace(0.0, 1.0, height).reshape(-1, 1)
        arr[:, :, 0] = (230 + (200 - 230) * ratios).astype(np.uint8)  # R
        arr[:, :, 1] = (210 + (220 - 210) * ratios).astype(np.uint8)  # G
        arr[:, :, 2] = 255  # B stays constant
        screenshot = Image.fromarray(arr)

        if not stickers:
            return screenshot

        # Calculate grid layout
        n = len(stickers)
        cols = min(n, max_per_row)
        rows = (n + cols - 1) // cols

        # Sticker sizing: fit within grid cells with padding
        padding = int(width * 0.05)
        title_space = int(height * 0.12)  # Space for title text at top
        cell_w = (width - padding * 2) // cols
        cell_h = (height - padding * 2 - title_space) // rows
        sticker_size = int(min(cell_w, cell_h) * 0.8)

        # Place stickers in grid
        start_y = title_space + padding
        for i, sticker in enumerate(stickers):
            row = i // cols
            col = i % cols

            # Resize sticker
            resized = sticker.resize((sticker_size, sticker_size), Image.LANCZOS)

            # Center in cell
            cell_x = padding + col * cell_w + (cell_w - sticker_size) // 2
            cell_y = start_y + row * cell_h + (cell_h - sticker_size) // 2

            # Paste with alpha
            screenshot.paste(resized, (cell_x, cell_y), resized)

        return screenshot

    # =========================================================================
    # STEP 6: Run Fastlane
    # =========================================================================
    def run_fastlane(self, skip_submit: bool = False) -> bool:
        """
        Invoke Fastlane to build, upload, and optionally submit the app.

        Args:
            skip_submit: If True, upload to App Store Connect but don't submit for review.

        Returns:
            True if Fastlane succeeded.
        """
        xcodeproj = self.project_dir / f"{self.project_name}.xcodeproj"

        if self.dry_run:
            print("\n[Step 6/6] DRY RUN — Skipping Fastlane invocation")
            print(f"  Would run: fastlane publish project:{xcodeproj}")
            return True

        print("\n[Step 6/6] Running Fastlane...")

        # Set environment for Fastlane
        env = os.environ.copy()
        env["XCODE_PROJECT"] = str(xcodeproj)

        lane = "upload" if skip_submit else "publish"
        cmd = ["fastlane", lane, f"project:{xcodeproj}"]

        print(f"  Command: {' '.join(cmd)}")
        print(f"  Working dir: {self.fastlane_dir.parent}")

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.fastlane_dir.parent),
                env=env,
                timeout=600,  # 10 minute timeout
            )
            if result.returncode != 0:
                print(f"\n  Fastlane failed with exit code {result.returncode}")
                return False
            print("\n  Fastlane completed successfully!")
            return True
        except FileNotFoundError:
            print("  ERROR: Fastlane not found. Install with: gem install fastlane")
            return False
        except subprocess.TimeoutExpired:
            print("  ERROR: Fastlane timed out after 10 minutes")
            return False

    # =========================================================================
    # FULL PIPELINE
    # =========================================================================
    def publish(
        self, skip_submit: bool = False, icon_source: str | None = None
    ) -> bool:
        """
        Run the full iMessage publishing pipeline.

        Args:
            skip_submit: If True, upload but don't submit for review.
            icon_source: Optional path to a custom icon image.

        Returns:
            True if all steps succeeded.
        """
        print("=" * 60)
        print(f"iMessage Publisher — {self.pack_name}")
        print(f"  Project: {self.project_name}")
        print(f"  Stickers: {self.sticker_count}")
        print(f"  Bundle ID: {self.bundle_id}")
        print(f"  Team ID: {self.team_id or '(not set)'}")
        print(f"  Dry run: {self.dry_run}")
        print("=" * 60)

        if not self.team_id and not self.dry_run:
            print("\nERROR: APPLE_TEAM_ID environment variable not set.")
            print("Set it in .env or export it before running.")
            return False

        # Step 1: Generate Xcode project structure (stickers + Info.plist)
        self.generate_xcode_project()

        # Step 2: Generate real .xcodeproj via xcodegen
        self.generate_xcode_project_file()

        # Step 3: Generate app icons
        self.generate_app_icons(icon_source)

        # Step 4: Populate Fastlane metadata from templates + config
        self.populate_metadata()

        # Step 5: Generate App Store screenshots
        self.generate_screenshots()

        # Step 6: Run Fastlane (build → upload → submit)
        success = self.run_fastlane(skip_submit=skip_submit)

        if success:
            print("\n" + "=" * 60)
            print("iMessage publishing pipeline completed!")
            print(f"  Build dir: {self.build_dir}")
            if self.dry_run:
                print("  (Dry run — no Fastlane commands were executed)")
            elif skip_submit:
                print("  App uploaded to App Store Connect (not submitted for review)")
            else:
                print("  App submitted for review. Check App Store Connect for status.")
            print("=" * 60)
        else:
            print("\n  Pipeline failed at Fastlane step.")

        return success


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="iMessage Sticker Pack Publisher — Build and submit to App Store",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run (prepare everything, don't submit):
    python imessage_publisher.py pack01_emotions_v1 --dry-run

    # Upload only (don't submit for review):
    python imessage_publisher.py pack01_emotions_v1 --skip-submit

    # Full publish (build + upload + submit for review):
    python imessage_publisher.py pack01_emotions_v1

Environment variables:
    APPLE_ID          - Your Apple ID email
    APPLE_TEAM_ID     - Apple Developer Team ID
    BUNDLE_ID         - App bundle identifier (e.g., com.yourbrand.stickers)
    MATCH_GIT_URL     - Git repo URL for Fastlane Match certificates
""",
    )
    parser.add_argument(
        "pack_dir",
        help="Path to the pack output directory (contains final/ subdir)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare everything but don't run Fastlane",
    )
    parser.add_argument(
        "--skip-submit",
        action="store_true",
        help="Upload to App Store Connect but don't submit for review",
    )
    parser.add_argument(
        "--icon",
        help="Path to custom icon source image (defaults to first sticker)",
    )
    parser.add_argument(
        "--pack-config",
        help="Path to pack_config.py (default: auto-detect from pack_dir)",
    )

    args = parser.parse_args()

    # Resolve pack config: explicit --pack-config, or auto-detect from pack_dir
    pack_config = None
    config_path = args.pack_config
    if not config_path:
        search = Path(args.pack_dir).resolve()
        for parent in [search] + list(search.parents):
            candidate = parent / "pack_config.py"
            if candidate.exists():
                config_path = str(candidate)
                print(f"  Auto-detected pack config: {config_path}")
                break
            if (parent / ".git").exists():
                break
    if config_path:
        pack_config = _load_pack_config(config_path)

    publisher = IMessagePublisher(
        pack_dir=args.pack_dir,
        pack_config=pack_config,
        dry_run=args.dry_run,
    )

    success = publisher.publish(
        skip_submit=args.skip_submit,
        icon_source=args.icon,
    )
    sys.exit(0 if success else 1)
