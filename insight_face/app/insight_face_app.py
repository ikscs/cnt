from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

import json
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFile, ImageFont

from if_predict import Predict
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

counter = Counter('insight_face')
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
    counter.__init__('insight_face')
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
        image = predict.load_image_file(io.BytesIO(file_bytes))
        if fmt == 'img':
            faces_data = predict.process_image(image, area=area)
        elif fmt == 'json':
            faces_data = predict.get_represent(image, confidence, area)
        else:
            faces_data = []
    except Exception as err:
        print(str(err))
        faces_data = []

    if fmt == 'img':
        pil_image = Image.fromarray(image)
        img = ImageDraw.Draw(pil_image)
        myFont = ImageFont.load_default(size=16)
        for face in faces_data:
            shape = [round(face['bbox'][0]), round(face['bbox'][1]), round(face['bbox'][2]), round(face['bbox'][3])]
            img.rectangle(shape, fill=None, outline="red")
            img.text((shape[0], shape[1]), str(face["age"]), font=myFont, fill={0: "red", 1: "blue"}.get(face['gender'], 'yellow'), stroke_width=3, stroke_fill="white")

        img_byte_arr = io.BytesIO()
        pil_image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        result = StreamingResponse(img_byte_arr, media_type="image/jpeg")

    elif fmt == 'json':
        data = []
        for e in faces_data:
            landmark = dict()
            landmark["x"] = round(e.bbox[0])
            landmark["y"] = round(e.bbox[1])
            landmark["w"] = round(e.bbox[2] - e.bbox[0])
            landmark["h"] = round(e.bbox[3] - e.bbox[1])
            data.append({"embedding": e.get('embedding'), "facial_area": landmark, "face_confidence": e.get('det_score')})
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
        image = predict.load_image_file(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, (area, detect_face))
    result = predict.process_image(image, area=area)
    counter.stop(request.url.path, (area, detect_face))

    return JSONResponse([convert_demography(e) for e in result])

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
        image = predict.load_image_file(io.BytesIO(file_bytes))
    except Exception as err:
        return JSONResponse(content={"error": str(err)}, status_code=400)

    counter.start(request.url.path, None)
    predict.process_image(image, is_one_person=True)
    counter.stop(request.url.path, None)

    return JSONResponse(content=convert_demography(predict.demography))

def convert_demography(inp):
    try:
        age = inp['age']
        m_gender = inp['gender'] * 100.0
    except Exception as err:
        return None
    result = {'age': age, 'gender': {'Man': m_gender, 'Woman': 100-m_gender}, 'dominant_gender': {True: 'Man', False: 'Woman'}.get(m_gender > 50.0)}
    return result

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
