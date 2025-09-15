import psutil
from db_wrapper import DB

from fastapi import FastAPI, Form, File, UploadFile
from typing import Optional
import json

from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from camera_hik import Camera as Camera_hik
from camera_dah import Camera as Camera_dah

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
        camera = Camera_hik(credentials)

        res = camera.set_osd(data['header'], data['title'], data['data'])
        sql = f'''
UPDATE osd SET cur_data='{data["data"]}'
WHERE origin_id={origin_id}
'''
        db.cursor.execute(sql)
        result.append(res)

    db.close()

    return JSONResponse(content={"status": 'Ok', "result": result, 'sql': sql})

@app.post('/check_connection.json')
async def check_connection(
        origin_id: Optional[int] = Form(None),
        origin_type_id: Optional[int] = Form(None),
        credentials: Optional[str] = Form(None),
    ):
    db = DB()
    db.open()

    if origin_id:
        sql = '''
SELECT vendor, credentials FROM origin o
JOIN origin_type t USING(origin_type_id)
WHERE o.is_enabled AND t.enabled AND protocol='ISAPI' AND vendor IN ('Hikvision', 'Dahua')
AND id=%s
'''
        db.cursor.execute(sql, [origin_id])
        row = db.cursor.fetchone()
        db.close()

        if not row or not row[1]:
            return JSONResponse(content={"is_connected": False, "error_txt": f'Origin {origin_id} does not exists, not configured, disabled, or check not implemented'})

        vendor, credentials = row

    else:
        sql = "SELECT vendor FROM origin_type WHERE origin_type_id=%s AND enabled AND protocol='ISAPI' AND vendor IN ('Hikvision', 'Dahua')"
        db.cursor.execute(sql, [origin_type_id])
        row = db.cursor.fetchone()
        db.close()

        if not row:
            return JSONResponse(content={"is_connected": False, "error_txt": f'Origin_type_id {origin_type_id} does not exists, not configured, disabled, or check not implemented'})

        vendor = row[0]
        try:
            credentials = json.loads(credentials)
        except Exception as err:
            return JSONResponse(content={"is_connected": False, "error_txt": str(err)})

    if vendor == 'Hikvision':
        camera = Camera_hik(credentials)
    elif vendor == 'Dahua':
        camera = Camera_dah(credentials)

    return JSONResponse(content={"is_connected": camera.is_connected, "error_txt": camera.error_txt})
