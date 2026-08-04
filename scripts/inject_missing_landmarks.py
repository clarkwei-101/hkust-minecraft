#!/usr/bin/env python3
"""
v1.7: Add the 4 missing HKUST landmarks + fix Sundial color.

Missing landmarks:
1. Armillary Sphere (浑天仪) — at UG Hall I-II junction (Fong Shu Chuen Promenade)
2. Shaw Auditorium (邵逸夫演艺中心) — at South entrance, 3-ring elliptical
3. Coastal Marine Lab (海岸海洋实验室) — at southeast waterfront
4. Jockey Club Tower / S H Ho Tower (UG Hall VI) — tallest dorm

Fix:
5. Sundial Circle of Time — change to RED (red concrete + red stained glass + red wool)
   Inspired by "Red Bird" (火鸟) — the steel sundial by Charles & Joan Walsh-Smith
"""
import sys
import math
from pathlib import Path
import shutil

WORKDIR = Path("/Users/yahweh/Desktop/ai应用社/hkust-minecraft")
SRC = WORKDIR / "worlds/working/v1.6"
DST = WORKDIR / "worlds/working/v1.7"

sys.path.insert(0, '/Users/yahweh/Library/Python/3.11/lib/python/site-packages')

from amulet import level as amulet_level
from amulet.api.block import Block


def B(ns, name):
    return Block(ns, name)


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


# Materials
RED_CONCRETE = B("minecraft", "red_concrete")
RED_WOOL = B("minecraft", "red_wool")
RED_STAINED_GLASS = B("minecraft", "red_stained_glass")
RED_TERRACOTTA = B("minecraft", "red_terracotta")
WHITE_CONCRETE = B("minecraft", "white_concrete")
BLACK_CONCRETE = B("minecraft", "black_concrete")
GOLD_BLOCK = B("minecraft", "gold_block")
QUARTZ_BLOCK = B("minecraft", "quartz_block")
QUARTZ_PILLAR = B("minecraft", "quartz_pillar")
QUARTZ_STAIRS = B("minecraft", "quartz_stairs")
LIGHT_GRAY_CONCRETE = B("minecraft", "light_gray_concrete")
GRAY_CONCRETE = B("minecraft", "gray_concrete")
SMOOTH_STONE = B("minecraft", "smooth_stone")
POLISHED_DIORITE = B("minecraft", "polished_diorite")
GLASS = B("minecraft", "glass")
SEA_LANTERN = B("minecraft", "sea_lantern")
GLOWSTONE = B("minecraft", "glowstone")
LANTERN = B("minecraft", "lantern")
OAK_PLANK = B("minecraft", "oak_planks")
OAK_LOG = B("minecraft", "oak_log")
OAK_FENCE = B("minecraft", "oak_fence")
WATER = B("minecraft", "water")
ICE = B("minecraft", "ice")
BLUE_STAINED_GLASS = B("minecraft", "blue_stained_glass")
DARK_OAK_LOG = B("minecraft", "dark_oak_log")
STONE_BRICKS = B("minecraft", "stone_bricks")
OAK_STAIRS = B("minecraft", "oak_stairs")
OAK_SLAB = B("minecraft", "oak_slab")
STONE_BRICK_SLAB = B("minecraft", "stone_brick_slab")
IRON_BLOCK = B("minecraft", "iron_block")
OAK_LEAVES = B("minecraft", "oak_leaves")
PRISMARINE = B("minecraft", "prismarine")
DARK_PRISMARINE = B("minecraft", "dark_prismarine")
CYAN_CONCRETE = B("minecraft", "cyan_concrete")
LIGHT_BLUE_CONCRETE = B("minecraft", "light_blue_concrete")
BOOKSHELF = B("minecraft", "bookshelf")
WHITE_WOOL = B("minecraft", "white_wool")
BLUE_WOOL = B("minecraft", "blue_wool")


# =============================================================================
# 1. ARMILLARY SPHERE (浑天仪) - NEW LANDMARK
# =============================================================================

