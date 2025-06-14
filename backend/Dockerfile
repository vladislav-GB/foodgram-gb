# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

WORKDIR /app/backend/foodgram

ENV PYTHONPATH="/app/backend/foodgram"

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]






