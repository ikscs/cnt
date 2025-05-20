from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

import json
import io
import numpy as np
from deepface import DeepFace
from PIL import Image, ImageDraw, ImageFile

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
  <input type='submit' value='Demography'>
</form>
'''

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'
    return data

@app.post('/represent.json')
async def represent_json(
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
    query_image = np.array(image)

    try:
        faces_data = DeepFace.represent(query_image, model_name=model, detector_backend=backend, enforce_detection=False)
    except Exception as err:
        print(str(err))
        faces_data = []

    if fmt == 'img':
        img = ImageDraw.Draw(image)
        for face in faces_data:
            shape = [(face['facial_area']['x'], face['facial_area']['y']), (face['facial_area']['x'] + face['facial_area']['w'], face['facial_area']['y'] + face['facial_area']['h'])]
            img.rectangle(shape, fill=None, outline="red")

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        gc.collect()
        return StreamingResponse(img_byte_arr, media_type="image/jpeg")

    elif fmt == 'json':
        gc.collect()
        return JSONResponse(content=faces_data)

@app.post('/demography.json')
async def demography_json(
    backend: str = Form(...),
    f: UploadFile = File(...),
    actions: str = Form(...)
):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image = Image.open(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)
    query_image = np.array(image)

    actions = [e.strip() for e in actions.split(',') if e]
    try:
        objs = DeepFace.analyze(img_path=query_image, detector_backend=backend, actions=actions, silent=True)
    except Exception as err:
        print(str(err))
        objs = []

    gc.collect()
    return JSONResponse(content=convert_numpy(objs))

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
