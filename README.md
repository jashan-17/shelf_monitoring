# Shelf Monitoring System

## Overview
End-to-end shelf monitoring application that classifies retail shelf stock levels from images and connects prediction workflows with storage and analytics.

## Features
- Image upload and camera prediction
- Real-time stock level classification
- Confidence score output
- Save predictions to PostgreSQL
- Dashboard for historical analysis
- dbt and Airflow pipeline integration
- About page and project overview in the frontend

## Tech Stack
- Frontend: React + Vite
- Backend: FastAPI
- ML: TensorFlow / Keras
- Database: PostgreSQL
- Analytics: dbt
- Orchestration: Airflow
- Containerization: Docker

## Architecture
Frontend → FastAPI → Model → PostgreSQL → dbt → Airflow

- Frontend handles image input
- Backend runs inference and prediction APIs
- Database stores saved results
- dbt transforms data
- Airflow manages workflows

## How to Run Locally

### Backend
- Install dependencies
- Run the FastAPI server

```bash
pip install -r requirements.txt
pip install -r backend/requirements-api.txt
python -m uvicorn src.api.main:app --reload --app-dir backend --host 127.0.0.1 --port 8010
```

### Frontend
- Install dependencies
- Run the Vite app

```bash
cd frontend
npm install
npm run dev
```

## Docker Deployment

### App Stack
- Uses `docker-compose.app.yml`
- Runs:
  - FastAPI API on `http://127.0.0.1:8010`
  - Frontend on `http://127.0.0.1:4173`
- Frontend proxies `/api` requests to the backend container through Nginx

```bash
docker compose -f docker-compose.app.yml up --build
```

### Stop App Stack

```bash
docker compose -f docker-compose.app.yml down
```

## Vercel + Render Deployment

### Backend on Render
- Render official FastAPI guide: https://render.com/docs/deploy-fastapi
- Render Python version docs: https://render.com/docs/python-version
- This repo now includes `render.yaml` for the backend service

Use these settings if you create the service manually:
- Runtime: `Python 3`
- Build command: `pip install -r backend/requirements-deploy.txt`
- Start command: `uvicorn src.api.main:app --app-dir backend --host 0.0.0.0 --port $PORT`

Set these Render environment variables:
- `DATABASE_URL`
- `DATABASE_SSLMODE=require`
- `DATABASE_CONNECT_TIMEOUT=10`
- `CORS_ORIGINS`
- `MODEL_PATH=backend/models/model_v2.keras`
- `FALLBACK_MODEL_PATH=backend/models/model.h5`

Notes:
- Render supports setting Python with `PYTHON_VERSION` or `.python-version`
- If the large model file is not present in deployment, the API now falls back gracefully instead of crashing
- For Render Postgres, use the Internal Database URL when the API and database are in the same Render region
- For any external cloud PostgreSQL provider, paste the provider's connection string into `DATABASE_URL`

### Frontend on Vercel
- Vercel Vite SPA docs: https://vercel.com/docs/frameworks/frontend/vite
- Vercel rewrites docs: https://vercel.com/docs/rewrites
- Deploy the `frontend` directory as the Vercel project root
- The repo now includes `frontend/vercel.json`

Frontend deployment setup:
- Framework preset: `Vite`
- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`

Important:
- `frontend/vercel.json` currently rewrites `/api/*` to `https://shelf-monitoring-api.onrender.com/api/*`
- If Render gives you a different service URL, update `frontend/vercel.json` to match it before production deploy
- The same `vercel.json` also enables React Router deep links by rewriting routes to `index.html`

### Recommended Order
1. Deploy the backend on Render first
2. Confirm the Render API works at `/docs`
3. Check the assigned Render service URL
4. Update `frontend/vercel.json` if the URL differs
5. Deploy the frontend on Vercel from the `frontend` directory
6. Open the Vercel site and test image upload and prediction

### Airflow (Optional)
- Start services with Docker Compose

```bash
docker compose up
```

## API Endpoints
- `POST /api/predict`
- `GET /api/summary`
- `GET /api/predictions`
- `POST /api/predictions/save`
- `GET /api/analytics/stock-levels`

## Example Workflow
- Upload image
- Get prediction
- Optionally save result
- View saved history in the dashboard

## Image Guidance
- Best results come from clear shelf-focused images
- Keep the shelf centered and visible across most of the frame
- Avoid large floor areas, wide aisle shots, blur, glare, or heavy watermarks when possible
- Results may vary on out-of-distribution images

## Author
Jashanpreet Singh
