from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

import json
import io
import numpy as np
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFile

from counter import Counter

import gc

ImageFile.LOAD_TRUNCATED_IMAGES = True

model = ['VGG-Face', 'Facenet', 'Facenet512', 'OpenFace', 'DeepFace','DeepID', 'ArcFace', 'Dlib', 'SFace', 'GhostFaceNet', 'Buffalo_L']
model_opt = ''.join([f'<option value="{e}">{e}</option>' for e in model])

backend = ['opencv', 'retinaface', 'mtcnn', 'ssd', 'dlib', 'mediapipe', 'yolov8', 'yolov11n', 'yolov11s', 'yolov11m', 'centerface', 'skip']
backend_opt = ''.join([f'<option value="{e}">{e}</option>' for e in backend])

body = '<form action="represent.json" method="POST" enctype="multipart/form-data">'
body += 'Backend <select name="backend">' + backend_opt + '</select><br>'
body += 'Model <select name="model">' + model_opt + '</select><br>'

body += '''
  <input type="radio" id="img" name="fmt" value="img" checked /><label for="img">Image</label><br>
  <input type="radio" id="jsn" name="fmt" value="json"/><label for="jsn">JSON</label><br>
  <input type="hidden" name="confidence" value="0.8">
  <input type='hidden' name='area' value='40'>
  <input type='file' name='f'><br>
  <input type='submit' value='submit'>
</form>
'''

body += '<hr><form action="demography.json" method="POST" enctype="multipart/form-data">'
body += 'Backend <select name="backend">' + backend_opt + '</select><br>'
body += '''
  <input type="hidden" name="actions" value="age, gender, race, emotion">
  <input type='file' name='f'><br>
  <input type='hidden' name='area' value='40'>
  <input type='submit' value='Demography'>
</form>
'''

counter = Counter('deep_face')
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'
    return data

@app.get("/info", response_class=JSONResponse)
async def info():
    return counter.info()

@app.get("/info_reset", response_class=JSONResponse)
async def info_reset():
    result = counter.info()
    counter.__init__('deep_face')
    return result

@app.post('/represent.json')
async def represent_json(
    request: Request,
    backend: str = Form(...),
    model: str = Form(...),
    f: UploadFile = File(...),
    fmt: str = Form(...),
    confidence: float = Form(...),
    area: int = Form(...)
):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, (backend, model, fmt, confidence, area))
    query_image = np.array(image)
    try:
        faces_data = DeepFace.represent(query_image, model_name=model, detector_backend=backend, enforce_detection=False)
    except Exception as err:
        print(str(err))
        faces_data = []

    if fmt == 'img':
        img = ImageDraw.Draw(image)
        for face in faces_data:
            if face['facial_area']['w'] < area:
                continue
            shape = [(face['facial_area']['x'], face['facial_area']['y']), (face['facial_area']['x'] + face['facial_area']['w'], face['facial_area']['y'] + face['facial_area']['h'])]
            img.rectangle(shape, fill=None, outline="red")

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        gc.collect()
        result = StreamingResponse(img_byte_arr, media_type="image/jpeg")

    elif fmt == 'json':
        content = [face for face in faces_data if face['facial_area']['w'] >= area]
        gc.collect()
        result = JSONResponse(content=content)

    counter.stop(request.url.path, (backend, model, fmt, confidence, area))
    return result

@app.post('/demography.json')
async def demography_json(
    request: Request,
    backend: str = Form(...),
    f: UploadFile = File(...),
    actions: str = Form(...),
    area: int = Form(...)
):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    actions = [e.strip() for e in actions.split(',') if e]
    counter.start(request.url.path, (backend, actions, area))
    query_image = np.array(image)

    try:
        objs = DeepFace.analyze(img_path=query_image, detector_backend=backend, actions=actions, silent=True, enforce_detection=False)
    except Exception as err:
        print(str(err))
        objs = []

    content = [e for e in convert_numpy(objs) if e['region']['w'] >= area]
    gc.collect()

    counter.stop(request.url.path, (backend, actions, area))
    return JSONResponse(content=content)

def convert_numpy(obj):
    if isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, tuple):
        return [convert_numpy(item) for item in obj]  # Convert tuple to list for JSON
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif obj is np.nan:
        return None
    else:
        return obj
