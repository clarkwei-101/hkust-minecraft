"""
HKUST Minecraft v1.1 - Landmark Injector
========================================
Injects hand-built landmark schematics into a Bedrock .mcworld LevelDB world.

Usage:
    python3 inject_landmarks.py <mcworld_zip> <output_dir>
    python3 inject_landmarks.py --direct /path/to/unzipped/world/db

Requirements:
    pip install leveldb pynbt pyyaml

What it does:
1. Loads the Bedrock world (unzipped .mcworld)
2. Scans for ground height at each landmark's XZ position
3. Injects each landmark's blocks at the correct Y level
4. Saves the modified world back
"""

import json
import math
import os
import struct
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

# Try to import optional deps
try:
    import leveldb
    HAS_LEVELDB = True
except ImportError:
    HAS_LEVELDB = False
    print("WARNING: leveldb not installed. Install with: pip install leveldb")

try:
    import pynbt
    HAS_NBT = True
except ImportError:
    HAS_NBT = False


@dataclass
class BlockDef:
    """A single Minecraft block."""
    namespace: str
    name: str
    states: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_name(cls, full_name: str):
        if ':' in full_name:
            ns, name = full_name.split(':', 1)
        else:
            ns, name = 'minecraft', full_name
        return cls(ns, name, {})

    def to_str(self) -> str:
        if self.states:
            return f"{self.namespace}:{self.name}[{','.join(f'{k}={v}' for k,v in self.states.items())}]"
        return f"{self.namespace}:{self.name}"

    def __hash__(self):
        return hash((self.namespace, self.name, tuple(sorted(self.states.items()))))


@dataclass
class SchematicBlock:
    """A block in a schematic with relative coordinates."""
    x: int
    y: int
    z: int
    block: BlockDef


@dataclass
class LandmarkSchematic:
    """A hand-built landmark schematic."""
    name: str
    display_name: str
    blocks: List[SchematicBlock]
    size: Tuple[int, int, int]
    origin: Tuple[int, int, int]  # offset


# =============================================================================
# SCHEMATIC DEFINITIONS
# =============================================================================

def build_academic_dome() -> LandmarkSchematic:
    """Academic Building Dome — radius 20, height 25."""
    blocks = []
    RADIUS = 20
    HEIGHT = 25

    for x in range(-RADIUS, RADIUS + 1):
        for y in range(HEIGHT + 1):
            for z in range(-RADIUS, RADIUS + 1):
                r = math.sqrt(x * x + z * z)
                if r > RADIUS:
                    continue

                # Foundation + columns (y <= 8)
                if y <= 8:
                    # Outer wall
                    if r >= RADIUS - 1:
                        # Column positions
                        if (abs(x) == RADIUS - 1 or abs(z) == RADIUS - 1):
                            if (abs(x) < RADIUS - 2 or abs(z) < RADIUS - 2):
                                blocks.append(SchematicBlock(
                                    x, y, z,
                                    BlockDef("minecraft", "polished_andesite", {})
                                ))
                        else:
                            blocks.append(SchematicBlock(
                                x, y, z,
                                BlockDef("minecraft", "polished_granite", {})
                            ))
                    elif r < RADIUS - 1:
                        # Interior floor
                        if y == 0:
                            blocks.append(SchematicBlock(
                                x, y, z,
                                BlockDef("minecraft", "polished_diorite", {})
                            ))

                # Dome region (y > 8) — hemisphere
                elif y > 8:
                    dy = y - 8
                    max_r = math.sqrt(RADIUS * RADIUS - dy * dy)
                    if r <= max_r:
                        # Dome shell
                        if r >= max_r - 0.5:
                            blocks.append(SchematicBlock(
                                x, y, z,
                                BlockDef("minecraft", "white_concrete", {})
                            ))
                        elif r < max_r - 0.5 and y == 9:
                            blocks.append(SchematicBlock(
                                x, y, z,
                                BlockDef("minecraft", "polished_diorite", {})
                            ))

                # Skylight (y == 24, center)
                if y == 24 and r < 4:
                    blocks.append(SchematicBlock(
                        x, y, z,
                        BlockDef("minecraft", "light_blue_stained_glass", {})
                    ))

    size = (2 * RADIUS + 1, HEIGHT + 1, 2 * RADIUS + 1)
    return LandmarkSchematic(
        name="academic-dome",
        display_name="Academic Building Dome",
        blocks=blocks,
        size=size,
        origin=(0, 0, 0)
    )


