package com.bobastickers.whatsapp;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.content.UriMatcher;
import android.content.res.AssetFileDescriptor;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.text.TextUtils;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * ContentProvider that exposes sticker pack data to WhatsApp.
 *
 * WhatsApp queries this provider using specific URI patterns to discover
 * available sticker packs, list stickers within packs, and retrieve
 * sticker image bytes.
 *
 * URI patterns:
 *   content://<authority>/metadata                         → All packs
 *   content://<authority>/metadata/<pack_id>               → Single pack
 *   content://<authority>/stickers/<pack_id>               → Stickers in a pack
 *   content://<authority>/stickers_asset/<pack_id>/<name>  → Sticker image
 */
public class StickerContentProvider extends ContentProvider {

    private static final String TAG = "StickerContentProvider";

    static final String AUTHORITY = BuildConfig.CONTENT_PROVIDER_AUTHORITY;

    // URI matcher codes
    private static final int METADATA_CODE = 1;
    private static final int METADATA_SINGLE_CODE = 2;
    private static final int STICKERS_CODE = 3;
    private static final int STICKERS_ASSET_CODE = 4;

    private static final UriMatcher URI_MATCHER = new UriMatcher(UriMatcher.NO_MATCH);

    static {
        URI_MATCHER.addURI(AUTHORITY, "metadata", METADATA_CODE);
        URI_MATCHER.addURI(AUTHORITY, "metadata/*", METADATA_SINGLE_CODE);
        URI_MATCHER.addURI(AUTHORITY, "stickers/*", STICKERS_CODE);
        URI_MATCHER.addURI(AUTHORITY, "stickers_asset/*/*", STICKERS_ASSET_CODE);
    }

    // Column names expected by WhatsApp for pack metadata
    private static final String STICKER_PACK_IDENTIFIER = "sticker_pack_identifier";
    private static final String STICKER_PACK_NAME = "sticker_pack_name";
    private static final String STICKER_PACK_PUBLISHER = "sticker_pack_publisher";
    private static final String STICKER_PACK_ICON = "sticker_pack_icon";
    private static final String ANDROID_PLAY_STORE_LINK = "android_play_store_link";
    private static final String IOS_APP_STORE_LINK = "ios_app_store_link";
    private static final String PUBLISHER_WEBSITE = "publisher_website";
    private static final String PRIVACY_POLICY_WEBSITE = "privacy_policy_website";
    private static final String LICENSE_AGREEMENT_WEBSITE = "license_agreement_website";
    private static final String IMAGE_DATA_VERSION = "image_data_version";
    private static final String AVOID_CACHE = "avoid_cache";

    // Column names for sticker list
    private static final String STICKER_FILE_NAME = "sticker_file_name";
    private static final String STICKER_EMOJI = "sticker_emoji";

    private static final String[] METADATA_COLUMNS = {
            STICKER_PACK_IDENTIFIER,
            STICKER_PACK_NAME,
            STICKER_PACK_PUBLISHER,
            STICKER_PACK_ICON,
            ANDROID_PLAY_STORE_LINK,
            IOS_APP_STORE_LINK,
            PUBLISHER_WEBSITE,
            PRIVACY_POLICY_WEBSITE,
            LICENSE_AGREEMENT_WEBSITE,
            IMAGE_DATA_VERSION,
            AVOID_CACHE,
    };

    private static final String[] STICKER_COLUMNS = {
            STICKER_FILE_NAME,
            STICKER_EMOJI,
    };

    private static volatile List<StickerPack> stickerPacks = Collections.emptyList();

    @Override
    public boolean onCreate() {
        try {
            List<StickerPack> assetPacks = StickerPackLoader.loadFromAssets(getContext());
            List<StickerPack> cachedPacks = StickerPackLoader.loadFromCache(getContext());
            stickerPacks = StickerPackLoader.mergePacks(assetPacks, cachedPacks);
        } catch (Exception e) {
            Log.e(TAG, "Failed to load sticker packs", e);
            stickerPacks = new ArrayList<>();
        }
        return true;
    }

    /**
     * Refresh the sticker packs list from assets + cache.
     * Call this after downloading and caching new packs from the server
     * so that WhatsApp can see newly added packs via the ContentProvider.
     *
     * @param context Application context.
     */
    public static void refreshPacks(Context context) {
        try {
            List<StickerPack> assetPacks = StickerPackLoader.loadFromAssets(context);
            List<StickerPack> cachedPacks = StickerPackLoader.loadFromCache(context);
            stickerPacks = StickerPackLoader.mergePacks(assetPacks, cachedPacks);
        } catch (Exception e) {
            Log.e(TAG, "Failed to refresh sticker packs", e);
        }
    }

    @Nullable
    @Override
    public Cursor query(
            @NonNull Uri uri,
            @Nullable String[] projection,
            @Nullable String selection,
            @Nullable String[] selectionArgs,
            @Nullable String sortOrder
    ) {
        int match = URI_MATCHER.match(uri);
        switch (match) {
            case METADATA_CODE:
                return getPackListCursor();

            case METADATA_SINGLE_CODE:
                return getSinglePackCursor(uri);

            case STICKERS_CODE:
                return getStickersCursor(uri);

            case STICKERS_ASSET_CODE:
                // Asset retrieval is handled via openFile/openAssetFile
                return null;

            default:
                throw new IllegalArgumentException("Unknown URI: " + uri);
        }
    }

