#!/usr/bin/env python3
"""Annotate v1.8 top-down with all features including v1.8 detail pass."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

# Coordinates in BLOCK coords (Z increases going down in the rendered image);
# the renderer uses (x, z) -> image (x*2, z*2) on a half-scale 1024x976 image.
ANNOTATIONS = [
    # === v1.8 NEW annotations ===
    {"x": 222, "z": 285, "label": "Reflecting Pool 中央水池 (NEW)", "color": (60, 90, 180), "size": 26},
    {"x": 88, "z": 168, "label": "Bus Terminus + Shuttles (NEW)", "color": (200, 70, 70), "size": 22},
    {"x": 280, "z": 504, "label": "South Bus Loop (NEW)", "color": (200, 70, 70), "size": 20},
    {"x": 140, "z": 280, "label": "Bus Stop", "color": (220, 50, 50), "size": 9},
    {"x": 300, "z": 280, "label": "Bus Stop", "color": (220, 50, 50), "size": 9},
    {"x": 440, "z": 200, "label": "Bus Stop", "color": (220, 50, 50), "size": 9},
    {"x": 640, "z": 200, "label": "Bus Stop", "color": (220, 50, 50), "size": 9},
    {"x": 250, "z": 510, "label": "Bus Stop", "color": (220, 50, 50), "size": 9},
    {"x": 660, "z": 300, "label": "Swim Pool 游泳池 + Lanes (NEW)", "color": (100, 200, 255), "size": 24},
    {"x": 645, "z": 240, "label": "Sports Field (NEW track lines)", "color": (50, 200, 50), "size": 18},
    {"x": 222, "z": 230, "label": "Sundial (red + stepped base)", "color": (255, 80, 80), "size": 18},
    {"x": 230, "z": 232, "label": "Statue Trio", "color": (255, 215, 0), "size": 9},

    # === Highlights of the campus pathway network ===
    {"x": 320, "z": 295, "label": "Central Spine (NEW path)", "color": (160, 160, 160), "size": 14},
    {"x": 220, "z": 250, "label": "Atrium Path", "color": (160, 160, 160), "size": 9},
    {"x": 480, "z": 240, "label": "Library Path", "color": (160, 160, 160), "size": 9},

    # Sakura / oak avenues
    {"x": 150, "z": 250, "label": "Sakura Avenue", "color": (255, 182, 193), "size": 14},
    {"x": 290, "z": 250, "label": "Sakura Avenue", "color": (255, 182, 193), "size": 14},
    {"x": 470, "z": 220, "label": "Tree-lined", "color": (50, 130, 30), "size": 9},
    {"x": 620, "z": 280, "label": "Tree-lined", "color": (50, 130, 30), "size": 9},
    {"x": 540, "z": 905, "label": "Coastal Sakura Strip", "color": (255, 182, 193), "size": 18},

    # Plaza benches
    {"x": 165, "z": 305, "label": "Plaza", "color": (170, 170, 170), "size": 8},
    {"x": 275, "z": 305, "label": "Plaza", "color": (170, 170, 170), "size": 8},

    # Seaview Walkway balustrade upgrade
    {"x": 540, "z": 944, "label": "Balustrade + Lamps", "color": (255, 255, 200), "size": 14},

    # Helipad
    {"x": 480, "z": 205, "label": "Helipad H (NEW)", "color": (255, 255, 255), "size": 10},

    # === Existing landmarks (kept) ===
    {"x": 220, "z": 160, "label": "Academic Dome", "color": (255, 215, 0), "size": 26},
    {"x": 222, "z": 230, "label": "Sundial (RED 火鸟)", "color": (255, 80, 80), "size": 26},
    {"x": 220, "z": 240, "label": "Fountain", "color": (255, 215, 0), "size": 20},
    {"x": 50, "z": 50, "label": "Seaview Walkway", "color": (135, 206, 250), "size": 30},
    {"x": 130, "z": 100, "label": "Library", "color": (255, 215, 0), "size": 26},
    {"x": 220, "z": 200, "label": "Atrium", "color": (255, 215, 0), "size": 20},
    {"x": 170, "z": 305, "label": "Armillary Sphere 浑天仪", "color": (255, 215, 0), "size": 18},
    {"x": 320, "z": 480, "label": "Shaw Auditorium 邵逸夫演艺中心", "color": (255, 215, 0), "size": 22},
    {"x": 550, "z": 60, "label": "Coastal Marine Lab 海岸海洋实验室", "color": (100, 200, 255), "size": 22},

    # Major buildings
    {"x": 184, "z": 626, "label": "LSK Business (NEW)", "color": (220, 220, 220), "size": 12},
    {"x": 302, "z": 460, "label": "Cheng Yu Tung (NEW)", "color": (220, 220, 220), "size": 12},
    {"x": 165, "z": 372, "label": "Lo Ka Chung (NEW)", "color": (220, 220, 220), "size": 12},
    {"x": 290, "z": 520, "label": "Innovation (NEW)", "color": (220, 220, 220), "size": 12},
    {"x": 340, "z": 510, "label": "Research 2 (NEW)", "color": (220, 220, 220), "size": 12},
    {"x": 288, "z": 398, "label": "Jockey Ent Ctr (NEW)", "color": (220, 220, 220), "size": 12},

    # Existing
    {"x": 210, "z": 185, "label": "Academic Building", "color": (220, 220, 220), "size": 11},
    {"x": 230, "z": 220, "label": "LG Complex", "color": (220, 220, 220), "size": 10},
]


def main():
    src = f"{WORKDIR}/worlds/final/hkust_topdown_v1.8.png"
    img = Image.open(src)
    print(f"Image size: {img.size}")
    draw = ImageDraw.Draw(img)

    try:
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
        font_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 9)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Renderer scale = 1:2 (one image px = 0.5 block). Plus offset (0,0).
    sx = img.size[0] / 816
    sz = img.size[1] / 976

    for a in ANNOTATIONS:
        # resize-aware mapping
        px = int(a["x"] * sx)
        py = int(a["z"] * sz)
        sz_font = font_large if a["size"] >= 18 else (font_med if a["size"] >= 10 else font_small)
        # Dot
        draw.ellipse(
            [px - 3, py - 3, px + 3, py + 3],
            fill=a["color"], outline=(0, 0, 0), width=1
        )
        # Label
        tx = px + 8
        ty = py - 8
        # Black outline + colored text
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            col = a["color"] if (ox, oy) == (0, 0) else (0, 0, 0)
            draw.text(
                (tx + ox, ty + oy),
                a["label"], font=sz_font, fill=col
            )

    img.save(f"{WORKDIR}/worlds/final/hkust_topdown_v1.8.png")
    print(f"Saved annotated to {WORKDIR}/worlds/final/hkust_topdown_v1.8.png")


if __name__ == "__main__":
    main()
