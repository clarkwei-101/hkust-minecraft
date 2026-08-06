#!/usr/bin/env python3.11
"""
HKUST Minecraft v2.3 — Phase B: Amenity & Micro-detail Injection
================================================================
Injects OSM amenity features that v2.1 left at default bedrock:
  - highway=bus_stop nodes    → red_concrete + oak_sign at road level
  - amenity=parking polygons  → black_concrete + white_carpet stripes
  - leisure=pitch polygons    → green_concrete + white_carpet stripes
  - leisure=sports_centre     → blue_concrete ring + sea_lantern accents
  - leisure=garden / park     → short_grass + poppy flower scatter
  - amenity=fountain          → water block + quartz pillar ring
  - amenity=toilets / atm     → small grey concrete + sign
  - amenity=clock             → quartz pillar + sea_lantern at top
  - amenity=taxi              → yellow_concrete pad
  - amenity=kindergarten      → orange_concrete playground
  - amenity=library           → bookshelf accent (won't duplicate existing)
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
# COORDINATE TRANSFORM (same anchor fit as Phase A)
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
# AMENITY BUILDERS
# =============================================================================
def draw_bus_stop(level, x, z, name=''):
    """Red concrete pad (3x3) + oak_sign post on side."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    # Red pad 3x3
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            place(level, x + dx, gy + 1, z + dz, B('minecraft', 'red_concrete'))
            placed += 1
    # White border
    for dx, dz in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        place(level, x + dx, gy + 1, z + dz, B('minecraft', 'white_concrete'))
        placed += 1
    # Sign post on north side
    place(level, x, gy + 2, z - 2, B('minecraft', 'oak_fence'))
    place(level, x, gy + 3, z - 2, B('minecraft', 'oak_sign', {'rotation': '4'}))
    placed += 2
    return placed


def draw_parking(level, nodes_xy):
    """Asphalt + white stripes for parking polygon. nodes_xy = [(x,z), …]."""
    if not nodes_xy:
        return 0
    placed = 0
    xs = [p[0] for p in nodes_xy]
    zs = [p[1] for p in nodes_xy]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    # Centre for ground height
    cx, cz = (minx + maxx) // 2, (minz + maxz) // 2
    gy = safe_ground_y(level, cx, cz)
    # Asphalt (black_concrete) under polygon, stripes inside
    for x in range(minx, maxx + 1):
        for z in range(minz, maxz + 1):
            # Sample ground at each cell to handle slope
            gy2 = safe_ground_y(level, x, z, lo=gy - 8, hi=gy + 8)
            place(level, x, gy2 + 1, z, B('minecraft', 'black_concrete'))
            placed += 1
            # White stripes along z axis (every 4 blocks)
            if (x - minx) % 4 == 0 and (z - minz) % 4 != 1:
                place(level, x, gy2 + 2, z, B('minecraft', 'white_carpet'))
                placed += 1
    return placed


def draw_pitch(level, nodes_xy, sport='pitch'):
    """Sport pitch — green_concrete + white_carpet boundary lines."""
    if not nodes_xy:
        return 0
    placed = 0
    xs = [p[0] for p in nodes_xy]
    zs = [p[1] for p in nodes_xy]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    cx, cz = (minx + maxx) // 2, (minz + maxz) // 2
    gy = safe_ground_y(level, cx, cz)
    # Green carpet field
    for x in range(minx, maxx + 1):
        for z in range(minz, maxz + 1):
            gy2 = safe_ground_y(level, x, z, lo=gy - 4, hi=gy + 4)
            place(level, x, gy2 + 1, z, B('minecraft', 'green_concrete'))
            placed += 1
            # White line around perimeter
            if x == minx or x == maxx or z == minz or z == maxz:
                place(level, x, gy2 + 2, z, B('minecraft', 'white_concrete'))
                placed += 1
    return placed


