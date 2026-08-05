#!/usr/bin/env python3
"""Annotate v1.9 top-down with new buildings + all v1.8 features."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

ANNOTATIONS = [
    # === v1.9 NEW buildings ===
    {"x": 360, "z": 337, "label": "Lo Kwee-Seong (罗桂祥楼) (NEW)", "color": (255, 100, 100), "size": 16},
    {"x": 232, "z": 230, "label": "Chia-Wei Woo Concourse 吴家玮学术长廊 (NEW)", "color": (255, 200, 100), "size": 12},
    {"x": 200, "z": 320, "label": "Tin Ka Ping Hall 田家炳楼 (NEW)", "color": (100, 200, 255), "size": 16},
    {"x": 580, "z": 870, "label": "President's Lodge 校长邸 (NEW)", "color": (255, 215, 0), "size": 14},
    {"x": 264, "z": 18, "label": "Library Extension (NEW)", "color": (255, 215, 0), "size": 12},
    {"x": 530, "z": 200, "label": "HPC 高性能计算中心 (NEW)", "color": (200, 100, 255), "size": 14},
    {"x": 670, "z": 290, "label": "Indoor Pool (NEW)", "color": (100, 200, 255), "size": 12},
    {"x": 354, "z": 13, "label": "Multi-storey Car Park (NEW)", "color": (130, 130, 130), "size": 12},
    {"x": 190, "z": 700, "label": "JC i-Village 赛马会创新村 (NEW)", "color": (255, 182, 193), "size": 14},
    {"x": 267, "z": 367, "label": "Annex (NEW)", "color": (180, 180, 180), "size": 9},
    {"x": 320, "z": 540, "label": "Alumni Commons (NEW)", "color": (255, 215, 0), "size": 9},
    {"x": 320, "z": 380, "label": "Yu Research (UC) (NEW)", "color": (255, 220, 100), "size": 10},
    {"x": 440, "z": 460, "label": "Med School (UC) (NEW)", "color": (255, 220, 100), "size": 10},

    # === Bridge Link ===
    {"x": 235, "z": 245, "label": "Bridge Lift", "color": (200, 50, 50), "size": 8},
    {"x": 220, "z": 380, "label": "Bridge Lift", "color": (200, 50, 50), "size": 8},
    {"x": 50, "z": 320, "label": "Bridge", "color": (220, 220, 220), "size": 8},
    {"x": 200, "z": 580, "label": "Bridge", "color": (220, 220, 220), "size": 8},

    # === v1.8 detail annotations (kept) ===
    {"x": 222, "z": 285, "label": "Reflecting Pool 中央水池", "color": (60, 90, 180), "size": 22},
    {"x": 88, "z": 168, "label": "Bus Terminus", "color": (200, 70, 70), "size": 18},
    {"x": 280, "z": 504, "label": "South Bus Loop", "color": (200, 70, 70), "size": 14},

    # === Existing landmarks ===
    {"x": 220, "z": 160, "label": "Academic Dome", "color": (255, 215, 0), "size": 22},
    {"x": 222, "z": 230, "label": "Sundial (RED 火鸟)", "color": (255, 80, 80), "size": 22},
    {"x": 130, "z": 100, "label": "Library", "color": (255, 215, 0), "size": 22},
    {"x": 220, "z": 200, "label": "Atrium", "color": (255, 215, 0), "size": 16},
    {"x": 170, "z": 305, "label": "Armillary Sphere 浑天仪", "color": (255, 215, 0), "size": 14},
    {"x": 320, "z": 480, "label": "Shaw Auditorium", "color": (255, 215, 0), "size": 18},
    {"x": 550, "z": 60, "label": "Coastal Marine Lab", "color": (100, 200, 255), "size": 18},

    # === Major buildings ===
    {"x": 184, "z": 626, "label": "LSK Business", "color": (220, 220, 220), "size": 11},
    {"x": 302, "z": 460, "label": "Cheng Yu Tung", "color": (220, 220, 220), "size": 11},
    {"x": 165, "z": 372, "label": "Lo Ka Chung UC", "color": (220, 220, 220), "size": 11},
    {"x": 290, "z": 520, "label": "Innovation", "color": (220, 220, 220), "size": 11},
    {"x": 340, "z": 510, "label": "Research 2", "color": (220, 220, 220), "size": 11},
    {"x": 288, "z": 398, "label": "Jockey Ent Ctr", "color": (220, 220, 220), "size": 11},
    {"x": 660, "z": 300, "label": "Swim Pool", "color": (100, 200, 255), "size": 18},
    {"x": 645, "z": 240, "label": "Sports Field", "color": (50, 200, 50), "size": 14},
]


def main():
    src = f"{WORKDIR}/worlds/final/hkust_topdown_v1.9.png"
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

    sx = img.size[0] / 816
    sz = img.size[1] / 976

    for a in ANNOTATIONS:
        px = int(a["x"] * sx)
        py = int(a["z"] * sz)
        sz_font = font_large if a["size"] >= 18 else (font_med if a["size"] >= 10 else font_small)
        draw.ellipse(
            [px - 3, py - 3, px + 3, py + 3],
            fill=a["color"], outline=(0, 0, 0), width=1
        )
        tx = px + 8
        ty = py - 8
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            col = a["color"] if (ox, oy) == (0, 0) else (0, 0, 0)
            draw.text((tx + ox, ty + oy), a["label"], font=sz_font, fill=col)

    img.save(f"{WORKDIR}/worlds/final/hkust_topdown_v1.9.png")
    print(f"Saved annotated.")


if __name__ == "__main__":
    main()