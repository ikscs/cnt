from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

from onnx_predict import Predict
from counter import Counter

predict = Predict()

body = 'Healthy<br>'
body += 'Use action /demography.json with embedding payload'

counter = Counter('cv2_onnx')
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
    counter.__init__('cv2_onnx')
    return result

@app.post('/demography.json')
async def demography_json(
    request: Request,
    area: int = Form(...),
    detect_face: bool = Form(True),
    emb: list[float] = Form(...)
):

    counter.start(request.url.path, (area, detect_face))
    predict.predict_age_gender(emb)
    counter.stop(request.url.path, (area, detect_face))

    return JSONResponse(content=[predict.demography])

@app.post('/demo_person.json')
async def demo_person_json(
    request: Request,
    emb: list[float] = Form(...)
):
    counter.start(request.url.path, None)
    predict.predict_age_gender(emb)
    counter.stop(request.url.path, None)

    return JSONResponse(content=predict.demography)
