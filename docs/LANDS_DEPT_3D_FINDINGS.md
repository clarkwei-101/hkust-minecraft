# Lands Department 3D Tiles — HKUST Coverage Analysis

**Date**: 2026-08-04  
**Author**: Cursor Agent  
**Goal**: Extract HKUST building heights from HK Lands Dept Cesium 3D Tiles for Minecraft v1.3 perfect replica

## Summary

❌ **HKUST academic campus is NOT covered by the Lands Department 3D building dataset.**

The HKUST area (lat 22.330-22.345, lon 114.258-114.273) contains **zero 3D building geometry** in the tileset. Adjacent tiles covering the campus area either:
- Have no R0 leaves in the HKUST bbox
- Contain only terrain or road geometry, not buildings

## What WAS Found

Surrounding tiles contain detailed 3D data for:
- Shek O village (south-east of HKUST) — many small residential buildings
- Clear Water Bay (south) — small buildings
- Mountain residential areas (north of HKUST) — ~80 small structures
- Coastal areas east of HKUST

### R0 Leaf Counts (within 1km of HKUST)
| Tile | Center | Leaves in HKUST bbox |
|------|--------|---------------------|
| F_Tile_+5_2_0+R9_0 | (22.342, 114.278) | 0 |
| F_Tile_+5_3_0+R9_0 | (22.415, 114.280) | 0 |
| Tile_+4_2_0+L0_0_0_0 | (22.339, 114.193) | 0 |

## Data Format Findings

The HK Lands Dept 3D Tiles uses:
- **Local ECEF frame**: translation `[-2401000, 5393000, 2405000]`, no rotation
- **Bounding boxes**: OBB with 3 orthogonal half-axes (East, Up, North)
- **Geometry**: B3DM files containing GLB with VEC3 float32 position attributes
- **LOD hierarchy**: R0 (highest detail, individual buildings) → R9 (lowest)
- **Tile naming**: `F_Tile_+X_Y_Z+Rn.json` or `.b3dm`

## Coordinate Conversion

```python
# Local to WGS84 lat/lon
def local_to_latlon(lx, ly, lz):
    # Add ECEF translation
    ecef = (lx - 2401000, ly + 5393000, lz + 2405000)
    # Then ECEF to lat/lon via standard ellipsoid math
    ...
```

## Why No HKUST Coverage

Most likely reasons:
1. **Privacy/Exclusion**: HKUST campus may have opted out of public 3D mapping
2. **Restricted area**: Campus grounds excluded from open datasets
3. **Tile boundaries**: Campus sits at the corner of multiple tiles, each containing only terrain

## Implications for v1.3

Since Lands Dept data can't help HKUST:
1. **Use OSM building=* tags** for adjacent buildings (already in Arnis base map)
2. **Hand-craft HKUST buildings** from photos/satellite imagery
3. **Use Lands Dept data for peripheral buildings** (residential, bus terminus, etc.)
4. **Reference HKUST official campus map** for accurate building footprints

## Files Created

- `/tmp/hk_tileset.json` — Main tileset (218k buildings)
- `/tmp/hkust_tile.json` — F_Tile_+5_2_0 (closest tile, no HKUST buildings)
- `/tmp/hkust_tile.b3dm` — 669K binary
- `/tmp/hkust_r8_0.json` / `hkust_r8_2.json` / `hkust_r8_3.json` — R8 sub-tiles
- `/tmp/hkust_tile_5_3_0.b3dm` — F_Tile_+5_3_0 (no HKUST buildings)
- `/tmp/hkust_tile_4_2_0.b3dm` — Tile_+4_2_0 (no HKUST buildings)
- `/tmp/tiles_cache/` — Cached tileset JSON files

## Cache

The recursive tile fetcher is cached at `/tmp/tiles_cache/`.
