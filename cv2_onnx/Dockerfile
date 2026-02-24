FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    mc \
    libxcb1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

COPY model/. /app/

WORKDIR /app

COPY app/. .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "cv2_onnx_app:app", "--host", "0.0.0.0", "--port", "8000"]
