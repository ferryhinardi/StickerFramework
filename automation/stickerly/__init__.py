"""
Sticker.ly Android emulator automation via uiautomator2.

Modules:
    config                 — Package name, selectors, timeouts, tag templates
    utils                  — ADB helpers, screenshot, progress, human delay
    emulator               — Emulator lifecycle (start/stop/snapshot/push files)
    stickerly_auth         — Login validation and session via AVD snapshots
    stickerly_create_pack  — Create pack and upload stickers
    stickerly_set_metadata — Fill pack name, author, tags
    stickerly_publish      — Final publish and share link capture
"""

from automation.stickerly.emulator import EmulatorManager
from automation.stickerly.stickerly_auth import StickerlyAuth
from automation.stickerly.stickerly_create_pack import StickerlyCreatePack
from automation.stickerly.stickerly_publish import StickerlyPublish
from automation.stickerly.stickerly_set_metadata import StickerlySetMetadata

__all__ = [
    "EmulatorManager",
    "StickerlyAuth",
    "StickerlyCreatePack",
    "StickerlySetMetadata",
    "StickerlyPublish",
]
