# 央 · 示例

## 输入

- `input/央.png`：800×720 毛笔字，棋盘格是烤进像素的（原图没有 alpha）。
- `hints/央.json`：5 笔的人工 waypoint，顺序为 竖 → 横折 → 横 → 撇 → 捺。

## 生成

```powershell
simple-glyph demo
# 或者
simple-glyph trace --image input/央.png --hints hints/央.json --out output --character 央
```

## 输出

| 文件 | 说明 |
|---|---|
| `output/央_centerline.svg` | 主交付：5 条开放中心线 |
| `output/央_centerline_colored.svg` | 分色 + 编号 |
| `output/央_animation.svg` | 逐笔书写动画 |
| `output/央_centerline.json` | 点列 / 顺序 / 长度 |
| `output/央_preview_checker.png` | 棋盘格预览 |
| `output/央_preview_white.png` | 白底预览 |
| `output/央_overlay.png` | 叠在原图上检查 |

## 注意

- 这是**中心线**，不是整字轮廓；
- 第 2 笔是草书连笔的横折，不是印刷体直角；
- 第 1 笔与第 2/3 笔共用起收笔位置，允许几像素的端点取舍；
- 原图水印/棋盘格不进入矢量。
