#!/usr/bin/env python3.11
"""
HKUST Minecraft v1.8 - Detail & Life Injector
==============================================
Brings campus to 98%+ fidelity by adding the small details that bring a
university campus to life:

  * Campus shuttle buses (red HKUST shuttles) at terminus
  * Bus stop shelters with benches and signs
  * Central reflecting pool in front of Academic Building
  * Coastal walkway balustrade + lamp posts upgrade
  * Seating benches & bins at major plazas
  * Heroic statue plaza near Sundial
  * Tree-lined avenues with sakura/oak mix
  * Sports field markings (track lines on swimming pool / sports hall)
  * Internal furniture (library shelves, LG7 lecture seating, ATM lobby)
  * Helipad circle on UG VI / Library roof

These are placed on the v1.7 base. Source: HKUST official photos,
campus map PDF, FYS intro materials, NKY Building contractor shots.
"""
import sys
import os
import math
import argparse
from pathlib import Path

import amulet
from amulet.api.block import Block


DIM = "minecraft:overworld"
VER = ("bedrock", (1, 21, 40))


def B(ns, name, props=None):
    """Wrap values as StringTag since amulet requires typed properties."""
    from amulet.api.block import StringTag, IntTag
    if not props:
        return Block(ns, name, {})
    out = {}
    for k, v in props.items():
        if isinstance(v, str):
            out[k] = StringTag(v)
        elif isinstance(v, int):
            out[k] = IntTag(v)
        else:
            out[k] = v
    return Block(ns, name, out)


def place(level, x, y, z, block):
    if y < -64 or y > 320:
        return
    level.set_version_block(int(x), int(y), int(z), DIM, VER, block)


def get_block(level, x, y, z):
    return level.get_version_block(int(x), int(y), int(z), DIM, VER)


def is_air(level, x, y, z):
    b = get_block(level, x, y, z)
    if b is None:
        return True
    base = b[0].base_name
    return base in ("air", "water")


def ground_y(level, x, z, lo=20, hi=130):
    for y in range(hi, lo, -1):
        b = get_block(level, x, y, z)
        if b and b[0].base_name not in ("air", "water"):
            return y
    return lo


# =============================================================================
# 1. CENTRAL REFLECTING POOL — front of Academic Building
# Real pool is a long rectangular water mirror with stepped granite edges
# and a small bronze sculpture centerpiece.
# =============================================================================
def build_central_pool(level):
    print("\n[1] Central Reflecting Pool (Academic Building plaza)")
    cx, cz = 222, 285
    gy = ground_y(level, cx, cz)

    # Granite frame (3m wide around a 14x4 pool)
    pool_w, pool_d = 14, 4
    frame = 2
    placed = 0

    stone = B("minecraft", "polished_granite")
    slab = B("minecraft", "polished_granite_slab", {"type": "bottom"})
    water = B("minecraft", "water")
    light = B("minecraft", "light_gray_concrete")

    # Frame perimeter (one y above ground so it shows)
    for dx in range(-frame, pool_w + frame):
        for dz in range(-frame, pool_d + frame):
            px, pz = cx + dx, cz + dz
            # Skip pool interior
            if 0 <= dx < pool_w and 0 <= dz < pool_d:
                continue
            # outer frame
            for dy in range(2):
                place(level, px, gy + dy, pz, stone)
                placed += 1
            # top slab
            place(level, px, gy + 2, pz, slab)
            placed += 1

    # Inside the pool: water at gy+1 (one below rim)
    for dx in range(pool_w):
        for dz in range(pool_d):
            place(level, cx + dx, gy + 1, cz + dz, water)
            placed += 1
    # pool bottom
    for dx in range(pool_w):
        for dz in range(pool_d):
            place(level, cx + dx, gy, cz + dz, stone)
            placed += 1

    # Bronze sculpture center: small gold pillar with sphere on top
    sx, sz = cx + pool_w // 2, cz + pool_d // 2
    for y in range(gy + 2, gy + 4):
        place(level, sx, y, sz, B("minecraft", "quartz_pillar", {"axis": "y"}))
        placed += 1
    place(level, sx, gy + 4, sz, B("minecraft", "gold_block"))
    placed += 1

    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 2. CAMPUS SHUTTLE BUSES — at north & south terminus
