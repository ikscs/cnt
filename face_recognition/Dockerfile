FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    mc \
    gcc \
    clang \
    clang-tools \
    libgl1-mesa-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY cafe/. .

COPY app/. .
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "face_recognition_app:app", "--host", "0.0.0.0", "--port", "8000"]