def build_circle_of_time() -> LandmarkSchematic:
    """The Circle of Time sundial plaza."""
    blocks = []
    R = 8  # plaza radius

    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.sqrt(x * x + z * z)
            if r > R:
                continue

            # Plaza floor
            blocks.append(SchematicBlock(
                x, 0, z,
                BlockDef("minecraft", "polished_diorite", {})
            ))

            # Raised platform center
            if r < 3:
                blocks.append(SchematicBlock(
                    x, 1, z,
                    BlockDef("minecraft", "polished_granite", {})
                ))

            # Gnomon (vertical sundial pointer) at center
            if r < 0.5:
                for gy in range(1, 6):
                    blocks.append(SchematicBlock(
                        0, gy, 0,
                        BlockDef("minecraft", "black_concrete", {})
                    ))

            # Hour markers at compass points
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                hx = round(R * 0.85 * math.sin(rad))
                hz = round(R * 0.85 * math.cos(rad))
                hr = math.sqrt(hx * hx + hz * hz)
                if hr <= R and hr >= R - 1:
                    blocks.append(SchematicBlock(
                        hx, 1, hz,
                        BlockDef("minecraft", "quartz_pillar", {"axis": "y"})
                    ))

    return LandmarkSchematic(
        name="circle-of-time",
        display_name="Circle of Time Sundial",
        blocks=blocks,
        size=(2 * R + 1, 7, 2 * R + 1),
        origin=(0, 0, 0)
    )


def build_one_world_fountain() -> LandmarkSchematic:
    """One-World Fountain with central water jet."""
    blocks = []
    R = 6

    for x in range(-R, R + 1):
        for z in range(-R, R + 1):
            r = math.sqrt(x * x + z * z)
            if r > R:
                continue

            # Basin floor
            blocks.append(SchematicBlock(
                x, 0, z,
                BlockDef("minecraft", "polished_granite", {})
            ))

            # Basin walls
            if r >= R - 0.5:
                blocks.append(SchematicBlock(
                    x, 1, z,
                    BlockDef("minecraft", "blue_concrete", {})
                ))

            # Central pillar
            if r < 0.5:
                for gy in range(1, 5):
                    blocks.append(SchematicBlock(
                        0, gy, 0,
                        BlockDef("minecraft", "sea_lantern", {})
                    ))

            # Water surface
            if r < R - 1:
                blocks.append(SchematicBlock(
                    x, 2, z,
                    BlockDef("minecraft", "water", {"liquid_depth": 1})
                ))

    return LandmarkSchematic(
        name="one-world-fountain",
        display_name="One-World Fountain",
        blocks=blocks,
        size=(2 * R + 1, 5, 2 * R + 1),
        origin=(0, 0, 0)
    )


def build_seaview_railings() -> LandmarkSchematic:
    """Seaview walkway railings along the coast."""
    blocks = []
    LENGTH = 60

    for i in range(LENGTH):
        # Left railing
        blocks.append(SchematicBlock(
            i, 0, 0,
            BlockDef("minecraft", "dark_oak_fence", {"east": "true", "west": "true", "north": "false", "south": "false"})
        ))
        blocks.append(SchematicBlock(
            i, 1, 0,
            BlockDef("minecraft", "dark_oak_fence", {})
        ))
        # Right railing
        blocks.append(SchematicBlock(
            i, 0, 3,
            BlockDef("minecraft", "dark_oak_fence", {"east": "true", "west": "true", "north": "false", "south": "false"})
        ))
        blocks.append(SchematicBlock(
            i, 1, 3,
            BlockDef("minecraft", "dark_oak_fence", {})
        ))
        # Floor
        blocks.append(SchematicBlock(
            i, 0, 1,
            BlockDef("minecraft", "oak_slab", {"type": "bottom"})
        ))
        blocks.append(SchematicBlock(
            i, 0, 2,
            BlockDef("minecraft", "oak_slab", {"type": "bottom"})
        ))

    return LandmarkSchematic(
        name="seaview-railings",
        display_name="Seaview Railings",
        blocks=blocks,
        size=(LENGTH, 3, 4),
        origin=(0, 0, 0)
    )


