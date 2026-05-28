FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY backend/server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/server/pyproject.toml .
RUN pip install -e .

COPY backend/server/app/ ./app/

EXPOSE 6767


ENTRYPOINT ["python", "-m", "app"]