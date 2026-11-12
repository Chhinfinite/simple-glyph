# 常见问题

## `ink mask is empty`

- 检查 `--threshold`：白底黑字一般 130–200；
- 检查图片是不是透明底：透明像素会被排除；
- 检查是不是亮色字/深色底：当前版本只取“暗墨”，亮字需要先反相。

## `no skeleton path A -> B`

- 两个 waypoint 被分到了不同连通域；
- 或者 BFS 在交叉点走到了另一笔；
- 把 waypoint 往目标笔画内部移，或把一笔拆成两段 hint；
- 也可以试 `--method skeletonize`。

## 中心线贴边 / 跑到笔画外

- 换 `medial_axis`；
- 检查 mask 是否把纸纹/阴影算进去了；
- 降低 `--threshold`，只取更黑的墨；
- 看 `_overlay.png` 确认是几何问题还是 hint 问题。

## 折角被抹圆

- 降低 `--sigma`（例如 1.2–1.5）；
- 折角两侧分别给 waypoint，不要让 BFS 直接抄近路；
- 后续版本会加 corner-aware 平滑。

## SVG 只有线，没有填充

这是设计选择。主交付是中心线，`fill="none"`。  
需要填充/笔宽时，使用 roadmap 中的 width 模式，或单独生成诊断填充。

## 动画不播放

- 用浏览器打开 `_animation.svg`；
- 某些图片查看器不支持 CSS animation，只显示静态首帧；
- 确认文件里有 `@keyframes sg-draw` 和 `pathLength="1"`。

## 透明背景变成白底

- SVG 默认没有背景 `<rect>`；
- 如果预览图是 PNG，检查 `_preview_checker.png` 和 `_preview_white.png` 的区别；
- 输入图如果是 RGB，需要先做 alpha matte 或阈值去背。

## Windows 上 `simple-glyph` 命令找不到

- 确认虚拟环境已激活；
- 重新执行 `pip install -e .`；
- 或直接用 `python -m simple_glyph ...`。

## 可以商用吗

代码是 MIT。  
但输入图片、字体、标准笔顺数据、示例图可能有各自的版权/许可；商用前请逐项确认。Hanzi Writer 数据的使用请遵循其仓库许可。
