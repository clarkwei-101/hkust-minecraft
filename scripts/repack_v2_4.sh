#!/usr/bin/env bash
# Pack v2.4 world as .mcworld (Phase D polish)
set -e
cd /Users/yahweh/Desktop/ai应用社/hkust-minecraft

# Update levelname.txt
echo "HKUST v2.4 — Phase D polish: sinkholes + underpasses + pavilions + lanterns + crosswalks (428k blocks)" > worlds/working/v2.4/levelname.txt

# Pack .mcworld from /worlds/working/v2.4/
rm -f worlds/final/HKUST-2026-Bedrock-v2.4.mcworld
cd worlds/working/v2.4
zip -r /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.4.mcworld . -x "*.lock" "LOCK" 2>&1 | tail -3

# Verify
echo ""
echo "=== Verifying .mcworld structure ==="
unzip -l /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.4.mcworld | head -15

echo ""
ls -la /Users/yahweh/Desktop/ai应用社/hkust-minecraft/worlds/final/HKUST-2026-Bedrock-v2.4.mcworld