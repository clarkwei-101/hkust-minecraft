#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.4 — Phase D: Sinkholes, Underpasses, Pavilions, Lighting
============================================================================
Reads OSM natural=tunnel/covered/natural=cliff/rock/earth_bank + service ways
and injects:
  - Sinkholes (5–7 cell craters at natural=cliff / rock / earth_bank centers)
  - Underpasses (stone_brick arch + sea_lantern at OSM tunnel=yes ways)
  - Pavilions (covered=yes ways → smooth_stone_slab roof + oak_fence posts)
  - Crosswalks (88 service ways → white_carpet zebra stripes at footway
    intersections)
  - Night lighting (lantern + glowstone along footways every ~10 blocks)
"""
import sys
import math
import json
import argparse
import random
from collections import defaultdict

sys.path.insert(0, '/Users/yahweh/Desktop/ai应用社/hkust-minecraft/scripts')
import pymctranslate_patch
pymctranslate_patch.apply(verbose=False)

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
    'terracotta', 'clay', 'mycelium', 'oak_leaves', 'acacia_leaves',
    'short_grass', 'tall_grass',
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
    return 60


# =============================================================================
# COORDINATE TRANSFORM (same anchor fit as Phase A/B/C)
# =============================================================================
ANCHOR_POINTS = [
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
# SINKHOLE: dig a 7x7 crater, replace air with stone layers
# =============================================================================
def draw_sinkhole(level, x, z, depth=4, radius=3):
    """Dig a 7x7 crater, expose stone sides + ladder on one wall."""
    placed = 0
    gy = safe_ground_y(level, x, z)
    # Replace top soil layer (grass_block / dirt) with air
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            r = math.sqrt(dx * dx + dz * dz)
            if r > radius + 0.5:
                continue
            # Step 1: dig air at top
            for y_off in range(0, depth):
                place(level, x + dx, gy - y_off, z + dz, B('minecraft', 'air'))
                placed += 1
            # Step 2: add stone ring on the inner wall
            if r > radius - 1.5:
                for y_off in range(depth - 1, -1, -1):
                    place(level, x + dx, gy - y_off, z + dz, B('minecraft', 'cobblestone'))
                    placed += 1
            # Step 3: stone floor
            place(level, x + dx, gy - depth, z + dz, B('minecraft', 'stone'))
            placed += 1
    # Ladder on north wall
    for y_off in range(1, depth):
        place(level, x - radius, gy - y_off, z, B('minecraft', 'ladder', {'facing_direction': '4'}))
        placed += 1
    return placed


# =============================================================================
# UNDERPASS: stone_brick arch at OSM tunnel=yes way endpoints
# =============================================================================
def draw_underpass(level, x1, z1, x2, z2, name=''):
    """Stone_brick arch (5 high) at both endpoints of tunnel."""
    placed = 0
    # Draw a thick arch
    for endpoint in [(x1, z1), (x2, z2)]:
        x, z = endpoint
        gy = safe_ground_y(level, x, z)
        # Arch 5x5 footprint, 4 high
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                r = math.sqrt(dx * dx + dz * dz)
                if r > 3:
                    continue
                # Vertical pillar
                for y_off in range(1, 4):
                    if r > 2.0 or y_off > 2:
                        place(level, x + dx, gy + y_off, z + dz, B('minecraft', 'stone_bricks'))
                        placed += 1
                    else:
                        # Hollow middle (tunnel interior)
                        place(level, x + dx, gy + y_off, z + dz, B('minecraft', 'air'))
                # Sea lantern at top center
                if r < 1.5:
                    place(level, x + dx, gy + 4, z + dz, B('minecraft', 'sea_lantern'))
                    placed += 1
    return placed


# =============================================================================
# PAVILION: smooth_stone_slab roof + oak_fence posts at covered ways
# =============================================================================
def draw_pavilion_segment(level, x1, z1, x2, z2, base_block=None):
    """Draw a covered segment: smooth_stone_slab roof 1 block above ground + fence posts every 4."""
    placed = 0
    dx = abs(x2 - x1)
    dz = abs(z2 - z1)
    sx = 1 if x1 < x2 else -1
    sz = 1 if z1 < z2 else -1
    err = dx - dz
    step = 0
    x, z = x1, z1
    while True:
        gy = safe_ground_y(level, x, z)
        # Roof slab 1 block above ground (only place over the path, not on building)
        if not is_blocked(level, x, gy + 4, z):
            place(level, x, gy + 4, z, B('minecraft', 'smooth_stone_slab', {'top_slot_bit': True}))
            placed += 1
        # Posts every 4 blocks
        if step % 4 == 0:
            for y_off in range(1, 4):
                place(level, x, gy + y_off, z, B('minecraft', 'oak_fence'))
                placed += 1
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


def is_blocked(level, x, y, z):
    """Return True if there's a building block at (x,y,z) (don't place pavilion over it)."""
    try:
        b = level.get_version_block(int(x), int(y), int(z), DIM, VER)
        bn = b[0].base_name if b else 'null'
    except Exception:
        return True
    if bn in ('air', 'null', 'err'):
        return False
    if bn in REAL_GROUND_SAFE:
        return False
    return True


# =============================================================================
# NIGHT LIGHTING: lantern + glowstone along footway key points
# =============================================================================
def draw_lantern(level, x, z):
    """Place a lantern on a 2-block fence post."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    place(level, x, gy + 1, z, B('minecraft', 'oak_fence'))
    place(level, x, gy + 2, z, B('minecraft', 'oak_fence'))
    place(level, x, gy + 3, z, B('minecraft', 'lantern'))
    placed += 3
    return placed