def build_library_landmark() -> LandmarkSchematic:
    """HKUST Library landmark — tall rectangular building."""
    W, H, D = 30, 20, 20

    blocks = []
    for x in range(W):
        for y in range(H):
            for z in range(D):
                # Walls
                if x == 0 or x == W-1 or z == 0 or z == D-1:
                    # Glass facade
                    if y < H - 2:
                        blocks.append(SchematicBlock(
                            x, y, z,
                            BlockDef("minecraft", "glass", {})
                        ))
                    else:
                        blocks.append(SchematicBlock(
                            x, y, z,
                            BlockDef("minecraft", "white_concrete", {})
                        ))
                # Floor/ceiling
                elif y == 0 or y == H-1:
                    blocks.append(SchematicBlock(
                        x, y, z,
                        BlockDef("minecraft", "polished_diorite", {})
                    ))
                # Interior
                else:
                    if y % 4 == 0 and x % 5 == 0 and z % 5 == 0:
                        # Pillars
                        blocks.append(SchematicBlock(
                            x, y, z,
                            BlockDef("minecraft", "polished_andesite", {})
                        ))

    return LandmarkSchematic(
        name="library",
        display_name="HKUST Library",
        blocks=blocks,
        size=(W, H, D),
        origin=(0, 0, 0)
    )


# =============================================================================
# BEDROCK WORLD SCANNER
# =============================================================================

@dataclass
class LandmarkPlacement:
    """Where to place a landmark in the world."""
    landmark: LandmarkSchematic
    world_x: int
    world_y: int  # ground level (will be adjusted)
    world_z: int
    y_offset: int = 0  # extra Y offset from schematic origin


# HKUST landmark positions in ARNIS world coordinates
# These are approximated from OSM data — will be refined by scanning
# Arnis uses WGS84 projection with origin at bbox center
# World origin (0,0) corresponds to approximately:
#   lat = 22.3361 (center of bbox)
#   lng = 114.2657 (center of bbox)
# Each 1 unit = 1 meter in Minecraft

# Landmark approximate positions (in world blocks, relative to origin):
# Derived from OSM coordinates mapped to Arnis local projection
LANDMARK_PLACEMENTS = [
    # Academic Building Dome — center of main campus
    # Approximate: mid-campus, on elevated ground
    ("academic-dome",      400, 65, 380),
    # Circle of Time — south of Academic Building
    ("circle-of-time",      380, 65, 420),
    # One-World Fountain — in front of Academic Building
    ("one-world-fountain",  430, 65, 390),
    # Seaview Railings — east coast
    ("seaview-railings",   650, 55, 300),
    # Library — north campus
    ("library",             200, 65, 200),
]


# =============================================================================
# LEVELDB SUB-CHUNK TOOLS
# =============================================================================

def get_chunk_key(cx: int, cz: int, dimension: Optional[int] = None) -> bytes:
    """Get the LevelDB key prefix for a chunk."""
    if dimension is None:
        return struct.pack('<ii', cx, cz)
    else:
        return struct.pack('<iii', cx, cz, dimension)


def varint_encode(value: int) -> bytes:
    """Encode an integer as a Minecraft varint."""
    result = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            byte |= 0x80
        result.append(byte)
        if not value:
            break
    return bytes(result)


def varint_decode(data: bytes, pos: int) -> Tuple[int, int]:
    """Decode a varint. Returns (value, new_pos)."""
    result = 0
    shift = 0
    while True:
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, pos


