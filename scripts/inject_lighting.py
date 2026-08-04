#!/usr/bin/env python3
"""
v1.6: Lighting system — make the campus glow at night.
- Streetlights along all paths and roads (sea lanterns on fence posts)
- Window glow on buildings (glowstone behind glass)
- Accent floodlights on landmarks (dome, sundial, fountain)
- Lanterns on benches and key buildings
- Light strips in underground passages
"""
import sys
import math
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.5e"
DST = WORKDIR / "worlds/working/v1.6"

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


SEA_LANTERN = B("minecraft", "sea_lantern")
GLOWSTONE = B("minecraft", "glowstone")
LANTERN = B("minecraft", "lantern")
OAK_FENCE = B("minecraft", "oak_fence")
IRON_BARS = B("minecraft", "iron_bars")
REDSTONE_LAMP = B("minecraft", "redstone_lamp")
TORCH = B("minecraft", "torch")
SOUL_TORCH = B("minecraft", "soul_torch")
SHROOMLIGHT = B("minecraft", "shroomlight")
END_ROD = B("minecraft", "end_rod")
OAK_LOG = B("minecraft", "oak_log")
STONE_BRICKS = B("minecraft", "stone_bricks")
LIGHT_GRAY_CONCRETE = B("minecraft", "light_gray_concrete")
QUARTZ_BLOCK = B("minecraft", "quartz_block")


def get_block(level, x, y, z):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    return level.get_version_block(x, y, z, dim, ver)


def place(level, x, y, z, block):
    dim = "minecraft:overworld"
    ver = ("bedrock", (1, 21, 40))
    level.set_version_block(x, y, z, dim, ver, block)


def get_ground_y(level, x, z):
    for y in range(120, 30, -1):
        b = get_block(level, x, y, z)
        if b and b[0].base_name not in ("air", "water"):
            return y
    return 60


def add_streetlight(level, x, z, height=4):
    """Place a streetlight at (x, z) — fence post + sea lantern on top."""
    placed = 0
    gy = get_ground_y(level, x, z)
    if gy < 30:
        return 0
    for dy in range(height):
        place(level, x, gy + 1 + dy, z, OAK_FENCE)
        placed += 1
    place(level, x, gy + height + 1, z, SEA_LANTERN)
    placed += 1
    return placed


