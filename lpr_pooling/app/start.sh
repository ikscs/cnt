#!/bin/bash

# Start FastAPI app using uvicorn in the background
uvicorn pooling_server:app --host 0.0.0.0 --port 8000 &

# Start pooling in the foreground
while true; do
  echo "Start camera pooling"
  python camera_pooling.py
done