def draw_sports_centre(level, nodes_xy, name=''):
    """Sports centre — blue_concrete + sea_lantern corners."""
    if not nodes_xy:
        return 0
    placed = 0
    xs = [p[0] for p in nodes_xy]
    zs = [p[1] for p in nodes_xy]
    minx, maxx = min(xs), max(xs)
    minz, maxz = min(zs), max(zs)
    cx, cz = (minx + maxx) // 2, (minz + maxz) // 2
    gy = safe_ground_y(level, cx, cz)
    # 3-block-thick blue ring around perimeter
    for x in range(minx, maxx + 1):
        for z in range(minz, maxz + 1):
            gy2 = safe_ground_y(level, x, z, lo=gy - 4, hi=gy + 4)
            on_edge = x in (minx, maxx) or z in (minz, maxz)
            if on_edge:
                place(level, x, gy2 + 1, z, B('minecraft', 'blue_concrete'))
                placed += 1
                # Lamp at corners
                if (x, z) in [(minx, minz), (minx, maxz), (maxx, minz), (maxx, maxz)]:
                    place(level, x, gy2 + 2, z, B('minecraft', 'sea_lantern'))
                    placed += 1
    return placed


def draw_garden(level, nodes_xy):
    """Garden — scattered grass + flowers."""
    if not nodes_xy:
        return 0
    placed = 0
    import random
    random.seed(42)
    for x, z in nodes_xy:
        gy = safe_ground_y(level, x, z)
        for _ in range(2):
            dx = random.randint(-1, 1)
            dz = random.randint(-1, 1)
            if random.random() < 0.7:
                place(level, x + dx, gy + 1, z + dz, B('minecraft', 'short_grass'))
            else:
                flower = random.choice(['poppy', 'dandelion', 'blue_orchid',
                                         'allium', 'cornflower', 'lily_of_the_valley'])
                place(level, x + dx, gy + 1, z + dz, B('minecraft', flower))
            placed += 1
    return placed


def draw_park(level, nodes_xy):
    """Park — denser greenery + occasional oak trees."""
    if not nodes_xy:
        return 0
    placed = 0
    import random
    random.seed(43)
    for x, z in nodes_xy:
        gy = safe_ground_y(level, x, z)
        # grass
        place(level, x, gy + 1, z, B('minecraft', 'short_grass'))
        placed += 1
        # occasional oak tree (1-block trunk + 3x3 leaves at +4)
        if random.random() < 0.05:
            place(level, x, gy + 1, z, B('minecraft', 'oak_log'))
            place(level, x, gy + 2, z, B('minecraft', 'oak_log'))
            place(level, x, gy + 3, z, B('minecraft', 'oak_log'))
            place(level, x, gy + 4, z, B('minecraft', 'oak_leaves', {'persistent_bit': True}))
            placed += 4
        # flower
        if random.random() < 0.15:
            f = random.choice(['poppy', 'dandelion', 'azure_bluet'])
            place(level, x, gy + 1, z, B('minecraft', f))
            placed += 1
    return placed


def draw_fountain(level, x, z):
    """Quartz pillar ring + central water."""
    placed = 0
    gy = safe_ground_y(level, x, z)
    # 4-block radius ring
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            r = math.sqrt(dx * dx + dz * dz)
            if 3.5 < r < 4.5:
                place(level, x + dx, gy + 1, z + dz, B('minecraft', 'quartz_pillar'))
                placed += 1
            elif r <= 2:
                place(level, x + dx, gy + 1, z + dz, B('minecraft', 'water'))
                placed += 1
    # Centre accent
    place(level, x, gy + 2, z, B('minecraft', 'sea_lantern'))
    placed += 1
    return placed


def draw_clock(level, x, z):
    """Quartz pillar + sea_lantern at top."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    for y in range(gy + 1, gy + 5):
        place(level, x, y, z, B('minecraft', 'quartz_pillar'))
        placed += 1
    place(level, x, gy + 5, z, B('minecraft', 'sea_lantern'))
    placed += 1
    # 4 sign accents around base
    for dx, dz, rot in ((-2, 0, '12'), (2, 0, '14'), (0, -2, '10'), (0, 2, '8')):
        place(level, x + dx, gy + 1, z + dz, B('minecraft', 'oak_sign', {'rotation': rot}))
        placed += 1
    return placed


def draw_atm(level, x, z):
    """Small grey concrete + quartz block (banking terminal)."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    for dx, dz in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        place(level, x + dx, gy + 1, z + dz, B('minecraft', 'light_gray_concrete'))
        placed += 1
    place(level, x, gy + 2, z, B('minecraft', 'sea_lantern'))
    placed += 1
    return placed


