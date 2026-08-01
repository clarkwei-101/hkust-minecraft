"""
Generate annotated top-down preview of HKUST Minecraft world.

Reads the Arnis-generated top-down PNG and overlays 4 pin markers
for the hand-built landmarks, plus a legend and title.
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

PROJECT = Path(__file__).parent.parent
INPUT_PNG = PROJECT / "previews/hkust-topdown.png"
OUTPUT_PNG = PROJECT / "previews/hkust-topdown-annotated.png"

# Bounding box of the generated world
BBOX = {
    "min_lat": 22.3317768,
    "min_lng": 114.2617409,
    "max_lat": 22.3404248,
    "max_lng": 114.2695826,
}

# 4 hand-built landmarks: (name, lat, lng, color, marker_index)
LANDMARKS = [
    ("Academic Dome",     22.3375,    114.2645,    "#FF6B6B", 1),
    ("Circle of Time",    22.33752,   114.26299,   "#FFD93D", 2),
    ("One-World Fountain", 22.337746, 114.264462,  "#6BCB77", 3),
    ("Seaview Lookout",   22.3325,    114.2640,    "#4D96FF", 4),
]


def latlng_to_pixel(lat, lng, img_w, img_h):
    """Map lat/lng to image pixel coordinates."""
    x = (lng - BBOX["min_lng"]) / (BBOX["max_lng"] - BBOX["min_lng"]) * img_w
    # Image y-axis: 0 is top (max_lat), 1 is bottom (min_lat)
    y = (BBOX["max_lat"] - lat) / (BBOX["max_lat"] - BBOX["min_lat"]) * img_h
    return x, y


def draw_marker(draw, x, y, color, idx, label):
    """Draw a circular pin marker with label."""
    R = 18
    # Outer halo
    draw.ellipse([x - R - 6, y - R - 6, x + R + 6, y + R + 6], fill=(0, 0, 0, 80))
    # Pin body
    draw.ellipse([x - R, y - R, x + R, y + R], fill=color, outline="white", width=3)
    # Pin tip (downward triangle)
    draw.polygon([(x - 8, y + R - 2), (x + 8, y + R - 2), (x, y + R + 12)], fill=color, outline="white")
    # Index number
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except (OSError, IOError):
        font = ImageFont.load_default()
        small = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), str(idx), font=font)
    text_w = text_bbox[2] - text_bbox[0]
    text_h = text_bbox[3] - text_bbox[1]
    draw.text((x - text_w / 2, y - text_h / 2 - 2), str(idx), fill="white", font=font)
    # Label
    label_bbox = draw.textbbox((0, 0), label, font=small)
    lw = label_bbox[2] - label_bbox[0]
    lh = label_bbox[3] - label_bbox[1]
    # Label background pill
    pad = 6
    draw.rectangle(
        [x - lw / 2 - pad, y + R + 16, x + lw / 2 + pad, y + R + 16 + lh + pad],
        fill=(20, 20, 20, 220),
        outline=color,
        width=2,
    )
    draw.text((x - lw / 2, y + R + 16 + pad / 2), label, fill="white", font=small)


def main():
    img = Image.open(INPUT_PNG).convert("RGBA")
    w, h = img.size
    print(f"Loaded {INPUT_PNG.name}: {w}x{h}")

    # Overlay layer
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Draw 4 landmark markers
    for name, lat, lng, color, idx in LANDMARKS:
        x, y = latlng_to_pixel(lat, lng, w, h)
        print(f"  Pin {idx} '{name}' at pixel ({x:.0f}, {y:.0f})")
        draw_marker(draw, x, y, color, idx, name)

    # Composite
    img = Image.alpha_composite(img, overlay)

    # Add title banner (bottom)
    banner_h = 60
    banner = Image.new("RGBA", (w, banner_h), (0, 0, 0, 200))
    img.paste(banner, (0, h - banner_h), banner)
    title_draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
        legend_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        legend_font = ImageFont.load_default()
    title_draw.text((20, h - banner_h + 8), "HKUST Clear Water Bay — 1:1 Minecraft Recreation",
                    fill="white", font=title_font)
    title_draw.text((20, h - banner_h + 36), "Built with Arnis v3.0.0 · 4 hand-built landmarks",
                    fill=(180, 180, 180), font=legend_font)

    # Add legend (top-left)
    legend_items = [(name, color) for name, _, _, color, _ in LANDMARKS]
    legend_w = 220
    legend_h = 30 + 26 * len(legend_items)
    legend = Image.new("RGBA", (legend_w, legend_h), (0, 0, 0, 180))
    img.paste(legend, (12, 12), legend)
    legend_draw = ImageDraw.Draw(img)
    legend_draw.text((20, 18), "Landmarks", fill="white", font=title_font)
    for i, (name, color) in enumerate(legend_items):
        y = 48 + i * 26
        # Color swatch
        legend_draw.ellipse([20, y + 2, 36, y + 18], fill=color, outline="white", width=2)
        legend_draw.text((46, y + 1), name, fill="white", font=legend_font)

    # Save
    img.convert("RGB").save(OUTPUT_PNG, "PNG", optimize=True)
    print(f"Saved {OUTPUT_PNG.name} ({OUTPUT_PNG.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
