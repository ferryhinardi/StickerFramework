package com.bobastickers.whatsapp;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

/**
 * Helper activity that sends the "Add to WhatsApp" intent.
 *
 * WhatsApp requires apps to fire a specific intent to register a sticker pack.
 * This activity encapsulates that intent logic and handles the result callback
 * (success / already added / WhatsApp not installed).
 *
 * Can be launched directly from other activities or used as a static helper.
 *
 * Intent extras expected when launching this activity:
 *   - EXTRA_STICKER_PACK_ID:   Pack identifier (String)
 *   - EXTRA_STICKER_PACK_NAME: Pack display name (String)
 */
public class AddStickerPackActivity extends AppCompatActivity {

    public static final String EXTRA_STICKER_PACK_ID = "sticker_pack_id";
    public static final String EXTRA_STICKER_PACK_NAME = "sticker_pack_name";

    private static final int ADD_PACK_REQUEST_CODE = 200;
    private static final String ACTION_ENABLE_STICKER_PACK =
            "com.whatsapp.intent.action.ENABLE_STICKER_PACK";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        String packId = getIntent().getStringExtra(EXTRA_STICKER_PACK_ID);
        String packName = getIntent().getStringExtra(EXTRA_STICKER_PACK_NAME);

        if (packId == null || packId.isEmpty()) {
            Toast.makeText(this, R.string.pack_add_failed, Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        addStickerPackToWhatsApp(packId, packName != null ? packName : "");
    }

    /**
     * Fire the WhatsApp intent to add a sticker pack.
     *
     * @param packId   Unique pack identifier.
     * @param packName Display name (used as intent extra).
     */
    private void addStickerPackToWhatsApp(String packId, String packName) {
        Intent intent = new Intent();
        intent.setAction(ACTION_ENABLE_STICKER_PACK);
        intent.putExtra("sticker_pack_id", packId);
        intent.putExtra("sticker_pack_authority",
                getPackageName() + ".stickercontentprovider");
        intent.putExtra("sticker_pack_name", packName);

        try {
            startActivityForResult(intent, ADD_PACK_REQUEST_CODE);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, R.string.whatsapp_not_installed, Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    /**
     * Static convenience method to launch the add-to-WhatsApp intent directly
     * from another activity, without navigating to this activity.
     *
     * @param activity  Calling activity (used for startActivityForResult).
     * @param packId    Pack identifier.
     * @param packName  Pack display name.
     */
    public static void addStickerPackToWhatsApp(
            Activity activity, String packId, String packName) {

        Intent intent = new Intent();
        intent.setAction(ACTION_ENABLE_STICKER_PACK);
        intent.putExtra("sticker_pack_id", packId);
        intent.putExtra("sticker_pack_authority",
                activity.getPackageName() + ".stickercontentprovider");
        intent.putExtra("sticker_pack_name", packName);

        try {
            activity.startActivityForResult(intent, ADD_PACK_REQUEST_CODE);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(activity, R.string.whatsapp_not_installed,
                    Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == ADD_PACK_REQUEST_CODE) {
            if (resultCode == RESULT_CANCELED) {
                if (data != null) {
                    String error = data.getStringExtra("validation_error");
                    if (error != null) {
                        if (error.contains("already_added")) {
                            Toast.makeText(this, R.string.pack_already_added,
                                    Toast.LENGTH_SHORT).show();
                        } else {
                            Toast.makeText(this, R.string.pack_add_failed,
                                    Toast.LENGTH_SHORT).show();
                        }
                    } else {
                        Toast.makeText(this, R.string.pack_add_failed,
                                Toast.LENGTH_SHORT).show();
                    }
                }
            } else {
                Toast.makeText(this, R.string.pack_added_successfully,
                        Toast.LENGTH_SHORT).show();
            }
            finish();
        }
    }
}
