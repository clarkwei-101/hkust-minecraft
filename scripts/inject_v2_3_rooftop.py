#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.3 — Phase C: Roof Garden & Greenery
=======================================================
Adds urban rooftop detail to all v2.3 buildings:
  - HVAC units (iron_block + black_concrete chimney)
  - Solar panels (blue_concrete arrays)
  - Water towers (dark_oak_fence + blue_concrete)
  - Green roof accents (short_grass + flower scatter)
  - Rooftop "lift room" (cyan_concrete mini box)
  - Surrounding greenery density boost

Greenery: scan vacant grass_block cells around campus and add scattered
oak trees + flower patches, avoiding footway/amenity cells.
"""
import sys
import math
import json
import argparse
import random
from collections import defaultdict

import amulet
from amulet.api.block import Block, StringTag, IntTag

DIM = "minecraft:overworld"
VER = ("bedrock", (1, 21, 40))

# Building footprints — same as inject_v2_1_final_v2.py
BUILDINGS = [
    (220, 240, 36, 20, "Academic Building"),
    (264, 220, 16, 16, "Library"),
    (320, 480, 28, 24, "Shaw Auditorium"),
    (184, 256, 12, 14, "LG7 Lecture Hall"),
    (222, 230, 20, 20, "Sundial Plaza"),
    (170, 305, 8, 8, "Armillary Sphere"),
    (500, 380, 6, 6, "Satellite Dish"),
    (480, 800, 5, 5, "Bus Stop"),
    (340, 880, 4, 4, "Bus Stop"),
    (220, 240, 8, 8, "Fountain"),
    (200, 510, 8, 8, "Bus Stop"),
    (620, 285, 22, 18, "Coastal Marine Lab"),
    (580, 870, 16, 12, "President's Lodge"),
    (264,  18, 18, 14, "Library Extension"),
    (530, 200, 14, 14, "HPC Facility"),
    (660, 290, 18, 24, "Indoor Swimming Pool"),
    (575, 850, 22, 18, "Multi-storey Car Park"),
    (190, 700, 24,  8, "JC i-Village"),
    (267, 367, 14, 10, "Annex Building"),
    (320, 540, 18, 14, "Alumni Commons"),
    (360, 337, 28, 16, "Lo Kwee-Seong Building"),
    (235, 235,  8, 24, "Chia-Wei Woo Concourse"),
    (200, 320, 22, 18, "Tin Ka Ping Hall"),
    (320, 380, 18, 12, "Daniel Yu Research"),
    (440, 460, 22, 14, "School of Medicine"),
    (222, 230, 24, 24, "Sundial Plaza (large)"),
]

# Small buildings: skip rooftop decoration
SKIP_ROOF = {"Bus Stop", "Fountain", "Armillary Sphere", "Satellite Dish",
             "Sundial Plaza", "Sundial Plaza (large)"}

TERRAIN = {
    'stone', 'dirt', 'grass_block', 'sand', 'gravel', 'sandstone', 'bedrock',
    'lava', 'coal_ore', 'iron_ore', 'gold_ore', 'redstone_ore', 'diamond_ore',
    'emerald_ore', 'granite', 'diorite', 'andesite', 'obsidian', 'cobblestone',
    'clay', 'clay_block', 'hardened_clay', 'terracotta', 'podzol', 'mycelium',
    'coarse_dirt', 'rooted_dirt', 'moss_block', 'moss_carpet', 'farmland',
    'mud', 'mud_bricks', 'packed_mud', 'soul_sand', 'soul_soil', 'basalt',
    'blackstone', 'magma_block', 'tuff', 'calcite', 'deepslate',
    'cobbled_deepslate', 'dirt_path', 'snow_block', 'powder_snow', 'ice',
    'packed_ice', 'blue_ice', 'red_sand', 'red_sandstone', 'snow', 'snow_layer',
    'short_grass', 'tall_grass', 'poppy', 'dandelion', 'blue_orchid',
    'azure_bluet', 'allium', 'cornflower', 'lily_of_the_valley',
    'kelp', 'kelp_plant', 'seagrass', 'tall_seagrass', 'lily_pad',
    'redstone_wire', 'rail', 'powered_rail', 'detector_rail',
    'activator_rail', 'chain', 'iron_bars', 'vine', 'lantern',
    'wall_torch', 'torch', 'soul_torch', 'soul_lantern',
    'redstone_torch', 'soul_fire', 'fire', 'water', 'lava',
}


def B(ns, name, props=None):
    out = {}
    for k, v in (props or {}).items():
        out[k] = StringTag(v) if isinstance(v, str) else IntTag(v)
    return Block(ns, name, out)


def place(level, x, y, z, block):
    if y < -64 or y > 320:
        return
    try:
        level.set_version_block(int(x), int(y), int(z), DIM, VER, block)
    except Exception:
        pass


def get_safe(level, x, y, z):
    try:
        b = level.get_version_block(int(x), int(y), int(z), DIM, VER)
        return b[0].base_name if b else 'null'
    except Exception:
        return 'err'


def find_roof_y(level, cx, cz, half_w, half_d, lo=60, hi=180):
    """Find topmost building block under footprint."""
    max_y = 0
    for x in range(cx - half_w, cx + half_w + 1):
        for z in range(cz - half_d, cz + half_d + 1):
            for y in range(hi, lo, -1):
                bn = get_safe(level, x, y, z)
                if bn in ('air', 'null', 'err', 'water', 'lava'):
                    continue
                if bn in TERRAIN:
                    continue
                if y > max_y:
                    max_y = y
                break
    return max_y


# =============================================================================
# ROOFTOP BUILDERS
# =============================================================================
def add_hvac(level, x, y, z):
    """HVAC unit — iron_block base + iron_block body + black_concrete chimney."""
    placed = 0
    # Base
    place(level, x, y + 1, z, B('minecraft', 'iron_block'))
    place(level, x + 1, y + 1, z, B('minecraft', 'iron_block'))
    place(level, x, y + 1, z + 1, B('minecraft', 'iron_block'))
    place(level, x + 1, y + 1, z + 1, B('minecraft', 'iron_block'))
    placed += 4
    # Body
    place(level, x, y + 2, z, B('minecraft', 'iron_block'))
    place(level, x + 1, y + 2, z, B('minecraft', 'iron_block'))
    place(level, x, y + 2, z + 1, B('minecraft', 'iron_block'))
    place(level, x + 1, y + 2, z + 1, B('minecraft', 'iron_block'))
    placed += 4
    # Chimney
    place(level, x + 1, y + 3, z + 1, B('minecraft', 'black_concrete'))
    place(level, x + 1, y + 4, z + 1, B('minecraft', 'black_concrete'))
    placed += 2
    return placed


def add_solar_panel(level, x, y, z, dx=1, dz=0):
    """Solar panel array — blue_concrete on roof."""
    placed = 0
    for off in range(3):
        place(level, x + dx * (off + 1), y + 1, z + dz * (off + 1), B('minecraft', 'blue_concrete'))
        placed += 1
    return placed


def add_water_tower(level, x, y, z):
    """Water tower — dark_oak_fence legs + blue_concrete drum."""
    placed = 0
    # 4 legs
    for dx, dz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        place(level, x + dx, y + 1, z + dz, B('minecraft', 'dark_oak_fence'))
        place(level, x + dx, y + 2, z + dz, B('minecraft', 'dark_oak_fence'))
        placed += 2
    # Drum (3x3x2 blue_concrete)
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            for yy in range(3, 5):
                place(level, x + dx, y + yy, z + dz, B('minecraft', 'blue_concrete'))
                placed += 1
    # Top accent
    place(level, x, y + 5, z, B('minecraft', 'sea_lantern'))
    placed += 1
    return placed


def add_lift_room(level, x, y, z):
    """Lift room — cyan_concrete cube."""
    placed = 0
    for dx in range(2):
        for dz in range(2):
            for yy in range(1, 3):
                place(level, x + dx, y + yy, z + dz, B('minecraft', 'cyan_concrete'))
                placed += 1
    return placed


def add_green_roof(level, x, y, z, w, d):
    """Green roof — short_grass + flower scatter on roof plane."""
    placed = 0
    for rx in range(-w // 2 + 1, w // 2):
        for rz in range(-d // 2 + 1, d // 2):
            if random.random() < 0.4:
                place(level, x + rx, y + 1, z + rz, B('minecraft', 'short_grass'))
                placed += 1
            elif random.random() < 0.05:
                flower = random.choice(['poppy', 'dandelion', 'azure_bluet', 'blue_orchid'])
                place(level, x + rx, y + 1, z + rz, B('minecraft', flower))
                placed += 1
    return placed


# =============================================================================
# GREEN SCATTER (trees + flower patches)
# =============================================================================
def add_tree(level, x, y, z):
    """Place an oak tree at (x, y, z) where y is grass_block top."""
    placed = 0
    place(level, x, y + 1, z, B('minecraft', 'oak_log'))
    place(level, x, y + 2, z, B('minecraft', 'oak_log'))
    place(level, x, y + 3, z, B('minecraft', 'oak_log'))
    place(level, x, y + 4, z, B('minecraft', 'oak_log'))
    placed += 4
    # Leaves 3x3 at top + 1x1 above
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            place(level, x + dx, y + 4, z + dz, B('minecraft', 'oak_leaves', {'persistent_bit': True}))
            placed += 1
    for dx, dz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        place(level, x + dx, y + 5, z + dz, B('minecraft', 'oak_leaves', {'persistent_bit': True}))
        placed += 1
    place(level, x, y + 5, z, B('minecraft', 'oak_leaves', {'persistent_bit': True}))
    place(level, x, y + 6, z, B('minecraft', 'oak_leaves', {'persistent_bit': True}))
    placed += 6
    return placed


def add_flower_patch(level, x, y, z):
    """A 3x3 flower patch."""
    placed = 0
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            f = random.choice(['poppy', 'dandelion', 'blue_orchid', 'allium',
                               'cornflower', 'azure_bluet', 'lily_of_the_valley'])
            place(level, x + dx, y + 1, z + dz, B('minecraft', f))
            placed += 1
    return placed


def is_footway_or_amenity(level, x, y, z):
    """Check if topmost block at (x, z) is a footway/amenity material."""
    bn = get_safe(level, x, y, z)
    return bn in ('gray_concrete', 'coarse_dirt', 'stone_brick_stairs',
                  'polished_andesite', 'green_carpet', 'red_concrete',
                  'white_concrete', 'black_concrete', 'green_concrete',
                  'blue_concrete', 'orange_concrete', 'yellow_concrete')


def grass_density_boost(level, ax, bx, az, bz):
    """Sample OSM-extent area and add trees/flowers on grass_block."""
    placed = 0
    # Campus bbox in world coords — use anchor scatter
    # x in [0, 815], z in [0, 975]
    random.seed(45)
    sample = 0
    trees = 0
    flowers = 0
    for x in range(0, 815, 6):  # every 6 blocks
        for z in range(0, 975, 6):
            if random.random() > 0.06:  # 6% density
                continue
            # Find top material at (x, z)
            for y in range(80, 30, -1):
                bn = get_safe(level, x, y, z)
                if bn in ('air', 'null', 'err'):
                    continue
                if bn == 'grass_block':
                    if is_footway_or_amenity(level, x, y, z):
                        break
                    if random.random() < 0.4:
                        add_tree(level, x, y, z)
                        trees += 1
                    elif random.random() < 0.7:
                        add_flower_patch(level, x, y, z)
                        flowers += 1
                    placed += 1
                break
            sample += 1
    print(f"  Sampled {sample} cells, placed {trees} trees + {flowers} flower patches")
    return placed


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default='worlds/working/v2.3')
    ap.add_argument('--out', default='worlds/working/v2.3')
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--skip-trees', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    random.seed(args.seed)

    if args.dry_run:
        print(f"Buildings: {len(BUILDINGS)}")
        for b in BUILDINGS:
            print(f"  {b}")
        return

    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)

    # Phase C1: Building rooftops
    print("\n=== Rooftop decoration ===")
    roof_total = 0
    for cx, cz, w, d, name in BUILDINGS:
        if name in SKIP_ROOF:
            continue
        half_w, half_d = w // 2, d // 2
        # Find roof_y
        roof_y = find_roof_y(level, cx, cz, half_w, half_d)
        if roof_y < 50:
            print(f"  Skipping {name} (roof_y={roof_y})")
            continue
        n_placed = 0
        # Green roof base (under equipment)
        n_placed += add_green_roof(level, cx, cz, roof_y, w, d)
        # Equipment count scales with building size
        area = w * d
        if area > 300:
            # Large: 2 HVAC + 1 water tower + 1 solar row + 1 lift room
            n_placed += add_hvac(level, cx - half_w + 2, roof_y, cz - half_d + 2)
            n_placed += add_hvac(level, cx + half_w - 4, roof_y, cz + half_d - 4)
            n_placed += add_water_tower(level, cx + 1, roof_y, cz + 1)
            n_placed += add_solar_panel(level, cx - half_w + 2, roof_y, cz + half_d - 2, dx=1, dz=0)
            n_placed += add_solar_panel(level, cx + half_w - 5, roof_y, cz - half_d + 2, dx=0, dz=1)
            n_placed += add_lift_room(level, cx - 1, roof_y, cz - 1)
        elif area > 100:
            # Medium: 1 HVAC + 1 water tower
            n_placed += add_hvac(level, cx - half_w + 2, roof_y, cz - half_d + 2)
            n_placed += add_water_tower(level, cx + half_w - 3, roof_y, cz + half_d - 3)
        else:
            # Small: 1 HVAC
            n_placed += add_hvac(level, cx, roof_y, cz)
        print(f"  ✓ {name:<28} roof_y={roof_y} +{n_placed} blocks")
        roof_total += n_placed
    print(f"Rooftop total: {roof_total} blocks")

    # Phase C2: Greenery density
    if not args.skip_trees:
        print("\n=== Greenery density boost ===")
        # Use simple anchor rect
        tree_total = grass_density_boost(level, 0, 0, 0, 0)
        print(f"Greenery total: {tree_total} cells")

    print(f"\nSaving to {args.out}…")
    level.save()
    level.close()
    print("Done.")


if __name__ == '__main__':
    main()