
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip --default-timeout=180 install --retries 10 --no-cache-dir flask gunicorn

RUN mkdir -p /app/database

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app.app:app"]
