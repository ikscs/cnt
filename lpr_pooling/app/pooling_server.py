import psutil
from fastapi import FastAPI, Form, File, UploadFile
from typing import Optional
import json

from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

def is_script_running(script_name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if script_name in proc.info['cmdline']:
               return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = 'healthy' if is_script_running('camera_pooling.py') else ''
    body = f'''{body}'''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data
