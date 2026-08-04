"""
Generate v1.3 annotated top-down preview showing 8 landmarks + 14 manual buildings.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).parent.parent
INPUT_PNG = PROJECT / "previews/hkust-topdown-v1.3.png"
OUTPUT_PNG = PROJECT / "worlds/final/hkust_topdown_v1.3.png"

# World bounds (from Arnis)
WORLD_X = 816
WORLD_Z = 976

# Map of MC coords to pixel coords (image is 204x244 from render_topdown --scale 4)
def mc_to_pixel(mc_x, mc_z, img_w, img_h):
    x = (mc_x / WORLD_X) * img_w
    y = (mc_z / WORLD_Z) * img_h
    return x, y

# Load manual buildings
with open(PROJECT / "data/manual_buildings.json") as f:
    manual = json.load(f)

# All 22 features
LANDMARKS_8 = [
    ("Academic Building Dome", 200, 500, "#FF6B6B"),
    ("Circle of Time", 185, 530, "#FFD93D"),
    ("One-World Fountain", 279, 663, "#6BCB77"),
    ("Seaview Walkway", 480, 380, "#4D96FF"),
    ("HKUST Library", 130, 580, "#A66CFF"),
    ("HKUST Atrium", 240, 560, "#FF9F40"),
    ("Lecture Hall LG7", 320, 620, "#FF66B3"),
    ("Underpass", 380, 450, "#A0A0A0"),
]

# Combine all features
FEATURES = LANDMARKS_8 + [(b["name"], b["mc_x"], b["mc_z"], "#00D4FF") for b in manual]

# Color legend
COLORS = {
    "Academic Building Dome": "#FF6B6B",
    "Circle of Time": "#FFD93D",
    "One-World Fountain": "#6BCB77",
    "Seaview Walkway": "#4D96FF",
    "HKUST Library": "#A66CFF",
    "HKUST Atrium": "#FF9F40",
    "Lecture Hall LG7": "#FF66B3",
    "Underpass": "#A0A0A0",
}

# Manual buildings get cyan
for b in manual:
    COLORS[b["name"]] = "#00D4FF"


def draw_marker(draw, x, y, color, label, small_font):
    """Draw a pin marker with label."""
    R = 8
    # Outer halo
    draw.ellipse([x - R - 4, y - R - 4, x + R + 4, y + R + 4], fill=(0, 0, 0, 100))
    # Pin body
    draw.ellipse([x - R, y - R, x + R, y + R], fill=color, outline="white", width=1)
    # Label
    label_bbox = draw.textbbox((0, 0), label, font=small_font)
    lw = label_bbox[2] - label_bbox[0]
    lh = label_bbox[3] - label_bbox[1]
    # Label position (alternate above/below to avoid overlap)
    if y < 30:
        ly = y + R + 4
    else:
        ly = y - R - lh - 4
    draw.rectangle(
        [x - lw / 2 - 3, ly, x + lw / 2 + 3, ly + lh + 3],
        fill=(20, 20, 20, 200),
        outline=color,
        width=1,
    )
    draw.text((x - lw / 2, ly + 1), label, fill="white", font=small_font)


def main():
    img = Image.open(INPUT_PNG).convert("RGBA")
    w, h = img.size
    print(f"Loaded {INPUT_PNG.name}: {w}x{h}")

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        small = ImageFont.load_default()
        title_font = ImageFont.load_default()

    # Draw all features
    for name, mc_x, mc_z, color in FEATURES:
        x, y = mc_to_pixel(mc_x, mc_z, w, h)
        draw_marker(draw, x, y, color, name, small)

    img = Image.alpha_composite(img, overlay)

    # Title banner
    banner_h = 32
    banner = Image.new("RGBA", (w, banner_h), (0, 0, 0, 200))
    img.paste(banner, (0, h - banner_h), banner)
    title_draw = ImageDraw.Draw(img)
    title_draw.text((10, h - banner_h + 4), "HKUST v1.3 — 8 Landmarks + 14 Manual Buildings",
                    fill="white", font=title_font)

    img.convert("RGB").save(OUTPUT_PNG, "PNG", optimize=True)
    print(f"Saved {OUTPUT_PNG.name} ({OUTPUT_PNG.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()