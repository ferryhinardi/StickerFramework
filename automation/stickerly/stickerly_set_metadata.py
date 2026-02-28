"""
Sticker.ly pack metadata automation.

In the actual Sticker.ly flow, metadata is limited:
- Pack name: set at creation time (editable via overflow menu -> Edit pack)
- Tags: set during the "Save to..." step when adding stickers
- No separate "author" field exists in the app UI

This module handles tag generation and metadata helpers.
"""

from __future__ import annotations

from automation.stickerly.config import (
    DEFAULTS,
    TAG_TEMPLATES,
)


class StickerlySetMetadata:
    """Build and manage pack metadata (tags, names) for Sticker.ly."""

    @staticmethod
    def build_tags(
        custom_tags: list[str] | None = None,
        character_type: str | None = None,
        pack_name: str | None = None,
    ) -> str:
        """
        Build a comma-separated tag string for the "Save to..." screen.

        Args:
            custom_tags: Explicit tags to include first.
            character_type: Character category for template tags
                           (e.g., "cat", "panda", "capybara").
            pack_name: Pack name to extract additional keywords from.

        Returns:
            Comma-separated tag string, e.g., "capybara, cute, kawaii, stickers"
        """
        tags: list[str] = []

        # Custom tags first
        if custom_tags:
            tags.extend(custom_tags)

        # Pack name words as tags (skip short words)
        if pack_name:
            for word in pack_name.lower().replace("-", " ").split():
                if len(word) > 2 and word not in ("the", "and", "for"):
                    tags.append(word)

        # Character-specific tags
        if character_type:
            char_tags = TAG_TEMPLATES.get(
                character_type.lower(), TAG_TEMPLATES["default"]
            )
            tags.extend(char_tags)

        # Base defaults
        tags.extend(DEFAULTS["tags_base"])

        # Deduplicate while preserving order
        seen = set()
        unique_tags = []
        for tag in tags:
            tag_lower = tag.lower().strip()
            if tag_lower and tag_lower not in seen:
                seen.add(tag_lower)
                unique_tags.append(tag.strip())

        # Limit to 20 tags, join with comma-space
        return ", ".join(unique_tags[:20])

    @staticmethod
    def detect_character_type(pack_id: str) -> str:
        """
        Detect the character type from a pack ID.

        Args:
            pack_id: Pack directory name, e.g., "cappy-capybara-3"

        Returns:
            Character type key matching TAG_TEMPLATES, or "default".
        """
        pack_lower = pack_id.lower()
        for key in TAG_TEMPLATES:
            if key != "default" and key in pack_lower:
                return key
        # Special cases
        if "cappy" in pack_lower or "capy" in pack_lower:
            return "capybara"
        if "mochi" in pack_lower:
            # chubby-mochi-cat, chubby-mochi-hamster, chubby-mochi-panda
            for animal in ("cat", "hamster", "panda"):
                if animal in pack_lower:
                    return animal
        if "boba" in pack_lower or "milo" in pack_lower:
            return "otter"
        return "default"
