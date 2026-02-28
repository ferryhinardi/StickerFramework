"""
Sticker.ly pack metadata automation.

Fills pack name, author/creator, and tags in the Sticker.ly app
using uiautomator2.
"""

from __future__ import annotations

import uiautomator2 as u2

from automation.stickerly.config import (
    DEFAULTS,
    ELEMENT_WAIT_TIMEOUT,
    SEL_AUTHOR_INPUT,
    SEL_PACK_NAME_INPUT,
    SEL_TAG_INPUT,
    TAG_TEMPLATES,
)
from automation.stickerly.utils import (
    ElementNotFound,
    find_element,
    human_delay,
    safe_click,
    safe_set_text,
    screenshot_on_failure,
)


class StickerlySetMetadata:
    """Fill pack metadata (name, author, tags) in the Sticker.ly app."""

    def set_metadata(
        self,
        device: u2.Device,
        pack_name: str,
        publisher: str | None = None,
        tags: list[str] | None = None,
        character_type: str | None = None,
    ) -> None:
        """
        Fill in pack metadata fields.

        Args:
            device: uiautomator2 Device instance.
            pack_name: Display name for the sticker pack.
            publisher: Creator/author name (defaults to config).
            tags: Custom tags. If None, auto-generates from character_type.
            character_type: Character category key for tag templates
                           (e.g., "cat", "panda", "capybara").
        """
        publisher = publisher or DEFAULTS["publisher"]

        with screenshot_on_failure(device, "set_metadata"):
            # Set pack name
            print(f"  Setting pack name: {pack_name}")
            self._fill_field(device, SEL_PACK_NAME_INPUT, pack_name)
            human_delay(500, 1000)

            # Set author
            print(f"  Setting author: {publisher}")
            self._fill_field(device, SEL_AUTHOR_INPUT, publisher)
            human_delay(500, 1000)

            # Set tags
            final_tags = self._build_tags(tags, character_type)
            print(f"  Adding {len(final_tags)} tags...")
            self._add_tags(device, final_tags)

        print("  Metadata set successfully.")

    def _fill_field(
        self,
        device: u2.Device,
        selector_group: dict,
        value: str,
    ) -> None:
        """Fill a text input field, handling potential issues."""
        try:
            safe_set_text(device, selector_group, value)
        except ElementNotFound:
            # Fallback: try finding any EditText and filling by index
            desc = selector_group.get("description", "unknown")
            print(f"    WARNING: Could not find '{desc}', trying EditText fallback...")
            edit_texts = device(className="android.widget.EditText")
            if edit_texts.count > 0:
                # Use the first empty one or the first overall
                for i in range(edit_texts.count):
                    et = edit_texts[i]
                    current = et.get_text() or ""
                    if not current.strip():
                        et.set_text(value)
                        return
                # If all have text, use the first one
                edit_texts[0].clear_text()
                edit_texts[0].set_text(value)
            else:
                raise

    def _add_tags(self, device: u2.Device, tags: list[str]) -> None:
        """
        Add tags one by one to the tag input field.

        The Sticker.ly tag flow typically works by:
        1. Tap the tag input
        2. Type a tag
        3. Press Enter or tap "Add"
        4. Repeat
        """
        for tag in tags:
            try:
                # Find and tap tag input
                el = find_element(device, SEL_TAG_INPUT, timeout=3)
                el.click()
                human_delay(200, 500)

                # Type the tag
                el.set_text(tag)
                human_delay(200, 500)

                # Press Enter to confirm the tag
                device.press("enter")
                human_delay(300, 700)

            except ElementNotFound:
                # Tag input may have a different UI pattern
                # Try typing directly and pressing enter
                try:
                    device.send_keys(tag)
                    human_delay(200, 500)
                    device.press("enter")
                    human_delay(300, 700)
                except Exception as exc:
                    print(f"    WARNING: Could not add tag '{tag}': {exc}")
                    break  # Stop adding tags if we can't find the input
            except Exception as exc:
                print(f"    WARNING: Could not add tag '{tag}': {exc}")
                continue

    def _build_tags(
        self,
        custom_tags: list[str] | None,
        character_type: str | None,
    ) -> list[str]:
        """
        Build a merged, deduplicated tag list.

        Order: custom tags > character-specific > base defaults.
        Limit to ~20 tags (Sticker.ly may have a cap).
        """
        tags: list[str] = []

        # Custom tags first
        if custom_tags:
            tags.extend(custom_tags)

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

        # Limit to 20 tags
        return unique_tags[:20]
