package com.bobastickers.whatsapp;

import android.content.Context;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Loads sticker packs from bundled assets and/or a remote API server.
 *
 * Loading order:
 *   1. Bundled assets (assets/contents.json) — always available offline
 *   2. Server API (optional) — fetches new/updated packs at runtime
 *   3. Cache directory — previously downloaded server packs
 *
 * The contents.json format matches the WhatsApp sticker pack schema:
 * {
 *   "sticker_packs": [
 *     {
 *       "identifier": "pack_01",
 *       "name": "Pack Name",
 *       "publisher": "Publisher",
 *       "tray_image_file": "tray_icon.webp",
 *       "publisher_website": "",
 *       "privacy_policy_website": "",
 *       "license_agreement_website": "",
 *       "image_data_version": "1",
 *       "avoid_cache": false,
 *       "stickers": [
 *         { "image_file": "01_happy.webp", "emojis": ["😀"] },
 *         ...
 *       ]
 *     }
 *   ]
 * }
 */
public class StickerPackLoader {

    private static final String TAG = "StickerPackLoader";
    private static final String ASSET_CONTENTS_FILE = "contents.json";

    /**
     * Load sticker packs from the app's bundled assets.
     *
     * @param context Application context for accessing assets.
     * @return List of sticker packs parsed from assets/contents.json.
     * @throws IOException If the assets file cannot be read.
     */
    public static List<StickerPack> loadFromAssets(Context context) throws IOException {
        try (InputStream is = context.getAssets().open(ASSET_CONTENTS_FILE);
             BufferedReader reader = new BufferedReader(
                     new InputStreamReader(is, StandardCharsets.UTF_8))) {

            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }

            return parseContentsJson(sb.toString());
        }
    }

    /**
     * Load sticker packs from the cache directory (previously downloaded from server).
     *
     * @param context Application context for accessing cache directory.
     * @return List of sticker packs found in cache, or empty list if none.
     */
    public static List<StickerPack> loadFromCache(Context context) {
        File cacheDir = new File(context.getCacheDir(), "stickers");
        File cacheContents = new File(cacheDir, ASSET_CONTENTS_FILE);

        if (!cacheContents.exists()) {
            return new ArrayList<>();
        }

        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(cacheContents))) {
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line);
                }
                return parseContentsJson(sb.toString());
            }
        } catch (IOException e) {
            Log.e(TAG, "Failed to load cached sticker packs", e);
            return new ArrayList<>();
        }
    }

    /**
     * Save sticker packs to the cache directory as contents.json.
     *
     * This writes the pack list in the standard WhatsApp sticker_packs JSON
     * schema so that {@link #loadFromCache(Context)} can read it back.
     *
     * @param context Application context for accessing cache directory.
     * @param packs   The list of sticker packs to persist.
     */
    public static void saveToCache(Context context, List<StickerPack> packs) {
        File cacheDir = new File(context.getCacheDir(), "stickers");
        if (!cacheDir.exists() && !cacheDir.mkdirs()) {
            Log.e(TAG, "Failed to create stickers cache directory");
            return;
        }

        JsonObject root = new JsonObject();
        JsonArray packsArray = new JsonArray();

        for (StickerPack pack : packs) {
            JsonObject packObj = new JsonObject();
            packObj.addProperty("identifier", pack.identifier);
            packObj.addProperty("name", pack.name);
            packObj.addProperty("publisher", pack.publisher);
            packObj.addProperty("tray_image_file", pack.trayImageFile);
            packObj.addProperty("android_play_store_link",
                    pack.androidPlayStoreLink != null ? pack.androidPlayStoreLink : "");
            packObj.addProperty("ios_app_store_link",
                    pack.iosAppStoreLink != null ? pack.iosAppStoreLink : "");
            packObj.addProperty("publisher_website",
                    pack.publisherWebsite != null ? pack.publisherWebsite : "");
            packObj.addProperty("privacy_policy_website",
                    pack.privacyPolicyWebsite != null ? pack.privacyPolicyWebsite : "");
            packObj.addProperty("license_agreement_website",
                    pack.licenseAgreementWebsite != null ? pack.licenseAgreementWebsite : "");
            packObj.addProperty("image_data_version",
                    pack.imageDataVersion != null ? pack.imageDataVersion : "1");
            packObj.addProperty("avoid_cache", pack.avoidCache);

            JsonArray stickersArray = new JsonArray();
            if (pack.stickers != null) {
                for (Sticker sticker : pack.stickers) {
                    JsonObject stickerObj = new JsonObject();
                    stickerObj.addProperty("image_file", sticker.imageFileName);
                    JsonArray emojisArray = new JsonArray();
                    if (sticker.emojis != null) {
                        for (String emoji : sticker.emojis) {
                            emojisArray.add(emoji);
                        }
                    }
                    stickerObj.add("emojis", emojisArray);
                    stickersArray.add(stickerObj);
                }
            }
            packObj.add("stickers", stickersArray);
            packsArray.add(packObj);
        }

        root.add("sticker_packs", packsArray);

        File cacheContents = new File(cacheDir, ASSET_CONTENTS_FILE);
        try (FileWriter writer = new FileWriter(cacheContents)) {
            writer.write(root.toString());
        } catch (IOException e) {
            Log.e(TAG, "Failed to save sticker packs to cache", e);
        }
    }

    /**
     * Fetch sticker packs from the remote API server.
     *
     * Makes a GET request to the server's /api/v1/packs endpoint and parses
     * the response into StickerPack objects. Sticker images are NOT downloaded
     * here — they are fetched lazily by the ContentProvider when WhatsApp
     * requests them.
     *
     * @param serverBaseUrl Base URL of the sticker API server (e.g., "http://10.0.2.2:8080").
     * @return List of sticker packs from the server, or empty list on failure.
     */
    public static List<StickerPack> fetchFromServer(String serverBaseUrl) {
        OkHttpClient client = new OkHttpClient();
        String url = serverBaseUrl + "/api/v1/packs";

        Request request = new Request.Builder()
                .url(url)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful() || response.body() == null) {
                Log.e(TAG, "Server returned " + response.code() + " for " + url);
                return new ArrayList<>();
            }

            String body = response.body().string();
            return parseServerResponse(body);
        } catch (IOException e) {
            Log.e(TAG, "Failed to fetch packs from server: " + url, e);
            return new ArrayList<>();
        }
    }

    /**
     * Download a sticker image from the server and save it to the cache directory.
     *
     * @param context       Application context for cache directory access.
     * @param serverBaseUrl Base URL of the sticker API server.
     * @param packId        The sticker pack identifier.
     * @param fileName      The sticker image filename.
     * @return true if the download succeeded, false otherwise.
     */
    public static boolean downloadStickerToCache(
            Context context, String serverBaseUrl, String packId, String fileName) {

        OkHttpClient client = new OkHttpClient();
        String url = serverBaseUrl + "/api/v1/stickers/" + packId + "/" + fileName;

        Request request = new Request.Builder()
                .url(url)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful() || response.body() == null) {
                Log.e(TAG, "Failed to download sticker: " + url + " (" + response.code() + ")");
                return false;
            }

            File cacheDir = new File(context.getCacheDir(), "stickers");
            File packDir = new File(cacheDir, packId);
            if (!packDir.exists() && !packDir.mkdirs()) {
                Log.e(TAG, "Failed to create cache directory: " + packDir);
                return false;
            }

            File outputFile = new File(packDir, fileName);
            try (java.io.FileOutputStream fos = new java.io.FileOutputStream(outputFile)) {
                fos.write(response.body().bytes());
            }

            return true;
        } catch (IOException e) {
            Log.e(TAG, "Failed to download sticker: " + url, e);
            return false;
        }
    }

    /**
     * Merge two lists of sticker packs, preferring server versions when
     * identifiers collide (server packs may have updated stickers).
     *
     * @param assetPacks  Packs loaded from bundled assets.
     * @param serverPacks Packs fetched from the server.
     * @return Merged list with no duplicate identifiers.
     */
    public static List<StickerPack> mergePacks(
            List<StickerPack> assetPacks, List<StickerPack> serverPacks) {

        // Use a linked hash map to preserve order and deduplicate
        java.util.LinkedHashMap<String, StickerPack> map = new java.util.LinkedHashMap<>();

        // Asset packs first (baseline)
        for (StickerPack pack : assetPacks) {
            map.put(pack.identifier, pack);
        }

        // Server packs override asset packs with same identifier
        for (StickerPack pack : serverPacks) {
            map.put(pack.identifier, pack);
        }

        return new ArrayList<>(map.values());
    }

    // -------------------------------------------------------------------
    // JSON parsing helpers
    // -------------------------------------------------------------------

    /**
     * Parse a contents.json string (WhatsApp sticker pack schema).
     */
    private static List<StickerPack> parseContentsJson(String json) {
        List<StickerPack> packs = new ArrayList<>();

        JsonObject root = JsonParser.parseString(json).getAsJsonObject();
        JsonArray packsArray = root.getAsJsonArray("sticker_packs");

        if (packsArray == null) {
            Log.w(TAG, "No 'sticker_packs' array found in contents.json");
            return packs;
        }

        for (JsonElement element : packsArray) {
            JsonObject obj = element.getAsJsonObject();
            StickerPack pack = parseSinglePack(obj);
            if (pack != null) {
                packs.add(pack);
            }
        }

        return packs;
    }

    /**
     * Parse the server's /api/v1/packs response.
     * Expected format: { "packs": [ { ... }, ... ] }
     * Falls back to parsing as a contents.json if "packs" key is absent.
     */
    private static List<StickerPack> parseServerResponse(String json) {
        List<StickerPack> packs = new ArrayList<>();

        JsonObject root = JsonParser.parseString(json).getAsJsonObject();

        // Try server format first
        JsonArray packsArray = root.getAsJsonArray("packs");
        if (packsArray == null) {
            // Fall back to contents.json format
            packsArray = root.getAsJsonArray("sticker_packs");
        }

        if (packsArray == null) {
            Log.w(TAG, "No packs array found in server response");
            return packs;
        }

        for (JsonElement element : packsArray) {
            JsonObject obj = element.getAsJsonObject();
            StickerPack pack = parseSinglePack(obj);
            if (pack != null) {
                packs.add(pack);
            }
        }

        return packs;
    }

    /**
     * Parse a single sticker pack JSON object into a StickerPack model.
     */
    private static StickerPack parseSinglePack(JsonObject obj) {
        try {
            StickerPack pack = new StickerPack();
            pack.identifier = getStringOrDefault(obj, "identifier", "");
            pack.name = getStringOrDefault(obj, "name", "");
            pack.publisher = getStringOrDefault(obj, "publisher", "");
            pack.trayImageFile = getStringOrDefault(obj, "tray_image_file", "");
            pack.androidPlayStoreLink = getStringOrDefault(obj, "android_play_store_link", "");
            pack.iosAppStoreLink = getStringOrDefault(obj, "ios_app_store_link", "");
            pack.publisherWebsite = getStringOrDefault(obj, "publisher_website", "");
            pack.privacyPolicyWebsite = getStringOrDefault(obj, "privacy_policy_website", "");
            pack.licenseAgreementWebsite = getStringOrDefault(obj, "license_agreement_website", "");
            pack.imageDataVersion = getStringOrDefault(obj, "image_data_version", "1");
            pack.avoidCache = obj.has("avoid_cache") && obj.get("avoid_cache").getAsBoolean();

            // Parse stickers
            pack.stickers = new ArrayList<>();
            JsonArray stickersArray = obj.getAsJsonArray("stickers");
            if (stickersArray != null) {
                for (JsonElement stickerElement : stickersArray) {
                    JsonObject stickerObj = stickerElement.getAsJsonObject();
                    String imageFile = getStringOrDefault(stickerObj, "image_file", "");
                    List<String> emojis = new ArrayList<>();

                    JsonArray emojisArray = stickerObj.getAsJsonArray("emojis");
                    if (emojisArray != null) {
                        for (JsonElement emoji : emojisArray) {
                            emojis.add(emoji.getAsString());
                        }
                    }

                    if (!imageFile.isEmpty()) {
                        pack.stickers.add(new Sticker(imageFile, emojis));
                    }
                }
            }

            if (pack.identifier.isEmpty()) {
                Log.w(TAG, "Skipping pack with empty identifier");
                return null;
            }

            return pack;
        } catch (Exception e) {
            Log.e(TAG, "Failed to parse sticker pack", e);
            return null;
        }
    }

    private static String getStringOrDefault(JsonObject obj, String key, String defaultValue) {
        if (obj.has(key) && !obj.get(key).isJsonNull()) {
            return obj.get(key).getAsString();
        }
        return defaultValue;
    }
}
