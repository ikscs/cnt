import os
import sys
import uuid
import subprocess

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional

from db_wrapper import DB
from service_exchange import Service_exchange

class Event_record(BaseModel):
    origin: str
    ts: str
    prefix: str
    name: str

#from dotenv import load_dotenv
#load_dotenv()

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PROCESSOR_SCRIPT = DIR_PATH + "/processor.py"

class custom_SQL():
    event_keys = ['origin', 'origin_id', 'ts', 'prefix', 'name']

    def __init__(self):
        self.sql_insert_incoming_with_ts = f"INSERT INTO incoming (file_uuid, origin, origin_id, title, filename, ts) VALUES(%s, %s, %s, %s, %s, %s) ON CONFLICT (file_uuid) DO NOTHING"

        fields = ', '.join(self.event_keys)
        vars_cnt = ','.join(['%s']*len(self.event_keys))
        self.sql_insert_event = f"INSERT INTO event_crossline ({fields}) VALUES({vars_cnt}) ON CONFLICT ({fields}) DO NOTHING"


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = '''<form action="upload.json" method="POST" enctype="multipart/form-data">
<label for="origin">origin (From):</label><input type="text" id="origin" name="origin"><br>
<label for="origin_id">origin_id:</label><input type="text" id="origin_id" name="origin_id"><br>
<label for="title">title (Subject):</label><input type="text" id="title" name="title"><br>
<input type='file' name='f'><br>
<input type='submit' value='submit'>
</form>
'''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data

@app.post('/upload.json', response_class=HTMLResponse)
async def upload_json(
    origin: str = Form(...),
    origin_id: int = Form(None),
    title: str = Form(...),
    f: UploadFile = File(...),
    ts: str = Form(None)
):

    file_uuid = uuid.uuid4().hex
    contents = await f.read()

    se = Service_exchange()
    content = se.set_img(file_uuid, contents)
    if not content:
        return None

    db = DB()
    db.open()
    custom_sql = custom_SQL()

    sql = custom_sql.sql_insert_incoming_with_ts
    if not ts:
        sql = sql.replace(', ts) VALUES(%s, %s', ') VALUES(%s')

    if origin_id == None:
        origin_id = origin
        sql = sql.replace('VALUES(%s, %s, %s', 'VALUES(%s, %s, get_id_by_origin(%s)')

    if not ts:
        data = [file_uuid, origin, origin_id, title, f.filename]
    else:
        data = [file_uuid, origin, origin_id, title, f.filename, ts]

    db.cursor.execute(sql, data)
    db.close()

    try:
        process = subprocess.Popen([sys.executable, PROCESSOR_SCRIPT],
            #stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(str(e))

    return file_uuid

@app.post('/events.json')
async def upload_json(
    events: List[Event_record]
):

    db = DB()
    db.open()
    custom_sql = custom_SQL()

    data = [[getattr(row, e, None) for e in custom_sql.event_keys] for row in events]
    db.cursor.executemany(custom_sql.sql_insert_event, data)
    db.close()

    return JSONResponse(content={'result': 'Ok', 'count': len(data)})
