# Contributing

感谢你愿意一起把「简单字迹生成」做得更好。这个项目很小，但希望提交是可复现、可检查的。

## 开发环境

```powershell
git clone https://github.com/Chhinfinite/simple-glyph.git
cd simple-glyph
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m pytest -q
```

## 提交前检查

```powershell
python -m pytest -q
ruff check src tests
```

如果改了输出格式或 SVG 结构，请同时更新：

- `README.md` 的“输出”部分；
- `docs/pipeline.md`；
- `tests/` 中对应的断言；
- `CHANGELOG.md`。

## 代码风格

- Python 3.9+；
- 行宽 100；
- 公共函数写 docstring；
- 不要引入需要联网的运行时依赖；
- 不要为了让测试通过而硬编码示例图的绝对路径。

## 提交信息

建议使用 Conventional Commits：

```text
feat: add bezier fitting
fix: keep stroke endpoints inside canvas
docs: explain hint JSON
test: cover render command
```

## 新增示例

示例图请放在 `examples/input/`，hint 放在 `examples/hints/`，并确保：

- 图像是 PNG/JPEG，尺寸合理（建议 < 1 MB）；
- 不包含他人的水印/版权素材，或已获得授权；
- `simple-glyph demo` 仍然可以跑通。

## 报告问题

请使用 issue 模板，附上：

- 输入图（可公开的最小复现）；
- hint JSON；
- 命令与完整报错；
- 期望输出 vs 实际输出。

不要在 issue 中贴私人照片、身份证、签名原图等敏感内容。
