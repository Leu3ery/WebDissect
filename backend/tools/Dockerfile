FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY backend/tools/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared_models/ ./shared_models/
RUN pip install ./shared_models

COPY backend/tools/pyproject.toml .
RUN pip install -e .

COPY backend/tools/app/ ./app/


ENTRYPOINT ["python", "-m", "app"]