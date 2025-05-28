import psutil
from db_wrapper import DB

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from camera_hik import Camera

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
    body = f'''{body}<br><form action="set_osd.json" method="POST">
<label for="point_id">point_id:</label><input type="text" id="point_id" name="point_id"><br>
<input type='submit' value='submit'>
</form>
'''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data

@app.post('/set_osd.json')
async def set_osd(point_id: int=Form(...)):
    db = DB()
    db.open()

    sql = f'''
SELECT origin_id, credentials, get_osd_info(origin) FROM osd os
JOIN origin ori on os.origin_id=ori.id
WHERE os.is_enabled AND ori.is_enabled
AND point_id={point_id}
'''
    db.cursor.execute(sql)
    result = []
    for origin_id, credentials, data in db.cursor.fetchall():
        if not data:
            continue
        camera = Camera(credentials)

        res = camera.set_osd(data['header'], data['title'], data['data'])
        sql = f'''
UPDATE osd SET cur_data='{data["data"]}'
WHERE origin_id={origin_id}
'''
        db.cursor.execute(sql)
        result.append(res)

    db.close()

    return JSONResponse(content={"status": 'Ok', "result": result, 'sql': sql})
