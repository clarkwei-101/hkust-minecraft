#!/usr/bin/env bash
# Pack v2.3 world as .mcworld
set -e
cd /Users/yahweh/Desktop/ai应用社/hkust-minecraft

# Update levelname.txt
echo "HKUST v2.3 — OSM Footways + Amenity + Rooftop Garden (424k blocks)" > worlds/working/v2.3/levelname.txt

# Pack .mcworld from /worlds/working/v2.3/
rm -f worlds/final/HKUST-2026-Bedrock-v2.3.mcworld
cd worlds/working/v2.3
zip -r /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.3.mcworld . -x "*.lock" "LOCK" 2>&1 | tail -3

# Verify structure
echo ""
echo "=== Verifying .mcworld structure ==="
unzip -l /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.3.mcworld | head -20

# Get size
echo ""
ls -la /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.3.mcworld