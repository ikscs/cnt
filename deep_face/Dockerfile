FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    mc \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY tf/. .

COPY app/. .
RUN pip install -r requirements.txt
RUN pip install tensorflow-2.13.0-cp310-cp310-linux_x86_64.whl
RUN pip cache purge

EXPOSE 8000

CMD ["uvicorn", "deep_face_app:app", "--host", "0.0.0.0", "--port", "8000"]