def build_armillary_sphere(level):
    """
    Located at Fong Shu Chuen Promenade between UG Hall I and UG Hall II.
    Real: 1:2 scale replica of Ming Dynasty armillary sphere (1437).
    """
    print("  → 浑天仪 Armillary Sphere (NEW)")
    placed = 0
    # Position: midway between UG Hall I (150, 300) and UG Hall II (195, 310)
    cx, cz = 170, 305
    gy = get_ground_y(level, cx, cz)

    # Square stone pedestal base (3m x 3m)
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    # Pedestal column (1m tall, 2x2 stone)
    for dx in range(-1, 2):
        for dz in range(-1, 2):
            for dy in range(2, 5):
                place(level, cx + dx, gy + dy, cz + dz, QUARTZ_BLOCK)
                placed += 1

    # Armillary sphere rings — 3 concentric circles
    # Outer ring (radius 4, bronze)
    sphere_base_y = gy + 5
    for angle_deg in range(0, 360, 3):
        angle = math.radians(angle_deg)
        rx = cx + round(4 * math.cos(angle))
        rz = cz + round(4 * math.sin(angle))
        for dy in range(-2, 3):
            place(level, rx, sphere_base_y + dy, rz, GOLD_BLOCK)
            placed += 1

    # Middle ring (radius 3, gold)
    for angle_deg in range(0, 360, 4):
        angle = math.radians(angle_deg)
        rx = cx + round(3 * math.cos(angle))
        rz = cz + round(3 * math.sin(angle))
        for dy in range(-1, 3):
            place(level, rx, sphere_base_y + dy, rz, IRON_BLOCK)
            placed += 1

    # Inner ring (radius 2, iron)
    for angle_deg in range(0, 360, 5):
        angle = math.radians(angle_deg)
        rx = cx + round(2 * math.cos(angle))
        rz = cz + round(2 * math.sin(angle))
        for dy in range(0, 3):
            place(level, rx, sphere_base_y + dy, rz, QUARTZ_BLOCK)
            placed += 1

    # Central axis pole
    for dy in range(0, 8):
        place(level, cx, sphere_base_y + dy, cz, GOLD_BLOCK)
        placed += 1
    # Top pearl (axis terminator)
    place(level, cx, sphere_base_y + 8, cz, SEA_LANTERN)
    placed += 1

    # Information plaque (oak sign stand)
    place(level, cx - 4, gy + 1, cz, OAK_FENCE)
    place(level, cx - 4, gy + 2, cz, OAK_PLANK)
    place(level, cx - 4, gy + 3, cz, OAK_PLANK)
    placed += 3

    return placed


# =============================================================================
# 2. SHAW AUDITORIUM (邵逸夫演艺中心) - NEW LANDMARK
# =============================================================================

