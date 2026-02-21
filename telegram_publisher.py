#!/usr/bin/env python3
"""
Telegram Sticker Publisher - Automate sticker set creation via Telegram Bot API.

Telegram is the MOST automatable sticker platform - full Bot API support.

Setup:
    1. Message @BotFather on Telegram -> /newbot -> get your bot token
    2. Message @userinfobot -> get your numeric user ID
    3. Set environment variables:
       export TELEGRAM_BOT_TOKEN="123456:ABC-DEF..."
       export TELEGRAM_USER_ID="987654321"

Usage:
    python telegram_publisher.py <sticker_dir> <pack_name> <pack_title>

    # Example:
    python telegram_publisher.py pack01_emotions_v1/final/telegram \\
        MochiEmotions_by_YourBot "Mochi Emotions Vol. 1"
"""

import os
import sys
import time
from pathlib import Path

import requests


class TelegramStickerPublisher:
    """Publish sticker packs to Telegram via Bot API."""

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
            sticker_paths: List of WebP/PNG file paths (512px on one side)
            emojis_list: List of emoji strings for each sticker
            sticker_format: "static", "animated", or "video"

        Returns:
            URL to the sticker pack: https://t.me/addstickers/<name>
        """
        if len(sticker_paths) != len(emojis_list):
            raise ValueError(
                f"Mismatch: {len(sticker_paths)} stickers but {len(emojis_list)} emoji entries"
            )

        if not sticker_paths:
            raise ValueError("Need at least 1 sticker")

        # Verify bot info to get bot username
        bot_info = self.get_bot_info()
        bot_username = bot_info["username"]

        # Ensure name ends with _by_<botname>
        suffix = f"_by_{bot_username}"
        if not name.endswith(suffix):
            name = f"{name}{suffix}"

        print(f"\nCreating Telegram sticker set: {title}")
        print(f"  Name: {name}")
        print(f"  Stickers: {len(sticker_paths)}")
        print(f"  Bot: @{bot_username}")

        # Build stickers array for the API
        # First, create the set with all stickers using createNewStickerSet
        stickers_json = []
        files_dict = {}

        for i, (path, emojis) in enumerate(zip(sticker_paths, emojis_list)):
            file_key = f"sticker_{i}"
            sticker_entry = {
                "sticker": f"attach://{file_key}",
                "emoji_list": list(emojis) if len(emojis) > 1 else [emojis],
                "format": sticker_format,
            }
            stickers_json.append(sticker_entry)
            files_dict[file_key] = open(path, "rb")

        try:
            import json

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
                for f in files_dict.values():
                    f.close()
                return self._create_set_sequential(
                    user_id, name, title, sticker_paths, emojis_list, sticker_format
                )
            for f in files_dict.values():
                f.close()
            raise
        finally:
            for f in files_dict.values():
                if not f.closed:
                    f.close()

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
        import json

        # Create set with first sticker
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
                files={"sticker": f},
            )

        print(f"  Created set with first sticker")

        # Add remaining stickers one by one
        for i in range(1, len(sticker_paths)):
            path = sticker_paths[i]
            emoji = emojis_list[i]

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
                        files={"sticker": f},
                    )
                    print(f"  Added [{i + 1}/{len(sticker_paths)}]: {Path(path).name}")
                except RuntimeError as e:
                    print(f"  FAILED [{i + 1}]: {Path(path).name} - {e}")

            time.sleep(0.5)  # Rate limit safety

        pack_url = f"https://t.me/addstickers/{name}"
        print(f"\n  Pack URL: {pack_url}")
        return pack_url

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
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(
            "Usage: python telegram_publisher.py <sticker_dir> <pack_name> <pack_title>"
        )
        print()
        print("Environment variables required:")
        print("  TELEGRAM_BOT_TOKEN  - Get from @BotFather")
        print("  TELEGRAM_USER_ID    - Get from @userinfobot")
        print()
        print("Example:")
        print("  python telegram_publisher.py pack01_emotions_v1/final/telegram \\")
        print('    MochiEmotions "Mochi Emotions Vol. 1"')
        sys.exit(1)

    sticker_dir = sys.argv[1]
    pack_name = sys.argv[2]
    pack_title = sys.argv[3]

    user_id = os.environ.get("TELEGRAM_USER_ID")
    if not user_id:
        print("Error: Set TELEGRAM_USER_ID environment variable")
        sys.exit(1)

    # Find sticker files
    sticker_files = sorted(
        list(Path(sticker_dir).glob("*.webp")) + list(Path(sticker_dir).glob("*.png"))
    )

    if not sticker_files:
        print(f"No sticker files found in {sticker_dir}")
        sys.exit(1)

    # Try to load emojis from pack config
    try:
        from pack_config import PACK_CONFIG

        emojis = load_emojis_from_config(PACK_CONFIG)
        # Match count to actual files
        if len(emojis) < len(sticker_files):
            emojis.extend(["\U0001f60a"] * (len(sticker_files) - len(emojis)))
        emojis = emojis[: len(sticker_files)]
    except ImportError:
        # Default: use smiley for all
        emojis = ["\U0001f60a"] * len(sticker_files)

    publisher = TelegramStickerPublisher()
    publisher.create_sticker_set(
        user_id=int(user_id),
        name=pack_name,
        title=pack_title,
        sticker_paths=[str(f) for f in sticker_files],
        emojis_list=emojis,
    )
