#!/usr/bin/env python3
"""
v1.4 detail injector: paths, parking, trees, sports fields
Adds campus details around the manual buildings.
"""
import json
import sys
from pathlib import Path
from amulet import level as amulet_level
from amulet.api.block import Block
from amulet.utils import block_coords_to_chunk_coords

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC_MCWORLD = WORKDIR / "worlds/working/v1.4"
DST_MCWORLD = WORKDIR / "worlds/working/v1.4-detailed"
DETAILS_JSON = WORKDIR / "data/campus_details.json"


def make_block(block_id):
    """Return a Bedrock Block given a string identifier like 'minecraft:stone_bricks' or shorthand."""
    if ":" not in block_id:
        block_id = f"minecraft:{block_id}"
    namespace, base_name = block_id.split(":", 1)
    return Block(namespace, base_name)


def get_ground_y(level, x, z):
    """Return the Y of the highest non-air block at (x, z)."""
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    for y in range(120, 30, -1):
        b = level.get_version_block(x, y, z, dim, ver)
        if b[0].base_name != "air":
            return y
    return 60


def place_block(level, x, y, z, block):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    level.set_version_block(x, y, z, dim, ver, block)


def place_block_above(level, x, z, dy, block):
    """Place a block dy above the ground at (x, z)."""
    gy = get_ground_y(level, x, z)
    place_block(level, x, gy + dy, z, block)


