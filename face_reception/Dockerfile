FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    mc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/. .
RUN pip install -r requirements.txt

RUN mkdir -p /var/screenshots

EXPOSE 8000

CMD ["uvicorn", "receiver:app", "--host", "0.0.0.0", "--port", "8000"]
