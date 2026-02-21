#!/usr/bin/env python3
"""
Split a sticker sheet into individual stickers with transparent backgrounds.
Each sticker is saved as a separate 512x512 PNG file.
"""

import os
import numpy as np
from PIL import Image


def remove_white_background(img, threshold=240):
    """Convert white/near-white pixels to transparent."""
    img = img.convert("RGBA")
    data = np.array(img)

    # Find pixels where R, G, B are all above the threshold (white-ish)
    white_mask = (
        (data[:, :, 0] > threshold)
        & (data[:, :, 1] > threshold)
        & (data[:, :, 2] > threshold)
    )

    # Set alpha to 0 for white pixels
    data[white_mask, 3] = 0

    return Image.fromarray(data)


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


def main():
    # ── Configure input/output per sticker pack ──
    pack_name = os.environ.get("STICKER_PACK", "Jesus Christ – Faith & Peace")

    # Pack-specific settings
    PACKS = {
        "chubby mochi cat": {
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
    }

    pack = PACKS[pack_name]
    input_path = os.path.join(os.path.dirname(__file__), pack_name, pack["input_file"])
    output_dir = os.path.join(os.path.dirname(__file__), pack_name, "split")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading image: {input_path}")
    img = Image.open(input_path)
    print(f"Image size: {img.size}")

    # Step 1: Remove white background
    threshold = pack.get("threshold", 240)
    print(f"Removing white background (threshold={threshold})...")
    img_transparent = remove_white_background(img, threshold=threshold)

    # Step 2: Find individual stickers
    print("Finding individual stickers...")
    bboxes = find_sticker_bboxes(
        img_transparent, min_size=80, grid_rows=pack["grid_rows"]
    )
    print(f"Found {len(bboxes)} stickers")

    # Step 3: Crop, resize, and save each sticker
    sticker_names = pack["names"]

    for i, bbox in enumerate(bboxes):
        name = sticker_names[i] if i < len(sticker_names) else f"sticker_{i + 1:02d}"
        sticker = crop_and_resize(img_transparent, bbox)
        output_path = os.path.join(output_dir, f"{name}.png")
        sticker.save(output_path, "PNG")
        print(f"  Saved: {output_path}")

    print(f"\nDone! {len(bboxes)} stickers saved to {output_dir}")


if __name__ == "__main__":
    main()
