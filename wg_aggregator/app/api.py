#!/usr/bin/env python3
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI, BackgroundTasks

from db_wrapper import DB
from wg_base import main

def apply_changes():
    db = DB()
    db.open()
    main(db.cursor)
    db.close()

apply_changes()

app = FastAPI(title="WireGuard Aggregator API")

@app.get('/', response_class=HTMLResponse)
async def hello():

    body = 'healthy' if True else ''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'

    return data

@app.get('/reload', response_class=HTMLResponse)
async def reload_cmd(background_tasks: BackgroundTasks):
    background_tasks.add_task(apply_changes)
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += 'Reload cmd sent Ok'
    data += '</body></html>'

    return data