# =============================================================================
# CROSSWALK: white_carpet zebra stripes across service way
# =============================================================================
def draw_crosswalk(level, x, z):
    """8-wide zebra crosswalk on a service road."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    for dx in range(-4, 5):
        # Alternating white/yellow stripes
        if dx % 2 == 0:
            place(level, x + dx, gy + 2, z, B('minecraft', 'white_carpet'))
        else:
            place(level, x + dx, gy + 2, z, B('minecraft', 'yellow_carpet'))
        placed += 1
    return placed


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default='worlds/working/v2.3')
    ap.add_argument('--osm', default='osm/hkust-overpass.json')
    ap.add_argument('--out', default='worlds/working/v2.4')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print(f"Loading OSM: {args.osm}")
    with open(args.osm) as f:
        osm = json.load(f)
    nodes = {n['id']: (n['lat'], n['lon']) for n in osm['elements'] if n.get('type') == 'node'}

    print("Fitting transform…")
    ax, bx, az, bz = fit_transform(ANCHOR_POINTS)

    if args.dry_run:
        # Counts
        tunnels = sum(1 for w in osm['elements'] if w.get('type') == 'way'
                      and w.get('tags', {}).get('tunnel') == 'yes')
        covered = sum(1 for w in osm['elements'] if w.get('type') == 'way'
                      and w.get('tags', {}).get('covered') == 'yes')
        cliffs = 0
        for w in osm['elements']:
            if w.get('type') != 'way':
                continue
            if w.get('tags', {}).get('natural') in ('cliff', 'rock', 'earth_bank'):
                cliffs += 1
        services = sum(1 for w in osm['elements'] if w.get('type') == 'way'
                       and w.get('tags', {}).get('highway') == 'service')
        footways = sum(1 for w in osm['elements'] if w.get('type') == 'way'
                       and w.get('tags', {}).get('highway') in ('footway', 'pedestrian'))
        print(f'  tunnels: {tunnels}')
        print(f'  covered: {covered}')
        print(f'  cliffs/rock/earth_bank: {cliffs}')
        print(f'  service roads: {services}')
        print(f'  footway+pedestrian: {footways}')
        return

    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)

    # ---- D1. Sinkholes at natural=cliff/rock/earth_bank (way centerpoints) ----
    print("\n=== Sinkholes ===")
    sink_count = 0
    sink_total = 0
    seen_pts = set()
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        t = w.get('tags', {})
        nat = t.get('natural')
        if nat not in ('cliff', 'rock', 'earth_bank'):
            continue
        nids = w.get('nodes', [])
        if not nids:
            continue
        # Use midpoint of way
        mid = nids[len(nids) // 2]
        if mid not in nodes:
            continue
        lat, lon = nodes[mid]
        x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
        # Only place one sinkhole per ~30-block cell
        cell = (x // 30, z // 30)
        if cell in seen_pts:
            continue
        seen_pts.add(cell)
        # Skip if too close to a known building (avoid digging through floors)
        gy = safe_ground_y(level, x, z)
        if gy < 55 or gy > 90:
            continue
        n_placed = draw_sinkhole(level, x, z, depth=4, radius=3)
        sink_count += 1
        sink_total += n_placed
        if sink_count >= 6:  # Cap at 6 sinkholes
            break
    print(f"  {sink_count} sinkholes, {sink_total} blocks")

    # ---- D2. Underpasses at tunnel=yes ways ----
    print("\n=== Underpasses ===")
    under_count = 0
    under_total = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('tunnel') != 'yes':
            continue
        nids = w.get('nodes', [])
        if len(nids) < 2:
            continue
        n1 = nodes.get(nids[0])
        n2 = nodes.get(nids[-1])
        if not n1 or not n2:
            continue
        x1, z1 = latlon_to_world(ax, bx, az, bz, n1[0], n1[1])
        x2, z2 = latlon_to_world(ax, bx, az, bz, n2[0], n2[1])
        n_placed = draw_underpass(level, x1, z1, x2, z2, w.get('tags', {}).get('name', ''))
        under_total += n_placed
        under_count += 1
    print(f"  {under_count} underpasses, {under_total} blocks")

    # ---- D3. Pavilions on covered=yes ways ----
    print("\n=== Pavilions (covered ways) ===")
    pav_count = 0
    pav_total = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('covered') != 'yes':
            continue
        nids = w.get('nodes', [])
        if len(nids) < 2:
            continue
        # Skip very short ways (≤ 2 nodes)
        if len(nids) <= 2:
            continue
        seg_total = 0
        for i in range(len(nids) - 1):
            a, b = nodes.get(nids[i]), nodes.get(nids[i + 1])
            if not a or not b:
                continue
            x1, z1 = latlon_to_world(ax, bx, az, bz, a[0], a[1])
            x2, z2 = latlon_to_world(ax, bx, az, bz, b[0], b[1])
            seg_total += draw_pavilion_segment(level, x1, z1, x2, z2)
        pav_total += seg_total
        pav_count += 1
        if pav_count % 10 == 0:
            print(f"    … {pav_count} pavilions, {pav_total} blocks")
    print(f"  {pav_count} pavilion segments, {pav_total} blocks")

    # ---- D4. Lanterns along key footway nodes (every ~10 blocks) ----
    print("\n=== Night lighting (lanterns) ===")
    light_count = 0
    light_total = 0
    sampled_cells = set()
    # Sample footway midpoints
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('highway') not in ('footway', 'pedestrian', 'path'):
            continue
        nids = w.get('nodes', [])
        if len(nids) < 3:
            continue
        # Take every 4th node as a lantern candidate
        for i in range(2, len(nids) - 2, 4):
            nid = nids[i]
            if nid not in nodes:
                continue
            lat, lon = nodes[nid]
            x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
            cell = (x // 12, z // 12)
            if cell in sampled_cells:
                continue
            sampled_cells.add(cell)
            n_placed = draw_lantern(level, x, z)
            light_total += n_placed
            light_count += 1
    print(f"  {light_count} lanterns, {light_total} blocks")

    # ---- D5. Crosswalks at service roads ----
    print("\n=== Crosswalks (service roads) ===")
    cross_count = 0
    cross_total = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('highway') != 'service':
            continue
        nids = w.get('nodes', [])
        if len(nids) < 6:
            continue
        # Take midpoint
        mid = len(nids) // 2
        nid = nids[mid]
        if nid not in nodes:
            continue
        lat, lon = nodes[nid]
        x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
        cell = (x // 25, z // 25)
        if cell in sampled_cells:
            continue
        sampled_cells.add(cell)
        n_placed = draw_crosswalk(level, x, z)
        cross_total += n_placed
        cross_count += 1
        if cross_count >= 12:  # Cap at 12 crosswalks
            break
    print(f"  {cross_count} crosswalks, {cross_total} blocks")

    print(f"\nTotal placed: {sink_total + under_total + pav_total + light_total + cross_total} blocks")
    print(f"  sinkholes: {sink_total}")
    print(f"  underpasses: {under_total}")
    print(f"  pavilions: {pav_total}")
    print(f"  lanterns: {light_total}")
    print(f"  crosswalks: {cross_total}")

    print(f"\nSaving to {args.out}…")
    level.save()
    level.close()
    print("Done.")


if __name__ == '__main__':
    main()