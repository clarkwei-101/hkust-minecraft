# HKUST 标志性建筑 - 手工补建设计文档

Arnis 不包含这些 OSM 语义信息,需要用 WorldEdit BE 或结构方块在 Bedrock 客户端手工补建。
所有结构基于 1:1 真实比例 (1 block = 1 m)。

---

## 1. 学术楼圆顶 (Academic Building Dome)

- **位置**: `22.3375, 114.2645` (主教学楼中庭)
- **真实尺寸**: 直径 ~40 m, 半球穹顶
- **建筑风格**: 圆形基座 + 4 根廊柱 + 半球穹顶
- **结构 ID**: `landmark-academic-dome`

### 材料清单 (Minecraft 方块)

| 用途 | 方块 | 数量估算 |
|---|---|---|
| 基座外墙 | 磨制花岗岩 (Polished Granite) | ~400 |
| 立柱 (×4) | 磨制安山岩柱 (Polished Andesite Pillars) | 16 |
| 穹顶主体 | 白色混凝土 (White Concrete) | ~600 |
| 穹顶天窗 | 浅蓝色染色玻璃 (Light Blue Stained Glass) | 12 |
| 顶部避雷针 | 铁栏杆 (Iron Fence) | 1 |
| 内部地面 | 抛光闪长岩 (Polished Diorite) | ~200 |

### WorldEdit BE 指令 (以圆心 0,0,0 为参考)

```mcfunction
# 基座外环 (半径 20)
fill -20 0 -20 20 1 20 polished_granite hollow

# 4 根立柱
fill -19 2 0 -21 8 0 polished_andesite_pillar
fill  19 2 0  21 8 0 polished_andesite_pillar
fill  0 2 -19 0 8 -21 polished_andesite_pillar
fill  0 2  19 0 8  21 polished_andesite_pillar

# 穹顶 (用 sphere 命令)
; sphere 白混凝土 半径 20 hollow 圆心 (0, 9, 0)

# 天窗
fill -3 24 -3 3 25 3 light_blue_stained_glass
```

### 设计参考

参考真实 HKUST 学术楼圆形中庭 — Google Maps `22.3375,114.2645` 3D 视图。

---

## 2. 时间之轮 / Red Bird 日晷 (Circle of Time Sundial)

- **位置**: `22.33752, 114.26299` (北门广场)
- **真实尺寸**: 基座 ~8 m 直径,晷针高 3 m
- **建筑风格**: 圆形大理石基座 + 青铜色晷针
- **结构 ID**: `landmark-circle-of-time`

### 材料清单

| 用途 | 方块 | 数量估算 |
|---|---|---|
| 基座台阶 (3 层) | 磨制闪长岩台阶 (Polished Diorite Slabs) | ~60 |
| 基座外缘 | 磨制闪长岩墙 (Polished Diorite Wall) | 36 |
| 晷面刻度 | 黑色混凝土 (Black Concrete) | 8 |
| 晷针 (鸟形) | 棕色染色玻璃 + 海泡石 (Brown Stained Glass + Calcite) | ~12 |

### WorldEdit BE 指令

```mcfunction
# 3 层圆形基座 (半径递减 4 / 3 / 2)
; cyl 磨制闪长岩 半径 4 hollow
; cyl 磨制闪长岩 半径 3 hollow y+1
; cyl 磨制闪长岩 半径 2 hollow y+2

# 12 个晷面刻度点
for i in 0..12: setblock (cos(i*30°) * 3, 2, sin(i*30°) * 3) black_concrete

# 中央晷针
fill 0 3 0 0 6 0 calcite
setblock 0 7 0 brown_stained_glass_pane
```

---

## 3. 天一泉 (One-World Fountain)

- **位置**: `22.337746, 114.264462` (中央广场)
- **真实尺寸**: 圆形水池 ~12 m 直径,中央喷泉柱高 5 m
- **建筑风格**: 大理石水池 + 三层水柱
- **结构 ID**: `landmark-one-world-fountain`

### 材料清单

| 用途 | 方块 | 数量估算 |
|---|---|---|
| 外圈石环 | 磨制大理石台阶 (Polished Diorite Slabs) | 24 |
| 水池内壁 | 蓝色混凝土 (Blue Concrete) | ~50 |
| 池水 | 水 (Water) | 113 (12m 直径 × 1m 深) |
| 中央柱 | 石英柱 (Quartz Pillar) | 5 |
| 顶部装饰 | 海晶灯 (Sea Lantern) | 1 |
| 底部蓝色灯 | 灵魂灯 (Soul Lantern) | 4 |

### WorldEdit BE 指令

```mcfunction
# 外圈石环 (圆环)
; cyl 磨制大理石台阶 半径 6 hollow

# 池内填水 (半径 5, 深 1)
; cyl 水 半径 5 y=-1 to y=0

# 中央喷泉柱
fill 0 0 0 0 4 0 quartz_pillar
setblock 0 5 0 sea_lantern

# 四角蓝色灯
setblock  4 0  4 soul_lantern
setblock -4 0  4 soul_lantern
setblock  4 0 -4 soul_lantern
setblock -4 0 -4 soul_lantern
```

---

## 4. 清水湾海边栏杆 + 观景台 (Seaview Railings + Lookouts)

- **位置**: 校园南侧海岸线 (大致沿 `lat 22.3325` 至 `lat 22.3340`)
- **真实尺寸**: 沿悬崖 ~600 m 木栏杆 + 3 个观景台 (每 200m 一个)
- **建筑风格**: 深色橡木栏杆 + 石基观景台
- **结构 ID**: `landmark-seaview-railings`

### 材料清单

| 用途 | 方块 | 数量估算 |
|---|---|---|
| 栏杆 (主) | 深色橡木栅栏 (Dark Oak Fence) | ~600 |
| 栏杆柱 | 深色橡木栅栏柱 (Dark Oak Fence Gate) | ~120 |
| 观景台石基 (×3) | 磨制花岗岩台阶 (Polished Granite Slabs) | 36 / 个 |
| 观景台座椅 (×6) | 橡木台阶 (Oak Slabs) | 12 |
| 路径地砖 | 灰化橡木台阶 (Spruce Slabs) | ~1200 |

### WorldEdit BE 指令 (沿 X 轴南北向)

```mcfunction
# 主栏杆 (沿 Z=-50 一条线, Y=地表+1)
fill -300 65 -50 300 66 -50 dark_oak_fence

# 每 100m 一根立柱
for z in -300..300 step 20: setblock $z 66 -50 dark_oak_fence

# 观景台 1 (Z=-200, 半径 4)
; cyl 磨制花岗岩台阶 半径 4 hollow y=65 to y=66
setblock -203 66 -50 oak_slab
setblock  203 66 -50 oak_slab

# 观景台 2 (Z=0) 和观景台 3 (Z=200) 同上
```

---

## 通用重建流程

### 在 Bedrock 客户端加载

1. 双击 `HKUST-2026-Bedrock.mcworld` 导入
2. 选 Creative 模式 (世界已自动设 creative)
3. 传送到 `0, 70, 0` (世界中心)
4. 用命令方块执行上述指令,或安装 WorldEdit BE addon 后逐个 landmark 粘贴
5. 完成后保存 → 导出新 `.mcworld` → 重命名 `HKUST-2026-Bedrock-Handbuild.mcworld`

### 替代方案: 程序生成

也可以写 Python 脚本用 `mcstructure` API 直接构建这些结构并注入到 .mcworld 中。
参考 Bedrock Structure Editor 项目: <https://github.com/bedrock-tools/structure-editor>
