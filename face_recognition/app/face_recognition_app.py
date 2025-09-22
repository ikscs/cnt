from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

import json
import io
import numpy as np
from copy import deepcopy
import face_recognition
from PIL import Image, ImageDraw, ImageFile, ImageFont

from cv2_predict import Predict
from counter import Counter

ImageFile.LOAD_TRUNCATED_IMAGES = True
predict = Predict()

body = '<form action="represent.json" method="POST" enctype="multipart/form-data">'
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
body += '''
  <input type='file' name='f'><br>
  <input type='hidden' name='area' value='40'>
  <input type='submit' value='Demography'>
</form>
'''

body += '<hr><form action="demo_person.json" method="POST" enctype="multipart/form-data">'
body += '''
  <input type='file' name='f'><br>
  <input type='submit' value='Demography one person'>
</form>
'''

counter = Counter('face_recognition')
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
    counter.__init__('face_recognition')
    return result

@app.post('/represent.json')
async def represent_json(
    request: Request,
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

    counter.start(request.url.path, (fmt, confidence, area))

    try:
        image_fr = face_recognition.load_image_file(io.BytesIO(file_bytes))
        faces_data = face_recognition.face_locations(image_fr)
    except Exception as err:
        print(str(err))
        faces_data = []

    if fmt == 'img':
        img = ImageDraw.Draw(image)  
        for face in faces_data:
            shape = [face[3], face[0], face[1], face[2]]
            if shape[2]-shape[0] < area:
                continue
            img.rectangle(shape, fill=None, outline="red")

            myFont = ImageFont.load_default(size=16)
            predict.process_image(image_fr[face[0]:face[2], face[3]:face[1]])
            img.text((face[3], face[2]), str(predict.demography["age"]), font=myFont, fill="red" if predict.demography["dominant_gender"]=='Woman' else "blue", stroke_width=3, stroke_fill="white")

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        result = StreamingResponse(img_byte_arr, media_type="image/jpeg")

    elif fmt == 'json':
        encodings = face_recognition.face_encodings(image_fr, known_face_locations=faces_data)
        landmarks = face_recognition.face_landmarks(image_fr, face_locations=faces_data, model="small")

        data = []
        for face, encoding, landmark in zip(faces_data, encodings, landmarks):
            landmark["x"] = face[3]
            landmark["y"] = face[0]
            landmark["w"] = face[1] - face[3]
            landmark["h"] = face[2] - face[0]
            if landmark["w"] < area:
                continue
            data.append({"embedding": encoding, "facial_area": landmark, "face_confidence": 1})
        result = JSONResponse(content=convert_numpy(data))

    counter.stop(request.url.path, (fmt, confidence, area))
    return result

@app.post('/demography.json')
async def demography_json(
    request: Request,
    f: UploadFile = File(...),
    area: int = Form(...),
    detect_face: bool = Form(True)
):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image_fr = face_recognition.load_image_file(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, (area, detect_face))
    objs = []
    if detect_face:
        try:
            faces_data = face_recognition.face_locations(image_fr)
            for top, right, bottom, left in faces_data:
                if right-left < area:
                    continue
                predict.process_image(image_fr[top:bottom, left:right])
                objs.append(deepcopy(predict.demography))
        except Exception as err:
            print(str(err))
            objs = []
    else:
        try:
            predict.process_image(image_fr)
            objs.append(predict.demography)
        except Exception as err:
            print(str(err))
            objs = []

    result = JSONResponse(content=convert_numpy(objs))
    counter.stop(request.url.path, (area, detect_face))

    return result

@app.post('/demo_person.json')
async def demo_person_json(
    request: Request,
    f: UploadFile = File(...)
):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image = face_recognition.load_image_file(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, None)
    predict.process_image(image)
    counter.stop(request.url.path, None)

    return JSONResponse(content=predict.demography)

@app.post('/get_confidence.json')
async def demo_person_json(
    request: Request,
    f: UploadFile = File(...),
    data: str = Form(None)

):

    try:
        file_bytes = await f.read()
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    try:
        image = face_recognition.load_image_file(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, None)
    face_confidence = predict.get_confidence(image)
    counter.stop(request.url.path, None)

    return JSONResponse(content={'face_confidence': face_confidence})

def convert_numpy(obj):
    if isinstance(obj, dict):
        return {key: convert_numpy(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(item) for item in obj]
    elif isinstance(obj, tuple):
        return [convert_numpy(item) for item in obj]
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
