#!/usr/bin/env python3
"""
iMessage Sticker Pack Preparer - Automate Xcode asset placement.

Creates the correct directory structure for an Xcode Sticker Pack Application.
Can also generate app icons and xcodegen YAML for a complete buildable project.

Prerequisites:
    - macOS with Xcode installed
    - Apple Developer Program membership ($99/year)
    - For --full mode: Pillow, xcodegen (brew install xcodegen)

Usage:
    # Prepare assets for an existing Xcode project:
    python prepare_imessage_pack.py <processed_dir> <xcode_stickerpack_dir>

    # Create a new Xcode project from scratch:
    python prepare_imessage_pack.py --create <pack_name> <processed_dir>

    # Full mode: project structure + app icons + xcodegen YAML:
    python prepare_imessage_pack.py --create <pack_name> <processed_dir> --full

    # Specify a custom icon source image:
    python prepare_imessage_pack.py --create <pack_name> <processed_dir> --full --icon icon.png

Example:
    python prepare_imessage_pack.py \\
        pack01_emotions_v1/final/imessage_large \\
        MochiEmotions/Stickers.xcstickers/Sticker\\ Pack.stickerpack
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def prepare_imessage_assets(
    processed_dir: str,
    xcode_stickerpack_dir: str,
    grid_size: str = "regular",
) -> int:
    """
    Copy processed stickers into the Xcode .stickerpack structure.

    Args:
        processed_dir: Path to pipeline output dir (PNG files)
        xcode_stickerpack_dir: Path to .stickerpack folder in Xcode project
        grid_size: "small" (300px), "regular" (408px), or "large" (618px)

    Returns:
        Number of stickers prepared
    """
    src = Path(processed_dir)
    dest = Path(xcode_stickerpack_dir)
    dest.mkdir(parents=True, exist_ok=True)

    pngs = sorted(src.glob("*.png"))
    if not pngs:
        print(f"No PNG files found in {processed_dir}")
        return 0

    print(f"\nPreparing {len(pngs)} stickers for iMessage")
    print(f"  Source: {src}")
    print(f"  Target: {dest}")
    print(f"  Grid size: {grid_size}")

    for png in pngs:
        sticker_dir = dest / f"{png.stem}.sticker"
        sticker_dir.mkdir(exist_ok=True)

        # Copy the image
        shutil.copy2(png, sticker_dir / png.name)

        # Create Contents.json for each sticker
        contents = {
            "info": {"version": 1, "author": "xcode"},
            "properties": {"filename": png.name},
        }
        with open(sticker_dir / "Contents.json", "w") as f:
            json.dump(contents, f, indent=2)

        print(f"  Added: {png.stem}")

    # Create pack-level Contents.json
    pack_contents = {
        "info": {"version": 1, "author": "xcode"},
        "properties": {"grid-size": grid_size},
    }
    with open(dest / "Contents.json", "w") as f:
        json.dump(pack_contents, f, indent=2)

    print(f"\nPrepared {len(pngs)} stickers in {dest}")
    return len(pngs)


# =============================================================================
# ICON SIZES REQUIRED FOR iMESSAGE STICKER APPS
# =============================================================================
# (width, height, scale, idiom, platform_or_None)
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


def _create_icon_image(
    source: "Image.Image", target_w: int, target_h: int
) -> "Image.Image":
    """
    Create an icon by fitting the source image into the target dimensions.

    Centers the sticker on a white background with 10% padding.
    Requires PIL/Pillow (imported lazily so the base module stays lightweight).
    """
    from PIL import Image

    icon = Image.new("RGBA", (target_w, target_h), (255, 255, 255, 255))

    # Calculate size with 10% padding
    padding = 0.1
    available_w = int(target_w * (1 - 2 * padding))
    available_h = int(target_h * (1 - 2 * padding))

    src_w, src_h = source.size
    ratio = min(available_w / src_w, available_h / src_h)
    new_w = int(src_w * ratio)
    new_h = int(src_h * ratio)

    resized = source.resize((new_w, new_h), Image.LANCZOS)

    offset_x = (target_w - new_w) // 2
    offset_y = (target_h - new_h) // 2
    icon.paste(resized, (offset_x, offset_y), resized)

    return icon


def generate_app_icons(
    iconset_dir: str | Path,
    icon_source: str | Path | None = None,
    sticker_dir: str | Path | None = None,
) -> int:
    """
    Generate all required iMessage app icon sizes from a source image.

    This is a standalone function that can be used independently of the
    IMessagePublisher class. Pass either an explicit icon_source image
    or a sticker_dir (the first PNG in alphabetical order will be used).

    Args:
        iconset_dir: Path to the .stickersiconset directory to write icons into.
        icon_source: Path to a specific source image. Takes priority.
        sticker_dir: Fallback — directory of PNGs; the first one is used.

    Returns:
        Number of icon sizes generated.
    """
    from PIL import Image

    iconset_dir = Path(iconset_dir)
    iconset_dir.mkdir(parents=True, exist_ok=True)

    # Resolve source image
    source_path = None
    if icon_source:
        source_path = Path(icon_source)
    elif sticker_dir:
        pngs = sorted(Path(sticker_dir).glob("*.png"))
        if pngs:
            source_path = pngs[0]

    if not source_path or not source_path.exists():
        print("  WARNING: No source image found for icon generation.")
        return 0

    print(f"  Icon source: {source_path.name}")
    img = Image.open(source_path).convert("RGBA")

    images_entries = []
    count = 0

    for width, height, scale, idiom, platform in ICON_SPECS:
        actual_w = width * scale
        actual_h = height * scale
        filename = f"icon_{actual_w}x{actual_h}.png"

        icon = _create_icon_image(img, actual_w, actual_h)
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

    img.close()
    print(f"  Generated {count} icon sizes in {iconset_dir.name}")
    return count


def generate_xcodegen_yaml(
    project_dir: str | Path,
    project_name: str,
    bundle_id_prefix: str = "com.yourbrand",
    team_id: str = "",
) -> Path:
    """
    Generate a xcodegen project.yml in *project_dir* and optionally run xcodegen.

    Looks for the template at ``templates/imessage_project.yml`` relative to the
    repo root (parent of the ``scripts/`` directory).  If the template is missing
    the function writes a minimal inline spec instead.

    Args:
        project_dir: Root of the Xcode project (where project.yml will live).
        project_name: e.g. "MochiEmotions".
        bundle_id_prefix: e.g. "com.yourbrand".
        team_id: Apple Developer Team ID (may be empty for local builds).

    Returns:
        Path to the generated project.yml.
    """
    project_dir = Path(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)

    repo_root = Path(__file__).resolve().parent.parent
    template_path = repo_root / "templates" / "imessage_project.yml"
    bundle_id = f"{bundle_id_prefix}.{project_name.lower()}"

    if template_path.exists():
        yaml_content = (
            template_path.read_text()
            .replace("{{PROJECT_NAME}}", project_name)
            .replace("{{BUNDLE_ID_PREFIX}}", bundle_id_prefix)
            .replace("{{TEAM_ID}}", team_id)
            .replace("{{BUNDLE_ID}}", bundle_id)
        )
    else:
        # Minimal inline fallback
        yaml_content = f"""\