    /**
     * Returns a cursor with metadata for all sticker packs.
     */
    private Cursor getPackListCursor() {
        MatrixCursor cursor = new MatrixCursor(METADATA_COLUMNS);
        for (StickerPack pack : stickerPacks) {
            cursor.addRow(buildPackRow(pack));
        }
        return cursor;
    }

    /**
     * Returns a cursor with metadata for a single sticker pack.
     */
    private Cursor getSinglePackCursor(Uri uri) {
        String packId = uri.getLastPathSegment();
        for (StickerPack pack : stickerPacks) {
            if (pack.identifier.equals(packId)) {
                MatrixCursor cursor = new MatrixCursor(METADATA_COLUMNS);
                cursor.addRow(buildPackRow(pack));
                return cursor;
            }
        }
        return new MatrixCursor(METADATA_COLUMNS);
    }

    /**
     * Builds a cursor row for a sticker pack (metadata columns).
     */
    private Object[] buildPackRow(StickerPack pack) {
        return new Object[]{
                pack.identifier,
                pack.name,
                pack.publisher,
                pack.trayImageFile,
                pack.androidPlayStoreLink != null ? pack.androidPlayStoreLink : "",
                pack.iosAppStoreLink != null ? pack.iosAppStoreLink : "",
                pack.publisherWebsite != null ? pack.publisherWebsite : "",
                pack.privacyPolicyWebsite != null ? pack.privacyPolicyWebsite : "",
                pack.licenseAgreementWebsite != null ? pack.licenseAgreementWebsite : "",
                pack.imageDataVersion != null ? pack.imageDataVersion : "1",
                pack.avoidCache ? 1 : 0,
        };
    }

    /**
     * Returns a cursor listing all stickers in a given pack.
     */
    private Cursor getStickersCursor(Uri uri) {
        String packId = uri.getLastPathSegment();
        MatrixCursor cursor = new MatrixCursor(STICKER_COLUMNS);

        for (StickerPack pack : stickerPacks) {
            if (pack.identifier.equals(packId) && pack.stickers != null) {
                for (Sticker sticker : pack.stickers) {
                    cursor.addRow(new Object[]{
                            sticker.imageFileName,
                            sticker.getEmojisString(),
                    });
                }
                break;
            }
        }
        return cursor;
    }

    /**
     * Opens a sticker image file for reading.
     *
     * WhatsApp calls this to retrieve the actual image bytes for a sticker.
     * The URI pattern is: stickers_asset/<pack_id>/<sticker_filename>
     *
     * Looks for the file in:
     *   1. App assets:  assets/<pack_id>/<filename>
     *   2. App cache:   cache/stickers/<pack_id>/<filename>  (server-downloaded)
     */
    @Nullable
    @Override
    public AssetFileDescriptor openAssetFile(@NonNull Uri uri, @NonNull String mode)
            throws FileNotFoundException {
        int match = URI_MATCHER.match(uri);
        if (match != STICKERS_ASSET_CODE) {
            throw new FileNotFoundException("Unknown URI: " + uri);
        }

        List<String> pathSegments = uri.getPathSegments();
        if (pathSegments.size() < 3) {
            throw new FileNotFoundException("Invalid sticker asset URI: " + uri);
        }

        String packId = pathSegments.get(1);
        String stickerFileName = pathSegments.get(2);

        // Validate: no path traversal
        if (packId.contains("..") || stickerFileName.contains("..")) {
            throw new FileNotFoundException("Invalid path: " + uri);
        }

        if (getContext() == null) {
            throw new FileNotFoundException("Context unavailable");
        }

        // Try 1: Load from bundled assets
        String assetPath = packId + "/" + stickerFileName;
        try {
            return getContext().getAssets().openFd(assetPath);
        } catch (IOException e) {
            // Not in assets — try cache
        }

        // Try 2: Load from cache (downloaded from server)
        File cacheDir = new File(getContext().getCacheDir(), "stickers");
        File stickerFile = new File(new File(cacheDir, packId), stickerFileName);
        if (stickerFile.exists()) {
            return new AssetFileDescriptor(
                    ParcelFileDescriptor.open(stickerFile, ParcelFileDescriptor.MODE_READ_ONLY),
                    0,
                    AssetFileDescriptor.UNKNOWN_LENGTH
            );
        }

        throw new FileNotFoundException("Sticker not found: " + assetPath);
    }

    // ---------------------------------------------------------------
    // Required ContentProvider overrides (unused for our read-only use)
    // ---------------------------------------------------------------

    @Nullable
    @Override
    public String getType(@NonNull Uri uri) {
        int match = URI_MATCHER.match(uri);
        switch (match) {
            case METADATA_CODE:
            case METADATA_SINGLE_CODE:
                return "vnd.android.cursor.dir/vnd." + AUTHORITY + ".metadata";
            case STICKERS_CODE:
                return "vnd.android.cursor.dir/vnd." + AUTHORITY + ".stickers";
            case STICKERS_ASSET_CODE:
                return "image/webp";
            default:
                throw new IllegalArgumentException("Unknown URI: " + uri);
        }
    }

    @Nullable
    @Override
    public Uri insert(@NonNull Uri uri, @Nullable ContentValues values) {
        throw new UnsupportedOperationException("Read-only provider");
    }

    @Override
    public int delete(@NonNull Uri uri, @Nullable String selection, @Nullable String[] selectionArgs) {
        throw new UnsupportedOperationException("Read-only provider");
    }

    @Override
    public int update(@NonNull Uri uri, @Nullable ContentValues values,
                      @Nullable String selection, @Nullable String[] selectionArgs) {
        throw new UnsupportedOperationException("Read-only provider");
    }
}
