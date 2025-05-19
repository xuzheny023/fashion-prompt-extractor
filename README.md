# 👗 AI Fashion Analyzer
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
Extract structural fashion keywords from AI-generated images and generate precise prompts for design use.

## 🧠 Project Overview

This tool analyzes clothing images—especially AI-generated design drafts—and extracts semantic structural elements such as collar type, sleeve style, and skirt shape. Based on these features, it generates a prompt suitable for use in Stable Diffusion or fashion design documentation.

## 🔧 Features

- 📸 Upload any fashion image (PNG/JPG)
- 🧩 Detect design features: neckline, sleeves, silhouette
- ✍ Auto-generate descriptive English prompt
- 🔄 Planned: keyword-based LoRA filtering and generation
- 🧪 Built for Streamlit (local deployment)

```markdown
## 📂 Project Structure

```text
ai-fashion-analyzer/
│
├── app.py                     # Streamlit entry
├── requirements.txt
├── data/
│   └── structure_keywords.json  # Feature-prompt mapping
├── src/
│   ├── structure_detect.py      # Simulated clothing structure extractor
│   └── prompt_builder.py        # Prompt builder from keywords
├── images/                    # Input samples (user upload)
└── outputs/                   # Generated outputs (future)
```
## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run app.py


```


© 2025 [Oceanus Xu (徐振洋)]  
This project is released under the MIT License.