name: {project_name}
options:
  bundleIdPrefix: {bundle_id_prefix}
settings:
  DEVELOPMENT_TEAM: {team_id}
targets:
  "{project_name} StickerPackExtension":
    type: app-extension.messages-sticker-pack
    platform: iOS
    sources:
      - path: Stickers.xcstickers
    settings:
      PRODUCT_BUNDLE_IDENTIFIER: {bundle_id}.StickerPackExtension
  "{project_name}":
    type: application.messages
    platform: iOS
    settings:
      PRODUCT_BUNDLE_IDENTIFIER: {bundle_id}
    dependencies:
      - target: "{project_name} StickerPackExtension"
"""

    project_yml = project_dir / "project.yml"
    project_yml.write_text(yaml_content)
    print(f"  Generated xcodegen spec: {project_yml}")

    # Attempt to run xcodegen if available
    try:
        result = subprocess.run(
            ["xcodegen", "generate", "--spec", str(project_yml)],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            print(f"  xcodegen stderr: {result.stderr}")
            print("  WARNING: xcodegen failed — manual Xcode setup may be needed.")
        else:
            print(
                f"  xcodegen succeeded: {project_dir / (project_name + '.xcodeproj')}"
            )
    except FileNotFoundError:
        print("  WARNING: xcodegen not found. Install with: brew install xcodegen")
        print("  Skipping .xcodeproj generation — manual Xcode setup will be needed.")
    except subprocess.TimeoutExpired:
        print("  WARNING: xcodegen timed out.")

    return project_yml


def create_xcode_project(
    project_name: str,
    sticker_dir: str,
    bundle_id_prefix: str = "com.yourbrand",
    output_dir: str = ".",
    icon_source: str | None = None,
    full: bool = False,
    team_id: str = "",
) -> Path:
    """
    Create a complete Xcode Sticker Pack Application project structure.

    In default mode this creates the directory structure and sticker assets.
    With ``full=True`` it also generates app icons, a xcodegen YAML spec,
    and (if xcodegen is installed) the .xcodeproj file — making the project
    ready to build without opening Xcode manually.

    Args:
        project_name: e.g., "MochiEmotions"
        sticker_dir: Directory with processed PNG stickers
        bundle_id_prefix: e.g., "com.yourbrand"
        output_dir: Where to create the project
        icon_source: Path to an image to use for app icons. If None and
            ``full=True``, the first sticker PNG is used automatically.
        full: When True, also generate app icons and xcodegen YAML.
        team_id: Apple Developer Team ID (used when ``full=True``).

    Returns:
        Path to the created project directory
    """
    project_dir = Path(output_dir) / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Create the .xcodeproj directory structure
    xcodeproj = project_dir / f"{project_name}.xcodeproj"
    xcodeproj.mkdir(exist_ok=True)

    # Create Stickers.xcstickers structure
    xcstickers = project_dir / "Stickers.xcstickers"
    xcstickers.mkdir(exist_ok=True)

    # Create iMessage App Icon set
    iconset = xcstickers / "iMessage App Icon.stickersiconset"
    iconset.mkdir(exist_ok=True)

    icon_contents = {
        "images": [
            {"filename": "", "idiom": "iphone", "scale": "2x", "size": "60x45"},
            {"filename": "", "idiom": "iphone", "scale": "3x", "size": "60x45"},
            {"filename": "", "idiom": "ipad", "scale": "2x", "size": "67x50"},
            {"filename": "", "idiom": "ipad", "scale": "2x", "size": "74x55"},
            {
                "filename": "",
                "idiom": "universal",
                "platform": "ios",
                "scale": "2x",
                "size": "27x20",
            },
            {
                "filename": "",
                "idiom": "universal",
                "platform": "ios",
                "scale": "3x",
                "size": "27x20",
            },
            {
                "filename": "",
                "idiom": "universal",
                "platform": "ios",
                "scale": "2x",
                "size": "32x24",
            },
            {
                "filename": "",
                "idiom": "universal",
                "platform": "ios",
                "scale": "3x",
                "size": "32x24",
            },
            {
                "filename": "",
                "idiom": "ios-marketing",
                "scale": "1x",
                "size": "1024x768",
            },
        ],
        "info": {"author": "xcode", "version": 1},
    }
    with open(iconset / "Contents.json", "w") as f:
        json.dump(icon_contents, f, indent=2)

    # Create xcstickers Contents.json
    xcstickers_contents = {
        "info": {"author": "xcode", "version": 1},
    }
    with open(xcstickers / "Contents.json", "w") as f:
        json.dump(xcstickers_contents, f, indent=2)

    # Create the sticker pack and populate it
    stickerpack = xcstickers / "Sticker Pack.stickerpack"
    count = prepare_imessage_assets(sticker_dir, str(stickerpack), "regular")

    # Create Info.plist for StickerPackExtension
    info_plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>{project_name}</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>{bundle_id_prefix}.{project_name.lower()}.StickerPackExtension</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>XPC!</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.message-payload-provider</string>
        <key>NSExtensionPrincipalClass</key>
        <string>StickerBrowserViewController</string>
    </dict>
</dict>
</plist>"""

    with open(project_dir / "Info.plist", "w") as f:
        f.write(info_plist)

    # ------------------------------------------------------------------
    # Full mode: generate app icons + xcodegen YAML / .xcodeproj
    # ------------------------------------------------------------------
    if full:
        print("\n--- Full mode: generating app icons ---")
        generate_app_icons(
            iconset_dir=iconset,
            icon_source=icon_source,
            sticker_dir=sticker_dir,
        )

        print("\n--- Full mode: generating xcodegen YAML ---")
        generate_xcodegen_yaml(
            project_dir=project_dir,
            project_name=project_name,
            bundle_id_prefix=bundle_id_prefix,
            team_id=team_id,
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print(f"\n{'=' * 60}")
    print(f"Xcode project structure created: {project_dir}")
    print(f"Stickers added: {count}")
    if full:
        print(f"App icons: generated in {iconset.name}")
        print(f"xcodegen spec: {project_dir / 'project.yml'}")
        print(f"\nNext steps:")
        print(f"  1. Configure signing (Apple Developer Team)")
        print(f"  2. Run: fastlane publish (or open .xcodeproj in Xcode)")
    else:
        print(f"\nNext steps:")
        print(f"  1. Open Xcode -> File -> New -> Project -> Sticker Pack Application")
        print(f"  2. Name it '{project_name}'")
        print(f"  3. Copy the Stickers.xcstickers folder into your Xcode project")
        print(f"  4. Or: drag the .stickerpack folder into Xcode's project navigator")
        print(f"  5. Add app icons (required for submission)")
        print(f"  6. Configure signing (Apple Developer Team)")
        print(f"  7. Archive -> Distribute -> App Store Connect")
    print(f"{'=' * 60}")

    return project_dir


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="iMessage Sticker Pack Preparer — Automate Xcode asset placement.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  # Prepare assets for an existing Xcode project:
  %(prog)s pack01/final/imessage_large MochiEmotions/Stickers.xcstickers/Sticker\\ Pack.stickerpack

  # Create a new Xcode project from scratch:
  %(prog)s --create MochiEmotions pack01/final/imessage_large

  # Full mode (icons + xcodegen):
  %(prog)s --create MochiEmotions pack01/final/imessage_large --full

  # Full mode with a custom icon source:
  %(prog)s --create MochiEmotions pack01/final/imessage_large --full --icon icon.png
""",
    )

    parser.add_argument(
        "--create",
        metavar="PROJECT_NAME",
        help="Create a new Xcode project structure with this name.",
    )
    parser.add_argument(
        "positional",
        nargs="*",
        help=(
            "Without --create: <processed_dir> <xcode_stickerpack_dir> [grid_size]. "
            "With --create: <processed_dir>."
        ),
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also generate app icons and xcodegen YAML (requires Pillow).",
    )
    parser.add_argument(
        "--icon",
        metavar="IMAGE",
        default=None,
        help="Source image for app icon generation (used with --full).",
    )
    parser.add_argument(
        "--bundle-id-prefix",
        default="com.yourbrand",
        help="Bundle ID prefix (default: com.yourbrand).",
    )
    parser.add_argument(
        "--team-id",
        default=os.environ.get("APPLE_TEAM_ID", ""),
        help="Apple Developer Team ID (default: $APPLE_TEAM_ID).",
    )
    parser.add_argument(
        "--grid-size",
        choices=["small", "regular", "large"],
        default="regular",
        help="Sticker grid size (default: regular).",
    )

    args = parser.parse_args()

    if args.create:
        # --create mode: expects exactly 1 positional (processed_dir)
        if len(args.positional) < 1:
            parser.error("--create requires: <processed_dir>")
        processed_dir = args.positional[0]
        create_xcode_project(
            project_name=args.create,
            sticker_dir=processed_dir,
            bundle_id_prefix=args.bundle_id_prefix,
            icon_source=args.icon,
            full=args.full,
            team_id=args.team_id,
        )
    else:
        # Asset-copy mode: expects 2 positionals (processed_dir, xcode_stickerpack_dir)
        if len(args.positional) < 2:
            parser.error("Requires: <processed_dir> <xcode_stickerpack_dir>")
        processed_dir = args.positional[0]
        xcode_dir = args.positional[1]
        prepare_imessage_assets(processed_dir, xcode_dir, args.grid_size)
