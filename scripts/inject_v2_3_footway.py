#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.3 — Phase A: Footway Network & Named Bridges
================================================================
Read OSM footway/steps/path/pedestrian/cycleway + bridge=yes ways from
osm/hkust-overpass.json and inject them into v2.1 world.

Anchor points (lat,lon) → (world_x, world_z) come from the 26 v2.1 landmarks
in inject_v2_1_final_v2.py + OSM building polygons.

Surface materials:
  footway   → gray_concrete (modern paved, matches HKUST pavers)
  path      → coarse_dirt / podzol (informal trails, e.g. around shoreline)
  steps     → stone_brick_stairs (Brescia-stone aesthetic)
  pedestrian→ polished_andesite (wide pedestrian plazas)
  cycleway  → green_carpet (subtle visual cue for cyclists)
  bridge=yes→ quartz_slab railings + fence_posts on footway segment
"""
import sys
import math
import json
import argparse
from collections import defaultdict

import amulet
from amulet.api.block import Block, StringTag, IntTag

DIM = "minecraft:overworld"
VER = ("bedrock", (1, 21, 40))

REAL_GROUND_SAFE = {
    'grass_block', 'dirt', 'sand', 'sandstone', 'stone', 'cobblestone',
    'gravel', 'snow', 'snow_block', 'podzol', 'coarse_dirt', 'rooted_dirt',
    'moss_block', 'moss_carpet', 'mossy_cobblestone', 'magma_block',
    'soul_sand', 'soul_soil', 'farmland', 'dirt_path', 'mud', 'mud_bricks',
    'packed_mud', 'tuff', 'calcite', 'deepslate', 'cobbled_deepslate',
    'blue_ice', 'packed_ice', 'ice', 'smooth_stone', 'polished_andesite',
    'polished_diorite', 'polished_granite', 'polished_deepslate',
    'polished_blackstone', 'polished_blackstone_bricks', 'cut_sandstone',
    'smooth_sandstone', 'smooth_red_sandstone', 'chiseled_stone_bricks',
    'chiseled_deepslate', 'red_sand', 'red_sandstone', 'hardened_clay',
    'terracotta', 'clay', 'mycelium',
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


def safe_ground_y(level, x, z, lo=0, hi=180):
    """Find ground level, swallowing PyMCTranslate exceptions for buggy blocks."""
    for y in range(hi, lo, -1):
        try:
            b = level.get_version_block(int(x), int(y), int(z), DIM, VER)
            bn = b[0].base_name if b else 'null'
        except Exception:
            continue
        if bn in REAL_GROUND_SAFE:
            return y
        if bn in ('air', 'null'):
            continue
    return 60  # default sea level


# =============================================================================
# COORDINATE TRANSFORM (lat/lon → MC x/z)
# =============================================================================
# Anchor points derived from:
#   (a) inject_v2_1_final_v2.py landmark positions (MC coords)
#   (b) OSM building polygons (lat/lon of nearest building tag)
# Fit:  world_x = ax * lon + bx,  world_z = az * lat + bz
# Plus Y-correction: v2.1 uses N→S increasing z, OSM lat increases northward,
# so negative az sign expected.

ANCHOR_POINTS = [
    # (world_x, world_z, lat, lon, label)
    (220, 240, 22.33750, 114.26450, "Academic Building"),
    (222, 230, 22.33752, 114.26299, "Sundial Plaza"),
    (264, 220, 22.33880, 114.26360, "Library"),
    (620, 285, 22.33300, 114.26850, "Coastal Marine Lab"),
    (660, 290, 22.33280, 114.26880, "Indoor Swimming Pool"),
    (580, 870, 22.33250, 114.26400, "President's Lodge"),
    (575, 850, 22.33220, 114.26500, "Multi-storey Car Park"),
    (440, 460, 22.33600, 114.26600, "School of Medicine"),
    (190, 700, 22.33500, 114.26200, "JC i-Village"),
    (650, 300, 22.33250, 114.26400, "Seaview Lookout"),
    (340, 880, 22.33100, 114.26450, "Bus Stop south-1"),
    (480, 800, 22.33150, 114.26650, "Bus Stop south-2"),
    (360, 337, 22.33720, 114.26570, "Lo Kwee-Seong Building"),
    (235, 235, 22.33752, 114.26380, "Chia-Wei Woo Concourse"),
    (320, 480, 22.33680, 114.26580, "Shaw Auditorium"),
]


def fit_transform(anchors):
    """Least-squares affine: world_x = ax*lng + bx; world_z = az*lat + bz."""
    import numpy as np
    xs = np.array([a[0] for a in anchors], dtype=float)
    zs = np.array([a[1] for a in anchors], dtype=float)
    lats = np.array([a[2] for a in anchors], dtype=float)
    lngs = np.array([a[3] for a in anchors], dtype=float)
    Ax = np.vstack([lngs, np.ones_like(lngs)]).T
    ax, bx = np.linalg.lstsq(Ax, xs, rcond=None)[0]
    Az = np.vstack([lats, np.ones_like(lats)]).T
    az, bz = np.linalg.lstsq(Az, zs, rcond=None)[0]
    return ax, bx, az, bz


def latlon_to_world(ax, bx, az, bz, lat, lon):
    return int(round(ax * lon + bx)), int(round(az * lat + bz))


# =============================================================================
# FOOTWAY INJECTION
# =============================================================================
FOOTWAY_MATERIALS = {
    'footway':    B('minecraft', 'gray_concrete'),
    'path':       B('minecraft', 'coarse_dirt'),
    'steps':      B('minecraft', 'stone_brick_stairs'),
    'pedestrian': B('minecraft', 'polished_andesite'),
    'cycleway':   B('minecraft', 'green_carpet'),
    'bridleway':  B('minecraft', 'coarse_dirt'),
    'track':      B('minecraft', 'coarse_dirt'),
}

# Materials for the paved centerline under a bridge
BRIDGE_RAIL = B('minecraft', 'quartz_slab', {'top_slot_bit': True})
BRIDGE_POST = B('minecraft', 'oak_fence')


def draw_footway(level, x1, z1, x2, z2, block, width=2):
    """Draw a footway segment from (x1,z1) to (x2,z2) using Bresenham + width."""
    # Bresenham line
    dx = abs(x2 - x1)
    dz = abs(z2 - z1)
    sx = 1 if x1 < x2 else -1
    sz = 1 if z1 < z2 else -1
    err = dx - dz
    placed = 0
    x, z = x1, z1
    while True:
        gy = safe_ground_y(level, x, z)
        for wy in range(gy + 1, gy + 2):
            for wx in range(x - width + 1, x + width):
                for wz in range(z - width + 1, z + width):
                    place(level, wx, wy, wz, block)
                    placed += 1
        if (x, z) == (x2, z2):
            break
        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            x += sx
        if e2 < dx:
            err += dx
            z += sz
    return placed


def draw_bridge(level, x1, z1, x2, z2, base_block):
    """Draw a footway + side railings + oak fence posts at 3-block intervals."""
    dx = abs(x2 - x1)
    dz = abs(z2 - z1)
    sx = 1 if x1 < x2 else -1
    sz = 1 if z1 < z2 else -1
    err = dx - dz
    placed = 0
    x, z = x1, z1
    step = 0
    while True:
        gy = safe_ground_y(level, x, z)
        # Path center (3 wide for bridge)
        for off in (-1, 0, 1):
            place(level, x + off, gy + 1, z, base_block)
            placed += 1
        # Side railings at ±2 (quartz slab low)
        place(level, x - 2, gy + 2, z, BRIDGE_RAIL)
        place(level, x + 2, gy + 2, z, BRIDGE_RAIL)
        placed += 2
        # Fence posts every 3 blocks
        if step % 3 == 0:
            place(level, x - 2, gy + 3, z, BRIDGE_POST)
            place(level, x + 2, gy + 3, z, BRIDGE_POST)
            placed += 2
        step += 1
        if (x, z) == (x2, z2):
            break
        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            x += sx
        if e2 < dx:
            err += dx
            z += sz
    return placed


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default='worlds/working/v2.1',
                    help='Bedrock world dir (default: worlds/working/v2.1)')
    ap.add_argument('--osm', default='osm/hkust-overpass.json',
                    help='OSM Overpass JSON (default: osm/hkust-overpass.json)')
    ap.add_argument('--out', default='worlds/working/v2.3',
                    help='Output world dir (default: worlds/working/v2.3)')
    ap.add_argument('--width', type=int, default=2,
                    help='Footway width (default: 2)')
    ap.add_argument('--only-bridges', action='store_true',
                    help='Only inject bridge=yes ways (Phase A subset)')
    ap.add_argument('--only-footway', action='store_true',
                    help='Only inject non-bridge footway-class ways')
    ap.add_argument('--dry-run', action='store_true',
                    help='Skip actual block writes')
    args = ap.parse_args()

    print(f"Loading OSM data: {args.osm}")
    with open(args.osm) as f:
        osm = json.load(f)
    nodes = {n['id']: (n['lat'], n['lon']) for n in osm['elements'] if n.get('type') == 'node'}

    # Fit lat/lon transform
    print(f"Fitting coordinate transform from {len(ANCHOR_POINTS)} anchors…")
    ax, bx, az, bz = fit_transform(ANCHOR_POINTS)
    print(f"  world_x = {ax:.1f} * lng + {bx:.1f}")
    print(f"  world_z = {az:.1f} * lat + {bz:.1f}")

    # Filter ways
    footway_ways = []
    bridge_ways = []
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        t = w.get('tags', {})
        hw = t.get('highway')
        if not hw:
            continue
        if hw in ('footway', 'path', 'steps', 'pedestrian', 'cycleway', 'bridleway', 'track'):
            nids = w.get('nodes', [])
            if len(nids) >= 2:
                footway_ways.append((w, hw, t.get('bridge') == 'yes'))
                if t.get('bridge') == 'yes':
                    bridge_ways.append((w, hw))
    print(f"Found {len(footway_ways)} footway-class ways "
          f"({len(bridge_ways)} with bridge=yes)")

    if args.dry_run:
        # Just print summary
        for w, hw, is_bridge in footway_ways[:8]:
            nids = w['nodes']
            n1 = nodes.get(nids[0])
            n2 = nodes.get(nids[-1])
            if n1 and n2:
                x1, z1 = latlon_to_world(ax, bx, az, bz, n1[0], n1[1])
                x2, z2 = latlon_to_world(ax, bx, az, bz, n2[0], n2[1])
                name = w.get('tags', {}).get('name', '')
                print(f"  {hw:11} bridge={is_bridge} ({x1},{z1})→({x2},{z2})  {name}")
        return

    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)

    footway_placed = 0
    bridge_placed = 0

    # Phase A1: bridges (draw with railings)
    if not args.only_footway:
        print(f"\n=== Drawing {len(bridge_ways)} bridges ===")
        for w, hw in bridge_ways:
            nids = w['nodes']
            base_block = FOOTWAY_MATERIALS.get(hw, B('minecraft', 'gray_concrete'))
            n_segments = 0
            for i in range(len(nids) - 1):
                a, b = nodes.get(nids[i]), nodes.get(nids[i + 1])
                if not a or not b:
                    continue
                x1, z1 = latlon_to_world(ax, bx, az, bz, a[0], a[1])
                x2, z2 = latlon_to_world(ax, bx, az, bz, b[0], b[1])
                n_segments += draw_bridge(level, x1, z1, x2, z2, base_block)
            name = w.get('tags', {}).get('name', '')
            print(f"  ✓ bridge {w['id']} {hw} ({n_segments} blocks) {name}")
            bridge_placed += n_segments

    # Phase A2: footways (no railings, just surface)
    if not args.only_bridges:
        print(f"\n=== Drawing {len(footway_ways)} footways ===")
        for w, hw, is_bridge in footway_ways:
            if is_bridge:
                continue  # already drawn above
            nids = w['nodes']
            block = FOOTWAY_MATERIALS.get(hw, B('minecraft', 'gray_concrete'))
            n_segments = 0
            for i in range(len(nids) - 1):
                a, b = nodes.get(nids[i]), nodes.get(nids[i + 1])
                if not a or not b:
                    continue
                x1, z1 = latlon_to_world(ax, bx, az, bz, a[0], a[1])
                x2, z2 = latlon_to_world(ax, bx, az, bz, b[0], b[1])
                n_segments += draw_footway(level, x1, z1, x2, z2, block, width=args.width)
            name = w.get('tags', {}).get('name', '')
            print(f"  ✓ {hw:11} ({n_segments} blocks) {name}")
            footway_placed += n_segments

    print(f"\nTotal placed: {footway_placed + bridge_placed} blocks "
          f"(footways {footway_placed}, bridges {bridge_placed})")

    print(f"\nSaving to {args.out}…")
    level.save()
    level.close()
    print("Done.")


if __name__ == '__main__':
    main()