def draw_path(level, x1, z1, x2, z2, width, material):
    """Draw a stone path between two points with given width."""
    block = make_block(material)
    if x1 == x2:  # vertical line (along Z)
        for z in range(min(z1, z2), max(z1, z2) + 1):
            for dx in range(-width // 2, width // 2 + 1):
                place_block_above(level, x1 + dx, z, 0, block)
    elif z1 == z2:  # horizontal line (along X)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for dz in range(-width // 2, width // 2 + 1):
                place_block_above(level, x, z1 + dz, 0, block)
    else:  # diagonal — Bresenham-ish via interpolation
        steps = max(abs(x2 - x1), abs(z2 - z1))
        for i in range(steps + 1):
            t = i / max(steps, 1)
            x = int(round(x1 + (x2 - x1) * t))
            z = int(round(z1 + (z2 - z1) * t))
            for dx in range(-width // 2, width // 2 + 1):
                for dz in range(-width // 2, width // 2 + 1):
                    place_block_above(level, x + dx, z + dz, 0, block)


def draw_parking(level, x, z, w, d, material):
    """Draw a parking lot rectangle."""
    block = make_block(material)
    for dx in range(w):
        for dz in range(d):
            place_block_above(level, x + dx, z + dz, 0, block)


def draw_tree(level, x, z, trunk, leaves):
    """Draw a simple oak tree (1 trunk + 3x3x3 leaves on top)."""
    trunk_block = make_block(trunk)
    leaves_block = make_block(leaves)
    gy = get_ground_y(level, x, z)
    # Trunk 4-5 blocks
    for dy in range(1, 6):
        place_block(level, x, gy + dy, z, trunk_block)
    # Leaves 3x3x3 on top
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            for dy in range(4, 8):
                if abs(dx) + abs(dz) + abs(dy - 5) <= 3:
                    place_block(level, x + dx, gy + dy, z + dz, leaves_block)


def draw_trees(level, cx, cz, radius, count, trunk, leaves):
    """Draw count trees randomly within radius of (cx, cz) using a deterministic seed."""
    import random
    rng = random.Random(cx * 1000 + cz)
    placed = 0
    attempts = 0
    while placed < count and attempts < count * 10:
        attempts += 1
        x = cx + rng.randint(-radius, radius)
        z = cz + rng.randint(-radius, radius)
        # Skip if too close to a path center (heuristic)
        if abs(x - 200) <= 3 and 200 <= z <= 200:  # skip main path
            continue
        if abs(x - 360) <= 4 and 380 <= z <= 430:  # skip bus road
            continue
        draw_tree(level, x, z, trunk, leaves)
        placed += 1
    return placed


def draw_sports_field(level, x, z, w, d, border, field):
    """Draw a sports field with green inner and white border."""
    border_block = make_block(border)
    field_block = make_block(field)
    # Inner field
    for dx in range(2, w - 2):
        for dz in range(2, d - 2):
            place_block_above(level, x + dx, z + dz, 0, field_block)
    # Border
    for dx in range(w):
        place_block_above(level, x + dx, z, 0, border_block)
        place_block_above(level, x + dx, z + d - 1, 0, border_block)
    for dz in range(d):
        place_block_above(level, x, z + dz, 0, border_block)
        place_block_above(level, x + w - 1, z + dz, 0, border_block)


def draw_benches(level, x, z, count, material):
    """Draw count benches in a row along X."""
    block = make_block(material)
    for i in range(count):
        bx = x + i * 4
        # bench = fence post on ground
        place_block_above(level, bx, z, 0, block)


def draw_lamps(level, x1, z1, x2, z2, spacing, material):
    """Draw lamp posts along a line."""
    block = make_block(material)
    if z1 == z2:  # horizontal
        for x in range(min(x1, x2), max(x1, x2) + 1, spacing):
            place_block_above(level, x, z1 + 2, 1, block)
            place_block_above(level, x, z1 + 2, 0, make_block("fence"))
    elif x1 == x2:  # vertical
        for z in range(min(z1, z2), max(z1, z2) + 1, spacing):
            place_block_above(level, x1 + 2, z, 1, block)
            place_block_above(level, x1 + 2, z, 0, make_block("fence"))


def main():
    import shutil
    if DST_MCWORLD.exists():
        shutil.rmtree(DST_MCWORLD)
    shutil.copytree(SRC_MCWORLD, DST_MCWORLD)

    print(f"Loading {DST_MCWORLD}")
    level = amulet_level.load_level(str(DST_MCWORLD))
    print("Loaded.")

    details = json.loads(DETAILS_JSON.read_text())
    counts = {"path": 0, "road": 0, "parking": 0, "tree": 0, "field": 0, "bench": 0, "lamp": 0}
    blocks_placed = 0

    for d in details:
        t = d["type"]
        if t == "path":
            draw_path(level, d["x1"], d["z1"], d["x2"], d["z2"], d["width"], d["material"])
            counts["path"] += 1
            blocks_placed += abs(d["x2"] - d["x1"] + d["z2"] - d["z1"]) * d["width"]
            print(f"  Path: {d['name']}")
        elif t == "road":
            draw_path(level, d["x1"], d["z1"], d["x2"], d["z2"], d["width"], d["material"])
            counts["road"] += 1
            blocks_placed += abs(d["x2"] - d["x1"] + d["z2"] - d["z1"]) * d["width"]
            print(f"  Road: {d['name']}")
        elif t == "parking":
            draw_parking(level, d["x"], d["z"], d["size"][0], d["size"][1], d["material"])
            counts["parking"] += 1
            blocks_placed += d["size"][0] * d["size"][1]
            print(f"  Parking: {d['name']} ({d['size'][0]}x{d['size'][1]})")
        elif t == "tree_cluster":
            n = draw_trees(level, d["x"], d["z"], d["radius"], d["count"], d["trunk"], d["leaves"])
            counts["tree"] += n
            blocks_placed += n * 25  # trunk + leaves
            print(f"  Tree cluster: {d['name']} ({n} trees)")
        elif t == "sports_field":
            draw_sports_field(level, d["x"], d["z"], d["size"][0], d["size"][1], d["border"], d["field"])
            counts["field"] += 1
            blocks_placed += d["size"][0] * d["size"][1]
            print(f"  Sports field: {d['name']}")
        elif t == "bench_row":
            draw_benches(level, d["x"], d["z"], d["count"], d["material"])
            counts["bench"] += d["count"]
            blocks_placed += d["count"]
            print(f"  Bench row: {d['name']} ({d['count']} benches)")
        elif t == "lamp_row":
            draw_lamps(level, d["x1"], d["z1"], d["x2"], d["z2"], d["spacing"], d["material"])
            counts["lamp"] += 1
            print(f"  Lamp row: {d['name']}")

    level.close()
    print(f"\nDone! Placed ~{blocks_placed} detail blocks.")
    print(f"Counts: {counts}")
    print(f"Saved to: {DST_MCWORLD}")


if __name__ == "__main__":
    main()
