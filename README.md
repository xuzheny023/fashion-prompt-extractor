# 👗 AI Fashion Analyzer
Extract structural fashion keywords from fashion images and generate intelligent prompt suggestions for design use.

## 🌟 Project Overview | 项目概述
This tool analyzes fashion or garment images (AI-generated or real) to automatically identify the fabric type and surface characteristics — including color, gloss, and texture patterns.
It then compares the detected features with a fabric database and recommends the most visually similar fabrics for real-world material selection or production guidance.

该工具可通过 AI 自动识别服装图片中的 颜色、光泽、纹理 等面料特征，并与面料库进行比对，
列出与图示视觉效果最相近的可替代面料，帮助用户快速找到合适的材质或开发参考。
## ✨ Features | 功能特色
Upload fashion or fabric images (PNG/JPG)
上传服装或面料图片（PNG/JPG）

Automatic background removal
自动去除背景，提取主体区域

AI-based fabric attribute detection
基于 AI 的面料属性识别（颜色、光泽、纹理）

Fabric similarity ranking & recommendation
根据视觉特征生成面料相似度排序与推荐

Customizable attribute weights
可自定义颜色 / 光泽 / 纹理权重，实现个性化推荐结果

Localized fine-tuning (region-based analysis)
支持局部区域细化分析与混合推荐模式

Built with Streamlit | 使用 Streamlit 构建
可在本地快速运行或在线部署

## 📂 Project Structure | 项目结构
```text
fashion-prompt-extractor/
├─ app.py
├─ requirements.txt
├─ data/
│  └─ fabric_rules.json
├─ src/
│  ├─ bg_remove.py
│  ├─ attr_extract.py
│  ├─ fabric_ranker.py
│  └─ utils.py
├─ images/
└─ outputs/
```

## 🛠️ How to Run | 使用方法
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 👨💻 Developer Guide | 开发者指南
- Formatting: run Black/Ruff before commit (configured in `pyproject.toml`, line width 100)
  - black . && ruff check .
  - Safety note: Always generate complete try/except blocks with at least one indented statement; do not leave `try:` empty.
  - On Windows, you can add a pre-commit step via a local git hook:
    - Create `.git/hooks/pre-commit` (no extension) with the following content:
      
      ```bash
      #!/usr/bin/env bash
      set -e
      black .
      ruff check .
      ```
      
    - Make it executable on Unix-like systems: `chmod +x .git/hooks/pre-commit`
- Encoding tools:
  - Scan non-UTF8 files: `python scripts/scan_non_utf8.py`
  - Convert to UTF-8: `python scripts/convert_to_utf8.py "locales/*.json" "data/**/*.json"`
 - Smoke test pipeline: `python scripts/smoke_run.py`

© 2025 [Oceanus Xu (徐振祥)] - Released under MIT License

## Extend with New Fabric Classes

- Add your new fabric keys into any JSON under `rules/packs/` (or prepare a list).
- Generate a starter pack with defaults:

```bash
python scripts/make_rule_skeleton.py --family sheens --out sheens_auto.json
```

- Fill in `display_name` (en/zh) and `notes` manually in the generated file.
- Merge and preview: enable “Use rule packs (merged)” in the sidebar.
- Evaluate quality on the “Evaluate Labeled Patches” page.