def build_shaw_auditorium(level):
    """
    Located at south entrance of campus.
    Real: 850-1,300 seat multi-purpose auditorium, 3-ring elliptical, Henning Larsen 2021.
    """
    print("  → 邵逸夫演艺中心 Shaw Auditorium (NEW)")
    placed = 0
    # Position at south entrance, around (300, 480) — far south of bus terminus
    cx, cz = 320, 480
    gy = get_ground_y(level, cx, cz)

    # Outer ellipse ring (radius ~16 along X, ~12 along Z) — quartz block
    for angle_deg in range(0, 360, 4):
        angle = math.radians(angle_deg)
        rx = cx + round(16 * math.cos(angle))
        rz = cz + round(12 * math.sin(angle))
        for dy in range(0, 8):
            place(level, rx, gy + dy + 1, rz, QUARTZ_BLOCK)
            placed += 1

    # Middle ellipse ring (radius 11, 8) — glass + white concrete
    for angle_deg in range(0, 360, 5):
        angle = math.radians(angle_deg)
        rx = cx + round(11 * math.cos(angle))
        rz = cz + round(8 * math.sin(angle))
        for dy in range(0, 7):
            if dy % 2 == 0:
                place(level, rx, gy + dy + 1, rz, GLASS)
            else:
                place(level, rx, gy + dy + 1, rz, WHITE_CONCRETE)
            placed += 1

    # Inner ellipse (radius 6, 4) — sculptural core (gold)
    for angle_deg in range(0, 360, 8):
        angle = math.radians(angle_deg)
        rx = cx + round(6 * math.cos(angle))
        rz = cz + round(4 * math.sin(angle))
        for dy in range(0, 9):
            place(level, rx, gy + dy + 1, rz, GOLD_BLOCK)
            placed += 1

    # Stage platform (white concrete floor inside)
    for dx in range(-5, 6):
        for dz in range(-3, 4):
            place(level, cx + dx, gy + 1, cz + dz, WHITE_CONCRETE)
            placed += 1

    # Tiered seating (oak stairs in concentric arcs)
    for radius in [8, 9, 10]:
        for angle_deg in range(0, 360, 6):
            angle = math.radians(angle_deg)
            rx = cx + round(radius * math.cos(angle))
            rz = cz + round(radius * math.sin(angle))
            place(level, rx, gy + 2, rz, OAK_STAIRS)
            placed += 1

    # Entrance pillars (4 corners)
    for dx, dz in [(-15, 0), (15, 0), (0, -11), (0, 11)]:
        for dy in range(0, 9):
            place(level, cx + dx, gy + dy + 1, cz + dz, QUARTZ_PILLAR)
            placed += 1

    # Lanterns around perimeter
    for angle_deg in range(0, 360, 30):
        angle = math.radians(angle_deg)
        rx = cx + round(17 * math.cos(angle))
        rz = cz + round(13 * math.sin(angle))
        place(level, rx, gy + 5, rz, LANTERN)
        placed += 1

    # Sign post at entrance
    place(level, cx - 16, gy + 1, cz + 12, OAK_FENCE)
    place(level, cx - 16, gy + 2, cz + 12, OAK_PLANK)
    placed += 2

    return placed


# =============================================================================
# 3. COASTAL MARINE LAB (海岸海洋实验室) - NEW LANDMARK
# =============================================================================

def build_coastal_marine_lab(level):
    """
    Real: Located at southeast waterfront, direct seawater access.
    Two buildings: lab + aquarium. Modern gray concrete + glass.
    """
    print("  → 海岸海洋实验室 Coastal Marine Lab (NEW)")
    placed = 0
    # Position at southeast coast around (550, 60)
    cx, cz = 550, 60
    gy = get_ground_y(level, cx, cz)

    # Main lab building (gray concrete + glass)
    # 30 wide x 12 deep x 8 tall
    for dx in range(-15, 16):
        for dz in range(-6, 7):
            for dy in range(0, 8):
                # Walls and glass
                if dx == -15 or dx == 15 or dz == -6 or dz == 6:
                    if dy > 0 and dy < 7 and (dy % 2 == 1):
                        place(level, cx + dx, gy + 1 + dy, cz + dz, GLASS)
                    else:
                        place(level, cx + dx, gy + 1 + dy, cz + dz, GRAY_CONCRETE)
                    placed += 1
                elif dy == 0 or dy == 7:
                    place(level, cx + dx, gy + 1 + dy, cz + dz, GRAY_CONCRETE)
                    placed += 1
                elif dy == 4:  # Floor split
                    place(level, cx + dx, gy + 1 + dy, cz + dz, LIGHT_GRAY_CONCRETE)
                    placed += 1

    # Aquarium extension (cyan-tinted glass dome behind main lab)
    cx2, cz2 = 550, 45
    gy2 = get_ground_y(level, cx2, cz2)
    for dx in range(-10, 11):
        for dz in range(-8, 9):
            # Hemispheric dome
            d = math.sqrt(dx * dx + dz * dz)
            if d <= 10:
                h = int(math.sqrt(max(0, 100 - d * d)))
                for dy in range(0, h + 1):
                    if d <= 8:
                        place(level, cx2 + dx, gy2 + 1 + dy, cz2 + dz, BLUE_STAINED_GLASS)
                    else:
                        place(level, cx2 + dx, gy2 + 1 + dy, cz2 + dz, LIGHT_BLUE_CONCRETE)
                    placed += 1

    # Seawater intake pipes (prismarine columns going into water)
    for pipe_x in [-12, -8, -4, 0, 4, 8, 12]:
        for y in range(gy - 2, gy + 5):
            place(level, cx + pipe_x, y, cz - 7, PRISMARINE)
            placed += 1
        place(level, cx + pipe_x, gy + 5, cz - 7, DARK_PRISMARINE)
        placed += 1

    # Sign at entrance
    place(level, cx + 16, gy + 1, cz, OAK_FENCE)
    place(level, cx + 16, gy + 2, cz, OAK_PLANK)
    place(level, cx + 16, gy + 3, cz, BLUE_STAINED_GLASS)
    placed += 3

    # Boat dock (oak planks extending into water)
    for dz in range(8, 18):
        for dx in range(-2, 3):
            place(level, cx + dx, gy, cz + dz, OAK_PLANK)
            placed += 1
    # Dock lanterns
    for dz in [10, 14, 18]:
        place(level, cx, gy + 2, cz + dz, LANTERN)
        placed += 1

    return placed


