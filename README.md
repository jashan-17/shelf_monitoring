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
