# ════════════════════════════════════════════════════════════════
# Dockerfile — Backend EduAI (FastAPI)
# À placer dans : backend/Dockerfile
# ════════════════════════════════════════════════════════════════

FROM python:3.12-slim

WORKDIR /app

# Copier d'abord requirements.txt seul (optimise le cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Port FastAPI
EXPOSE 8000

# Démarrage : host 0.0.0.0 obligatoire pour Docker (sinon non accessible)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