# =============================================================================
# 4. JOCKEY CLUB TOWER / S H HO TOWER (UG HALL VI) - NEW LANDMARK
# =============================================================================

def build_jockey_club_tower(level):
    """
    Real: Tallest undergraduate residence (42m).
    We already have UG Hall VI in manual_buildings.json (42m, light gray).
    Upgrade with prominent signage + detailed windows.
    """
    print("  → 赛马会楼 / 何善衡楼 (UG Hall VI enhanced)")
    placed = 0
    cx, cz = 470, 290  # UG Hall VI location from manual_buildings.json

    # The building was already drawn, just add:
    # 1. Distinctive tower crown (red concrete accent on top)
    gy = get_ground_y(level, cx, cz)
    for dx in range(-3, 4):
        for dz in range(-2, 3):
            place(level, cx + dx, gy + 14, cz + dz, RED_CONCRETE)
            placed += 1

    # 2. Rooftop beacon (sea lantern visible from afar)
    place(level, cx, gy + 15, cz, SEA_LANTERN)
    placed += 1

    # 3. HKUST logo panel (3 Greek letters upsilon/psi/tau) at base
    # Using quartz pillars with red tops to spell U/P/T
    # Place 3 pillars along front facade
    for i, dx in enumerate([-15, -10, -5]):
        for dy in range(0, 3):
            place(level, cx + dx, gy + 1 + dy, cz - 7, QUARTZ_PILLAR)
            placed += 1
        place(level, cx + dx, gy + 4, cz - 7, RED_CONCRETE)
        placed += 1

    # 4. Year of founding plaque (1991)
    place(level, cx + 18, gy + 1, cz, OAK_FENCE)
    place(level, cx + 18, gy + 2, cz, GOLD_BLOCK)
    place(level, cx + 18, gy + 3, cz, GOLD_BLOCK)
    placed += 3

    return placed


# =============================================================================
# 5. RED SUNDIAL (CIRCLE OF TIME) - FIX COLOR
# =============================================================================

