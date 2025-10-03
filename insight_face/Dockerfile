FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    mc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/. .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "insight_face_app:app", "--host", "0.0.0.0", "--port", "8000"]
