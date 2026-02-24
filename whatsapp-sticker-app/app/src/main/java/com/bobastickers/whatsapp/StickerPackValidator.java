package com.bobastickers.whatsapp;

import android.content.Context;
import android.util.Log;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

/**
 * Validates sticker packs against WhatsApp's strict requirements.
 *
 * WhatsApp silently rejects non-conforming packs, so runtime validation
 * before triggering the "Add to WhatsApp" intent prevents a poor UX.
 *
 * WhatsApp requirements (hard constraints):
 *   - 3–30 stickers per pack
 *   - Sticker images: WebP, exactly 512x512, ≤100KB
 *   - Tray icon: WebP or PNG, exactly 96x96, ≤50KB
 *   - Each sticker must have at least 1 emoji association
 *   - Pack must have non-empty identifier, name, and publisher
 */
public class StickerPackValidator {

    private static final String TAG = "StickerPackValidator";

    public static final int MIN_STICKERS_PER_PACK = 3;
    public static final int MAX_STICKERS_PER_PACK = 30;
    public static final int STICKER_WIDTH = 512;
    public static final int STICKER_HEIGHT = 512;
    public static final long STICKER_MAX_BYTES = 100 * 1024;      // 100 KB
    public static final long TRAY_ICON_MAX_BYTES = 50 * 1024;      // 50 KB
    public static final int TRAY_ICON_WIDTH = 96;
    public static final int TRAY_ICON_HEIGHT = 96;

    /**
     * Validate a sticker pack's metadata (no file I/O).
     *
     * Checks that all required fields are present and sticker count
     * falls within WhatsApp's 3–30 range.
     *
     * @param pack The sticker pack to validate.
     * @return List of error messages. Empty list means valid.
     */
    public static List<String> validateMetadata(StickerPack pack) {
        List<String> errors = new ArrayList<>();

        if (pack.identifier == null || pack.identifier.trim().isEmpty()) {
            errors.add("Pack identifier is missing or empty");
        }

        if (pack.name == null || pack.name.trim().isEmpty()) {
            errors.add("Pack name is missing or empty");
        }

        if (pack.publisher == null || pack.publisher.trim().isEmpty()) {
            errors.add("Pack publisher is missing or empty");
        }

        if (pack.trayImageFile == null || pack.trayImageFile.trim().isEmpty()) {
            errors.add("Tray image file is missing or empty");
        }

        if (pack.stickers == null || pack.stickers.isEmpty()) {
            errors.add("Pack has no stickers");
        } else {
            if (pack.stickers.size() < MIN_STICKERS_PER_PACK) {
                errors.add("Pack has " + pack.stickers.size() + " stickers, "
                        + "minimum is " + MIN_STICKERS_PER_PACK);
            }
            if (pack.stickers.size() > MAX_STICKERS_PER_PACK) {
                errors.add("Pack has " + pack.stickers.size() + " stickers, "
                        + "maximum is " + MAX_STICKERS_PER_PACK);
            }

            for (int i = 0; i < pack.stickers.size(); i++) {
                Sticker sticker = pack.stickers.get(i);
                if (sticker.imageFileName == null || sticker.imageFileName.trim().isEmpty()) {
                    errors.add("Sticker #" + (i + 1) + " has no image filename");
                }
                if (sticker.emojis == null || sticker.emojis.isEmpty()) {
                    errors.add("Sticker #" + (i + 1) + " (" + sticker.imageFileName
                            + ") has no emoji associations");
                }
            }
        }

        return errors;
    }

    /**
     * Validate that all sticker files exist in assets and meet size constraints.
     *
     * This performs file I/O to check that every sticker referenced in the pack
     * is actually present in the app's assets and is within WhatsApp's size limits.
     *
     * @param context Application context for asset access.
     * @param pack    The sticker pack to validate.
     * @return List of error messages. Empty list means all files valid.
     */
    public static List<String> validateFiles(Context context, StickerPack pack) {
        List<String> errors = new ArrayList<>();

        if (pack.stickers == null) {
            return errors;
        }

        // Validate tray icon
        if (pack.trayImageFile != null && !pack.trayImageFile.isEmpty()) {
            String trayPath = pack.identifier + "/" + pack.trayImageFile;
            long traySize = getAssetFileSize(context, trayPath);
            if (traySize < 0) {
                // Try cache
                traySize = getCacheFileSize(context, pack.identifier, pack.trayImageFile);
            }
            if (traySize < 0) {
                errors.add("Tray icon file not found: " + trayPath);
            } else if (traySize > TRAY_ICON_MAX_BYTES) {
                errors.add("Tray icon too large: " + (traySize / 1024) + "KB "
                        + "(max " + (TRAY_ICON_MAX_BYTES / 1024) + "KB)");
            }
        }

        // Validate each sticker file
        for (int i = 0; i < pack.stickers.size(); i++) {
            Sticker sticker = pack.stickers.get(i);
            if (sticker.imageFileName == null || sticker.imageFileName.isEmpty()) {
                continue;  // Already caught by validateMetadata
            }

            String assetPath = pack.identifier + "/" + sticker.imageFileName;
            long fileSize = getAssetFileSize(context, assetPath);
            if (fileSize < 0) {
                // Try cache
                fileSize = getCacheFileSize(context, pack.identifier, sticker.imageFileName);
            }

            if (fileSize < 0) {
                errors.add("Sticker #" + (i + 1) + " file not found: " + assetPath);
            } else if (fileSize > STICKER_MAX_BYTES) {
                errors.add("Sticker #" + (i + 1) + " (" + sticker.imageFileName + ") "
                        + "too large: " + (fileSize / 1024) + "KB "
                        + "(max " + (STICKER_MAX_BYTES / 1024) + "KB)");
            }
        }

        return errors;
    }

    /**
     * Run full validation (metadata + files).
     *
     * @param context Application context.
     * @param pack    The sticker pack to validate.
     * @return List of all validation errors. Empty list means the pack is valid
     *         and safe to add to WhatsApp.
     */
    public static List<String> validateFull(Context context, StickerPack pack) {
        List<String> errors = new ArrayList<>();
        errors.addAll(validateMetadata(pack));
        errors.addAll(validateFiles(context, pack));
        return errors;
    }

    /**
     * Quick check: is this pack valid enough to show the "Add to WhatsApp" button?
     *
     * @param pack The sticker pack to check.
     * @return true if the pack passes basic metadata validation.
     */
    public static boolean isPackAddable(StickerPack pack) {
        return validateMetadata(pack).isEmpty();
    }

    // -------------------------------------------------------------------
    // File size helpers
    // -------------------------------------------------------------------

    /**
     * Get the size of a file in the assets directory.
     *
     * @return File size in bytes, or -1 if the file doesn't exist.
     */
    private static long getAssetFileSize(Context context, String assetPath) {
        try {
            InputStream is = context.getAssets().open(assetPath);
            // Read through the stream to count bytes (assets may be compressed)
            byte[] buffer = new byte[8192];
            long total = 0;
            int read;
            while ((read = is.read(buffer)) != -1) {
                total += read;
            }
            is.close();
            return total;
        } catch (IOException e) {
            return -1;
        }
    }

    /**
     * Get the size of a file in the cache directory.
     *
     * @return File size in bytes, or -1 if the file doesn't exist.
     */
    private static long getCacheFileSize(Context context, String packId, String fileName) {
        java.io.File cacheDir = new java.io.File(context.getCacheDir(), "stickers");
        java.io.File file = new java.io.File(new java.io.File(cacheDir, packId), fileName);
        if (file.exists()) {
            return file.length();
        }
        return -1;
    }
}
