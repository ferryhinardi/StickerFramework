package com.yourbrand.stickers;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageButton;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.bumptech.glide.Glide;
import com.google.android.material.appbar.MaterialToolbar;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Main launcher activity displaying all available sticker packs.
 *
 * Loading flow:
 *   1. Show progress bar
 *   2. Load bundled packs from assets (synchronous, fast)
 *   3. Display immediately
 *   4. Asynchronously fetch server packs and merge
 *
 * Each pack card shows: tray icon, name, publisher, and an "add" button.
 * Tapping the card opens {@link StickerPackDetailsActivity}.
 * Tapping the add button triggers the WhatsApp intent via {@link AddStickerPackActivity}.
 */
public class StickerPackListActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private TextView emptyView;
    private ProgressBar progressBar;

    private final List<StickerPack> stickerPacks = new ArrayList<>();
    private StickerPackAdapter adapter;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sticker_pack_list);

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        recyclerView = findViewById(R.id.sticker_pack_list);
        emptyView = findViewById(R.id.empty_view);
        progressBar = findViewById(R.id.progress_bar);

        adapter = new StickerPackAdapter();
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);

        loadStickerPacks();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Refresh the list when returning from details/add activities
        if (!stickerPacks.isEmpty()) {
            adapter.notifyDataSetChanged();
        }
    }

    /**
     * Load sticker packs: assets first (immediate), then server (async merge).
     */
    private void loadStickerPacks() {
        showLoading(true);

        executor.execute(() -> {
            // Step 1: Load bundled packs from assets
            List<StickerPack> assetPacks = new ArrayList<>();
            try {
                assetPacks = StickerPackLoader.loadFromAssets(StickerPackListActivity.this);
            } catch (IOException e) {
                // No bundled packs — not fatal, server packs may still load
            }

            // Step 2: Load cached server packs
            List<StickerPack> cachedPacks = StickerPackLoader.loadFromCache(
                    StickerPackListActivity.this);

            // Merge assets + cache for immediate display
            List<StickerPack> merged = StickerPackLoader.mergePacks(assetPacks, cachedPacks);

            // Update UI with what we have so far
            final List<StickerPack> initialPacks = new ArrayList<>(merged);
            mainHandler.post(() -> {
                stickerPacks.clear();
                stickerPacks.addAll(initialPacks);
                adapter.notifyDataSetChanged();
                showLoading(false);
                updateEmptyState();
            });

            // Step 3: Fetch from server in background
            String serverUrl = BuildConfig.STICKER_API_BASE_URL;
            if (serverUrl != null && !serverUrl.isEmpty()) {
                List<StickerPack> serverPacks = StickerPackLoader.fetchFromServer(serverUrl);
                if (!serverPacks.isEmpty()) {
                    List<StickerPack> finalMerged = StickerPackLoader.mergePacks(
                            initialPacks, serverPacks);
                    mainHandler.post(() -> {
                        stickerPacks.clear();
                        stickerPacks.addAll(finalMerged);
                        adapter.notifyDataSetChanged();
                        updateEmptyState();
                    });
                }
            }
        });
    }

    private void showLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        recyclerView.setVisibility(loading ? View.GONE : View.VISIBLE);
    }

    private void updateEmptyState() {
        if (stickerPacks.isEmpty()) {
            emptyView.setVisibility(View.VISIBLE);
            recyclerView.setVisibility(View.GONE);
        } else {
            emptyView.setVisibility(View.GONE);
            recyclerView.setVisibility(View.VISIBLE);
        }
    }

    // ---------------------------------------------------------------
    // RecyclerView Adapter
    // ---------------------------------------------------------------

    private class StickerPackAdapter extends RecyclerView.Adapter<StickerPackAdapter.ViewHolder> {

        @NonNull
        @Override
        public ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
            View view = LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_sticker_pack, parent, false);
            return new ViewHolder(view);
        }

        @Override
        public void onBindViewHolder(@NonNull ViewHolder holder, int position) {
            StickerPack pack = stickerPacks.get(position);
            holder.bind(pack);
        }

        @Override
        public int getItemCount() {
            return stickerPacks.size();
        }

        class ViewHolder extends RecyclerView.ViewHolder {

            private final ImageView trayIcon;
            private final TextView packName;
            private final TextView packPublisher;
            private final ImageButton addButton;

            ViewHolder(@NonNull View itemView) {
                super(itemView);
                trayIcon = itemView.findViewById(R.id.tray_icon);
                packName = itemView.findViewById(R.id.pack_name);
                packPublisher = itemView.findViewById(R.id.pack_publisher);
                addButton = itemView.findViewById(R.id.add_button);
            }

            void bind(StickerPack pack) {
                packName.setText(pack.name);
                packPublisher.setText(pack.publisher);

                // Load tray icon from assets or cache
                loadTrayIcon(pack);

                // Card click → open pack details
                itemView.setOnClickListener(v -> {
                    Intent intent = new Intent(
                            StickerPackListActivity.this,
                            StickerPackDetailsActivity.class);
                    intent.putExtra(StickerPackDetailsActivity.EXTRA_PACK_ID,
                            pack.identifier);
                    startActivity(intent);
                });

                // Add button click → add to WhatsApp
                addButton.setOnClickListener(v -> {
                    if (StickerPackValidator.isPackAddable(pack)) {
                        AddStickerPackActivity.addStickerPackToWhatsApp(
                                StickerPackListActivity.this,
                                pack.identifier, pack.name);
                    } else {
                        Toast.makeText(StickerPackListActivity.this,
                                R.string.pack_invalid, Toast.LENGTH_SHORT).show();
                    }
                });
            }

            /**
             * Load the tray icon for a sticker pack using Glide.
             *
             * Tries the assets directory first (via asset URI),
             * then falls back to the cache directory.
             */
            private void loadTrayIcon(StickerPack pack) {
                if (pack.trayImageFile == null || pack.trayImageFile.isEmpty()) {
                    trayIcon.setImageResource(android.R.drawable.ic_menu_gallery);
                    return;
                }

                String assetPath = pack.identifier + "/" + pack.trayImageFile;
                Uri assetUri = Uri.parse("file:///android_asset/" + assetPath);

                File cacheDir = new File(
                        itemView.getContext().getCacheDir(), "stickers");
                File iconFile = new File(
                        new File(cacheDir, pack.identifier), pack.trayImageFile);

                Glide.with(itemView)
                        .load(assetUri)
                        .placeholder(android.R.drawable.ic_menu_gallery)
                        .error(
                                Glide.with(itemView)
                                        .load(iconFile)
                                        .placeholder(android.R.drawable.ic_menu_gallery)
                                        .error(android.R.drawable.ic_menu_gallery)
                        )
                        .into(trayIcon);
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        executor.shutdown();
    }
}
