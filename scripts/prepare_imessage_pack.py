#!/usr/bin/env python3
"""
iMessage Sticker Pack Preparer - Automate Xcode asset placement.

Creates the correct directory structure for an Xcode Sticker Pack Application.
After running this script, open the Xcode project and build/archive.

Prerequisites:
    - macOS with Xcode installed
    - Apple Developer Program membership ($99/year)

Usage:
    # Prepare assets for an existing Xcode project:
    python prepare_imessage_pack.py <processed_dir> <xcode_stickerpack_dir>

    # Create a new Xcode project from scratch:
    python prepare_imessage_pack.py --create <pack_name> <processed_dir>

Example:
    python prepare_imessage_pack.py \\
        pack01_emotions_v1/final/imessage_large \\
        MochiEmotions/Stickers.xcstickers/Sticker\\ Pack.stickerpack
"""

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


def create_xcode_project(
    project_name: str,
    sticker_dir: str,
    bundle_id_prefix: str = "com.yourbrand",
    output_dir: str = ".",
) -> Path:
    """
    Create a complete Xcode Sticker Pack Application project structure.

    NOTE: This creates the directory structure. You still need to:
    1. Open in Xcode
    2. Add app icons
    3. Configure signing (Team, Bundle ID)
    4. Archive and submit to App Store Connect

    Args:
        project_name: e.g., "MochiEmotions"
        sticker_dir: Directory with processed PNG stickers
        bundle_id_prefix: e.g., "com.yourbrand"
        output_dir: Where to create the project

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

    print(f"\n{'=' * 60}")
    print(f"Xcode project structure created: {project_dir}")
    print(f"Stickers added: {count}")
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
    if len(sys.argv) < 3:
        print("Usage:")
        print("  # Prepare assets for existing Xcode project:")
        print(
            "  python prepare_imessage_pack.py <processed_dir> <xcode_stickerpack_dir>"
        )
        print()
        print("  # Create new project structure:")
        print(
            "  python prepare_imessage_pack.py --create <project_name> <processed_dir>"
        )
        print()
        print("Example:")
        print(
            "  python prepare_imessage_pack.py --create MochiEmotions pack01_emotions_v1/final/imessage_large"
        )
        sys.exit(1)

    if sys.argv[1] == "--create":
        project_name = sys.argv[2]
        processed_dir = sys.argv[3]
        create_xcode_project(project_name, processed_dir)
    else:
        processed_dir = sys.argv[1]
        xcode_dir = sys.argv[2]
        grid_size = sys.argv[3] if len(sys.argv) > 3 else "regular"
        prepare_imessage_assets(processed_dir, xcode_dir, grid_size)