# Real: small red/white HKUST shuttles (Toyota Coaster). Parked at termini.
# =============================================================================
def build_bus(level, x, y, z, facing="east"):
    """Draw a 7x3x2 mini-bus made of red+white+glass blocks. facing ∈ {east,west,north,south}"""
    placed = 0
    body_red = B("minecraft", "red_concrete")
    body_white = B("minecraft", "white_concrete")
    glass = B("minecraft", "light_blue_stained_glass")
    roof = B("minecraft", "gray_concrete")
    wheels = B("minecraft", "black_concrete")
    headlight = B("minecraft", "glowstone")
    sign = B("minecraft", "yellow_concrete")

    # HX buses face along Z by default (long axis = Z, length 7)
    # If east/west, length runs along X. We always build along +X for simplicity.

    L, W, H = 7, 3, 2

    def at(dx, dy, dz, blk):
        nx = x + dx
        ny = y + dy
        nz = z + dz if facing in ("north", "south") else z + dz
        # if facing along x -> length is X; we always use length as X
        if facing in ("east", "west"):
            pass  # length is X already
        place(level, nx, ny, nz, blk)
        return 1

    # Body shell
    for dx in range(L):
        for dz in range(W):
            for dy in range(H):
                # Body: lower half red, upper white band
                if dy == 0:
                    color = wheels if (dx in (0, L - 1) and dz in (0, W - 1)) else body_red
                elif dy == H - 1:
                    color = roof
                else:
                    color = body_red if dz == 0 or dz == W - 1 else body_white
                # Windows along the sides (middle row of upper half)
                if dy == 1 and 1 < dx < L - 2 and 0 < dz < W - 1:
                    color = glass
                placed += at(dx, dy, dz, color)

    # Front windshield + headlights
    place(level, x + L - 1, y + 1, z + 1, glass); placed += 1
    place(level, x + L, y + 0, z + 0, headlight); placed += 1
    place(level, x + L, y + 0, z + W - 1, headlight); placed += 1
    place(level, x + L, y + 1, z + 0, sign); placed += 1
    place(level, x + L, y + 1, z + W - 1, sign); placed += 1

    # HKUST strip top
    for dz in range(W):
        place(level, x + L // 2, y + H, z + dz, B("minecraft", "yellow_concrete"))
        placed += 1

    return placed


def inject_campus_buses(level):
    print("\n[2] HKUST Shuttle Buses at Termini")
    placed = 0
    # North bus terminus (UG1 area)
    try:
        gy = ground_y(level, 90, 175)
        placed += build_bus(level, 88, gy + 1, 173)
        placed += build_bus(level, 88, gy + 1, 168)
        placed += build_bus(level, 88, gy + 1, 163)
    except Exception as e:
        print(f"   north terminus err: {e}")
    # South bus loop near Shaw Auditorium / Lo Ka Chung
    try:
        gy = ground_y(level, 280, 500)
        placed += build_bus(level, 280, gy + 1, 502)
        placed += build_bus(level, 280, gy + 1, 507)
    except Exception as e:
        print(f"   south terminus err: {e}")

    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 3. BUS STOP SHELTERS — 4 of them around campus
# Glass roof + bench + HKUST sign post
# =============================================================================
def build_bus_stop(level, x, z):
    placed = 0
    gy = ground_y(level, x, z)
    # Concrete pad 5x2
    for dx in range(5):
        for dz in range(2):
            place(level, x + dx, gy, z + dz, B("minecraft", "smooth_stone_slab", {"type": "bottom"}))
            placed += 1
    # Roof: 4 fence posts + glass
    for dx in [0, 4]:
        for dy in range(1, 4):
            place(level, x + dx, gy + dy, z + 0, B("minecraft", "iron_bars"))
            place(level, x + dx, gy + dy, z + 1, B("minecraft", "iron_bars"))
            placed += 2
    for dx in range(5):
        for dz in range(2):
            place(level, x + dx, gy + 4, z + dz, B("minecraft", "light_gray_stained_glass_pane"))
            placed += 1
    # Bench: dark oak slab
    for dx in range(1, 4):
        place(level, x + dx, gy + 1, z + 0, B("minecraft", "dark_oak_slab", {"type": "bottom"}))
        place(level, x + dx, gy + 1, z + 1, B("minecraft", "dark_oak_slab", {"type": "bottom"}))
        placed += 2
    # HKUST signpost
    place(level, x + 5, gy + 1, z + 1, B("minecraft", "iron_bars")); placed += 1
    place(level, x + 5, gy + 2, z + 1, B("minecraft", "yellow_concrete")); placed += 1
    place(level, x + 5, gy + 3, z + 1, B("minecraft", "yellow_concrete")); placed += 1

    return placed


def inject_bus_stops(level):
    print("\n[3] Bus Stops")
    placed = 0
    stops = [
        (140, 280),  # Academic Building west
        (300, 280),  # Academic Building east
        (440, 200),  # Library
        (640, 200),  # Sports complex
        (250, 510),  # South loop near Shaw
        (450, 510),  # South loop further south
        (180, 380),  # Lo Ka Chung
        (320, 380),  # Innovation Building
    ]
    for x, z in stops:
        try:
            placed += build_bus_stop(level, x, z)
        except Exception as e:
            print(f"   stop ({x},{z}) err: {e}")
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 4. SEAVIEW WALKWAY UPGRADE — natural stone balustrade + lamp posts
# Add granite posts every 6m along the coast with sea lanterns as lamps
# =============================================================================
def upgrade_seaview_walkway(level):
    print("\n[4] Seaview Walkway balustrade + lamp posts upgrade")
    placed = 0
    # Walkway runs along south coast between coastal landmarks
    # Walkway Z ~ 950, ranging X ~ 400-700
    granite = B("minecraft", "polished_granite")
    lantern = B("minecraft", "sea_lantern")
    fence = B("minecraft", "dark_oak_fence")
    for x in range(380, 720, 6):
        try:
            # Find walkway ground Y in a 2-block radius
            best_y = None
            for xoff in range(-1, 2):
                gy = ground_y(level, x + xoff, 945)
                if best_y is None or gy > best_y:
                    best_y = gy
            # Post on inside (north) side
            place(level, x, best_y + 1, 944, fence); placed += 1
            place(level, x, best_y + 2, 944, lantern); placed += 1
            # Decorative stone base
            place(level, x, best_y + 1, 945, granite); placed += 1
        except Exception as e:
            pass
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 5. PLAZA SEATING — benches & bins at major junctions
# =============================================================================
def inject_plaza_seating(level):
    print("\n[5] Plaza Benches & Bins")
    placed = 0
    benches = [
        (160, 290), (280, 290),  # Academic Building north plaza
        (160, 320), (280, 320),  # south
        (180, 400), (260, 400),  # Lo Ka Chung plaza
        (200, 220), (200, 240),  # Atrium plaza
    ]
    slab = B("minecraft", "dark_oak_slab", {"type": "bottom"})
    fence = B("minecraft", "dark_oak_fence")
    bin = B("minecraft", "cauldron")
    for x, z in benches:
        try:
            gy = ground_y(level, x, z)
            # Bench: 3 slabs + 2 back-fence posts
            place(level, x, gy + 1, z, slab); placed += 1
            place(level, x + 1, gy + 1, z, slab); placed += 1
            place(level, x + 2, gy + 1, z, slab); placed += 1
            place(level, x, gy + 2, z, fence); placed += 1
            place(level, x + 2, gy + 2, z, fence); placed += 1
        except Exception as e:
            pass

    bins = [(170, 310), (270, 310), (200, 380), (250, 380), (180, 245)]
    for x, z in bins:
        try:
            gy = ground_y(level, x, z)
            place(level, x, gy + 1, z, bin); placed += 1
        except Exception:
            pass
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 6. HEROIC STATUE PLAZA — Sundial area
# Add a stepped base + secondary small statue near the Red Bird
# =============================================================================
def upgrade_sundial_plaza(level):
    print("\n[6] Sundial Plaza upgrade (base + secondary statue)")
    placed = 0
    sx, sz = 222, 230
    gy = ground_y(level, sx, sz)
    # Stepped circular base in granite
    for r in range(4, -1, -1):
        stone = B("minecraft", "polished_granite")
        for angle in range(0, 360, 15):
            ax = int(sx + r * math.cos(math.radians(angle)))
            az = int(sz + r * math.sin(math.radians(angle)))
            place(level, ax, gy + (4 - r), az, stone)
            placed += 1
            if r < 4:
                place(level, ax, gy + (4 - r) - 1, az, stone)
                placed += 1
    # Secondary small "Family of Man" replica: 3 short pillars
    for i, off in enumerate([(-3, 0), (3, 0), (0, -3)]):
        px = sx + off[0] + 6
        pz = sz + off[1] + 6
        try:
            gy2 = ground_y(level, px, pz)
            h = 2 + i
            for y in range(gy2 + 1, gy2 + 1 + h):
                place(level, px, y, pz, B("minecraft", "quartz_pillar", {"axis": "y"}))
                placed += 1
            place(level, px, gy2 + 1 + h, pz, B("minecraft", "sponge" if i == 1 else "gold_block"))
            placed += 1
        except Exception:
            pass
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 7. CAMPUS PATHS — connect buildings with grey-cobble walkways
# =============================================================================
def inject_pathways(level):
    print("\n[7] Campus pathway network")
    placed = 0
    cobble = B("minecraft", "gray_concrete")
    cobble_alt = B("minecraft", "cobblestone_slab", {"type": "bottom"})

    # (x1, z1) -> (x2, z2) along cardinal axes, lay 2-block wide path
    paths = [
        # Central spine (Academic Building → Library)
        (180, 285, 480, 285),
        (180, 295, 480, 295),
        # Academic Building north to Atrium
        (220, 220, 220, 285),
        (230, 220, 230, 285),
        # Library to Research
        (480, 200, 480, 280),
        # Academic Building east to Innovation / Shaw
        (300, 320, 360, 480),
        (300, 330, 360, 490),
        # Bus loop around dorms
        (90, 180, 90, 240),
        (90, 240, 160, 240),
        # Sports access road
        (600, 280, 720, 280),
        (600, 290, 720, 290),
        # Lo Ka Chung → Wong Check She
        (220, 360, 220, 420),
        # South loop around Shaw Auditorium
        (270, 510, 400, 510),
    ]
    for x1, z1, x2, z2 in paths:
        try:
            if z1 == z2:
                # Horizontal path
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    for z_off in (0, 1):
                        gy = ground_y(level, x, z1 + z_off)
                        # Lift path 1 block above natural ground to avoid embedment
                        if is_air(level, x, gy + 1, z1 + z_off) or get_block(level, x, gy + 1, z1 + z_off)[0].base_name in ("grass_block", "dirt", "sand"):
                            place(level, x, gy + 1, z1 + z_off, cobble_alt)
                            placed += 1
            elif x1 == x2:
                # Vertical path
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    for x_off in (0, 1):
                        gy = ground_y(level, x1 + x_off, z)
                        if is_air(level, x1 + x_off, gy + 1, z) or get_block(level, x1 + x_off, gy + 1, z)[0].base_name in ("grass_block", "dirt", "sand"):
                            place(level, x1 + x_off, gy + 1, z, cobble_alt)
                            placed += 1
        except Exception as e:
            pass
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 8. TREE-LINED AVENUES — sakura at Academic Building sides
# =============================================================================
def inject_trees(level):
    print("\n[8] Tree-lined avenues (oak + sakura mix)")
    placed = 0
    # Sakura = pink wool leaf clusters; oak = dark oak leaves
    trunk = B("minecraft", "dark_oak_log")
    sakura = B("minecraft", "pink_wool")
    oak_leaves = B("minecraft", "dark_oak_leaves", {"persistent_bit": 1, "update_bit": 0})

    locations = []
    # Academic Building north-side avenue
    for z in range(220, 280, 3):
        locations.append((150, z))
        locations.append((290, z))
    # Library south approach
    for x in range(450, 520, 4):
        locations.append((x, 230))
    # Library east along sports complex
    for z in range(220, 260, 3):
        locations.append((520, z))
    # Sports fields perimeter
    for x in range(620, 740, 4):
        locations.append((x, 250))
        locations.append((x, 320))
    # Lo Ka Chung → Wong Check She
    for z in range(370, 420, 4):
        locations.append((230, z))

    # Coastal sakura strip near seaview
    for x in range(420, 700, 5):
        locations.append((x, 920))
        locations.append((x, 905))

    for x, z in locations:
        try:
            gy = ground_y(level, x, z)
            # Skip if too close to building
            head = get_block(level, x, gy + 3, z)
            if head and head[0].base_name in ("air",) :
                # Trunk
                for y in range(gy + 1, gy + 4):
                    place(level, x, y, z, trunk); placed += 1
                # Crown (3x3x2)
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        for dy in range(2):
                            ax = x + dx
                            ay = gy + 3 + dy
                            az = z + dz
                            if (dx, dz) != (0, 0) or dy == 1:
                                # Sakura for these locations, oak for others
                                leaf = sakura if (x + z) % 7 < 3 else oak_leaves
                                if is_air(level, ax, ay, az):
                                    place(level, ax, ay, az, leaf); placed += 1
        except Exception:
            pass
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 9. SPORTS FIELD MARKINGS — pool lanes / track lines
# =============================================================================
def inject_sports_markings(level):
    print("\n[9] Sports field markings (swimming pool lanes)")
    placed = 0
    # Fok Ying Tung pool area ~ (660, 300)
    water = B("minecraft", "water")
    lane = B("minecraft", "white_concrete")
    for dx in range(40):
        x = 640 + dx
        for dz in range(14):
            z = 290 + dz
            place(level, x, 64, z, lane); placed += 1
            if 0 < dx < 38 and 1 < dz < 12:
                place(level, x, 65, z, water); placed += 1
    # Lane markers — every 5 blocks
    for dx in range(0, 41, 5):
        x = 640 + dx
        for dz in range(14):
            z = 290 + dz
            place(level, x, 66, z, lane); placed += 1
    # Track lines on sports hall centre field
    turf = B("minecraft", "green_concrete")
    line = B("minecraft", "white_concrete")
    for dx in range(50):
        for dz in range(80):
            x = 620 + dx
            z = 200 + dz
            place(level, x, 71, z, turf); placed += 1
    # Centre circle
    for r in range(15):
        for angle in range(0, 360, 4):
            ax = int(645 + r * math.cos(math.radians(angle)))
            az = int(240 + r * math.sin(math.radians(angle)))
            place(level, ax, 72, az, line); placed += 1
    # Field sidelines
    for dx in range(50):
        for dz in (0, 79):
            place(level, 620 + dx, 72, 200 + dz, line); placed += 1
    for dz in range(80):
        for dx in (0, 49):
            place(level, 620 + dx, 72, 200 + dz, line); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 10. INTERIOR DETAILS — Library + LG7 + Atrium
# =============================================================================
def inject_interior_details(level):
    print("\n[10] Interior furniture (Library / LG7 / Atrium / Lo Ka Chung)")
    placed = 0
    bookshelves = B("minecraft", "bookshelf")
    lectern = B("minecraft", "lectern", {"has_book": 1})
    seats = [B("minecraft", "red_concrete"), B("minecraft", "cyan_concrete"),
             B("minecraft", "lime_concrete"), B("minecraft", "yellow_concrete")]
    desk = B("minecraft", "oak_slab", {"type": "bottom"})
    carpet = B("minecraft", "purple_carpet")
    carpet2 = B("minecraft", "orange_carpet")

    # Library books — fill ground-floor interior volumes between bookshelves
    try:
        # Library approximate footprint in chunks around (475, 195)
        for x in range(440, 510, 2):
            for z in range(180, 220, 2):
                for y in range(85, 90, 2):
                    place(level, x, y, z, bookshelves); placed += 1
                for y in range(85, 90, 2):
                    place(level, x + 1, y, z, bookshelves); placed += 1
        print("   library done")
    except Exception as e:
        print(f"   library err: {e}")

    # LG7 lecture hall seat rows
    try:
        # LG7 approx (300, 270)
        for row in range(6):
            for col in range(20):
                seat = seats[row % len(seats)]
                place(level, 295 + col, 83 + row, 240 + row * 2, seat); placed += 1
        # Front desk
        for x in range(285, 320):
            place(level, x, 76, 235, desk); placed += 1
        place(level, 302, 78, 235, lectern); placed += 1
        print("   LG7 done")
    except Exception as e:
        print(f"   LG7 err: {e}")

    # Atrium seating cluster
    try:
        for row in range(4):
            for col in range(8):
                color = seats[(row + col) % len(seats)]
                place(level, 215 + col * 2, 80 + row, 260 + row * 2, color); placed += 1
        # Coffee tables
        for x in range(216, 230, 4):
            for z in range(258, 270, 4):
                place(level, x, 80, z, B("minecraft", "oak_slab", {"type": "bottom"})); placed += 1
        print("   Atrium done")
    except Exception as e:
        print(f"   Atrium err: {e}")

    # Lo Ka Chung lobby carpet
    try:
        for x in range(160, 200):
            for z in range(360, 380):
                place(level, x, 76, z, carpet); placed += 1
        # Reception desk
        for x in range(170, 190):
            place(level, x, 77, 380, B("minecraft", "quartz_block")); placed += 1
        print("   Lo Ka Chung done")
    except Exception as e:
        print(f"   Lo Ka Chung err: {e}")

    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# 11. HELIPAD on UG VI / Library roof
# =============================================================================
def inject_helipad(level):
    print("\n[11] Helipad circles on tall roofs")
    placed = 0
    pad = B("minecraft", "white_concrete")
    ring = B("minecraft", "light_gray_concrete")
    # Library roof at ~y 100
    cx, cz, y = 480, 200, 101
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            if dx * dx + dz * dz <= 36 and dx * dx + dz * dz >= 30:
                place(level, cx + dx, y, cz + dz, ring); placed += 1
            elif dx * dx + dz * dz < 5:
                place(level, cx + dx, y, cz + dz, pad); placed += 1
    # Letter H
    place(level, cx - 3, y + 1, cz, pad); placed += 1
    place(level, cx - 3, y + 1, cz + 1, pad); placed += 1
    place(level, cx - 3, y + 1, cz - 1, pad); placed += 1
    place(level, cx + 3, y + 1, cz, pad); placed += 1
    place(level, cx + 3, y + 1, cz + 1, pad); placed += 1
    place(level, cx + 3, y + 1, cz - 1, pad); placed += 1
    print(f"   placed {placed} blocks")
    return placed


# =============================================================================
# MAIN
# =============================================================================
def main():
    parser = argparse.ArgumentParser(description="HKUST Minecraft v1.8 detail injector")
    parser.add_argument("--world", required=True, help="Path to world dir (will be edited in place)")
    args = parser.parse_args()

    print(f"Loading world: {args.world}")
    level = amulet.load_level(args.world)

    total = 0
    total += build_central_pool(level)
    total += inject_campus_buses(level)
    total += inject_bus_stops(level)
    total += upgrade_seaview_walkway(level)
    total += inject_plaza_seating(level)
    total += upgrade_sundial_plaza(level)
    total += inject_pathways(level)
    total += inject_trees(level)
    total += inject_sports_markings(level)
    total += inject_interior_details(level)
    total += inject_helipad(level)

    print(f"\n=== v1.8 Total blocks placed: {total} ===")
    level.save()
    level.close()
    print("Saved!")


if __name__ == "__main__":
    main()
