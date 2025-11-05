FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    mc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app/. .
RUN pip install -r requirements.txt

RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
