FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-deploy.txt /tmp/requirements-deploy.txt
RUN pip install --no-cache-dir -r /tmp/requirements-deploy.txt

COPY backend /app/backend
COPY .env.example /app/.env.example

EXPOSE 8010

CMD ["uvicorn", "src.api.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8010"]
