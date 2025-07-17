FROM python:3-slim

RUN apt-get update && apt-get install -y \
    mc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .
RUN chmod +x *.py

EXPOSE 5000

CMD ["uvicorn", "fs_db_wrap:asgi_app", "--host", "0.0.0.0", "--port", "5000"]
