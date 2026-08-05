#!/usr/bin/env python3
"""
HKUST Minecraft v1.7 - Complete Academic Buildings Injection
==========================================================

Adds ALL missing HKUST academic buildings based on real campus map:

Academic Buildings:
1. Lee Shau Kee Business Building (李兆基商学大楼) - Business school main building
2. Cheng Yu Tung Building (郑裕彤楼) - Engineering building
3. Lo Ka Chung University Center (卢家驄大学中心) - University center
4. Martin Ka Shing Lee Innovation Building (李家诚创科大樓) - Innovation building (NEW)
5. New Research Building 2 (新科研楼2) - Research building (NEW)
6. Jockey Club Enterprise Center (香港赛马会创新科技中心) - Innovation hub

Sports & Recreation:
7. Fok Ying Tung Sports Center (霍英东体育中心) - Sports center
8. Fok Ying Tung Swimming Pool (霍英东游泳池) - Outdoor pool

Landmarks (from inject_missing_landmarks.py):
9. Armillary Sphere (浑天仪) - Ming dynasty replica
10. Shaw Auditorium (邵逸夫演艺中心) - Performing arts center
11. Coastal Marine Lab (海岸海洋实验室) - Marine research

Already existed in v1.6:
- Academic Building (学术大楼)
- Lecture Hall LG Complex (LG1-LG7)
- Library Extension (图书馆新翼)
- S.H. Ho Sports Hall (何善衡体育馆)
- Wong Check She Research Center (黄焯书科研中心)
- All Undergraduate/Postgraduate Halls

This script adds the MISSING ones based on real HKUST campus map coordinates.
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


# =============================================================================
# MATERIALS - HKUST Color Palette
# =============================================================================

# Concrete colors (main building materials)
WHITE_CONCRETE = B("minecraft", "white_concrete")
LIGHT_GRAY_CONCRETE = B("minecraft", "light_gray_concrete")
GRAY_CONCRETE = B("minecraft", "gray_concrete")
DARK_GRAY_CONCRETE = B("minecraft", "gray_concrete")
BLACK_CONCRETE = B("minecraft", "black_concrete")
BROWN_CONCRETE = B("minecraft", "brown_concrete")

# Decorative materials
GOLD_BLOCK = B("minecraft", "gold_block")
QUARTZ_BLOCK = B("minecraft", "quartz_block")
QUARTZ_PILLAR = B("minecraft", "quartz_pillar")
IRON_BLOCK = B("minecraft", "iron_block")

# Glass
GLASS = B("minecraft", "glass")
GLASS_GRAY = B("minecraft", "gray_stained_glass")
GLASS_LIGHT_BLUE = B("minecraft", "light_blue_stained_glass")
GLASS_BLUE = B("minecraft", "blue_stained_glass")
GLASS_CYAN = B("minecraft", "cyan_stained_glass")

# Lighting
SEA_LANTERN = B("minecraft", "sea_lantern")
GLOWSTONE = B("minecraft", "glowstone")
LANTERN = B("minecraft", "lantern")

# Wood
OAK_PLANK = B("minecraft", "oak_planks")
OAK_LOG = B("minecraft", "oak_log")
OAK_FENCE = B("minecraft", "oak_fence")
OAK_SLAB = B("minecraft", "oak_slab")
DARK_OAK_PLANK = B("minecraft", "dark_oak_planks")
DARK_OAK_LOG = B("minecraft", "dark_oak_log")
BIRCH_PLANK = B("minecraft", "birch_planks")

# Stone
STONE_BRICKS = B("minecraft", "stone_bricks")
COBBLESTONE = B("minecraft", "cobblestone")
SMOOTH_STONE = B("minecraft", "smooth_stone")
POLISHED_GRANITE = B("minecraft", "polished_granite")
POLISHED_DIORITE = B("minecraft", "polished_diorite")
POLISHED_ANDESITE = B("minecraft", "polished_andesite")

# Water/Aquatic
WATER = B("minecraft", "water")
PRISMARINE = B("minecraft", "prismarine")
DARK_PRISMARINE = B("minecraft", "dark_prismarine")
SAND = B("minecraft", "sand")
GRAVEL = B("minecraft", "gravel")

# Misc
BRICK = B("minecraft", "bricks")
RED_BRICK = B("minecraft", "red_nether_brick")
OAK_DOOR = B("minecraft", "oak_door")
IRON_DOOR = B("minecraft", "iron_door")
OAK_LEAVES = B("minecraft", "oak_leaves")
GRASS = B("minecraft", "grass")
GRASS_BLOCK = B("minecraft", "grass_block")
DIRT = B("minecraft", "dirt")

# Colors for distinctive buildings
RED_CONCRETE = B("minecraft", "red_concrete")
BLUE_CONCRETE = B("minecraft", "blue_concrete")
GREEN_CONCRETE = B("minecraft", "green_concrete")
CYAN_CONCRETE = B("minecraft", "cyan_concrete")
YELLOW_CONCRETE = B("minecraft", "yellow_concrete")
ORANGE_CONCRETE = B("minecraft", "orange_concrete")
PURPLE_CONCRETE = B("minecraft", "purple_concrete")


# =============================================================================
# BUILDING CONSTRUCTION HELPERS
# =============================================================================

def build_rectangular_building(level, cx, cz, width, depth, height, wall_block, roof_block=None, has_windows=True, window_block=None):
    """Build a generic rectangular building with windows."""
    placed = 0
    gy = get_ground_y(level, cx, cz)
    
    if roof_block is None:
        roof_block = DARK_GRAY_CONCRETE
    if window_block is None:
        window_block = GLASS_LIGHT_BLUE
    
    hw = width // 2
    hd = depth // 2
    
    # Foundation
    for dx in range(-hw - 1, hw + 2):
        for dz in range(-hd - 1, hd + 2):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Walls
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window_row = has_windows and (y >= 4 and y < height + 1 and (y - 2) % 3 == 0)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                
                if is_top:
                    place(level, cx + dx, y, cz + dz, roof_block)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window_row:
                        place(level, cx + dx, y, cz + dz, window_block)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, wall_block)
                        placed += 1
    
    # Entrance door
    for dx in range(-1, 2):
        place(level, cx + dx, 2, cz + hd, OAK_DOOR)
        place(level, cx + dx, 3, cz + hd, OAK_DOOR)
        placed += 6
    
    return placed, gy


def build_tower_building(level, cx, cz, width, depth, height, wall_block, roof_block=None):
    """Build a tall tower building with distinct crown."""
    placed = 0
    gy = get_ground_y(level, cx, cz)
    
    if roof_block is None:
        roof_block = DARK_GRAY_CONCRETE
    
    hw = width // 2
    hd = depth // 2
    
    # Foundation
    for dx in range(-hw - 1, hw + 2):
        for dz in range(-hd - 1, hd + 2):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Main tower body
    for y in range(2, height + 1):
        is_crown = (y >= height - 2)
        is_window_row = (y >= 4 and (y - 2) % 3 == 0)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                
                if is_crown:
                    # Crown section
                    place(level, cx + dx, y, cz + dz, roof_block)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window_row:
                        place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, wall_block)
                        placed += 1
    
    # Crown decorations
    for dx in range(-hw, hw + 1):
        for dz in range(-hd, hd + 1):
            place(level, cx + dx, height + 2, cz + dz, roof_block)
            placed += 1
    
    # Beacon on top
    place(level, cx, height + 3, cz, SEA_LANTERN)
    placed += 1
    
    return placed, gy


# =============================================================================
# 1. LEE SHAU KEE BUSINESS BUILDING (李兆基商學大樓)
# =============================================================================

def build_lee_shau_kee_business_building(level):
    """
    Real: Lee Shau Kee Business Building - Main business school building.
    Located at south of campus, distinctive glass facade with blue accents.
    """
    print("  → 李兆基商学大楼 Lee Shau Kee Business Building")
    placed = 0
    
    # Position from OSM: mc_x=184, mc_z=626
    cx, cz = 184, 626
    
    # Build main building: 50 wide x 35 deep x 12 tall (4 floors)
    # Business school: modern glass building with blue-tinted windows
    hw, hd, height = 25, 17, 14
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation plaza
    for dx in range(-hw - 2, hw + 3):
        for dz in range(-hd - 2, hd + 3):
            place(level, cx + dx, gy + 1, cz + dz, POLISHED_GRANITE)
            placed += 1
    
    # Main facade - glass curtain wall with white concrete frame
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_floor = (y % 4 == 0)
        is_window = ((y - 2) % 3 == 0 and y >= 3 and y < height + 1)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                on_corner = (abs(dx) == hw and abs(dz) == hd)
                
                if is_top:
                    # Roof with blue tint
                    place(level, cx + dx, y, cz + dz, BLUE_CONCRETE)
                    placed += 1
                elif on_corner:
                    # Corner pillars - white concrete
                    place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_floor:
                        # Floor division line
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
                    elif is_window:
                        # Glass windows - blue tinted
                        place(level, cx + dx, y, cz + dz, GLASS_BLUE)
                        placed += 1
                    else:
                        # Concrete frame
                        place(level, cx + dx, y, cz + dz, LIGHT_GRAY_CONCRETE)
                        placed += 1
    
    # Entrance canopy (canopy extending out)
    for dx in range(-5, 6):
        for dz in range(hd + 1, hd + 4):
            place(level, cx + dx, 3, cz + dz, WHITE_CONCRETE)
            placed += 1
        place(level, cx + dx, 4, cz + dz, BLUE_CONCRETE)
        placed += 1
    
    # Main entrance doors
    for dx in range(-2, 3):
        place(level, cx + dx, 2, cz + hd, GLASS)
        place(level, cx + dx, 3, cz + hd, GLASS)
        placed += 10
    
    # University logo area (quartz with gold)
    for dx in range(-3, 4):
        place(level, cx + dx, 2, cz - hd - 1, QUARTZ_BLOCK)
        placed += 1
    place(level, cx, 3, cz - hd - 1, GOLD_BLOCK)
    placed += 1
    
    # Sign post
    place(level, cx - hw - 3, gy + 1, cz, OAK_FENCE)
    place(level, cx - hw - 3, gy + 2, cz, OAK_PLANK)
    place(level, cx - hw - 3, gy + 3, cz, QUARTZ_BLOCK)
    placed += 3
    
    return placed


# =============================================================================
# 2. CHENG YU TUNG BUILDING (鄭裕彤樓)
# =============================================================================

def build_cheng_yu_tung_building(level):
    """
    Real: Cheng Yu Tung Building - Engineering building.
    Located at north campus, brick and concrete facade.
    """
    print("  → 郑裕彤楼 Cheng Yu Tung Building")
    placed = 0
    
    # Position from OSM: mc_x=302, mc_z=460
    cx, cz = 302, 460
    
    hw, hd, height = 20, 15, 10  # 3 floors
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-hw - 1, hw + 2):
        for dz in range(-hd - 1, hd + 2):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Main building - brick facade with large windows
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window = ((y - 2) % 3 == 0 and y >= 3)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                
                if is_top:
                    place(level, cx + dx, y, cz + dz, DARK_GRAY_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        place(level, cx + dx, y, cz + dz, GLASS_GRAY)
                        placed += 1
                    else:
                        # Brick texture (orange-brown)
                        place(level, cx + dx, y, cz + dz, BRICK)
                        placed += 1
    
    # Entrance
    for dx in range(-2, 3):
        place(level, cx + dx, 2, cz + hd, OAK_DOOR)
        place(level, cx + dx, 3, cz + hd, OAK_DOOR)
        placed += 10
    
    # Engineering logo (gear-like quartz decoration)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        rx = cx + round(2 * math.cos(rad))
        rz = cz + hd + 1 + round(1 * math.sin(rad))
        place(level, rx, 3, rz, QUARTZ_PILLAR)
        placed += 1
    
    return placed


# =============================================================================
# 3. LO KA CHUNG UNIVERSITY CENTER (盧家驄大學中心)
# =============================================================================

def build_lo_ka_chung_center(level):
    """
    Real: Lo Ka Chung University Center - University administration and events center.
    Modern white building with distinctive roof structure.
    """
    print("  → 卢家驄大学中心 Lo Ka Chung University Center")
    placed = 0
    
    # Position from OSM: mc_x=165, mc_z=372
    cx, cz = 165, 372
    
    hw, hd, height = 18, 12, 8  # 2-3 floors
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation with plaza
    for dx in range(-hw - 3, hw + 4):
        for dz in range(-hd - 3, hd + 4):
            place(level, cx + dx, gy + 1, cz + dz, POLISHED_DIORITE)
            placed += 1
    
    # Main building - white concrete with large glass panels
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window = ((y - 2) % 3 == 0 and y >= 3)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                
                if is_top:
                    # Flat roof with slight overhang
                    place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        place(level, cx + dx, y, cz + dz, GLASS)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
    
    # Entrance with columns
    for dx in [-4, 0, 4]:
        for dz in range(hd + 1, hd + 3):
            for dy in range(2, height):
                place(level, cx + dx, dy, cz + dz, QUARTZ_PILLAR)
                placed += 1
    
    # University crest (gold and white)
    place(level, cx, 4, cz + hd + 1, GOLD_BLOCK)
    place(level, cx - 1, 4, cz + hd + 1, WHITE_CONCRETE)
    place(level, cx + 1, 4, cz + hd + 1, WHITE_CONCRETE)
    placed += 3
    
    return placed


# =============================================================================
# 4. MARTIN KA SHING LEE INNOVATION BUILDING (李家誠創科大樓)
# =============================================================================

def build_martin_lee_innovation_building(level):
    """
    Real: Martin Ka Shing Lee Innovation Building - Tech innovation hub.
    Modern glass building with green/sustainable features.
    """
    print("  → 李家诚创科大樓 Martin Ka Shing Lee Innovation Building")
    placed = 0
    
    # Position: south of Shaw Auditorium, around (290, 520)
    cx, cz = 290, 520
    
    hw, hd, height = 22, 14, 12  # 4 floors
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation with eco-friendly grass plaza
    for dx in range(-hw - 2, hw + 3):
        for dz in range(-hd - 2, hd + 3):
            if (dx + dz) % 4 == 0:
                place(level, cx + dx, gy + 1, cz + dz, GRASS)
                placed += 1
            else:
                place(level, cx + dx, gy + 1, cz + dz, SMOOTH_STONE)
                placed += 1
    
    # Main building - green-tinted glass facade
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window = ((y - 2) % 3 == 0 and y >= 3)
        is_green_accent = (y == height)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                on_corner = (abs(dx) == hw and abs(dz) == hd)
                
                if is_top:
                    # Green roof garden
                    place(level, cx + dx, y, cz + dz, GREEN_CONCRETE)
                    placed += 1
                elif on_corner:
                    place(level, cx + dx, y, cz + dz, GREEN_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        # Green-tinted glass
                        place(level, cx + dx, y, cz + dz, GLASS_CYAN)
                        placed += 1
                    elif is_green_accent:
                        place(level, cx + dx, y, cz + dz, GREEN_CONCRETE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
    
    # Solar panel arrays on roof (dark blocks)
    for dx in range(-hw + 2, hw - 2, 4):
        for dz in range(-hd + 2, hd - 2, 4):
            place(level, cx + dx, height + 2, cz + dz, BLACK_CONCRETE)
            placed += 1
    
    # Entrance with green accent
    for dx in range(-3, 4):
        place(level, cx + dx, 2, cz + hd, IRON_DOOR)
        place(level, cx + dx, 3, cz + hd, IRON_DOOR)
        placed += 14
    
    # Innovation hub sign
    place(level, cx - hw - 2, gy + 1, cz, OAK_FENCE)
    place(level, cx - hw - 2, gy + 2, cz, GREEN_CONCRETE)
    place(level, cx - hw - 2, gy + 3, cz, GOLD_BLOCK)
    placed += 3
    
    return placed


# =============================================================================
# 5. NEW RESEARCH BUILDING 2 (新科研樓2)
# =============================================================================

def build_new_research_building_2(level):
    """
    Real: New Research Building 2 - Modern research facility.
    Contemporary glass and concrete design.
    """
    print("  → 新科研楼2 New Research Building 2")
    placed = 0
    
    # Position: near Shaw Auditorium, around (340, 510)
    cx, cz = 340, 510
    
    hw, hd, height = 16, 12, 10  # 3 floors
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-hw - 1, hw + 2):
        for dz in range(-hd - 1, hd + 2):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Main building - modern glass and concrete
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window = ((y - 2) % 3 == 0 and y >= 3)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                on_corner = (abs(dx) == hw and abs(dz) == hd)
                
                if is_top:
                    place(level, cx + dx, y, cz + dz, GRAY_CONCRETE)
                    placed += 1
                elif on_corner:
                    place(level, cx + dx, y, cz + dz, QUARTZ_BLOCK)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        place(level, cx + dx, y, cz + dz, GLASS)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, LIGHT_GRAY_CONCRETE)
                        placed += 1
    
    # Entrance
    for dx in range(-2, 3):
        place(level, cx + dx, 2, cz + hd, OAK_DOOR)
        place(level, cx + dx, 3, cz + hd, OAK_DOOR)
        placed += 10
    
    return placed


# =============================================================================
# 6. JOCKEY CLUB ENTERPRISE CENTER (香港賽馬會創新科技中心)
# =============================================================================

def build_jockey_club_enterprise_center(level):
    """
    Real: Hong Kong Jockey Club Enterprise Center - Innovation and entrepreneurship hub.
    Distinctive building with Jockey Club branding.
    """
    print("  → 香港赛马会创新科技中心 Jockey Club Enterprise Center")
    placed = 0
    
    # Position from OSM: mc_x=288, mc_z=398
    cx, cz = 288, 398
    
    hw, hd, height = 20, 14, 12  # 4 floors
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation plaza
    for dx in range(-hw - 2, hw + 3):
        for dz in range(-hd - 2, hd + 3):
            place(level, cx + dx, gy + 1, cz + dz, POLISHED_GRANITE)
            placed += 1
    
    # Main building - white with gold accents (Jockey Club colors)
    for y in range(2, height + 2):
        is_top = (y == height + 1)
        is_window = ((y - 2) % 3 == 0 and y >= 3)
        is_gold_accent = (y == 6 or y == height)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                on_corner = (abs(dx) == hw and abs(dz) == hd)
                
                if is_top:
                    # Gold crown
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_corner:
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_gold_accent:
                        place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                        placed += 1
                    elif is_window:
                        place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
    
    # Jockey Club emblem (red circle on white)
    for dx in range(-2, 3):
        place(level, cx + dx, 4, cz - hd - 1, RED_CONCRETE)
        placed += 1
    place(level, cx, 5, cz - hd - 1, WHITE_CONCRETE)
    placed += 1
    
    # Entrance with red accent pillars
    for dx in [-4, 4]:
        for dy in range(2, 6):
            place(level, cx + dx, dy, cz + hd, RED_CONCRETE)
            placed += 1
    
    return placed


# =============================================================================
# 7. FOK YING TUNG SPORTS CENTER (霍英東體育中心)
# =============================================================================

def build_fok_ying_tung_sports_center(level):
    """
    Real: Fok Ying Tung Sports Center - Large indoor sports complex.
    Contains gymnasium, basketball courts, fitness center.
    """
    print("  → 霍英东体育中心 Fok Ying Tung Sports Center")
    placed = 0
    
    # Position: east side of campus, near water sports facilities
    cx, cz = 450, 150
    
    hw, hd, height = 35, 25, 10  # Large single-story complex
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-hw - 1, hw + 2):
        for dz in range(-hd - 1, hd + 2):
            place(level, cx + dx, gy + 1, cz + dz, GRAVEL)
            placed += 1
    
    # Main hall - large open space with high roof
    for y in range(2, height + 2):
        is_roof = (y >= height)
        
        for dx in range(-hw, hw + 1):
            for dz in range(-hd, hd + 1):
                on_edge_x = (abs(dx) == hw)
                on_edge_z = (abs(dz) == hd)
                is_pillar = (abs(dx) % 15 == 0 and abs(dz) % 15 == 0)
                
                if is_roof:
                    # Pitched roof using stairs
                    roof_y = height + 1 + int((abs(dx) + abs(dz)) / 20)
                    if y == roof_y:
                        place(level, cx + dx, y, cz + dz, DARK_GRAY_CONCRETE)
                        placed += 1
                elif on_edge_x or on_edge_z:
                    place(level, cx + dx, y, cz + dz, RED_CONCRETE)
                    placed += 1
                elif is_pillar:
                    # Support pillars
                    place(level, cx + dx, y, cz + dz, GRAY_CONCRETE)
                    placed += 1
    
    # Windows along sides (high windows)
    for dx in range(-hw, hw + 1):
        for dz in range(-hd, hd + 1):
            if abs(dz) == hd:
                if (dx + 5) % 10 == 0:
                    place(level, cx + dx, 6, cz + dz, GLASS_LIGHT_BLUE)
                    placed += 1
    
    # Entrance with covered walkway
    for dx in range(-10, 11):
        for dy in range(2, 5):
            place(level, cx + dx, dy, cz + hd, GRAY_CONCRETE)
            placed += 1
        place(level, cx + dx, 5, cz + hd, RED_CONCRETE)
        placed += 1
    
    # Sports equipment symbol
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        rx = cx + round(5 * math.cos(rad))
        rz = cz + hd + 3 + round(2 * math.sin(rad))
        place(level, rx, 3, rz, ORANGE_CONCRETE)
        placed += 1
    
    return placed


# =============================================================================
# 8. FOK YING TUNG SWIMMING POOL (霍英東游泳池)
# =============================================================================

def build_fok_ying_tung_swimming_pool(level):
    """
    Real: Fok Ying Tung Swimming Pool - Olympic-size outdoor pool.
    Blue pool with surrounding deck.
    """
    print("  → 霍英东游泳池 Fok Ying Tung Swimming Pool")
    placed = 0
    
    # Position: near sports center
    cx, cz = 480, 180
    
    # Pool dimensions (Olympic: 50m x 25m)
    pool_w, pool_d = 25, 15
    deck_w = 8
    
    gy = get_ground_y(level, cx, cz)
    
    # Surrounding deck
    for dx in range(-pool_w//2 - deck_w, pool_w//2 + deck_w + 1):
        for dz in range(-pool_d//2 - deck_w, pool_d//2 + deck_w + 1):
            place(level, cx + dx, gy + 1, cz + dz, SMOOTH_STONE)
            placed += 1
    
    # Pool basin (deep)
    for dx in range(-pool_w//2, pool_w//2 + 1):
        for dz in range(-pool_d//2, pool_d//2 + 1):
            # Pool edge (rim)
            if abs(dx) == pool_w//2 or abs(dz) == pool_d//2:
                place(level, cx + dx, gy + 1, cz + dz, WHITE_CONCRETE)
                placed += 1
            else:
                # Pool floor - blue
                place(level, cx + dx, gy, cz + dz, BLUE_CONCRETE)
                placed += 1
    
    # Water (deep blue)
    for dx in range(-pool_w//2 + 1, pool_w//2):
        for dz in range(-pool_d//2 + 1, pool_d//2):
            place(level, cx + dx, gy + 1, cz + dz, WATER)
            placed += 1
    
    # Diving platforms (3 levels)
    for level_y in [2, 4, 6]:
        place(level, cx + pool_w//2 + 2, gy + level_y, cz, WHITE_CONCRETE)
        placed += 1
        # Support pillar
        for y in range(1, level_y):
            place(level, cx + pool_w//2 + 2, gy + y, cz, GRAY_CONCRETE)
            placed += 1
    
    # Starting blocks
    for dx in range(-2, 3):
        place(level, cx + dx, gy + 2, cz - pool_d//2, WHITE_CONCRETE)
        placed += 1
    
    # Lane dividers (cyan concrete strips)
    for dz in range(-pool_d//2 + 2, pool_d//2):
        for lane in range(-3, 4):
            place(level, cx + lane * 3, gy + 1, cz + dz, CYAN_CONCRETE)
            placed += 1
    
    # Pool house/changing rooms
    for dx in range(5, 12):
        for dz in range(-4, 5):
            place(level, cx + dx, gy + 2, cz + dz, WHITE_CONCRETE)
            placed += 1
            place(level, cx + dx, gy + 3, cz + dz, CYAN_CONCRETE)
            placed += 1
    
    return placed


# =============================================================================
# 9. UNIVERSITY APARTMENTS (大學宿舍 A/B/C/D座)
# =============================================================================

def build_university_apartments(level):
    """
    Real: University Apartments - 4 towers (A, B, C, D) for visiting scholars.
    Modern high-rise apartments.
    """
    print("  → 大学宿舍 A/B/C/D座 University Apartments")
    placed = 0
    
    # Tower A: mc_x=200, mc_z=492
    # Tower B: mc_x=184, mc_z=428
    # Tower C: mc_x=173, mc_z=353
    # Tower D: mc_x=158, mc_z=391
    
    towers = [
        (200, 492, "A"),
        (184, 428, "B"),
        (173, 353, "C"),
        (158, 391, "D"),
    ]
    
    for cx, cz, name in towers:
        gy = get_ground_y(level, cx, cz)
        height = 12  # 4 floors
        
        # Foundation plaza
        for dx in range(-8, 9):
            for dz in range(-8, 9):
                place(level, cx + dx, gy + 1, cz + dz, SMOOTH_STONE)
                placed += 1
        
        # Tower body
        for y in range(2, height + 2):
            is_window = ((y - 2) % 3 == 0)
            
            for dx in range(-6, 7):
                for dz in range(-6, 7):
                    on_edge_x = (abs(dx) == 6)
                    on_edge_z = (abs(dz) == 6)
                    on_corner = (abs(dx) == 6 and abs(dz) == 6)
                    
                    if y == height + 1:
                        place(level, cx + dx, y, cz + dz, DARK_GRAY_CONCRETE)
                        placed += 1
                    elif on_corner:
                        place(level, cx + dx, y, cz + dz, QUARTZ_BLOCK)
                        placed += 1
                    elif on_edge_x or on_edge_z:
                        if is_window:
                            place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                            placed += 1
                        else:
                            place(level, cx + dx, y, cz + dz, LIGHT_GRAY_CONCRETE)
                            placed += 1
        
        # Tower label
        place(level, cx, gy + 2, cz - 7, OAK_FENCE)
        place(level, cx, gy + 3, cz - 7, WHITE_CONCRETE)
        placed += 2
    
    return placed


# =============================================================================
# 10. JOCKEY CLUB GLOBAL GRADUATE TOWER (賽馬會集賢樓)
# =============================================================================

def build_jockey_club_global_graduate_tower(level):
    """
    Real: Jockey Club Global Graduate Tower - Graduate student housing.
    Tall tower building with distinctive appearance.
    """
    print("  → 赛马会集贤楼 Jockey Club Global Graduate Tower")
    placed = 0
    
    # Position from OSM: mc_x=97, mc_z=557, height=28m
    cx, cz = 97, 557
    height = 14  # ~28m (2m per floor)
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-10, 11):
        for dz in range(-10, 11):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Main tower
    for y in range(2, height + 2):
        is_window = ((y - 2) % 3 == 0)
        is_floor = (y % 5 == 0)
        is_crown = (y >= height - 1)
        
        for dx in range(-8, 9):
            for dz in range(-8, 9):
                on_edge_x = (abs(dx) == 8)
                on_edge_z = (abs(dz) == 8)
                on_corner = (abs(dx) == 8 and abs(dz) == 8)
                
                if y == height + 1:
                    # Crown
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_corner:
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_crown:
                        place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                        placed += 1
                    elif is_floor:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
                    elif is_window:
                        place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, LIGHT_GRAY_CONCRETE)
                        placed += 1
    
    # Beacon
    place(level, cx, height + 3, cz, SEA_LANTERN)
    placed += 1
    
    return placed


# =============================================================================
# 11. DJI HALL / 大疆創新樓 (UG HALL XI)
# =============================================================================

def build_dji_hall(level):
    """
    Real: DJI Hall (UG Hall XI) - Undergraduate residence sponsored by DJI.
    Modern tall dormitory.
    """
    print("  → 大疆创新楼 DJI Hall (UG Hall XI)")
    placed = 0
    
    # Position from OSM: mc_x=55, mc_z=591
    cx, cz = 55, 591
    height = 12
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-8, 9):
        for dz in range(-8, 9):
            place(level, cx + dx, gy + 1, cz + dz, STONE_BRICKS)
            placed += 1
    
    # Building
    for y in range(2, height + 2):
        is_window = ((y - 2) % 3 == 0)
        is_crown = (y >= height)
        
        for dx in range(-6, 7):
            for dz in range(-6, 7):
                on_edge_x = (abs(dx) == 6)
                on_edge_z = (abs(dz) == 6)
                
                if y == height + 1:
                    place(level, cx + dx, y, cz + dz, BLACK_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_crown:
                        place(level, cx + dx, y, cz + dz, BLACK_CONCRETE)
                        placed += 1
                    elif is_window:
                        place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, LIGHT_GRAY_CONCRETE)
                        placed += 1
    
    # DJI-style beacon (cyan light)
    place(level, cx, height + 2, cz, CYAN_CONCRETE)
    place(level, cx, height + 3, cz, SEA_LANTERN)
    placed += 2
    
    return placed


# =============================================================================
# 12. LI DAK SUM CONFERENCE LODGE (李達三葉耀珍伉儷李本俊會議大樓)
# =============================================================================

def build_li_dak_sum_conference_lodge(level):
    """
    Real: Li Dak Sum Yip Yio Chin Kenneth Li Conference Lodge.
    Conference center and guest house.
    """
    print("  → 李达三会议大楼 Li Dak Sum Conference Lodge")
    placed = 0
    
    # Position from OSM: mc_x=45, mc_z=771
    cx, cz = 45, 771
    height = 6
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation with garden setting
    for dx in range(-15, 16):
        for dz in range(-12, 13):
            if (dx + dz) % 3 == 0:
                place(level, cx + dx, gy + 1, cz + dz, GRASS)
                placed += 1
            else:
                place(level, cx + dx, gy + 1, cz + dz, SMOOTH_STONE)
                placed += 1
    
    # Main building - elegant white
    for y in range(2, height + 2):
        is_window = ((y - 2) % 3 == 0)
        
        for dx in range(-12, 13):
            for dz in range(-8, 9):
                on_edge_x = (abs(dx) == 12)
                on_edge_z = (abs(dz) == 8)
                
                if y == height + 1:
                    place(level, cx + dx, y, cz + dz, DARK_GRAY_CONCRETE)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        place(level, cx + dx, y, cz + dz, GLASS)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
    
    # Entrance columns
    for dx in [-4, 0, 4]:
        for dy in range(2, height):
            place(level, cx + dx, dy, cz + 8, QUARTZ_PILLAR)
            placed += 1
    
    # Conference crest
    place(level, cx, 4, cz + 9, GOLD_BLOCK)
    placed += 1
    
    return placed


# =============================================================================
# 13. JOCKEY CLUB INSTITUTE FOR ADVANCED STUDY (IAS)
# =============================================================================

def build_jockey_club_ias_building(level):
    """
    Real: Hong Kong Jockey Club Institute for Advanced Study (IAS).
    Premium research institute building.
    """
    print("  → 赛马会高等研究院 Jockey Club IAS")
    placed = 0
    
    # Position: near Lo Ka Chung Building, around (80, 680)
    cx, cz = 80, 680
    height = 10
    
    gy = get_ground_y(level, cx, cz)
    
    # Foundation
    for dx in range(-14, 15):
        for dz in range(-10, 11):
            place(level, cx + dx, gy + 1, cz + dz, POLISHED_DIORITE)
            placed += 1
    
    # Main building - prestigious white with gold
    for y in range(2, height + 2):
        is_window = ((y - 2) % 3 == 0)
        
        for dx in range(-12, 13):
            for dz in range(-8, 9):
                on_edge_x = (abs(dx) == 12)
                on_edge_z = (abs(dz) == 8)
                on_corner = (abs(dx) == 12 and abs(dz) == 8)
                
                if y == height + 1:
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_corner:
                    place(level, cx + dx, y, cz + dz, GOLD_BLOCK)
                    placed += 1
                elif on_edge_x or on_edge_z:
                    if is_window:
                        place(level, cx + dx, y, cz + dz, GLASS_LIGHT_BLUE)
                        placed += 1
                    else:
                        place(level, cx + dx, y, cz + dz, WHITE_CONCRETE)
                        placed += 1
    
    # IAS crest
    place(level, cx, 4, cz - 9, GOLD_BLOCK)
    place(level, cx - 1, 4, cz - 9, RED_CONCRETE)
    place(level, cx + 1, 4, cz - 9, RED_CONCRETE)
    placed += 3
    
    return placed


# =============================================================================
# MAIN
# =============================================================================

def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    print(f"Loading {DST}")
    level = amulet_level.load_level(str(DST))

    total = 0
    print("\n=== v1.7: Adding All Missing HKUST Buildings ===")
    print("\n--- Academic Buildings ---")
    
    total += build_lee_shau_kee_business_building(level)
    total += build_cheng_yu_tung_building(level)
    total += build_lo_ka_chung_center(level)
    total += build_martin_lee_innovation_building(level)
    total += build_new_research_building_2(level)
    total += build_jockey_club_enterprise_center(level)
    
    print("\n--- Sports & Recreation ---")
    total += build_fok_ying_tung_sports_center(level)
    total += build_fok_ying_tung_swimming_pool(level)
    
    print("\n--- Student Housing ---")
    total += build_university_apartments(level)
    total += build_jockey_club_global_graduate_tower(level)
    total += build_dji_hall(level)
    total += build_li_dak_sum_conference_lodge(level)
    
    print("\n--- Research Institute ---")
    total += build_jockey_club_ias_building(level)

    level.close()
    print(f"\n=== Total new blocks: ~{total} ===")
    print(f"Saved to: {DST}")


if __name__ == "__main__":
    main()
