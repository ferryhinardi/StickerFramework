package com.bobastickers.whatsapp;

import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.GridLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Displays the details of a single sticker pack: tray icon, name, publisher,
 * sticker count, and a grid of all stickers in the pack.
 *
 * Launched from {@link StickerPackListActivity} with the pack identifier
 * passed as an Intent extra.
 *
 * The "Add to WhatsApp" button validates the pack first, then fires the
 * WhatsApp intent via {@link AddStickerPackActivity}.
 */
public class StickerPackDetailsActivity extends AppCompatActivity {

    public static final String EXTRA_PACK_ID = "extra_pack_id";

    private static final int GRID_SPAN_COUNT = 4;

    private StickerPack stickerPack;

    private ProgressBar progressBar;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sticker_pack_details);

        progressBar = findViewById(R.id.progress_bar);

        String packId = getIntent().getStringExtra(EXTRA_PACK_ID);
        if (packId == null || packId.isEmpty()) {
            Toast.makeText(this, R.string.error_loading_packs, Toast.LENGTH_SHORT).show();
            finish();
            return;
        }

        // Show loading state while we look up the pack off the main thread
        showLoading(true);

        executor.execute(() -> {
            StickerPack result = findPack(packId);
            mainHandler.post(() -> {
                showLoading(false);
                if (result == null) {
                    Toast.makeText(StickerPackDetailsActivity.this,
                            R.string.error_loading_packs, Toast.LENGTH_SHORT).show();
                    finish();
                    return;
                }
                stickerPack = result;
                setupToolbar();
                bindPackInfo();
                setupStickerGrid();
                setupAddButton();
            });
        });
    }

    /**
     * Load all packs from assets + cache and find the one matching the identifier.
     * This method performs I/O and must be called from a background thread.
     */
    private StickerPack findPack(String identifier) {
        List<StickerPack> packs = new ArrayList<>();

        // Load from assets
        try {
            packs.addAll(StickerPackLoader.loadFromAssets(this));
        } catch (IOException ignored) {
        }

        // Merge cached packs
        List<StickerPack> cachedPacks = StickerPackLoader.loadFromCache(this);
        packs = StickerPackLoader.mergePacks(packs, cachedPacks);

        for (StickerPack pack : packs) {
            if (identifier.equals(pack.identifier)) {
                return pack;
            }
        }
        return null;
    }

    private void showLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
    }

    private void setupToolbar() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        if (getSupportActionBar() != null) {
            getSupportActionBar().setDisplayHomeAsUpEnabled(true);
            getSupportActionBar().setTitle(stickerPack.name);
        }
        toolbar.setNavigationOnClickListener(v -> getOnBackPressedDispatcher().onBackPressed());
    }

    private void bindPackInfo() {
        ImageView trayIcon = findViewById(R.id.tray_icon);
        TextView packName = findViewById(R.id.pack_name);
        TextView packPublisher = findViewById(R.id.pack_publisher);
        TextView stickerCount = findViewById(R.id.sticker_count);

        packName.setText(stickerPack.name);
        packPublisher.setText(getString(R.string.publisher_label, stickerPack.publisher));
        stickerCount.setText(getString(R.string.sticker_count_format,
                stickerPack.getTotalSize()));

        loadTrayIcon(trayIcon);
    }

    /**
     * Load the tray icon using Glide. Tries assets URI first, then cache file.
     */
    private void loadTrayIcon(ImageView imageView) {
        if (stickerPack.trayImageFile == null || stickerPack.trayImageFile.isEmpty()) {
            imageView.setImageResource(android.R.drawable.ic_menu_gallery);
            return;
        }

        // Try assets first via Glide's asset URI scheme
        String assetPath = stickerPack.identifier + "/" + stickerPack.trayImageFile;
        Uri assetUri = Uri.parse("file:///android_asset/" + assetPath);

        // Try cache directory as fallback
        File cacheDir = new File(getCacheDir(), "stickers");
        File iconFile = new File(new File(cacheDir, stickerPack.identifier),
                stickerPack.trayImageFile);

        // Use the cache file if the asset probably doesn't exist (we can't
        // check synchronously without I/O, so prefer asset URI and let Glide
        // handle the error with a fallback).
        Object model = iconFile.exists() ? iconFile : assetUri;

        Glide.with(this)
                .load(assetUri)
                .placeholder(android.R.drawable.ic_menu_gallery)
                .error(
                        // If asset load fails, try cache file
                        Glide.with(this)
                                .load(iconFile)
                                .placeholder(android.R.drawable.ic_menu_gallery)
                                .error(android.R.drawable.ic_menu_gallery)
                )
                .into(imageView);
    }

    private void setupStickerGrid() {
        RecyclerView stickerGrid = findViewById(R.id.sticker_grid);
        stickerGrid.setLayoutManager(new GridLayoutManager(this, GRID_SPAN_COUNT));

        List<Sticker> stickers = stickerPack.stickers != null
                ? stickerPack.stickers
                : Collections.emptyList();
        stickerGrid.setAdapter(new StickerGridAdapter(stickers));
    }

    private void setupAddButton() {
        MaterialButton addButton = findViewById(R.id.add_to_whatsapp_button);
        addButton.setOnClickListener(v -> {
            if (StickerPackValidator.isPackAddable(stickerPack)) {
                AddStickerPackActivity.addStickerPackToWhatsApp(
                        StickerPackDetailsActivity.this,
                        stickerPack.identifier, stickerPack.name);
            } else {
                Toast.makeText(StickerPackDetailsActivity.this,
                        R.string.pack_invalid, Toast.LENGTH_SHORT).show();
            }
        });
    }

    // -----------------------------------------------------------------
    // Sticker Grid Adapter
    // -----------------------------------------------------------------

    private class StickerGridAdapter
            extends RecyclerView.Adapter<StickerGridAdapter.ViewHolder> {

        private final List<Sticker> stickers;

        StickerGridAdapter(List<Sticker> stickers) {
            this.stickers = stickers;
        }

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_sticker, parent, false);
            return new ViewHolder(view);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            Sticker sticker = stickers.get(position);
            holder.bind(sticker);
        }

        @Override
        public int getItemCount() {
            return stickers.size();
        }

        class ViewHolder extends RecyclerView.ViewHolder {

            private final ImageView stickerImage;

            ViewHolder(@NonNull View itemView) {
                super(itemView);
                stickerImage = itemView.findViewById(R.id.sticker_image);
            }

            void bind(Sticker sticker) {
                if (sticker.imageFileName == null || sticker.imageFileName.isEmpty()) {
                    stickerImage.setImageResource(android.R.drawable.ic_menu_gallery);
                    return;
                }

                String assetPath = stickerPack.identifier + "/" + sticker.imageFileName;
                Uri assetUri = Uri.parse("file:///android_asset/" + assetPath);

                File cacheDir = new File(
                        stickerImage.getContext().getCacheDir(), "stickers");
                File stickerFile = new File(
                        new File(cacheDir, stickerPack.identifier),
                        sticker.imageFileName);

                Glide.with(stickerImage)
                        .load(assetUri)
                        .placeholder(android.R.drawable.ic_menu_gallery)
                        .error(
                                Glide.with(stickerImage)
                                        .load(stickerFile)
                                        .placeholder(android.R.drawable.ic_menu_gallery)
                                        .error(android.R.drawable.ic_menu_gallery)
                        )
                        .into(stickerImage);
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
