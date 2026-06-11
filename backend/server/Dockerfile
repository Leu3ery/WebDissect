FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    ENV=production \
    DB_DIR=/app/db

COPY backend/server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/server/pyproject.toml .
COPY backend/server/app/ ./app/
RUN pip install --no-cache-dir -e .

EXPOSE 6767

ENTRYPOINT ["python", "-m", "app"]
