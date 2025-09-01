#!/bin/bash

service cron start &
uvicorn main:app --host 0.0.0.0 --port 8000
