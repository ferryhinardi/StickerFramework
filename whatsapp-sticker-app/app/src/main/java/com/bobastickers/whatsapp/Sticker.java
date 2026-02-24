package com.bobastickers.whatsapp;

import java.util.List;

/**
 * Data model representing a single sticker within a pack.
 *
 * Each sticker is a 512x512 WebP image (<=100KB) with associated emoji tags.
 */
public class Sticker {

    /** Filename of the sticker image (e.g., "01_happy.webp"). */
    public String imageFileName;

    /** List of emoji tags associated with this sticker. */
    public List<String> emojis;

    public Sticker() {
    }

    public Sticker(String imageFileName, List<String> emojis) {
        this.imageFileName = imageFileName;
        this.emojis = emojis;
    }

    /**
     * Returns emoji list as a comma-separated string for WhatsApp cursor.
     */
    public String getEmojisString() {
        if (emojis == null || emojis.isEmpty()) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < emojis.size(); i++) {
            if (i > 0) sb.append(",");
            sb.append(emojis.get(i));
        }
        return sb.toString();
    }
}
