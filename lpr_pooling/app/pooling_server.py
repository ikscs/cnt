import psutil
from fastapi import FastAPI, Form, File, UploadFile
from typing import Optional
import json

from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

def is_script_running(script_name):
    for proc in psutil.process_iter(['cmdline']):
        try:
            if script_name in ' '.join(proc.info['cmdline']):
               return proc.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception as err:
            continue
    return False

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = ''
    if is_script_running('camera_pooling.py'):
        body = 'healthy'
    body = f'''{body}'''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data

@app.get('/test.json')
async def test_json():
    return JSONResponse(content={"value_str": "str1", "value_bool": True, "value_int": 77, "value_float": 1.23})
