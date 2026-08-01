"""
HKUST landmark .schem generator.

Generates Sponge Schematic v3 JSON files as blueprint references
for the 4 hand-built HKUST landmarks. These can be imported via
WorldEdit BE addon /schem load command.

Run:
    python3 landmarks/generate_schems.py

Outputs:
    - 01-academic-dome.schem
    - 02-circle-of-time-sundial.schem
    - 03-one-world-fountain.schem
    - 04-seaview-railings.schem
"""
import json
import math
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

# Minecraft Bedrock block state IDs (部分常用)
BLOCKS = {
    "air":                ("minecraft", "air", 0),
    "polished_granite":   ("minecraft", "polished_granite", 0),
    "polished_andesite_pillar": ("minecraft", "polished_andesite_pillar", 0),
    "white_concrete":     ("minecraft", "white_concrete", 0),
    "light_blue_stained_glass": ("minecraft", "light_blue_stained_glass", 0),
    "iron_fence":         ("minecraft", "iron_bars", 0),
    "polished_diorite":   ("minecraft", "polished_diorite", 0),
    "black_concrete":     ("minecraft", "black_concrete", 0),
    "brown_stained_glass_pane": ("minecraft", "brown_stained_glass_pane", 0),
    "calcite":            ("minecraft", "calcite", 0),
    "blue_concrete":      ("minecraft", "blue_concrete", 0),
    "water":              ("minecraft", "water", 0),
    "quartz_pillar":      ("minecraft", "quartz_pillar", 0),
    "sea_lantern":        ("minecraft", "sea_lantern", 0),
    "soul_lantern":       ("minecraft", "soul_lantern", 0),
    "dark_oak_fence":     ("minecraft", "dark_oak_fence", 0),
    "oak_slab":           ("minecraft", "oak_slab", 0),
    "spruce_slab":        ("minecraft", "spruce_slab", 0),
    "polished_granite_slab": ("minecraft", "polished_granite_slab", 0),
}


def make_schem_block(x, y, z, block_name):
    """Create a Sponge Schematic v3 block entry."""
    namespaced, block, state = BLOCKS[block_name]
    return {
        "pos": [x, y, z],
        "state": 0,  # simplified - real schem encodes palette index
        "nbt": {
            "block_name": f"minecraft:{block}",
        },
    }


def build_academic_dome():
    """1. 学术楼圆顶 — 半径 20, 高度 25"""
    blocks = []
    RADIUS = 20
    HEIGHT = 25
    for x in range(-RADIUS, RADIUS + 1):
        for y in range(HEIGHT + 1):
            for z in range(-RADIUS, RADIUS + 1):
                r = math.sqrt(x * x + z * z)
                if r > RADIUS:
                    continue
                # 基座 + 立柱区 (y <= 8)
                if y <= 8:
                    # 外缘墙
                    if r >= RADIUS - 1:
                        if (abs(x) == RADIUS or abs(z) == RADIUS) and (abs(x) < RADIUS - 2 or abs(z) < RADIUS - 2):
                            blocks.append(make_schem_block(x, y, z, "polished_andesite_pillar"))
                        else:
                            blocks.append(make_schem_block(x, y, z, "polished_granite"))
                # 穹顶区 (半球)
                elif y > 8:
                    dy = y - 8
                    if r <= math.sqrt(RADIUS * RADIUS - dy * dy):
                        if r >= math.sqrt(RADIUS * RADIUS - dy * dy) - 0.5:
                            blocks.append(make_schem_block(x, y, z, "white_concrete"))
                        # 内部地面
                        elif y == 9 and r < RADIUS - 1:
                            blocks.append(make_schem_block(x, y, z, "polished_diorite"))
                # 天窗
                if y == 24 and r < 4:
                    blocks.append(make_schem_block(x, y, z, "light_blue_stained_glass"))
    return {
        "name": "academic-dome",
        "size": [2 * RADIUS + 1, HEIGHT + 1, 2 * RADIUS + 1],
        "blocks": blocks,
        "origin": [0, 0, 0],
    }


def build_circle_of_time():
    """2. 时间之轮日晷 — 半径 4, 高度 7"""
    blocks = []
    RADIUS = 4
    for x in range(-RADIUS, RADIUS + 1):
        for y in range(7):
            for z in range(-RADIUS, RADIUS + 1):
                r = math.sqrt(x * x + z * z)
                if r > RADIUS:
                    continue
                # 3 层基座
                if r < RADIUS - 1:
                    blocks.append(make_schem_block(x, y, z, "polished_diorite"))
                # 12 个晷面刻度
                if y == 2 and r > 2.5 and r < 3:
                    angle = math.degrees(math.atan2(z, x))
                    if int(round(angle / 30)) % 2 == 0:
                        blocks.append(make_schem_block(x, y, z, "black_concrete"))
                # 中央晷针
                if x == 0 and z == 0 and 3 <= y <= 6:
                    blocks.append(make_schem_block(x, y, z, "calcite"))
                if x == 0 and y == 7 and z == 0:
                    blocks.append(make_schem_block(x, y, z, "brown_stained_glass_pane"))
    return {
        "name": "circle-of-time-sundial",
        "size": [2 * RADIUS + 1, 8, 2 * RADIUS + 1],
        "blocks": blocks,
        "origin": [0, 0, 0],
    }


