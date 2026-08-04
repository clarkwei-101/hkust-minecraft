#!/usr/bin/env python3
"""
v1.5-B: Inject remaining OSM buildings (those NOT in manual_buildings.json)
Uses data/hkust_osm_buildings_mc.json coordinates.
Generates simpler box schematics with height, footprint, and material.
"""
import json
import sys
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.5"
DST = WORKDIR / "worlds/working/v1.5b"
OSM_JSON = WORKDIR / "data/hkust_osm_buildings_mc.json"
MANUAL_JSON = WORKDIR / "data/manual_buildings.json"

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


# Material map by building type
TYPE_MATERIAL = {
    "dormitory": "light_gray_concrete",
    "staff": "light_gray_concrete",
    "academic": "white_concrete",
    "university": "white_concrete",
    "default": "gray_concrete",
}


def get_ground_y(level, x, z):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    for y in range(120, 30, -1):
        b = level.get_version_block(x, y, z, dim, ver)
        if b[0].base_name != "air":
            return y
    return 60


def place(level, x, y, z, block):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    level.set_version_block(x, y, z, dim, ver, block)


def build_box(level, cx, cz, w, d, height, ground_y, mat_block):
    """Draw a box at (cx, cz) with width w, depth d, height starting at ground_y+1."""
    base_y = ground_y + 1
    # Walls (outline)
    for x in range(cx - w // 2, cx + w // 2 + 1):
        for z in range(cz - d // 2, cz + d // 2 + 1):
            for y in range(base_y, base_y + height):
                # Only outer shell
                if x == cx - w // 2 or x == cx + w // 2 or z == cz - d // 2 or z == cz + d // 2 or y == base_y or y == base_y + height - 1:
                    place(level, x, y, z, mat_block)


def build_window_box(level, cx, cz, w, d, height, ground_y, mat_block, glass_block):
    """Draw a box with light blue glass windows on every other floor."""
    base_y = ground_y + 1
    for x in range(cx - w // 2, cx + w // 2 + 1):
        for z in range(cz - d // 2, cz + d // 2 + 1):
            for y in range(base_y, base_y + height):
                if x == cx - w // 2 or x == cx + w // 2 or z == cz - d // 2 or z == cz + d // 2:
                    # Side walls: every 3rd floor = window
                    if (y - base_y) % 3 == 1 and 0 < x - (cx - w // 2) < w and 0 < z - (cz - d // 2) < d:
                        # Glass only on face, not corners
                        if (x == cx - w // 2 and z not in (cz - d // 2, cz + d // 2)) or \
                           (x == cx + w // 2 and z not in (cz - d // 2, cz + d // 2)) or \
                           (z == cz - d // 2 and x not in (cx - w // 2, cx + w // 2)) or \
                           (z == cz + d // 2 and x not in (cx - w // 2, cx + w // 2)):
                            place(level, x, y, z, glass_block)
                        else:
                            place(level, x, y, z, mat_block)
                    else:
                        place(level, x, y, z, mat_block)
                elif y == base_y or y == base_y + height - 1:
                    place(level, x, y, z, mat_block)


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    osm_data = json.load(open(OSM_JSON))
    manual = json.load(open(MANUAL_JSON))
    manual_names = {m["name"] for m in manual}
    print(f"OSM buildings: {len(osm_data['buildings'])}")
    print(f"Manual buildings: {len(manual_names)}")

    # Find OSM buildings that are NOT in manual list
    osm_to_inject = []
    seen_names = set()
    for b in osm_data["buildings"]:
        # Match by approximate position (within 20 blocks of a manual building)
        is_manual = False
        for m in manual:
            if abs(b["mc_x"] - m["mc_x"]) < 20 and abs(b["mc_z"] - m["mc_z"]) < 20:
                is_manual = True
                break
        if not is_manual and b["mc_x"] > 0:
            name = b.get("name", f"OSM-{b['osm_id']}")
            # Deduplicate by name
            if name not in seen_names:
                seen_names.add(name)
                osm_to_inject.append(b)

    print(f"To inject: {len(osm_to_inject)}")

    blocks_placed = 0
    success = 0
    skipped = 0

    for b in osm_to_inject:
        cx = b["mc_x"]
        cz = b["mc_z"]
        h_m = b.get("height_m", 12)
        if h_m is None or h_m < 5:
            h_m = 10
        height_blocks = max(3, int(h_m / 3.0))  # 3m per block
        # Footprint: estimate from building type
        btype = b.get("type", "default")
        if btype == "dormitory":
            w, d = 30, 12
        elif btype in ("academic", "university"):
            w, d = 50, 30
        else:
            w, d = 25, 20
        mat = TYPE_MATERIAL.get(btype, "gray_concrete")
        mat_block = B("minecraft", mat)
        glass_block = B("minecraft", "light_blue_stained_glass")

        gy = get_ground_y(level, cx, cz)
        if gy < 35:
            skipped += 1
            continue
        # Skip if already at landmark area (220, 200)
        if abs(cx - 220) < 5 and abs(cz - 200) < 5:
            skipped += 1
            continue

        try:
            build_window_box(level, cx, cz, w, d, height_blocks, gy, mat_block, glass_block)
            blocks_placed += 2 * (w + d) * height_blocks  # walls
            success += 1
            if success <= 10:
                print(f"  + {b.get('name', 'OSM')} at ({cx},{cz}) h={height_blocks} mat={mat}")
        except Exception as e:
            print(f"  ! {b.get('name', 'OSM')}: {e}")
            skipped += 1

    level.close()
    print(f"\nDone! {success} buildings injected, {skipped} skipped, ~{blocks_placed} new blocks.")


if __name__ == "__main__":
    main()
