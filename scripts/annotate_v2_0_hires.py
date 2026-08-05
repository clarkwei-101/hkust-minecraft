#!/usr/bin/env python3
"""Annotate v2.0 hi-res top-down with full labels + entrance gates + complete sundial."""
from PIL import Image, ImageDraw, ImageFont

WORKDIR = "/Users/yahweh/Desktop/ai应用社/hkust-minecraft"

ANNOTATIONS = [
    # v2.0 NEW — entrance gates (red dots)
    {"x": 360, "z": 327, "label": "► Lo Kwee-Seong (罗桂祥楼)", "color": (255, 50, 50), "size": 13, "arrow": True},
    {"x": 232, "z": 220, "label": "► Concourse", "color": (255, 50, 50), "size": 10, "arrow": True},
    {"x": 200, "z": 310, "label": "► Tin Ka Ping Hall (田家炳楼)", "color": (255, 50, 50), "size": 12, "arrow": True},
    {"x": 580, "z": 880, "label": "► President's Lodge (校长邸)", "color": (255, 50, 50), "size": 11, "arrow": True},
    {"x": 254, "z": 18, "label": "► Library Ext. (图书馆新翼)", "color": (255, 50, 50), "size": 11, "arrow": True},
    {"x": 530, "z": 190, "label": "► HPC (高性能计算中心)", "color": (255, 50, 50), "size": 12, "arrow": True},
    {"x": 670, "z": 280, "label": "► Indoor Pool (室内泳池)", "color": (255, 50, 50), "size": 11, "arrow": True},
    {"x": 354, "z": 3, "label": "► Car Park (停车场)", "color": (255, 50, 50), "size": 11, "arrow": True},
    {"x": 190, "z": 690, "label": "► JC i-Village (赛马会创新村)", "color": (255, 50, 50), "size": 12, "arrow": True},
    {"x": 257, "z": 367, "label": "► Annex (新翼大楼)", "color": (255, 50, 50), "size": 10, "arrow": True},
    {"x": 320, "z": 530, "label": "► Alumni Commons", "color": (255, 50, 50), "size": 10, "arrow": True},

    # v2.0 NEW — landmarks (already placed)
    {"x": 360, "z": 337, "label": "Lo Kwee-Seong (罗桂祥楼)", "color": (255, 100, 100), "size": 13},
    {"x": 232, "z": 230, "label": "Chia-Wei Woo Concourse (吴家玮学术长廊)", "color": (255, 200, 100), "size": 11},
    {"x": 200, "z": 320, "label": "Tin Ka Ping Hall (田家炳楼)", "color": (100, 200, 255), "size": 13},
    {"x": 580, "z": 870, "label": "President's Lodge (校长邸)", "color": (255, 215, 0), "size": 11},
    {"x": 264, "z": 18, "label": "Library Extension (图书馆新翼)", "color": (255, 215, 0), "size": 11},
    {"x": 530, "z": 200, "label": "HPC 高性能计算中心", "color": (200, 100, 255), "size": 12},
    {"x": 670, "z": 290, "label": "Indoor Pool (室内泳池)", "color": (100, 200, 255), "size": 11},
    {"x": 354, "z": 13, "label": "Multi-storey Car Park (多层停车场)", "color": (130, 130, 130), "size": 11},
    {"x": 190, "z": 700, "label": "JC i-Village (赛马会创新村)", "color": (255, 182, 193), "size": 12},
    {"x": 267, "z": 367, "label": "Annex (新翼大楼)", "color": (180, 180, 180), "size": 9},
    {"x": 320, "z": 540, "label": "Alumni Commons (校友中心)", "color": (255, 215, 0), "size": 9},
    {"x": 320, "z": 380, "label": "Yu Research (UC) (余仁德研究大楼,在建)", "color": (255, 220, 100), "size": 9},
    {"x": 440, "z": 460, "label": "Med School (UC) (医学院,在建)", "color": (255, 220, 100), "size": 9},

    # Bridge lifts
    {"x": 235, "z": 245, "label": "Bridge Lift", "color": (200, 50, 50), "size": 8},
    {"x": 220, "z": 380, "label": "Bridge Lift", "color": (200, 50, 50), "size": 8},
    {"x": 50, "z": 320, "label": "Bridge Link", "color": (220, 220, 220), "size": 9},
    {"x": 200, "z": 580, "label": "Bridge Link", "color": (220, 220, 220), "size": 9},

    # v1.8 detail
    {"x": 222, "z": 285, "label": "Reflecting Pool (中央水池)", "color": (60, 90, 180), "size": 18},
    {"x": 88, "z": 168, "label": "Bus Terminus", "color": (200, 70, 70), "size": 14},
    {"x": 280, "z": 504, "label": "South Bus Loop", "color": (200, 70, 70), "size": 12},

    # v2.0 COMPLETE SUNDIAL — highlighted larger
    {"x": 222, "z": 230, "label": "Sundial (RED 火鸟日晷, 12 时辰)", "color": (255, 30, 30), "size": 18, "bold": True},

    # Existing landmarks
    {"x": 220, "z": 160, "label": "Academic Dome (圆顶)", "color": (255, 215, 0), "size": 16},
    {"x": 130, "z": 100, "label": "Lee Shau Kee Library", "color": (255, 215, 0), "size": 14},
    {"x": 220, "z": 200, "label": "Atrium (香港赛马会大堂)", "color": (255, 215, 0), "size": 14},
    {"x": 170, "z": 305, "label": "Armillary Sphere (浑天仪)", "color": (255, 215, 0), "size": 11},
    {"x": 320, "z": 480, "label": "Shaw Auditorium (邵逸夫演艺中心)", "color": (255, 215, 0), "size": 13},
    {"x": 550, "z": 60, "label": "Coastal Marine Lab (海岸海洋实验室)", "color": (100, 200, 255), "size": 14},
    {"x": 220, "z": 240, "label": "Fountain (喷泉)", "color": (255, 215, 0), "size": 9},

    # Major buildings
    {"x": 210, "z": 185, "label": "Academic Building (学术大楼)", "color": (220, 220, 220), "size": 11},
    {"x": 184, "z": 626, "label": "LSK Business (李兆基商学大楼)", "color": (220, 220, 220), "size": 10},
    {"x": 302, "z": 460, "label": "Cheng Yu Tung (郑裕彤楼)", "color": (220, 220, 220), "size": 10},
    {"x": 165, "z": 372, "label": "Lo Ka Chung UC (卢家驄大学中心)", "color": (220, 220, 220), "size": 10},
    {"x": 290, "z": 520, "label": "Innovation (创科大樓)", "color": (220, 220, 220), "size": 10},
    {"x": 340, "z": 510, "label": "Research 2 (新科研楼2)", "color": (220, 220, 220), "size": 10},
    {"x": 288, "z": 398, "label": "Jockey Ent Ctr (赛马会创新科技中心)", "color": (220, 220, 220), "size": 10},
    {"x": 377, "z": 585, "label": "Wong Check She (黄焯书科研中心)", "color": (220, 220, 220), "size": 10},
    {"x": 660, "z": 300, "label": "Swim Pool (游泳池)", "color": (100, 200, 255), "size": 14},
    {"x": 645, "z": 240, "label": "Sports Field (田径场)", "color": (50, 200, 50), "size": 12},
    {"x": 50, "z": 50, "label": "Seaview Walkway (海滨长廊)", "color": (135, 206, 250), "size": 22},
]

