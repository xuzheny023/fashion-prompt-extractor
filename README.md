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

© 2025 [Oceanus Xu (徐振祥)] - Released under MIT License
