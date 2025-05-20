#!/bin/bash

# Start script1.py in the background
python camera_pooling.py &

# Start FastAPI app using uvicorn in the foreground
uvicorn hik_server:app --host 0.0.0.0 --port 8000