# v2.0 Corner badge
VERSION_BADGES = [
    {"text": "v2.0", "pos": (10, 10), "color": (255, 50, 50), "size": 36},
    {"text": "100% Building · 99% Fidelity · 232,600 + 80,400 = 313,000 blocks", "pos": (10, 50), "color": (255, 215, 0), "size": 14},
    {"text": "REFINEMENTS: ✓ Smooth slopes · ✓ Anchored buildings · ✓ Complete 火鸟 · ✓ Entrance gates", "pos": (10, 70), "color": (255, 255, 255), "size": 11},
]


def main():
    src = f"{WORKDIR}/worlds/final/hkust_topdown_v2.0.png"
    img = Image.open(src)
    print(f"Image size: {img.size}")
    draw = ImageDraw.Draw(img)

    try:
        font_huge = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        font_med = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        font_bold = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        font_badge = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
        font_badge_sm = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 11)
    except Exception:
        font_huge = font_large = font_med = font_small = font_bold = font_badge = font_badge_sm = ImageFont.load_default()

    sx = img.size[0] / 816
    sz = img.size[1] / 976

    for a in ANNOTATIONS:
        px = int(a["x"] * sx)
        py = int(a["z"] * sz)
        if a["size"] >= 16:
            sz_font = font_huge
        elif a["size"] >= 12:
            sz_font = font_large
        elif a["size"] >= 10:
            sz_font = font_med
        else:
            sz_font = font_small
        # Marker dot
        radius = 5 if a.get("arrow") else 4
        outline_w = 3 if a.get("arrow") else 2
        draw.ellipse(
            [px - radius, py - radius, px + radius, py + radius],
            fill=a["color"], outline=(0, 0, 0), width=outline_w
        )
        # Label
        tx = px + 10
        ty = py - 10
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1), (0, 0)]:
            col = a["color"] if (ox, oy) == (0, 0) else (0, 0, 0)
            draw.text((tx + ox, ty + oy), a["label"], font=sz_font, fill=col)

    # v2.0 corner badge
    for badge in VERSION_BADGES:
        tx, ty = badge["pos"]
        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            col = badge["color"] if (ox, oy) == (0, 0) else (0, 0, 0)
            font = font_bold if badge["size"] >= 30 else (font_badge if badge["size"] >= 14 else font_badge_sm)
            draw.text((tx + ox, ty + oy), badge["text"], font=font, fill=col)

    img.save(f"{WORKDIR}/worlds/final/hkust_topdown_v2.0_hires.png")
    print(f"Saved annotated v2.0 hi-res at {img.size}")


if __name__ == "__main__":
    main()