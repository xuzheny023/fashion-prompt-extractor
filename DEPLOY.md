# Deploying (Cloud-Only)

## Streamlit Cloud
1. Connect repo, set **main** as default branch.
2. App file: `app.py`
3. Add secrets if needed: `FABRIC_API_URL`, `FABRIC_API_KEY`.

## Docker (example)
```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
```

Build & run:
```bash
docker build -t fpe-cloud .
docker run -p 8501:8501 -e FABRIC_API_URL=$FABRIC_API_URL -e FABRIC_API_KEY=$FABRIC_API_KEY fpe-cloud
```

## Railway/Fly.io
- Use Dockerfile above; set env vars in dashboard.

