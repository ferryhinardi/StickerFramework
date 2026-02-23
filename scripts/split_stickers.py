#!/usr/bin/env python3
"""
Split a sticker sheet into individual stickers with transparent backgrounds.
Each sticker is saved as a separate 512x512 PNG file.
"""

import os
import numpy as np
from pathlib import Path
from PIL import Image

# Repo root (parent of scripts/)
_SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = _SCRIPTS_DIR.parent


def remove_white_background(img, threshold=230):
    """
    Remove white background using flood-fill from corners.

    Only removes white pixels that are connected to the image corners,
    preserving interior white details (eye whites, fur highlights, text,
    speech bubbles, clothing). Uses 8-connectivity so diagonal background
    regions are also captured. Samples a 5x5 patch at each corner instead
    of a single pixel to be robust against edge content.
    """
    from scipy.ndimage import label as scipy_label

    img = img.convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # Mark pixels white enough to be background candidates
    white_mask = np.all(arr > threshold, axis=2)

    # Label connected regions using 8-connectivity (diagonal connections included)
    structure = np.ones((3, 3), dtype=int)
    labeled, _ = scipy_label(white_mask, structure=structure)

    # Sample a 5x5 patch at each corner; collect all labels present there
    patch = 5
    corner_labels = set()
    for cy_slice, cx_slice in [
        (slice(0, patch), slice(0, patch)),
        (slice(0, patch), slice(w - patch, w)),
        (slice(h - patch, h), slice(0, patch)),
        (slice(h - patch, h), slice(w - patch, w)),
    ]:
        for lbl in np.unique(labeled[cy_slice, cx_slice]):
            if lbl > 0:
                corner_labels.add(lbl)

    # Build background mask: only white pixels connected to corners
    bg_mask = np.zeros((h, w), dtype=bool)
    for lbl in corner_labels:
        bg_mask |= labeled == lbl

    # Compose RGBA: background → alpha=0, content → alpha=255
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[:, :, :3] = arr
    result[:, :, 3] = np.where(bg_mask, 0, 255)

    return Image.fromarray(result, "RGBA")


def blank_text_zones(
    img_array, grid_cols, grid_rows, text_fraction=0.28, row_starts=None
):
    """
    Blank out (set to white) the top text-label zone of every grid cell in the
    source sheet before background removal.  This prevents the text label from
    being treated as part of the character blob.

    The text boundary is detected per-cell by scanning from the top of the cell
    downward and finding where the horizontal content span first exceeds
    ``body_span_threshold`` (indicating character body, not narrow text).  This
    is more robust than a fixed fraction because the character body may start
    immediately after the text with no gap.

    For sheets with non-uniform row spacing (e.g. Pack 5), pass explicit
    ``row_starts`` pixel coordinates to override uniform-grid auto-detection.

    Args:
        img_array           : H × W × 3  uint8 numpy array (RGB)
        grid_cols           : number of columns in the grid
        grid_rows           : number of rows in the grid
        text_fraction       : fallback fraction of content cell height to blank
                              when auto-detection fails (default 0.28)
        row_starts          : optional list of length ``grid_rows`` giving the
                              absolute y-coordinate where each grid row starts.

    Returns:
        Modified copy of img_array with text zones blanked to white.
    """
    result = img_array.copy()
    h, w = result.shape[:2]
    bg_threshold = 240  # pixels brighter than this on all channels = background

    cell_w = w / grid_cols
    uniform_cell_h = h / grid_rows

    # Build row boundaries
    if row_starts is not None:
        row_boundaries = []
        for r in range(grid_rows):
            y0 = row_starts[r]
            y1 = row_starts[r + 1] if r + 1 < grid_rows else h
            row_boundaries.append((y0, y1))
    else:
        row_boundaries = [
            (int(round(r * uniform_cell_h)), int(round((r + 1) * uniform_cell_h)))
            for r in range(grid_rows)
        ]

    for r, (row_y0, row_y1) in enumerate(row_boundaries):
        row_h = max(row_y1 - row_y0, 1)
        # body_span_threshold: a row whose non-white x-span exceeds this is
        # considered character body (not a text label).  Using 40% of cell width.
        body_span_threshold = (w / grid_cols) * 0.40

        for c in range(grid_cols):
            cx0 = int(round(c * cell_w))
            cx1 = int(round((c + 1) * cell_w))

            # Scan rows top→down; find the first row whose content x-span
            # exceeds body_span_threshold — that is the start of the character.
            char_start_abs = None
            for abs_y in range(row_y0, row_y1):
                row_pixels = result[abs_y, cx0:cx1, :]
                non_bg = np.where(np.any(row_pixels < bg_threshold, axis=1))[0]
                if len(non_bg) >= 2:
                    span = int(non_bg[-1]) - int(non_bg[0])
                    if span > body_span_threshold:
                        char_start_abs = abs_y
                        break

            if char_start_abs is not None:
                # Blank everything from row top up to (but not including) the
                # first character body row.
                blank_end = char_start_abs
            else:
                # Fallback: use fixed fraction
                blank_end = row_y0 + int(round(row_h * text_fraction))

            blank_end = min(blank_end, row_y1)
            if blank_end > row_y0:
                result[row_y0:blank_end, cx0:cx1, :] = 255

    return result


