import json
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from db_wrapper import DB
from sender import Sender, get_email_cfg
from datetime import date

from xlsx_report import mk_xlsx_report

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def hello():
    body = 'healthy' if True else ''
    data = '<html><head></head>'
    data += '<link rel="icon" href="data:image/png;base64,iVBORw0KGgo=">'
    data += '<body>'
    data += body
    data += '</body></html>'
    return data

@app.post('/send_mail.json')
async def send_mail(
    recipient: str=Form(...),
    subject: str=Form(...),
    data: str=Form(...),
    chart: str=Form(...)
):
    db = DB()
    db.open()

    email_cfg = get_email_cfg(db.cursor)
    db.close()

    if not email_cfg:
        return JSONResponse(content={"status": 'Error', "result": "Configuration error"})

    if not recipient or '@' not in recipient:
        return JSONResponse(content={"status": 'Error', "result": "Wrong recipient"})

    sender = Sender(email_cfg)

    today = date.today()
    subject = f'{subject} {today}'

    data = json.loads(data)
    body = list_to_html(data, subject)
    xlsx_data = mk_xlsx_report(subject, data)

    sender.recipient = recipient

    sender.send_email(subject, '', html=body, attachment_data=xlsx_data, attachment_name=f'{subject}.xlsx')

    return JSONResponse(content={"status": 'Ok'})

def list_to_html(data_list, subject):
    if not data_list:
        return "<table></table>"

    headers = data_list[0].keys()

    html_table = f"<h1>{subject}</h1>\n"

    html_table += "<table cellpadding=\"5\" border='1' style='border-collapse: collapse;'>\n"
    html_table += "  <thead>\n    <tr>\n"
    for header in headers:
        html_table += f"      <th>{header}</th>\n"
    html_table += "    </tr>\n  </thead>\n"

    html_table += "  <tbody>\n"
    for row_dict in data_list:
        html_table += "    <tr>\n"
        for header in headers:
            value = row_dict.get(header, "")
            html_table += f"      <td>{value}</td>\n"
        html_table += "    </tr>\n"
    html_table += "  </tbody>\n"
    html_table += "</table>"

    return html_table