def fix_sundial_color(level):
    """
    Replace existing Sundial (built from POLISHED_DIORITE + QUARTZ_PILLAR)
    with a RED version to match real HKUST's "Red Bird" 火鸟.
    Real: Red steel sculpture by Charles & Joan Walsh-Smith (1991),
    8.5m tall, on a stepped podium in a flowing pool, with carved mural.
    """
    print("  → Sundial: 改用红色 (火鸟 Red Bird)")
    placed = 0
    cx, cz = 222, 230
    gy = get_ground_y(level, cx, cz)

    # Clear existing Sundial area
    for dx in range(-12, 13):
        for dz in range(-12, 13):
            for y in range(gy, gy + 16):
                cur = get_block(level, cx + dx, y, cz + dz)
                if cur and cur[0].base_name in (
                    "polished_diorite", "quartz_pillar", "quartz_block",
                    "quartz_stairs", "sea_lantern", "smooth_stone", "water",
                    "gold_block",
                ):
                    place(level, cx + dx, y, cz + dz, B("minecraft", "air"))
                    placed += 1

    # Stepped podium (4 concentric squares — red stone)
    for tier, (r, h) in enumerate([(10, 1), (7, 2), (4, 3), (2, 4)]):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                # Only outer ring of each tier
                if abs(dx) == r or abs(dz) == r:
                    for dy in range(h):
                        place(level, cx + dx, gy + 1 + dy, cz + dz, RED_TERRACOTTA)
                        placed += 1

    # Pool around the base (water)
    for dx in range(-12, 13):
        for dz in range(-12, 13):
            if max(abs(dx), abs(dz)) > 10 and max(abs(dx), abs(dz)) <= 12:
                place(level, cx + dx, gy + 1, cz + dz, WATER)
                placed += 1

    # Central red steel sculpture — twisted flame/bird shape
    # Base ring
    for angle_deg in range(0, 360, 5):
        angle = math.radians(angle_deg)
        rx = cx + round(1.5 * math.cos(angle))
        rz = cz + round(1.5 * math.sin(angle))
        for dy in range(0, 3):
            place(level, rx, gy + 5 + dy, rz, RED_CONCRETE)
            placed += 1

    # Twisted upward strokes (8 curved arms)
    for arm in range(8):
        arm_angle = math.radians(arm * 45)
        for h in range(8):
            t = h / 8
            radius = 1.5 - t * 0.5  # Narrows toward top
            twist = h * 0.4
            rx = cx + round(radius * math.cos(arm_angle + twist))
            rz = cz + round(radius * math.sin(arm_angle + twist))
            place(level, rx, gy + 5 + h, rz, RED_CONCRETE)
            placed += 1

    # Top crown (8.5m high — total height from ground)
    place(level, cx, gy + 12, cz, RED_CONCRETE)
    place(level, cx, gy + 13, cz, RED_CONCRETE)
    placed += 2

    # Top gnomon pointer (gold block — sticks up like a sundial needle)
    for dy in range(13, 18):
        place(level, cx, gy + dy, cz, GOLD_BLOCK)
        placed += 1

    # 12 zodiac ring markers (already added in v1.5 but use red stained glass)
    for i in range(12):
        angle = i * (math.pi / 6)
        rx = cx + round(9 * math.cos(angle))
        rz = cz + round(9 * math.sin(angle))
        # Replace gold with red stained glass
        cur = get_block(level, rx, gy + 1, rz)
        if cur and cur[0].base_name == "gold_block":
            place(level, rx, gy + 1, rz, RED_STAINED_GLASS)
            placed += 1

    # 4 cardinal markers (red concrete pillars)
    for angle in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        rx = cx + round(11 * math.cos(angle))
        rz = cz + round(11 * math.sin(angle))
        for dy in range(2):
            cur = get_block(level, rx, gy + 1 + dy, rz)
            if cur and cur[0].base_name != "air":
                place(level, rx, gy + 1 + dy, rz, RED_CONCRETE)
                placed += 1

    # Plaque (oak sign post at base)
    place(level, cx + 12, gy + 1, cz, OAK_FENCE)
    place(level, cx + 12, gy + 2, cz, OAK_PLANK)
    placed += 2

    return placed


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    total = 0
    print("\n=== v1.7: Completing the missing landmarks ===")

    total += build_armillary_sphere(level)
    total += build_shaw_auditorium(level)
    total += build_coastal_marine_lab(level)
    total += build_jockey_club_tower(level)
    total += fix_sundial_color(level)

    level.close()
    print(f"\n=== Total new blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    main()