def find_sticker_bboxes(img, min_size=50, grid_rows=4):
    """
    Find bounding boxes of individual stickers by detecting connected
    non-transparent regions.

    Args:
        img: RGBA PIL Image with transparent background
        min_size: Minimum pixel dimension to count as a sticker
        grid_rows: Expected number of rows in the grid (for sort buckets)
    """
    data = np.array(img)
    # Create a binary mask of non-transparent pixels
    mask = data[:, :, 3] > 0

    from scipy import ndimage

    labeled, num_features = ndimage.label(mask)

    bboxes = []
    for i in range(1, num_features + 1):
        ys, xs = np.where(labeled == i)
        if len(ys) < min_size * min_size:
            # Skip tiny fragments/noise
            continue
        bbox = (xs.min(), ys.min(), xs.max(), ys.max())
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w > min_size and h > min_size:
            bboxes.append(bbox)

    # Sort: top row first (by center-y bucket), then left to right (by x)
    row_height = img.height // max(grid_rows, 1)
    bboxes.sort(key=lambda b: ((b[1] + b[3]) // 2 // row_height, b[0]))
    return bboxes


def crop_and_resize(img, bbox, target_size=512, padding=10):
    """Crop a sticker from the image and resize to target_size x target_size."""
    x1, y1, x2, y2 = bbox
    # Add small padding
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(img.width, x2 + padding)
    y2 = min(img.height, y2 + padding)

    cropped = img.crop((x1, y1, x2, y2))

    # Resize while keeping aspect ratio, then paste on a square canvas
    w, h = cropped.size
    scale = min(target_size / w, target_size / h) * 0.9  # 90% to leave margin
    new_w = int(w * scale)
    new_h = int(h * scale)
    cropped = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Center on a transparent 512x512 canvas
    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    canvas.paste(cropped, (offset_x, offset_y), cropped)

    return canvas


def _find_row_bands(arr, min_band_height=30):
    """
    Scan the image vertically to find content row bands separated by white gutters.
    Returns list of (y0, y1) tuples for each content band.
    """
    h, w = arr.shape[:2]
    row_content = [np.sum(np.any(arr[row, :, :] < 230, axis=1)) for row in range(h)]
    content_rows = [r for r, c in enumerate(row_content) if c >= 5]
    if not content_rows:
        return [(0, h)]

    bands = []
    band_start = content_rows[0]
    prev = content_rows[0]
    for r in content_rows[1:]:
        if r > prev + 20:  # gap of >20 white rows = new band
            if prev - band_start >= min_band_height:
                bands.append((band_start, prev + 1))
            band_start = r
        prev = r
    if prev - band_start >= min_band_height:
        bands.append((band_start, prev + 1))
    return bands


def _find_col_ranges_in_band(arr, y0, y1, grid_cols, min_gap=8):
    """
    Within a horizontal row band, detect the true x-ranges for each column
    by finding white vertical gutters.  Falls back to uniform division if
    auto-detection doesn't yield exactly grid_cols ranges.

    Returns list of (x0, x1) tuples, one per column, in left-to-right order.
    """
    import statistics

    band = arr[y0:y1, :, :]
    w = arr.shape[1]

    col_content = [np.sum(np.any(band[:, col, :] < 230, axis=1)) for col in range(w)]
    mean_c = statistics.mean(col_content) if any(c > 0 for c in col_content) else 1
    threshold = mean_c * 0.15

    # Find low-content columns
    low_cols = [col for col in range(w) if col_content[col] < threshold]

    # Group into separator ranges
    sep_groups = []
    if low_cols:
        g = [low_cols[0]]
        for col in low_cols[1:]:
            if col == g[-1] + 1:
                g.append(col)
            else:
                sep_groups.append(g)
                g = [col]
        sep_groups.append(g)

    # Filter out tiny gaps that aren't real separators
    sep_groups = [g for g in sep_groups if len(g) >= min_gap]

    # Build content ranges between separators
    boundaries = [0] + [g[len(g) // 2] for g in sep_groups] + [w]
    content_ranges = []
    for i in range(len(boundaries) - 1):
        x0 = boundaries[i]
        x1 = boundaries[i + 1]
        sub = [col_content[c] for c in range(x0, x1)]
        non_empty = [x0 + j for j, v in enumerate(sub) if v > 2]
        if non_empty and non_empty[-1] - non_empty[0] > 20:
            content_ranges.append((non_empty[0], non_empty[-1] + 1))

    if len(content_ranges) == grid_cols:
        return content_ranges

    # Fallback: uniform division
    cell_w = w / grid_cols
    return [
        (int(round(c * cell_w)), int(round((c + 1) * cell_w))) for c in range(grid_cols)
    ]


def extract_grid_cells(
    img,
    grid_cols,
    grid_rows,
    row_starts=None,
    target_size=512,
    uniform_cols=False,
    col_starts=None,
    row_col_starts=None,
):
    """
    Extract stickers by dividing the image into a grid.
    Row boundaries are either provided via ``row_starts`` or auto-detected
    from white horizontal gutters.  Column boundaries are auto-detected per
    row band from white vertical gutters — this handles sheets where text
    labels overflow the nominal cell width.

    For each cell the non-transparent bounding box is found and the content
    is fit onto a ``target_size × target_size`` canvas.

    Args:
        img          : RGBA PIL Image (background already removed)
        grid_cols    : number of grid columns
        grid_rows    : number of grid rows
        row_starts   : optional list of content-row start y-coordinates (len=grid_rows)
        target_size  : output canvas size in pixels
        uniform_cols : if True, skip column auto-detection and always use uniform
                       division; use this when decorative elements or text cause
                       false column separators to be detected
        col_starts   : optional list of explicit column boundary x-coordinates
                       (length = grid_cols + 1, e.g. [0, 285, 550, 822, 1024]).
                       When provided, overrides both uniform_cols and auto-detection.
        row_col_starts : optional dict mapping row index (0-based) to a per-row
                         col_starts list (length = grid_cols + 1).  Rows not in the
                         dict fall back to ``col_starts`` / auto-detection as usual.

    Yields:
        PIL RGBA images, one per grid cell in reading order (row-major, left-right)
    """
    w, h = img.size
    data = np.array(img)
    # Use RGB for separator detection (alpha channel is already removed bg)
    rgb = data[:, :, :3]

    # Build explicit column ranges from col_starts if provided
    if col_starts is not None:
        explicit_col_ranges = [
            (col_starts[c], col_starts[c + 1]) for c in range(grid_cols)
        ]
    else:
        explicit_col_ranges = None

    # Build per-row overrides from row_col_starts
    row_col_overrides = {}
    if row_col_starts is not None:
        for row_idx, rcs in row_col_starts.items():
            row_col_overrides[int(row_idx)] = [
                (rcs[c], rcs[c + 1]) for c in range(grid_cols)
            ]

    # Precompute uniform column ranges (used when uniform_cols=True or as fallback)
    cell_w = w / grid_cols
    uniform_col_ranges = [
        (int(round(c * cell_w)), int(round((c + 1) * cell_w))) for c in range(grid_cols)
    ]

    # Build row boundaries
    if row_starts is not None:
        row_boundaries = [
            (row_starts[r], row_starts[r + 1] if r + 1 < grid_rows else h)
            for r in range(grid_rows)
        ]
    else:
        bands = _find_row_bands(rgb, min_band_height=30)
        if len(bands) == grid_rows:
            row_boundaries = bands
        else:
            # Fallback to uniform division
            cell_h = h / grid_rows
            row_boundaries = [
                (int(round(r * cell_h)), int(round((r + 1) * cell_h)))
                for r in range(grid_rows)
            ]

    for r, (ry0, ry1) in enumerate(row_boundaries):
        # Determine column boundaries for this row band
        if r in row_col_overrides:
            col_ranges = row_col_overrides[r]
        elif explicit_col_ranges is not None:
            col_ranges = explicit_col_ranges
        elif uniform_cols:
            col_ranges = uniform_col_ranges
        else:
            col_ranges = _find_col_ranges_in_band(rgb, ry0, ry1, grid_cols)

        for c, (cx0, cx1) in enumerate(col_ranges):
            cell_data = data[ry0:ry1, cx0:cx1, :]
            alpha = cell_data[:, :, 3]

            # Find connected components and discard left-edge body bleed:
            # content from the previous cell's sticker body that physically
            # crosses the column boundary. These fragments appear entirely
            # within the leftmost 25% of the cell width and are disconnected
            # from the main sticker body.
            #
            # To avoid also discarding text-label characters that start near
            # the left edge, we only filter components that are tall relative
            # to the cell (> 30% of cell height) — body bleed spans a large
            # vertical range while text characters are short and sit in the
            # top portion of the cell.
            from scipy.ndimage import label as _scipy_label

            labeled_cell, n_comp = _scipy_label(alpha > 0)
            if n_comp == 0:
                yield Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
                continue

            cell_w = cell_data.shape[1]
            cell_h = cell_data.shape[0]

            keep_mask = np.zeros_like(alpha, dtype=bool)
            for i in range(1, n_comp + 1):
                comp_mask = labeled_cell == i
                cxs = np.where(comp_mask)[1]
                cys = np.where(comp_mask)[0]
                # Discard left-edge body bleed: entirely within leftmost 25%
                # AND tall enough to be sticker-body bleed (> 30% of cell height).
                # Short components (text labels, sparkles) are kept even if they
                # sit within the leftmost 25%.
                comp_height = int(cys.max()) - int(cys.min())
                is_left_edge = cxs.max() < cell_w * 0.25
                is_tall = comp_height > cell_h * 0.30
                if is_left_edge and is_tall:
                    continue
                keep_mask |= comp_mask

            if not keep_mask.any():
                # Fallback: nothing survived — keep everything
                keep_mask = alpha > 0
                # Fallback: nothing survived — keep everything
                keep_mask = alpha > 0

            ys, xs = np.where(keep_mask)

            pad = 4
            ymin = max(0, int(ys.min()) - pad)
            ymax = min(cell_data.shape[0], int(ys.max()) + pad + 1)
            xmin = max(0, int(xs.min()) - pad)
            xmax = min(cell_data.shape[1], int(xs.max()) + pad + 1)

            # Zero out bleed pixels so they don't appear in the output
            filtered_data = cell_data.copy()
            filtered_data[~keep_mask, 3] = 0

            cropped_arr = filtered_data[ymin:ymax, xmin:xmax, :]
            cropped = Image.fromarray(cropped_arr, "RGBA")

            cw, ch = cropped.size
            scale = min(target_size / cw, target_size / ch) * 0.9
            new_w = max(1, int(cw * scale))
            new_h = max(1, int(ch * scale))
            cropped = cropped.resize((new_w, new_h), Image.LANCZOS)

            canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
            off_x = (target_size - new_w) // 2
            off_y = (target_size - new_h) // 2
            canvas.paste(cropped, (off_x, off_y), cropped)
            yield canvas


def main():
    # ── Configure input/output per sticker pack ──
    # Keys are display names; "pack_dir" is the kebab-case dir under packs/
    pack_name = os.environ.get("STICKER_PACK", "Jesus Christ – Faith & Peace")

    # Pack-specific settings (pack_dir = folder name under packs/)
    PACKS = {
        "chubby mochi cat": {
            "pack_dir": "chubby-mochi-cat",
            "input_file": "ChatGPT Image Feb 21, 2026, 05_09_28 PM.png",
            "grid_rows": 3,
            "names": [
                "01_what",
                "02_lol",
                "03_ok",
                "04_nope",
                "05_bye",
                "06_lets_go",
                "07_im_done",
                "08_perfect",
                "09_sure",
                "10_yesss",
            ],
        },
        "chubby mochi hamster 2": {
            "pack_dir": "chubby-mochi-hamster-2",
            "input_file": "sticker_pack.png",
            "grid_rows": 5,
            "names": [
                "01_hellooo",
                "02_thank_you",
                "03_sorry",
                "04_love_you",
                "05_hmph",
                "06_busy",
                "07_okayyy",
                "08_waiting",
                "09_noooo",
                "10_sleepy",
                "11_miss_you",
                "12_yayyy",
                "13_lets_go",
            ],
        },
        "Little Angel – Daily Blessings": {
            "pack_dir": "little-angel",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "names": [
                "01_good_morning",
                "02_god_bless_you",
                "03_praying_for_you",
                "04_thank_you_lord",
                "05_amen",
                "06_stay_strong",
                "07_have_faith",
                "08_peace_be_with_you",
                "09_dont_worry",
                "10_you_are_blessed",
                "11_hallelujah",
                "12_thank_you",
                "13_sorry",
                "14_god_is_good",
                "15_trust_him",
                "16_good_night",
            ],
        },
        "Jesus Christ – Faith & Peace": {
            "pack_dir": "jesus-faith-and-peace",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "threshold": 235,
            "names": [
                "01_god_bless_you",
                "02_peace_be_with_you",
                "03_have_faith",
                "04_praying_for_you",
                "05_do_not_fear",
                "06_i_am_with_you",
                "07_trust_in_him",
                "08_god_is_good",
                "09_amen",
                "10_stay_strong",
                "11_thank_you_lord",
                "12_forgive",
                "13_love_one_another",
                "14_be_kind",
                "15_you_are_loved",
                "16_good_night",
            ],
        },
        "Jesus Christ 2": {
            "pack_dir": "jesus-christ-2",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "threshold": 235,
            "names": [
                "01_walk_by_faith",
                "02_trust_his_plan",
                "03_keep_praying",
                "04_faith_over_fear",
                "05_his_grace_is_enough",
                "06_seek_him_first",
                "07_give_thanks",
                "08_let_your_light_shine",
                "09_be_still",
                "10_follow_me",
                "11_god_is_with_you",
                "12_rejoice",
                "13_believe",
                "14_love_never_fails",
                "15_hope_in_him",
                "16_give_it_to_god",
            ],
        },
        "Jesus Christ 1": {
            "pack_dir": "jesus-christ-1",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "threshold": 235,
            "names": [
                "01_god_bless_you",
                "02_peace_be_with_you",
                "03_have_faith",
                "04_praying_for_you",
                "05_do_not_fear",
                "06_i_am_with_you",
                "07_trust_in_him",
                "08_god_is_good",
                "09_amen",
                "10_stay_strong",
                "11_thank_you_lord",
                "12_forgive",
                "13_love_one_another",
                "14_be_kind",
                "15_you_are_loved",
                "16_good_night",
            ],
        },
        "Corporate Sloth – Tired but Trying": {
            "pack_dir": "corporate-sloth",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "names": [
                "01_good_morning",
                "02_on_my_way",
                "03_in_a_meeting",
                "04_busy",
                "05_deadline_mode",
                "06_please_review",
                "07_noted",
                "08_approved",
                "09_lets_discuss",
                "10_still_working",
                "11_need_coffee",
                "12_sorry",
                "13_thank_you",
                "14_almost_done",
                "15_overtime",
                "16_celebrate",
            ],
        },
        "Boba & Milo – Cheerful Otter Duo": {
            "pack_dir": "boba-milo-1",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "grid_cols": 4,
            "row_starts": [37, 287, 542, 778],
            "col_starts": [0, 285, 550, 822, 1024],
            "row_col_starts": {
                2: [0, 290, 550, 789, 1024],
                3: [0, 316, 555, 823, 1024],
            },
            "use_grid_crop": True,
            "skip_text_blank": True,
            "names": [
                "01_pagi",
                "02_semangat",
                "03_thank_you",
                "04_maaf_ya",
                "05_yay",
                "06_deadline",
                "07_aku_bantu",
                "08_capek_ya",
                "09_hehe",
                "10_ups",
                "11_lunch_yuk",
                "12_cuddle",
                "13_high_five",
                "14_tunggu_ya",
                "15_good_job",
                "16_proud",
            ],
        },
        "Boba & Milo – Cheerful Otter Duo 2": {
            "pack_dir": "boba-milo-2",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "use_grid_crop": True,
            "skip_text_blank": True,
            "names": [
                "01_morning",
                "02_fighting",
                "03_thank_you",
                "04_apology",
                "05_celebration",
                "06_deadline_panic",
                "07_helping",
                "08_tired",
                "09_playful_laugh",
                "10_shocked",
                "11_lunch_invite",
                "12_focused",
                "13_calm",
                "14_wholesome_support",
                "15_focused_time",
                "16_good_job",
            ],
        },
        "Boba & Milo – Cheerful Otter Duo 3": {
            "pack_dir": "boba-milo-3",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "use_grid_crop": True,
            "skip_text_blank": True,
            # Row 1 & 2 have <8px gaps between sticker bodies so auto-detection
            # falls back to uniform 256px columns, clipping stickers on the right.
            # These overrides place column cuts midway between the sticker bodies.
            "row_col_starts": {
                1: [0, 312, 550, 779, 1024],
                2: [0, 281, 542, 780, 1024],
            },
            "names": [
                "01_miss_you",
                "02_nervous",
                "03_proud_of_you",
                "04_overthinking",
                "05_lets_do_it_together",
                "06_sleepy",
                "07_embarrassed",
                "08_thankful",
                "09_confused",
                "10_motivated",
                "11_relieved",
                "12_oops_my_bad",
                "13_dont_worry",
                "14_excited_secret",
                "15_youre_amazing",
                "16_team_mode",
            ],
        },
        "Boba & Milo – Cheerful Otter Duo 4": {
            "pack_dir": "boba-milo-4",
            "input_file": "sticker_pack.png",
            "grid_rows": 4,
            "use_grid_crop": True,
            "skip_text_blank": True,
            "names": [
                "01_miss_you",
                "02_nervous",
                "03_proud_of_you",
                "04_overthinking",
                "05_lets_do_it_together",
                "06_sleepy",
                "07_embarrassed",
                "08_thankful",
                "09_confused",
                "10_motivated",
                "11_relieved",
                "12_oops_my_bad",
                "13_dont_worry",
                "14_excited_secret",
                "15_youre_amazing",
                "16_team_mode",
            ],
        },
        "Cappy the Chill Capybara (Sheet 1)": {
            "pack_dir": "cappy-capybara",
            "input_file": "composite_sheet_1.png",
            "grid_rows": 3,
            "grid_cols": 3,
            "use_grid_crop": True,
            "skip_text_blank": True,
            # DALL-E produced a 3×3 grid (9 stickers) instead of 2×4
            "row_starts": [43, 381, 700],
            "col_starts": [0, 377, 713, 1024],
            "names": [
                "01_good_morning",
                "02_ok_thumbs_up",
                "03_thank_you",
                "04_love",
                "05_lol",
                "06_hungry",
                "07_heart",
                "08_sleepy",
                "09_working_hard",
            ],
        },
        "Cappy the Chill Capybara (Sheet 2)": {
            "pack_dir": "cappy-capybara",
            "input_file": "composite_sheet_2.png",
            "grid_rows": 3,
            "grid_cols": 3,
            "use_grid_crop": True,
            "skip_text_blank": True,
            # DALL-E produced a 3×3 grid (9 stickers) instead of 2×4
            "row_starts": [41, 395, 686],
            "col_starts": [0, 379, 706, 1024],
            "names": [
                "10_excited",
                "11_sad",
                "12_angry",
                "13_bye",
                "14_thinking",
                "15_sorry",
                "16_cheering",
                "17_cheering_2",
                "18_good_night",
            ],
        },
        "Boba & Milo – Cheerful Otter Duo 5": {
            "pack_dir": "boba-milo-5",
            "input_file": "sticker_pack.png",
            "grid_rows": 5,
            "grid_cols": 3,
            "skip_text_blank": True,
            "row_starts": [181, 441, 693, 955, 1193],
            "use_grid_crop": True,
            "names": [
                "01_marhaban_ya_ramadan",
                "02_sahur_time",
                "03_semangat_puasa",
                "04_sahur_time_sleepy",
                "05_semangat_puasa_2",
                "06_alhamdulillah",
                "07_waktunya_berbuka",
                "08_makan_bareng_yuk",
                "09_tarawih_time",
                "10_capek_tapi_berkah",
                "11_sabar_ya",
                "12_haus_banget",
                "13_doa_dulu",
                "14_selamat_idul_fitri",
                "15_mohon_maaf_lahir_batin",
            ],
        },
    }

    pack = PACKS[pack_name]
    pack_dir = REPO_ROOT / "packs" / pack["pack_dir"]
    input_path = str(pack_dir / pack["input_file"])
    output_dir = str(pack_dir / "split")
    os.makedirs(output_dir, exist_ok=True)

    # Remove stale PNG files from previous runs so orphans don't accumulate.
    # For multi-sheet packs (same pack_dir, different input_file), only remove
    # files whose names match THIS sheet's sticker names to preserve other sheets.
    expected_names = {f"{n}.png" for n in pack.get("names", [])}
    for stale in Path(output_dir).glob("*.png"):
        if expected_names and stale.name not in expected_names:
            continue  # belongs to a different sheet of the same pack
        stale.unlink()

    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    print(f"Image size: {img.size}")

    # Step 1 (optional): Blank out the top text-label zone in every grid cell.
    # Only done when text labels should be removed from the sticker.
    # Set "skip_text_blank": True in the pack config to keep text as part of the design.
    grid_cols = pack.get("grid_cols", 4)
    grid_rows = pack["grid_rows"]
    row_starts = pack.get("row_starts", None)
    skip_text_blank = pack.get("skip_text_blank", False)

    if skip_text_blank:
        print("Skipping text-zone blanking (text is part of the sticker design)...")
        img_arr = np.array(img.convert("RGB"))
    else:
        text_fraction = pack.get("text_fraction", 0.28)
        print(
            f"Blanking text zones ({grid_cols}×{grid_rows} grid, "
            f"top {text_fraction * 100:.0f}% of each cell)..."
        )
        img_arr = np.array(img.convert("RGB"))
        img_arr = blank_text_zones(
            img_arr, grid_cols, grid_rows, text_fraction, row_starts=row_starts
        )
    img = Image.fromarray(img_arr, "RGB")

    # Step 2: Remove white background
    threshold = pack.get("threshold", 240)
    print(f"Removing white background (threshold={threshold})...")
    img_transparent = remove_white_background(img, threshold=threshold)

    # Step 3: Extract stickers and save
    sticker_names = pack["names"]
    use_grid_crop = pack.get("use_grid_crop", False)
    uniform_cols = pack.get("uniform_cols", False)
    col_starts = pack.get("col_starts", None)
    row_col_starts = pack.get("row_col_starts", None)

    if use_grid_crop:
        # Grid-based extraction: one sticker per cell, reading order
        print(
            f"Extracting stickers via grid crop "
            f"({grid_cols}×{grid_rows} = {grid_cols * grid_rows} cells)..."
        )
        stickers = list(
            extract_grid_cells(
                img_transparent,
                grid_cols,
                grid_rows,
                row_starts=row_starts,
                uniform_cols=uniform_cols,
                col_starts=col_starts,
                row_col_starts=row_col_starts,
            )
        )
        print(f"Extracted {len(stickers)} stickers")
        for i, sticker in enumerate(stickers):
            name = (
                sticker_names[i] if i < len(sticker_names) else f"sticker_{i + 1:02d}"
            )
            output_path = os.path.join(output_dir, f"{name}.png")
            sticker.save(output_path, "PNG")
            print(f"  Saved: {output_path}")
        print(f"\nDone! {len(stickers)} stickers saved to {output_dir}")
    else:
        # Blob-detection extraction (default for uniform sheets)
        print("Finding individual stickers via blob detection...")
        bboxes = find_sticker_bboxes(img_transparent, min_size=80, grid_rows=grid_rows)
        print(f"Found {len(bboxes)} stickers")
        for i, bbox in enumerate(bboxes):
            name = (
                sticker_names[i] if i < len(sticker_names) else f"sticker_{i + 1:02d}"
            )
            sticker = crop_and_resize(img_transparent, bbox)
            output_path = os.path.join(output_dir, f"{name}.png")
            sticker.save(output_path, "PNG")
            print(f"  Saved: {output_path}")
        print(f"\nDone! {len(bboxes)} stickers saved to {output_dir}")


if __name__ == "__main__":
    main()
