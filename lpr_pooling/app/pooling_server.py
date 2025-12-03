import psutil
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Any, Dict, List
from pydantic import BaseModel

from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from camera_tyto import Camera as Camera_tyto
from adapter import adapt_action

Camera = {'Tyto': Camera_tyto, }

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
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins = ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class PayloadBase(BaseModel):
    credentials: Dict[str, Any]
    vendor: str

class PayloadEventImages(PayloadBase):
    uuid: str

class PayloadAction(PayloadBase):
    action: str
    plates: Optional[List[str]] = []
    brands: Optional[List[str | None]] = []
    owners: Optional[List[str | None]] = []

def get_camera(data):
    if data.vendor not in Camera:
        return False, JSONResponse(content={"result": False, "message": f"Vendor {data.vendor} not realized"})

    camera = Camera[data.vendor](data.credentials)
    if not camera.is_connected:
        return False, JSONResponse(content={"result": False, "message": camera.error_txt})

    return camera, None

@app.post('/check_connection')
async def check_connection(data: PayloadBase):
    camera, response = get_camera(data)
    if not camera:
        return response

    return JSONResponse(content={"result": camera.is_connected, "message": camera.error_txt})

@app.post('/get_event_images')
async def get_event_images(data: PayloadEventImages):
    camera, response = get_camera(data)
    if not camera:
        return response

    result = camera.get_by_uuid(data.uuid)
    if not result:
        return JSONResponse(content={"result": False})
    else:
        result["result"] = True
        return JSONResponse(content=result)

@app.post('/get_snapshot')
async def get_snapshot(data: PayloadBase):
    camera, response = get_camera(data)
    if not camera:
        return response

    result = camera.get_snapshot()
    if not result:
        return JSONResponse(content={"result": False})
    else:
        return JSONResponse(content={"result": True, 'image': result})

@app.post('/make_action')
async def make_action(data: PayloadAction):
    camera, response = get_camera(data)
    if not camera:
        return response

    result = camera.make_action(data.action, data.plates, data.brands, data.owners)
    result = adapt_action(data.vendor, data.action, result)

    return JSONResponse(content=result)
