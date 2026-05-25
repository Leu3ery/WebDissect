FROM python:3.14-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared_models/ ./shared_models/
RUN pip install ./shared_models

COPY server/app/ ./app/


CMD ["python", "-m", "app"]