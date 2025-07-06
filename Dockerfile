# Dockerfile

# --- Stage 1: Build the React Frontend ---
    FROM node:18-alpine AS builder
    WORKDIR /app/frontend
    COPY frontend/package.json frontend/package-lock.json ./
    RUN npm ci
    COPY frontend/ ./
    RUN npm run build
    
    # --- Stage 2: Build the Final Python Application ---
    FROM python:3.9-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY backend/ ./backend/
    COPY scripts/ ./scripts/
    
    # --- NEW: Copy the saved model artifacts, NOT mlruns ---
    COPY saved_artifacts/ ./saved_artifacts/
    
    COPY --from=builder /app/frontend/build ./frontend/build
    EXPOSE 7860
    CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--chdir", "backend", "api:app"]