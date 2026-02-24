package com.yourbrand.stickers;

import java.util.List;

/**
 * Data model representing a WhatsApp sticker pack.
 *
 * Maps to the contents.json format and provides data for the
 * ContentProvider cursor responses that WhatsApp expects.
 */
public class StickerPack {

    /** Unique identifier for this pack (e.g., "cappy_emotions_01"). */
    public String identifier;

    /** Display name shown in WhatsApp (e.g., "Cappy Emotions Vol. 1"). */
    public String name;

    /** Publisher name (e.g., "Your Brand"). */
    public String publisher;

    /** Filename of the tray icon (96x96 PNG). */
    public String trayImageFile;

    /** URL or empty string for the app's Play Store listing. */
    public String androidPlayStoreLink;

    /** URL or empty string for the iOS App Store listing. */
    public String iosAppStoreLink;

    /** Publisher website URL. */
    public String publisherWebsite;

    /** Privacy policy URL. */
    public String privacyPolicyWebsite;

    /** License agreement URL. */
    public String licenseAgreementWebsite;

    /** Version string for cache invalidation (e.g., "1"). */
    public String imageDataVersion;

    /** Whether WhatsApp should avoid caching (0 = cache, 1 = no cache). */
    public boolean avoidCache;

    /** Whether this pack has been added to WhatsApp. */
    public boolean isWhatsAppAdded;

    /** List of stickers in this pack. */
    public List<Sticker> stickers;

    public StickerPack() {
    }

    public StickerPack(
            String identifier,
            String name,
            String publisher,
            String trayImageFile,
            String publisherWebsite,
            String privacyPolicyWebsite,
            String licenseAgreementWebsite,
            String imageDataVersion,
            boolean avoidCache
    ) {
        this.identifier = identifier;
        this.name = name;
        this.publisher = publisher;
        this.trayImageFile = trayImageFile;
        this.androidPlayStoreLink = "";
        this.iosAppStoreLink = "";
        this.publisherWebsite = publisherWebsite;
        this.privacyPolicyWebsite = privacyPolicyWebsite;
        this.licenseAgreementWebsite = licenseAgreementWebsite;
        this.imageDataVersion = imageDataVersion;
        this.avoidCache = avoidCache;
    }

    /**
     * Returns the total number of stickers in this pack.
     */
    public int getTotalSize() {
        return stickers != null ? stickers.size() : 0;
    }
}