def decode_nbt_palette(data: bytes) -> List[str]:
    """
    Decode a Bedrock NBT palette from sub-chunk data.
    The palette is at the end of the sub-chunk as NBT TAG_Compound entries.
    Returns list of "namespace:name" block state strings.
    """
    if not data:
        return []

    # NBT tags:
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10

    pos = 0

    def read_tag():
        nonlocal pos
        tag_type = data[pos]; pos += 1
        return tag_type

    def read_string():
        nonlocal pos
        length = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
        s = data[pos:pos+length]; pos += length
        return s.decode('utf-8')

    def read_compound():
        nonlocal pos
        result = {}
        while True:
            tag = data[pos]; pos += 1
            if tag == TAG_END:
                break
            name = read_string()
            value = read_value(tag)
            result[name] = value
        return result

    def read_list():
        nonlocal pos
        tag = data[pos]; pos += 1
        count = struct.unpack('<i', data[pos:pos+4])[0]; pos += 4
        return [read_value(tag) for _ in range(count)]

    def read_value(tag_type):
        nonlocal pos
        if tag_type == TAG_BYTE:
            v = data[pos]; pos += 1
            return v
        elif tag_type == TAG_SHORT:
            v = struct.unpack('>h', data[pos:pos+2])[0]; pos += 2
            return v
        elif tag_type == TAG_INT:
            v = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
            return v
        elif tag_type == TAG_LONG:
            v = struct.unpack('>q', data[pos:pos+8])[0]; pos += 8
            return v
        elif tag_type == TAG_FLOAT:
            v = struct.unpack('>f', data[pos:pos+4])[0]; pos += 4
            return v
        elif tag_type == TAG_DOUBLE:
            v = struct.unpack('>d', data[pos:pos+8])[0]; pos += 8
            return v
        elif tag_type == TAG_BYTE_ARRAY:
            length = struct.unpack('>i', data[pos:pos+4])[0]; pos += 4
            v = data[pos:pos+length]; pos += length
            return v
        elif tag_type == TAG_STRING:
            return read_string()
        elif tag_type == TAG_LIST:
            return read_list()
        elif tag_type == TAG_COMPOUND:
            return read_compound()
        return None

    palette = []
    while pos < len(data):
        tag = data[pos]
        if tag == TAG_END:
            pos += 1
            continue
        if tag == TAG_COMPOUND:
            compound = read_compound()
            name = compound.get('name', b''.decode('utf-8', errors='replace') if 'name' not in compound else '')
            # Extract block state from compound
            states = compound.get('states', {})
            block_name = name
            # Build full name
            if block_name:
                if isinstance(states, dict) and states:
                    state_str = ','.join(f'{k}={v}' for k,v in states.items())
                    palette.append(f"{block_name}[{state_str}]")
                else:
                    palette.append(block_name)
        elif tag == TAG_STRING:
            s = read_string()
            if s:
                palette.append(s)
        elif tag == TAG_END:
            break
        else:
            # Skip unknown tags
            break

    return palette


