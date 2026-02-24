#!/usr/bin/env python3
"""
Telegram Sticker Publisher - Automate sticker set creation via Telegram Bot API.

Telegram is the MOST automatable sticker platform - full Bot API support.
Supports static (WebP/PNG), animated (TGS/Lottie), and video (WebM VP9) formats.

Setup:
    1. Message @BotFather on Telegram -> /newbot -> get your bot token
    2. Message @userinfobot -> get your numeric user ID
    3. Set environment variables:
       export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
       export TELEGRAM_USER_ID="987654321"

Usage:
    python telegram_publisher.py <sticker_dir> <pack_name> <pack_title> [--format FORMAT]

    # Static stickers (default):
    python telegram_publisher.py pack01_emotions_v1/final/telegram \\
        MochiEmotions_by_YourBot "Mochi Emotions Vol. 1"

    # Animated TGS stickers:
    python telegram_publisher.py pack01_emotions_v1/final/telegram_animated \\
        MochiAnimated_by_YourBot "Mochi Animated Vol. 1" --format animated

    # Video WebM stickers:
    python telegram_publisher.py pack01_emotions_v1/final/telegram_video \\
        MochiVideo_by_YourBot "Mochi Video Vol. 1" --format video
"""

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

# Ensure sibling scripts are importable regardless of CWD
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import requests

# ---------------------------------------------------------------------------
# Format constants and limits
# ---------------------------------------------------------------------------
# Telegram Bot API sticker format identifiers
FORMAT_STATIC = "static"
FORMAT_ANIMATED = "animated"
FORMAT_VIDEO = "video"

# File extensions per format
FORMAT_EXTENSIONS = {
    FORMAT_STATIC: (".webp", ".png"),
    FORMAT_ANIMATED: (".tgs",),
    FORMAT_VIDEO: (".webm",),
}

# Maximum file sizes (bytes) per Telegram documentation
FORMAT_MAX_SIZE = {
    FORMAT_STATIC: 512_000,  # 512 KB for static WebP/PNG
    FORMAT_ANIMATED: 64_000,  # 64 KB for TGS
    FORMAT_VIDEO: 256_000,  # 256 KB for WebM
}

# MIME types for correct file upload
FORMAT_MIME = {
    ".webp": "image/webp",
    ".png": "image/png",
    ".tgs": "application/x-tgs",
    ".webm": "video/webm",
}


def detect_sticker_format(file_path: str) -> str:
    """Detect sticker format from file extension.

    Args:
        file_path: Path to a sticker file.

    Returns:
        One of "static", "animated", or "video".

    Raises:
        ValueError: If the extension is not a recognized sticker format.
    """
    ext = Path(file_path).suffix.lower()
    for fmt, extensions in FORMAT_EXTENSIONS.items():
        if ext in extensions:
            return fmt
    raise ValueError(
        f"Unrecognized sticker file extension '{ext}'. "
        f"Expected one of: {', '.join(e for exts in FORMAT_EXTENSIONS.values() for e in exts)}"
    )


