# 处理流程

## 总览

```text
输入图片
  │
  ├─ 1. 读图 / 灰度 / alpha
  │
  ├─ 2. 阈值 → ink mask
  │
  ├─ 3. medial_axis / skeletonize
  │
  ├─ 4. hint waypoints → 最近骨架点
  │
  ├─ 5. 8 邻域 BFS → 每笔路径
  │
  ├─ 6. 高斯平滑 → 等距重采样
  │
  └─ 7. SVG / JSON / PNG / 动画
```

## 1. 读图

`simple_glyph.image.load_rgb()` 统一转成 RGB，保留原始画布。  
如果输入是 RGBA，`ink_mask()` 会要求 `alpha > 8`，透明像素不会被误判成墨。

## 2. 墨迹 mask

```python
gray = np.asarray(image.convert("L"))
mask = gray < threshold
```

默认 `threshold=200`。  
- 纯黑字 + 白底：130–200 都可以；
- 有灰色飞白：阈值提高会保留更多飞白，也会把水印/阴影带进来；
- 有纸纹：先做轻度去噪，或改用 alpha matte（见 `alpha_from_luminance`）。

## 3. 骨架

两种后端：

| 方法 | 特点 | 建议 |
|---|---|---|
| `medial_axis` | 更居中，交叉处更稳 | 默认 |
| `skeletonize` | 更贴边，细笔画更明显 | 需要贴边时 |

骨架像素被看成 8 邻域图上的节点。

## 4. waypoint 吸附

每个 hint 的 waypoint 只要求“落在目标笔画附近”。  
程序对每个点找最近的骨架像素：

```python
node = nearest_node(waypoint, nodes)
```

这解决了“手点不准”的问题：点可以偏 10–20px，只要还在同一笔附近。

## 5. BFS 连接

相邻 waypoint 之间用 BFS 找最短路径。  
路径只允许走骨架节点，所以最终线一定落在墨迹内部。

失败情况：

- 两个 waypoint 被分到不同连通域 → 没有路径；
- 交叉点把路径带到另一笔 → 需要把 waypoint 移近目标笔，或换 `medial_axis`；
- 笔画断开 → 先修 mask，或拆成两条 hint。

## 6. 平滑与重采样

```python
pts = gaussian_filter1d(pts, sigma=2.2)
pts = resample(pts, spacing=2.5)
```

- `sigma` 太大会吃掉折角；
- `spacing` 太小会让 SVG 节点过多；
- 2.5px 是 800×720 画布的经验值。

## 7. 输出

### 中心线 SVG

- 5 条 `<path>`；
- `fill="none"`；
- 不闭合（没有 `Z`）；
- 没有背景 `<rect>`；
- `viewBox="0 0 800 720"`。

### 动画 SVG

用 CSS 的 `stroke-dasharray` / `stroke-dashoffset`：

```css
@keyframes sg-draw { to { stroke-dashoffset: 0 } }
.sg-stroke {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: sg-draw var(--dur) ease-in-out forwards;
  animation-delay: var(--delay);
}
```

每条 path 加 `pathLength="1"`，所以不用计算真实弧长，也能按比例画完。  
动画是纯 SVG/CSS，没有 JS、没有外部依赖。

### JSON

```json
{
  "schema": "simple-glyph/1",
  "character": "央",
  "canvas": [800, 720],
  "order": [{"index": 1, "id": "1", "label": "竖"}],
  "strokes": [
    {
      "id": "1",
      "label": "竖",
      "color": "#c62828",
      "points": [[205.0, 225.0], [225.0, 270.0]],
      "length": 120.5
    }
  ]
}
```

## 8. 质量检查

- 每条中心线是否都在墨迹内部；
- 交叉处有没有 180° 回环；
- 起笔/收笔方向是否符合笔顺；
- SVG 是否仍然是开放路径；
- 动画是否完整画完，且最后一帧没有残影。