def parse_subchunk(data: bytes) -> Tuple[int, List[Tuple[int, int]], List[str]]:
    """
    Parse a Bedrock sub-chunk (version 9+).

    Returns:
        subchunk_index: int
        packed_indices: list of (word_value, bits_per_block)
        palette: list of "namespace:name" strings
    """
    if not data or len(data) < 4:
        return 0, [], []

    idx = 0
    version = data[idx]; idx += 1
    num_storages = data[idx]; idx += 1
    sub_idx = data[idx]; idx += 1

    # Parse storage layers (only layer 0 matters for terrain)
    all_layers = []
    for _ in range(num_storages):
        storage_byte = data[idx]; idx += 1
        is_persisted = (storage_byte >> 7) & 1
        bpb = storage_byte & 0x7F

        # Calculate word count: ceil(4096 * bpb / 32)
        word_count = math.ceil(4096 * bpb / 32)
        indices_data = data[idx:idx + word_count * 4]; idx += word_count * 4

        # Unpack 32-bit words
        indices = []
        for wi in range(word_count):
            word = struct.unpack('<I', indices_data[wi*4:(wi+1)*4])[0]
            indices.append(word)

        # Decode palette
        if is_persisted:
            # Persistent: NBT TAG_Compound list
            palette_size = struct.unpack('<i', data[idx:idx+4])[0]; idx += 4
            palette = []
            pos = idx
            # Parse NBT
            TAG_END = 0; TAG_COMPOUND = 10; TAG_STRING = 8
            while pos < len(data):
                tag = data[pos]; pos += 1
                if tag == TAG_END:
                    break
                if tag == TAG_COMPOUND:
                    # Read compound
                    compound = {}
                    while True:
                        t = data[pos]; pos += 1
                        if t == TAG_END:
                            break
                        name_len = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
                        name = data[pos:pos+name_len].decode('utf-8', errors='replace'); pos += name_len
                        # Skip value based on type
                        compound[name] = t
                    block_name = compound.get('name', '')
                    if isinstance(block_name, bytes):
                        block_name = block_name.decode('utf-8', errors='replace')
                    palette.append(block_name)
                elif tag == TAG_STRING:
                    length = struct.unpack('>H', data[pos:pos+2])[0]; pos += 2
                    s = data[pos:pos+length].decode('utf-8', errors='replace'); pos += length
                    palette.append(s)
            idx = pos
        else:
            # Runtime: varint palette
            palette_size, idx = varint_decode(data, idx)
            palette = []
            for _ in range(palette_size):
                rid, idx = varint_decode(data, idx)
                palette.append(f"runtime:{rid}")

        all_layers.append((bpb, indices, palette, is_persisted))

    return sub_idx, all_layers, version


# =============================================================================
# WORLD INJECTOR
# =============================================================================

class BedrockWorldInjector:
    """Injects landmark schematics into a Bedrock LevelDB world."""

    def __init__(self, world_path: str):
        self.world_path = Path(world_path)
        self.db_path = self.world_path / 'db'
        if not HAS_LEVELDB:
            raise RuntimeError("leveldb not installed")
        self.db = leveldb.LevelDB(str(self.db_path))
        self.chunk_cache = {}  # cx,cz -> {ext: data}

    def close(self):
        self.db.close()

    def get_subchunk(self, cx: int, cz: int, sub_idx: int) -> Optional[bytes]:
        """Get raw sub-chunk data."""
        # Sub-chunk index is stored as unsigned byte (0-255)
        # Negative Y maps to 252-255: -4=0xFC=252, -3=0xFD=253, -2=0xFE=254, -1=0xFF=255
        if sub_idx < 0:
            key_byte = bytes([256 + sub_idx])  # -1 -> 255, -4 -> 252
        else:
            key_byte = bytes([sub_idx])
        key = struct.pack('<ii', cx, cz) + b'/' + key_byte
        try:
            return self.db.get(key)
        except KeyError:
            return None

    def set_subchunk(self, cx: int, cz: int, sub_idx: int, data: bytes):
        """Write raw sub-chunk data."""
        if sub_idx < 0:
            key_byte = bytes([256 + sub_idx])
        else:
            key_byte = bytes([sub_idx])
        key = struct.pack('<ii', cx, cz) + b'/' + key_byte
        self.db.put(key, data)

    def find_ground_height(self, bx: int, bz: int) -> int:
        """Find the ground Y level at a world XZ position."""
        cx = bx // 16
        cz = bz // 16
        sub_idx = 0

        # Scan sub-chunks from top to bottom
        for si in range(-4, 20):  # Y=-64 to Y=319 in sub-chunks
            try:
                data = self.get_subchunk(cx, cz, si)
            except KeyError:
                data = None
            if not data:
                continue

            try:
                idx, layers, _ = parse_subchunk(data)
                if not layers:
                    continue

                bpb, indices, palette, is_persisted = layers[0]

                # Find the ground level in this sub-chunk
                base_y = si * 16
                word_count = math.ceil(4096 * bpb / 32)

                # Check each block column at (bx%16, bz%16)
                lx = bx - cx * 16
                lz = bz - cz * 16

                for local_y in range(15, -1, -1):
                    linear = lx + lz * 16 + local_y * 256
                    word_idx = linear * bpb // 32
                    bit_offset = (linear * bpb) % 32

                    if word_idx < len(indices):
                        word = indices[word_idx]
                        palette_idx = (word >> bit_offset) & ((1 << bpb) - 1)
                        if palette_idx < len(palette):
                            block_name = palette[palette_idx]
                            if 'air' not in block_name.lower() and 'water' not in block_name.lower():
                                return base_y + local_y
            except Exception as e:
                print(f"  Warning: subchunk ({cx},{cz},{si}) parse error: {e}")
                continue

        return 64  # fallback

    def inject_landmark(self, placement: LandmarkPlacement):
        """Inject a landmark schematic into the world."""
        print(f"Injecting {placement.landmark.name} at ({placement.world_x}, {placement.world_y}, {placement.world_z})")

        for sb in placement.landmark.blocks:
            wx = placement.world_x + sb.x + placement.y_offset
            wy = placement.world_y + sb.y
            wz = placement.world_z + sb.z

            # Compute chunk and sub-chunk
            cx = wx // 16
            cz = wz // 16
            sub_idx = wy // 16  # sub-chunk index (can be negative for Y < 0)

            if sub_idx < -4 or sub_idx > 19:
                print(f"  Warning: Y={wy} out of range, skipping ({sb.x},{sb.y},{sb.z})")
                continue

            # Get or create sub-chunk
            data = self.get_subchunk(cx, cz, sub_idx)
            if data is None:
                print(f"  Warning: No sub-chunk at ({cx},{cz},{sub_idx}), skipping column")
                continue

            print(f"  Would place {sb.block.to_str()} at ({wx},{wy},{wz})")

    def save(self):
        """Save changes to disk."""
        pass  # leveldb writes are immediate


