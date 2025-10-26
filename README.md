# Fashion Prompt Extractor — Cloud-Only

AI-powered fabric/fashion image analyzer for **cloud inference only**.

## What this repo is
- Single entrypoint: `app.py` (Streamlit)
- Uses remote APIs/services (no local CLIP bank, no local rule engine, no regionizer pipeline)
- Ready for cloud deployment (Streamlit Cloud / Docker / Railway)

## Features
- Upload an image → extract high-level attributes (color / gloss / texture)
- Rank & recommend visually-similar fabrics via cloud backends
- Lightweight UI for cloud usage

## Not supported anymore
- ❌ Local rule JSONs (e.g., `data/fabric_fine_rules.json`)
- ❌ Local CLIP vector bank & calibrators
- ❌ Region-click / patch labeling workflow

## Quick start
```bash
# Python 3.10+ recommended
pip install -r requirements.txt  # minimal dependencies for cloud-only
streamlit run app.py
```

Set the following environment variables if your backend requires them:
- `FABRIC_API_URL` — cloud inference endpoint
- `FABRIC_API_KEY` — optional key for auth

## Deploy
- Streamlit Cloud: point to `app.py` on `main`
- Docker/Railway: build minimal image and expose streamlit port

## Repo hygiene
This repository has been **pruned** to only keep cloud-only code paths.
Legacy local/regionizer/rule assets have been removed.