def draw_taxi(level, x, z):
    """Yellow concrete pad."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            place(level, x + dx, gy + 1, z + dz, B('minecraft', 'yellow_concrete'))
            placed += 1
    # Letter 'T' on top
    place(level, x, gy + 2, z, B('minecraft', 'black_concrete'))
    place(level, x + 1, gy + 2, z, B('minecraft', 'black_concrete'))
    place(level, x - 1, gy + 2, z, B('minecraft', 'black_concrete'))
    place(level, x, gy + 2, z + 1, B('minecraft', 'black_concrete'))
    placed += 4
    return placed


def draw_playground(level, nodes_xy):
    """Playground — orange carpet with wood plank scattered blocks."""
    if not nodes_xy:
        return 0
    placed = 0
    import random
    random.seed(44)
    for x, z in nodes_xy:
        gy = safe_ground_y(level, x, z)
        # Sand base
        place(level, x, gy + 1, z, B('minecraft', 'sand'))
        placed += 1
        # Random equipment
        if random.random() < 0.3:
            place(level, x, gy + 2, z, B('minecraft', 'oak_fence'))
            place(level, x, gy + 3, z, B('minecraft', 'oak_fence'))
            place(level, x, gy + 4, z, B('minecraft', 'oak_planks'))
            placed += 3
        elif random.random() < 0.5:
            place(level, x, gy + 2, z, B('minecraft', 'orange_concrete'))
            placed += 1
    return placed


def draw_toilets(level, x, z):
    """Small grey structure."""
    gy = safe_ground_y(level, x, z)
    placed = 0
    for dx, dz in [(0, 0), (1, 0), (0, 1), (1, 1)]:
        place(level, x + dx, gy + 1, z + dz, B('minecraft', 'gray_concrete'))
        placed += 1
    place(level, x, gy + 2, z, B('minecraft', 'oak_door'))
    placed += 1
    return placed


# =============================================================================
# MAIN
# =============================================================================
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--world', default='worlds/working/v2.3')
    ap.add_argument('--osm', default='osm/hkust-overpass.json')
    ap.add_argument('--out', default='worlds/working/v2.3')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    print(f"Loading OSM: {args.osm}")
    with open(args.osm) as f:
        osm = json.load(f)
    nodes = {n['id']: (n['lat'], n['lon']) for n in osm['elements'] if n.get('type') == 'node'}

    print("Fitting transform…")
    ax, bx, az, bz = fit_transform(ANCHOR_POINTS)

    if args.dry_run:
        # Just print counts
        cnt = defaultdict(int)
        for n in osm['elements']:
            if n.get('type') != 'node':
                continue
            t = n.get('tags', {})
            if t.get('highway') == 'bus_stop':
                cnt['bus_stop'] += 1
            elif t.get('amenity') == 'fountain':
                cnt['fountain'] += 1
            elif t.get('amenity') == 'clock':
                cnt['clock'] += 1
            elif t.get('amenity') == 'atm':
                cnt['atm'] += 1
            elif t.get('amenity') == 'taxi':
                cnt['taxi'] += 1
            elif t.get('amenity') == 'toilets':
                cnt['toilets'] += 1
            elif t.get('amenity') == 'kindergarten':
                cnt['kindergarten'] += 1
        for w in osm['elements']:
            if w.get('type') != 'way':
                continue
            t = w.get('tags', {})
            if t.get('amenity') == 'parking':
                cnt['parking'] += 1
            if t.get('leisure') == 'pitch':
                cnt['pitch'] += 1
            if t.get('leisure') == 'sports_centre':
                cnt['sports_centre'] += 1
            if t.get('leisure') == 'garden':
                cnt['garden'] += 1
            if t.get('leisure') == 'park':
                cnt['park'] += 1
            if t.get('leisure') == 'playground':
                cnt['playground'] += 1
        for k, v in sorted(cnt.items()):
            print(f'  {k}: {v}')
        return

    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)

    placed_total = 0

    # ---- 1. Bus stops (node) ----
    print("\n=== Bus stops ===")
    bus_count = 0
    for n in osm['elements']:
        if n.get('type') != 'node':
            continue
        if n.get('tags', {}).get('highway') != 'bus_stop':
            continue
        x, z = latlon_to_world(ax, bx, az, bz, n['lat'], n['lon'])
        n_placed = draw_bus_stop(level, x, z, n.get('tags', {}).get('name', ''))
        bus_count += n_placed
        placed_total += n_placed
    print(f"  {bus_count} blocks for bus stops")

    # ---- 2. Fountain / Clock / ATM / Taxi / Toilets / Kindergarten ----
    node_specs = [
        ('amenity', 'fountain', draw_fountain, 'Fountain'),
        ('amenity', 'clock', draw_clock, 'Clock'),
        ('amenity', 'atm', draw_atm, 'ATM'),
        ('amenity', 'taxi', draw_taxi, 'Taxi'),
        ('amenity', 'toilets', draw_toilets, 'Toilets'),
    ]
    for tag_k, tag_v, fn, label in node_specs:
        cnt = 0
        for n in osm['elements']:
            if n.get('type') != 'node':
                continue
            t = n.get('tags', {})
            if t.get(tag_k) != tag_v:
                continue
            x, z = latlon_to_world(ax, bx, az, bz, n['lat'], n['lon'])
            n_placed = fn(level, x, z)
            cnt += n_placed
            placed_total += n_placed
        print(f"  {label}: {cnt} blocks")

    # ---- 3. Parking polygons (way) ----
    print("\n=== Parking polygons ===")
    park_count = 0
    park_ways = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('amenity') != 'parking':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            park_count += draw_parking(level, nxyz)
            park_ways += 1
    print(f"  {park_count} blocks across {park_ways} parking lots")

    # ---- 4. Pitches (tennis / football) ----
    print("\n=== Pitches ===")
    pitch_count = 0
    pitch_ways = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('leisure') != 'pitch':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            pitch_count += draw_pitch(level, nxyz)
            pitch_ways += 1
    print(f"  {pitch_count} blocks across {pitch_ways} pitches")

    # ---- 5. Sports centres ----
    print("\n=== Sports centres ===")
    sport_count = 0
    sport_ways = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('leisure') != 'sports_centre':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            sport_count += draw_sports_centre(level, nxyz, w.get('tags', {}).get('name', ''))
            sport_ways += 1
    print(f"  {sport_count} blocks across {sport_ways} sports centres")

    # ---- 6. Gardens ----
    print("\n=== Gardens ===")
    garden_count = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('leisure') != 'garden':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            garden_count += draw_garden(level, nxyz)
    print(f"  {garden_count} blocks in gardens")

    # ---- 7. Parks ----
    print("\n=== Parks ===")
    park_block_count = 0
    park_ways = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('leisure') != 'park':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            park_block_count += draw_park(level, nxyz)
            park_ways += 1
    print(f"  {park_block_count} blocks across {park_ways} parks")

    # ---- 8. Playgrounds ----
    print("\n=== Playgrounds ===")
    play_count = 0
    for w in osm['elements']:
        if w.get('type') != 'way':
            continue
        if w.get('tags', {}).get('leisure') != 'playground':
            continue
        nids = w.get('nodes', [])
        nxyz = []
        for nid in nids:
            if nid in nodes:
                lat, lon = nodes[nid]
                x, z = latlon_to_world(ax, bx, az, bz, lat, lon)
                nxyz.append((x, z))
        if nxyz:
            play_count += draw_playground(level, nxyz)
    print(f"  {play_count} blocks in playgrounds")

    print(f"\nTotal placed: {placed_total} blocks")

    print(f"Saving to {args.out}…")
    level.save()
    level.close()
    print("Done.")


if __name__ == '__main__':
    main()