def add_path_lights(level, points, spacing=8):
    """Place streetlights along a polyline defined by points."""
    placed = 0
    for i in range(len(points) - 1):
        x1, z1 = points[i]
        x2, z2 = points[i + 1]
        dx, dz = x2 - x1, z2 - z1
        dist = max(abs(dx), abs(dz))
        steps = max(1, dist // spacing)
        for s in range(steps + 1):
            t = s / max(1, steps)
            x = int(round(x1 + dx * t))
            z = int(round(z1 + dz * t))
            placed += add_streetlight(level, x, z, height=4)
    return placed


def add_window_glow(level, cx, cz, w, d, height):
    """Add glowstone behind windows on a building's facade."""
    placed = 0
    gy = get_ground_y(level, cx, cz) + 1
    if gy < 30:
        return 0
    # For each floor, place glowstone behind front/back windows
    for floor in range(1, height):
        for dx in range(1, w - 1, 2):
            # Front wall (z = cz - d//2)
            place(level, cx - w // 2 + dx, gy + floor, cz - d // 2 - 1, GLOWSTONE)
            place(level, cx - w // 2 + dx, gy + floor, cz + d // 2 + 1, GLOWSTONE)
            placed += 2
    return placed


def add_accent_floodlight(level, cx, cz, base_y, height):
    """Add a tall quartz pillar with sea lantern at top (floodlight)."""
    placed = 0
    for dy in range(height):
        place(level, cx, base_y + dy, cz, QUARTZ_BLOCK)
        placed += 1
    place(level, cx, base_y + height, cz, SEA_LANTERN)
    placed += 1
    # Surrounding glowstone at base
    for dx, dz in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
        place(level, cx + dx, base_y, cz + dz, GLOWSTONE)
        placed += 1
    return placed


def add_lantern_row(level, points, spacing=6):
    """Place hanging lanterns at points."""
    placed = 0
    for x, z in points:
        gy = get_ground_y(level, x, z)
        if gy < 30:
            continue
        place(level, x, gy + 5, z, LANTERN)
        placed += 1
    return placed


def add_chandelier(level, x, z, gy):
    """Central chandelier at (x, z) hanging at gy."""
    placed = 0
    place(level, x, gy, z, OAK_FENCE)
    place(level, x, gy + 1, z, GLOWSTONE)
    placed += 2
    # Cross arms
    for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        place(level, x + dx, gy + 1, z + dz, GLOWSTONE)
        placed += 1
    return placed


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    total = 0
    print("\n=== Lighting system ===")

    # 1. Path lights along main paths (same as v1.4-detailed paths)
    print("  → Path lights")
    central_path = [(200, 200), (350, 200)]
    total += add_path_lights(level, central_path, spacing=10)

    north_south = [(210, 150), (210, 300)]
    total += add_path_lights(level, north_south, spacing=10)

    dorm_loop = [(130, 330), (610, 330)]
    total += add_path_lights(level, dorm_loop, spacing=15)

    lakeside = [(50, 100), (50, 180)]
    total += add_path_lights(level, lakeside, spacing=10)

    sports_path = [(90, 230), (90, 380)]
    total += add_path_lights(level, sports_path, spacing=10)

    east_bus = [(360, 380), (360, 430)]
    total += add_path_lights(level, east_bus, spacing=8)

    # Road lights
    main_ew = [(60, 380), (620, 380)]
    total += add_path_lights(level, main_ew, spacing=20)

    main_ns = [(90, 200), (90, 380)]
    total += add_path_lights(level, main_ns, spacing=20)

    print(f"  Path lights placed: {total}")

    # 2. Window glow on major buildings
    print("  → Window glow on major buildings")
    buildings = [
        # (cx, cz, w, d, height)
        (210, 185, 60, 50, 7),   # Academic Building
        (230, 220, 90, 25, 5),   # LG Complex
        (130, 100, 40, 35, 8),   # Library Extension
        (90, 230, 50, 50, 6),    # Sports Hall
        (280, 240, 30, 25, 4),   # Wong Check She Center
        (150, 300, 40, 14, 9),   # UG Hall I
        (195, 310, 40, 14, 9),   # UG Hall II
        (245, 310, 50, 14, 10),  # UG Hall VII
        (280, 290, 50, 14, 9),   # PG Hall I
        (320, 310, 45, 14, 7),   # PG Hall II
        (360, 290, 40, 14, 9),   # UG Hall III
        (410, 290, 40, 14, 9),   # UG Hall IV
        (470, 290, 40, 12, 14),  # UG Hall VI (tallest)
        (530, 290, 40, 14, 9),   # UG Hall VIII
        (590, 290, 40, 14, 9),   # UG Hall IX
        (360, 410, 40, 30, 2),   # Bus Terminus
    ]
    for cx, cz, w, d, h in buildings:
        n = add_window_glow(level, cx, cz, w, d, h)
        total += n
    print(f"  Window glow placed: {n * len(buildings)}")

    # 3. Accent floodlights on landmarks
    print("  → Landmark accent lighting")
    # Dome floodlights (4 around base)
    for dx, dz in [(-12, -12), (12, -12), (-12, 12), (12, 12)]:
        gy = get_ground_y(level, 220 + dx, 160 + dz) + 1
        total += add_accent_floodlight(level, 220 + dx, 160 + dz, gy, 6)

    # Sundial accent (4 cardinal)
    for dx, dz in [(-12, 0), (12, 0), (0, -12), (0, 12)]:
        gy = get_ground_y(level, 222 + dx, 230 + dz) + 1
        total += add_accent_floodlight(level, 222 + dx, 230 + dz, gy, 4)

    # Fountain accent (4 around)
    for dx, dz in [(-10, -10), (10, -10), (-10, 10), (10, 10)]:
        gy = get_ground_y(level, 220 + dx, 240 + dz) + 1
        total += add_accent_floodlight(level, 220 + dx, 240 + dz, gy, 5)

    # Atrium central chandelier
    gy_atrium = get_ground_y(level, 220, 210) + 8
    total += add_chandelier(level, 220, 210, gy_atrium)

    # Library chandelier
    gy_lib = get_ground_y(level, 130, 100) + 10
    total += add_chandelier(level, 130, 100, gy_lib)

    # Sports Hall central light
    gy_sh = get_ground_y(level, 90, 230) + 8
    total += add_chandelier(level, 90, 230, gy_sh)

    # 4. Lanterns along Atrium perimeter
    atrium_perim = [(205, 195), (235, 195), (205, 225), (235, 225)]
    total += add_lantern_row(level, atrium_perim, spacing=4)

    # 5. Entrance lanterns at major buildings
    print("  → Entrance lanterns")
    entrance_lanterns = [
        (180, 185), (240, 185),  # Academic Building entrance
        (200, 220), (260, 220),  # LG Complex
        (110, 100), (150, 100),  # Library
        (70, 230), (110, 230),   # Sports Hall
        (150, 290), (150, 310),  # UG Hall I
        (245, 290), (245, 330),  # UG Hall VII
        (360, 400), (360, 420),  # Bus Terminus
    ]
    for x, z in entrance_lanterns:
        gy = get_ground_y(level, x, z)
        if gy >= 30:
            place(level, x, gy + 2, z, LANTERN)
            total += 1

    # 6. Underpass lighting (sea lanterns along the tunnel ceiling)
    print("  → Underpass tunnel lighting")
    for x in range(248, 268, 3):
        place(level, x, 60, 252, SEA_LANTERN)
        place(level, x, 60, 258, SEA_LANTERN)
        total += 2

    # 7. Seaview Walkway accent lanterns
    print("  → Seaview walkway lanterns")
    for z in range(40, 100, 5):
        gy = get_ground_y(level, 50, z)
        if gy >= 30:
            place(level, 50, gy + 4, z, LANTERN)
            total += 1

    level.close()
    print(f"\n=== Total lighting blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    main()