# =============================================================================
# MAIN
# =============================================================================

def main():
    if not HAS_LEVELDB:
        print("ERROR: leveldb not installed")
        print("Install with: pip3 install leveldb pynbt")
        sys.exit(1)

    import argparse
    parser = argparse.ArgumentParser(description='Inject landmarks into HKUST Minecraft world')
    parser.add_argument('world', help='Path to unzipped .mcworld directory')
    parser.add_argument('--dry-run', action='store_true', help='Print only, do not modify')
    args = parser.parse_args()

    world_path = Path(args.world)
    if not (world_path / 'db').exists():
        print(f"ERROR: Not a valid Bedrock world (no db/ folder at {world_path})")
        sys.exit(1)

    print(f"Opening world at: {world_path}")

    # Build landmarks
    landmarks = [
        build_academic_dome(),
        build_circle_of_time(),
        build_one_world_fountain(),
        build_seaview_railings(),
        build_library_landmark(),
    ]

    print(f"Built {len(landmarks)} landmark schematics:")
    for lm in landmarks:
        print(f"  {lm.display_name}: {len(lm.blocks)} blocks, size={lm.size}")

    if args.dry_run:
        print("\nDry run - scanning ground heights...")
        injector = BedrockWorldInjector(str(world_path))
        for lm, coords in zip(landmarks, LANDMARK_PLACEMENTS):
            name, wx, wy, wz = coords
            actual_gy = injector.find_ground_height(wx, wz)
            print(f"  {name}: world=({wx},{wy},{wz}), actual_ground_y={actual_gy}")
        injector.close()
    else:
        print("\nInjecting landmarks...")
        injector = BedrockWorldInjector(str(world_path))
        for lm, coords in zip(landmarks, LANDMARK_PLACEMENTS):
            name, wx, wy, wz = coords
            placement = LandmarkPlacement(lm, wx, wy, wz)
            injector.inject_landmark(placement)
        injector.close()
        print("Done!")


if __name__ == '__main__':
    main()