def validate_sticker_file(file_path: str, sticker_format: str | None = None) -> None:
    """Validate a sticker file's size against Telegram limits.

    Args:
        file_path: Path to the sticker file.
        sticker_format: Format string; auto-detected if None.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file exceeds the size limit for its format.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Sticker file not found: {file_path}")

    if sticker_format is None:
        sticker_format = detect_sticker_format(file_path)

    max_size = FORMAT_MAX_SIZE.get(sticker_format)
    if max_size is None:
        return  # unknown format, skip validation

    actual_size = path.stat().st_size
    if actual_size > max_size:
        raise ValueError(
            f"Sticker file too large for '{sticker_format}' format: "
            f"{actual_size:,} bytes > {max_size:,} bytes limit — {path.name}"
        )


def find_sticker_files(
    directory: str, sticker_format: str = FORMAT_STATIC
) -> list[Path]:
    """Find sticker files in a directory matching the given format.

    Args:
        directory: Directory to search.
        sticker_format: One of "static", "animated", "video".

    Returns:
        Sorted list of matching file paths.
    """
    dir_path = Path(directory)
    extensions = FORMAT_EXTENSIONS.get(sticker_format, FORMAT_EXTENSIONS[FORMAT_STATIC])
    files = []
    for ext in extensions:
        files.extend(dir_path.glob(f"*{ext}"))
    return sorted(set(files))


class TelegramStickerPublisher:
    """Publish sticker packs to Telegram via Bot API.

    Supports static (WebP/PNG), animated (TGS), and video (WebM) sticker
    formats.  Format is auto-detected from file extensions when not explicitly
    specified.
    """

    def __init__(self, bot_token: str | None = None):
        """
        Args:
            bot_token: Telegram bot token from @BotFather.
                       Falls back to TELEGRAM_BOT_TOKEN env var.
        """
        self.token = bot_token or os.environ.get("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError(
                "Telegram bot token required. Set TELEGRAM_BOT_TOKEN env var "
                "or pass bot_token."
            )
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def _api_call(self, method: str, data: dict = None, files: dict = None) -> dict:
        """Make a Telegram Bot API call."""
        url = f"{self.base_url}/{method}"
        response = requests.post(url, data=data, files=files, timeout=30)
        result = response.json()

        if not result.get("ok"):
            error_desc = result.get("description", "Unknown error")
            error_code = result.get("error_code", "?")
            raise RuntimeError(f"Telegram API error [{error_code}]: {error_desc}")

        return result

    def get_bot_info(self) -> dict:
        """Get bot information (verify token is valid)."""
        result = self._api_call("getMe")
        return result["result"]

    def create_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        sticker_paths: list[str],
        emojis_list: list[str],
        sticker_format: str = "static",
    ) -> str:
        """
        Create a new sticker set on Telegram.

        Args:
            user_id: Your Telegram user ID (get from @userinfobot)
            name: Short name for the set (alphanumeric + underscore).
                  MUST end with _by_<botname>
            title: Display title of the sticker pack
            sticker_paths: List of sticker file paths.
                  Static: WebP/PNG (512px on one side, ≤512KB)
                  Animated: TGS (≤64KB)
                  Video: WebM VP9 (≤256KB)
            emojis_list: List of emoji strings for each sticker
            sticker_format: "static", "animated", or "video".
                  Auto-detected from first file if set to "auto".

        Returns:
            URL to the sticker pack: https://t.me/addstickers/<name>
        """
        if len(sticker_paths) != len(emojis_list):
            raise ValueError(
                f"Mismatch: {len(sticker_paths)} stickers but {len(emojis_list)} emoji entries"
            )

        if not sticker_paths:
            raise ValueError("Need at least 1 sticker")

        # Auto-detect format from file extension if requested
        if sticker_format == "auto":
            sticker_format = detect_sticker_format(sticker_paths[0])

        # Validate all files before starting upload
        print(
            f"\n  Validating {len(sticker_paths)} sticker files ({sticker_format})..."
        )
        for path in sticker_paths:
            validate_sticker_file(path, sticker_format)

        # Verify bot info to get bot username
        bot_info = self.get_bot_info()
        bot_username = bot_info["username"]

        # Ensure name ends with _by_<botname>
        suffix = f"_by_{bot_username}"
        if not name.endswith(suffix):
            name = f"{name}{suffix}"

        print(f"\nCreating Telegram sticker set: {title}")
        print(f"  Name: {name}")
        print(f"  Format: {sticker_format}")
        print(f"  Stickers: {len(sticker_paths)}")
        print(f"  Bot: @{bot_username}")

        # Build stickers array for the API
        stickers_json = []
        files_dict = {}

        for i, (path, emojis) in enumerate(zip(sticker_paths, emojis_list)):
            file_key = f"sticker_{i}"
            sticker_entry = {
                "sticker": f"attach://{file_key}",
                "emoji_list": emojis if isinstance(emojis, list) else [emojis],
                "format": sticker_format,
            }
            stickers_json.append(sticker_entry)

            # Open file with correct MIME type for Telegram
            p = Path(path)
            mime = FORMAT_MIME.get(p.suffix.lower(), "application/octet-stream")
            files_dict[file_key] = (p.name, open(path, "rb"), mime)

        try:
            self._api_call(
                "createNewStickerSet",
                data={
                    "user_id": user_id,
                    "name": name,
                    "title": title,
                    "stickers": json.dumps(stickers_json),
                },
                files=files_dict,
            )
        except RuntimeError as e:
            # If batch fails, fall back to one-by-one creation
            if "too many" in str(e).lower() or "STICKER_PNG_NOPNG" in str(e):
                print(f"  Batch creation failed ({e}), trying one-by-one...")
                for _, fobj, _ in files_dict.values():
                    fobj.close()
                return self._create_set_sequential(
                    user_id, name, title, sticker_paths, emojis_list, sticker_format
                )
            for _, fobj, _ in files_dict.values():
                fobj.close()
            raise
        finally:
            for val in files_dict.values():
                fobj = val[1] if isinstance(val, tuple) else val
                if not fobj.closed:
                    fobj.close()

        pack_url = f"https://t.me/addstickers/{name}"
        print(f"\n  Pack created successfully!")
        print(f"  URL: {pack_url}")
        return pack_url

    def _create_set_sequential(
        self,
        user_id: int,
        name: str,
        title: str,
        sticker_paths: list[str],
        emojis_list: list[str],
        sticker_format: str,
    ) -> str:
        """Fallback: create set with first sticker, then add rest one by one."""

        # Create set with first sticker
        first_path = Path(sticker_paths[0])
        mime = FORMAT_MIME.get(first_path.suffix.lower(), "application/octet-stream")
        with open(sticker_paths[0], "rb") as f:
            sticker_data = {
                "sticker": "attach://sticker",
                "emoji_list": [emojis_list[0]],
                "format": sticker_format,
            }
            self._api_call(
                "createNewStickerSet",
                data={
                    "user_id": user_id,
                    "name": name,
                    "title": title,
                    "stickers": json.dumps([sticker_data]),
                },
                files={"sticker": (first_path.name, f, mime)},
            )

        print(f"  Created set with first sticker")

        # Add remaining stickers one by one
        for i in range(1, len(sticker_paths)):
            path = sticker_paths[i]
            emoji = emojis_list[i]
            p = Path(path)
            mime = FORMAT_MIME.get(p.suffix.lower(), "application/octet-stream")

            with open(path, "rb") as f:
                sticker_data = {
                    "sticker": "attach://sticker",
                    "emoji_list": [emoji],
                    "format": sticker_format,
                }
                try:
                    self._api_call(
                        "addStickerToSet",
                        data={
                            "user_id": user_id,
                            "name": name,
                            "sticker": json.dumps(sticker_data),
                        },
                        files={"sticker": (p.name, f, mime)},
                    )
                    print(f"  Added [{i + 1}/{len(sticker_paths)}]: {p.name}")
                except RuntimeError as e:
                    print(f"  FAILED [{i + 1}]: {p.name} - {e}")

            time.sleep(0.5)  # Rate limit safety

        pack_url = f"https://t.me/addstickers/{name}"
        print(f"\n  Pack URL: {pack_url}")
        return pack_url

    def create_animated_sticker_set(
        self,
        user_id: int,
        name: str,
        title: str,
        sticker_dir: str,
        emojis_list: list[str],
        sticker_format: str = "animated",
    ) -> str:
        """Create an animated or video sticker set from a directory.

        Convenience wrapper around :meth:`create_sticker_set` that discovers
        TGS or WebM files automatically.

        Args:
            user_id: Telegram numeric user ID.
            name: Short name for the set (will have ``_by_<bot>`` appended).
            title: Display title of the sticker pack.
            sticker_dir: Directory containing ``.tgs`` or ``.webm`` files.
            emojis_list: Emoji strings (one per sticker).
            sticker_format: ``"animated"`` for TGS or ``"video"`` for WebM.

        Returns:
            URL to the sticker pack.
        """
        sticker_files = find_sticker_files(sticker_dir, sticker_format)
        if not sticker_files:
            ext = ", ".join(FORMAT_EXTENSIONS.get(sticker_format, ()))
            raise FileNotFoundError(
                f"No {sticker_format} sticker files ({ext}) found in {sticker_dir}"
            )

        # Trim or pad emojis to match file count
        if len(emojis_list) < len(sticker_files):
            emojis_list = emojis_list + ["\U0001f60a"] * (
                len(sticker_files) - len(emojis_list)
            )
        emojis_list = emojis_list[: len(sticker_files)]

        return self.create_sticker_set(
            user_id=user_id,
            name=name,
            title=title,
            sticker_paths=[str(f) for f in sticker_files],
            emojis_list=emojis_list,
            sticker_format=sticker_format,
        )

    def delete_sticker_set(self, name: str) -> bool:
        """Delete an entire sticker set (useful for re-creating)."""
        try:
            self._api_call("deleteStickerSet", data={"name": name})
            print(f"Deleted sticker set: {name}")
            return True
        except RuntimeError as e:
            print(f"Failed to delete set {name}: {e}")
            return False


def load_emojis_from_config(pack_config: dict) -> list[str]:
    """Extract emoji list from pack config."""
    return [s["emoji"] for s in pack_config["stickers"]]


# =============================================================================
# CLI ENTRY POINT
# =============================================================================
def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Publish sticker packs to Telegram via Bot API.",
        epilog=(
            "Examples:\n"
            "  # Static stickers (default):\n"
            "  python telegram_publisher.py pack01/final/telegram MyPack 'My Pack'\n\n"
            "  # Animated TGS stickers:\n"
            "  python telegram_publisher.py pack01/final/telegram_animated "
            "MyAnimated 'Animated Pack' --format animated\n\n"
            "  # Video WebM stickers:\n"
            "  python telegram_publisher.py pack01/final/telegram_video "
            "MyVideo 'Video Pack' --format video\n\n"
            "  # Delete an existing set first, then recreate:\n"
            "  python telegram_publisher.py pack01/final/telegram MyPack 'My Pack' "
            "--delete-existing\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("sticker_dir", help="Directory containing sticker files")
    parser.add_argument("pack_name", help="Short name for the sticker set")
    parser.add_argument("pack_title", help="Display title of the sticker pack")
    parser.add_argument(
        "--format",
        choices=["static", "animated", "video", "auto"],
        default="auto",
        help="Sticker format (default: auto-detect from files)",
    )
    parser.add_argument(
        "--delete-existing",
        action="store_true",
        help="Delete the existing set with this name before creating",
    )
    parser.add_argument(
        "--pack-config",
        help="Path to pack_config.py (auto-reads emojis per sticker)",
    )
    return parser


if __name__ == "__main__":
    parser = _build_parser()
    args = parser.parse_args()

    user_id = os.environ.get("TELEGRAM_USER_ID")
    if not user_id:
        print("Error: Set TELEGRAM_USER_ID environment variable")
        sys.exit(1)

    # Determine format
    sticker_format = args.format
    if sticker_format == "auto":
        # Probe directory for file types
        dir_path = Path(args.sticker_dir)
        if list(dir_path.glob("*.tgs")):
            sticker_format = FORMAT_ANIMATED
        elif list(dir_path.glob("*.webm")):
            sticker_format = FORMAT_VIDEO
        else:
            sticker_format = FORMAT_STATIC

    # Find sticker files
    sticker_files = find_sticker_files(args.sticker_dir, sticker_format)

    if not sticker_files:
        exts = ", ".join(FORMAT_EXTENSIONS.get(sticker_format, ()))
        print(f"No sticker files ({exts}) found in {args.sticker_dir}")
        sys.exit(1)

    print(f"Found {len(sticker_files)} {sticker_format} sticker(s)")

    # Try to load emojis from pack config
    emojis = None
    if args.pack_config:
        cfg_path = Path(args.pack_config).resolve()
        spec = importlib.util.spec_from_file_location("pack_config_dynamic", cfg_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        emojis = load_emojis_from_config(mod.PACK_CONFIG)

    if emojis is None:
        # Default: use smiley for all
        emojis = ["\U0001f60a"] * len(sticker_files)

    # Match count to actual files
    if len(emojis) < len(sticker_files):
        emojis.extend(["\U0001f60a"] * (len(sticker_files) - len(emojis)))
    emojis = emojis[: len(sticker_files)]

    publisher = TelegramStickerPublisher()

    if args.delete_existing:
        bot_info = publisher.get_bot_info()
        full_name = args.pack_name
        suffix = f"_by_{bot_info['username']}"
        if not full_name.endswith(suffix):
            full_name = f"{full_name}{suffix}"
        publisher.delete_sticker_set(full_name)

    publisher.create_sticker_set(
        user_id=int(user_id),
        name=args.pack_name,
        title=args.pack_title,
        sticker_paths=[str(f) for f in sticker_files],
        emojis_list=emojis,
        sticker_format=sticker_format,
    )
