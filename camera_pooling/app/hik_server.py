import os
import psycopg2

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from camera_hik import Camera

def get_pg_conn():
    conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ.get('POSTGRES_PORT'), user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], dbname=os.environ['POSTGRES_DB'])
    return conn

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = '''<form action="set_osd.json" method="POST">
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
    conn = get_pg_conn()
    cur = conn.cursor()

    schema = os.environ['POSTGRES_SCHEMA']
    sql = f'''
SELECT origin_id, credentials, {schema}.get_osd_info(origin) FROM {schema}.osd os
JOIN {schema}.origin ori on os.origin_id=ori.id
WHERE os.is_enabled AND ori.is_enabled
AND point_id={point_id}
'''
    cur.execute(sql)
    result = []
    for origin_id, credentials, data in cur.fetchall():
        if not data:
            continue
        camera = Camera(credentials['host'], credentials['port'], credentials['user'], credentials['password'])

        res = camera.set_osd(data['header'], data['title'], data['data'])
        sql = f'''
UPDATE {schema}.osd SET cur_data='{data["data"]}'
WHERE origin_id={origin_id}
'''
        cur.execute(sql)
        result.append(res)

    conn.commit()
    cur.close()
    conn.close()

    return JSONResponse(content={"status": 'Ok', "result": result, 'sql': sql})