def build_one_world_fountain():
    """3. 天一泉 — 半径 6, 高度 6"""
    blocks = []
    RADIUS = 6
    for x in range(-RADIUS, RADIUS + 1):
        for y in range(6):
            for z in range(-RADIUS, RADIUS + 1):
                r = math.sqrt(x * x + z * z)
                if r > RADIUS:
                    continue
                # 外圈石环
                if r >= RADIUS - 1:
                    blocks.append(make_schem_block(x, y, z, "polished_diorite"))
                # 池水
                elif y == 0 and r < RADIUS - 1:
                    blocks.append(make_schem_block(x, y, z, "water"))
                # 池内壁
                elif r >= RADIUS - 2 and y == 0:
                    blocks.append(make_schem_block(x, y, z, "blue_concrete"))
                # 中央喷泉柱
                if x == 0 and z == 0 and y < 5:
                    blocks.append(make_schem_block(x, y, z, "quartz_pillar"))
                if x == 0 and y == 5 and z == 0:
                    blocks.append(make_schem_block(x, y, z, "sea_lantern"))
                # 四角灯
                if abs(x) == 4 and abs(z) == 4 and y == 0:
                    blocks.append(make_schem_block(x, y, z, "soul_lantern"))
    return {
        "name": "one-world-fountain",
        "size": [2 * RADIUS + 1, 6, 2 * RADIUS + 1],
        "blocks": blocks,
        "origin": [0, 0, 0],
    }


def build_seaview_railings():
    """4. 清水湾海边栏杆 + 观景台 — 长 600m, 高 3"""
    blocks = []
    LENGTH = 600
    HALF = LENGTH // 2
    for x in range(-HALF, HALF + 1):
        for y in range(3):
            for z in range(-2, 3):
                # 主栏杆线
                if z == 0 and y == 1:
                    blocks.append(make_schem_block(x, y, z, "dark_oak_fence"))
                # 每 20m 一根立柱
                if x % 20 == 0 and z == 0 and y == 2:
                    blocks.append(make_schem_block(x, y, z, "dark_oak_fence"))
                # 路径地砖
                if z < 0 and y == 0:
                    blocks.append(make_schem_block(x, y, z, "spruce_slab"))
                # 3 个观景台 (z = -200, 0, 200)
                for cz in [-200, 0, 200]:
                    if abs(x - cz) < 4 and abs(x - cz) > 1 and z == 0 and y == 0:
                        blocks.append(make_schem_block(x, y, z, "polished_granite_slab"))
                    if abs(x - cz) == 2 and z == 0 and y == 1:
                        blocks.append(make_schem_block(x, y, z, "oak_slab"))
    return {
        "name": "seaview-railings",
        "size": [LENGTH + 1, 3, 5],
        "blocks": blocks,
        "origin": [0, 0, 0],
    }


def write_schem(spec, filename):
    """Write Sponge Schematic v3 JSON file."""
    schem = {
        "version": 3,
        "data_version": 3837,  # MC 1.21
        "name": spec["name"],
        "size": spec["size"],
        "origin": spec["origin"],
        "palette": {
            "default": "minecraft:air",
            "blocks": list(set(
                f"minecraft:{BLOCKS[block][1]}"
                for entry in spec["blocks"]
                for block in [entry["nbt"]["block_name"].replace("minecraft:", "")]
            )),
        },
        "block_entities": [],
        "entities": [],
        "blocks": spec["blocks"],
    }
    output_path = OUTPUT_DIR / filename
    output_path.write_text(json.dumps(schem, indent=2))
    print(f"  Wrote {output_path.name}: {len(spec['blocks'])} blocks, size {spec['size']}")


if __name__ == "__main__":
    print(f"Generating HKUST landmark .schem files in {OUTPUT_DIR}")
    print()
    print("[1/4] Academic Building Dome...")
    write_schem(build_academic_dome(), "01-academic-dome.schem")
    print("[2/4] Circle of Time Sundial...")
    write_schem(build_circle_of_time(), "02-circle-of-time-sundial.schem")
    print("[3/4] One-World Fountain...")
    write_schem(build_one_world_fountain(), "03-one-world-fountain.schem")
    print("[4/4] Seaview Railings...")
    write_schem(build_seaview_railings(), "04-seaview-railings.schem")
    print()
    print("Done. Load these in WorldEdit BE with /schem load ")
