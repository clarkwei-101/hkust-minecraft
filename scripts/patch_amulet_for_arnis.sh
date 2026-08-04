#!/bin/bash
# HKUST Minecraft v1.1 - amulet Compatibility Patch
# ===============================================
# Applies patches to amulet-core to read Arnis-generated Bedrock 1.21.40 worlds.
#
# This is needed because Arnis uses a slightly different LevelDB format than
# standard Bedrock:
#   1. '+' key data is 540 bytes (512 heightmap + 28 biome) instead of 544
#   2. Biome loop consumes data in 5-byte chunks, causing struct.unpack error
#
# Run this script after `pip install amulet-core` to enable HKUST world editing.
#
# Applies to: /Users/yahweh/Library/Python/3.11/lib/python/site-packages/amulet/

set -e

AMULET_SITE="/Users/yahweh/Library/Python/3.11/lib/python/site-packages/amulet"
PATCH_FILE="$AMULET_SITE/level/formats/leveldb_world/interface/chunk/base_leveldb_interface.py"

if [ ! -f "$PATCH_FILE" ]; then
    echo "ERROR: amulet not found at $PATCH_FILE"
    echo "Install with: pip3 install amulet-core"
    exit 1
fi

echo "Applying amulet Arnis compatibility patches..."

# ----- PATCH 1: Pad 540-byte '+' key to 544 bytes -----
# File: base_leveldb_interface.py
# Context: after "if b"+" in chunk_data:"
# Change: add padding for 540-byte Arnis heightmap+biome data

python3 << 'PATCH_EOF'
import sys
patch_file = "/Users/yahweh/Library/Python/3.11/lib/python/site-packages/amulet/level/formats/leveldb_world/interface/chunk/base_leveldb_interface.py"

with open(patch_file, 'r') as f:
    content = f.read()

# Check if already patched
if "Arnis uses a 512-byte heightmap" in content:
    print("  [SKIP] PATCH 1 already applied")
else:
    # Find and patch the b"+" block
    old = '''        if b"+" in chunk_data:
            height, biome = self._decode_height_3d_biomes(
                chunk_data[b"+"], bounds[0] >> 4
            )'''

    new = '''        if b"+" in chunk_data:
            plus_data = chunk_data[b"+"]
            # Arnis uses a 512-byte heightmap + 28-byte biome header (total 540)
            # Standard Bedrock stores additional uint32_t height + biome data (544 bytes)
            # Pad to 544 bytes so _decode_height_3d_biomes has enough for its struct.unpack("<I")
            if len(plus_data) == 540:
                plus_data = plus_data + b"\\x00\\x00\\x00\\x00"
            height, biome = self._decode_height_3d_biomes(
                plus_data, bounds[0] >> 4
            )'''

    if old in content:
        content = content.replace(old, new)
        print("  [APPLY] PATCH 1: 540-byte '+' key padding")
    else:
        print("  [WARN] PATCH 1 pattern not found - manual review needed")
        sys.exit(1)

    with open(patch_file, 'w') as f:
        f.write(content)

# ----- PATCH 2: Guard _decode_height_3d_biomes against short biome data -----
with open(patch_file, 'r') as f:
    content = f.read()

if "# Arnis biome length guard" in content:
    print("  [SKIP] PATCH 2 already applied")
else:
    old = '''        while data:
            data, bits_per_value, arr = self._decode_packed_array(data)
            if bits_per_value == 0:
                value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
                # TODO: when the new biome system supports ints just return the value
                biomes[cy] = numpy.full((4, 4, 4), value, dtype=numpy.uint32)
            elif bits_per_value > 0:
                arr = arr[::4, ::4, ::4]
                palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
                biomes[cy] = numpy.frombuffer(data, "<i4", palette_len)[arr].astype(
                    numpy.uint32
                )
                data = data[4 * palette_len :]
            cy += 1'''

    new = '''        while data:
            data, bits_per_value, arr = self._decode_packed_array(data)
            if bits_per_value == 0:
                # Guard: need at least 4 bytes for struct.unpack("<I")
                # Arnis stores 28-byte biome data that doesn't align with amulet's
                # 5-byte-per-biome-loop assumption
                if len(data) < 5:
                    break
                value, data = struct.unpack(f"<I", data[:4])[0], data[4:]
                # TODO: when the new biome system supports ints just return the value
                biomes[cy] = numpy.full((4, 4, 4), value, dtype=numpy.uint32)
            elif bits_per_value > 0:
                arr = arr[::4, ::4, ::4]
                # Guard: need at least 4 bytes for palette_len
                if len(data) < 4:
                    break
                palette_len, data = struct.unpack("<I", data[:4])[0], data[4:]
                biomes[cy] = numpy.frombuffer(data, "<i4", palette_len)[arr].astype(
                    numpy.uint32
                )
                data = data[4 * palette_len :]
            cy += 1'''

    if old in content:
        content = content.replace(old, new)
        print("  [APPLY] PATCH 2: biome decode length guards")
    else:
        print("  [WARN] PATCH 2 pattern not found - manual review needed")
        sys.exit(1)

    with open(patch_file, 'w') as f:
        f.write(content)

# Clear Python cache
import os, glob
for pyc in glob.glob(os.path.join("/Users/yahweh/Library/Python/3.11/lib/python/site-packages/amulet", "**/*.pyc"), recursive=True):
    os.remove(pyc)
for cache in glob.glob(os.path.join("/Users/yahweh/Library/Python/3.11/lib/python/site-packages/amulet", "**/__pycache__"), recursive=True):
    import shutil
    shutil.rmtree(cache, ignore_errors=True)

print("  [CLEAR] Python bytecode cache cleared")
print("\nPatch complete. You can now load Arnis-generated Bedrock worlds with amulet.")
print("Test: python3 -c 'import amulet; amulet.load_level(\"/path/to/world\")'")
PATCH_EOF

echo ""
echo "Done!"
