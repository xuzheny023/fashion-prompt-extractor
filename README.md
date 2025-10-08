# 👗 AI Fashion Analyzer
Extract structural fashion keywords from fashion images and generate intelligent prompt suggestions for design use.

## 🌟 Project Overview | 项目概述
This tool analyzes fashion images (AI-generated or real) by removing background, detecting clothing structures, 
and mapping them to descriptive keywords. It then generates prompts suitable for Stable Diffusion or design documentation.

## ✨ Features | 功能特色
- Upload any fashion image (PNG/JPG)
- Automatic background removal
- Detect clothing structures (neckline, sleeves, waist, skirt, etc.)
- Fabric recommendation (list possible fabrics for similar visual effect)
- Auto-generate descriptive English prompts
- Built with Streamlit

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
