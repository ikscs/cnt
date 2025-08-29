#!/usr/local/bin/python
import os
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime, timedelta
from dateutil import tz
import json
from sender import Sender, get_email_cfg

class DB:
    def open(self):
        self.conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ.get('POSTGRES_PORT'),
            user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'],
            dbname=os.environ['POSTGRES_DB']
        )
        self.cursor = self.conn.cursor()
        self.schema = os.environ['POSTGRES_SCHEMA']
        sql = f'SET search_path = {self.schema}, "$user", public;'
        self.cursor.execute(sql)

    def close(self):
        self.cursor.close()
        self.conn.close()

def main():
    dt = datetime.now()
    if dt.microsecond == 0:
        dt += timedelta(microseconds=1)
    to_zone = tz.tzlocal()

    db = DB()
    db.open()

    email_cfg = get_email_cfg(db.cursor)
    if not email_cfg:
        db.close()
        return
    sender = Sender(email_cfg)

    sql_select = '''
SELECT s.id, s.cron, s.last_dt, maillist, v.query, v.report_config::jsonb->>'params', v.report_name, v.report_name_lang, s.params
FROM report_schedule s
LEFT JOIN v_perm_report v USING(app_id, report_id, lang)
WHERE s.enable
'''

    sql_update = "UPDATE report_schedule SET last_dt=now() WHERE id=%s;"

    db.cursor.execute(sql_select)
    result = db.cursor.fetchall()

    for id, cron, last_dt, maillist, query, report_config_params, report_name, report_name_lang, params in result:
        itr = croniter(cron, dt)
        last_run = itr.get_prev(datetime)
        last_run = last_run.astimezone(to_zone)

        if not maillist or '@' not in maillist:
            continue

        if (last_dt != None) and last_dt >= last_run:
            continue

        parameters = []
        for p in json.loads(report_config_params):
            k = p['name']
            v = params.get(k)
            parameters.append({'name': k, 'value': v})

        if report_name_lang:
            report_name = report_name_lang

        data = exec_report(db.cursor, query, parameters)
        if data:
            body = list_to_html(data)

            sender.recipient = maillist
            sender.send_email(report_name, '', html=body)

        db.cursor.execute(sql_update, [id,])
        db.conn.commit()

    db.close()

def exec_report(cursor, query, parameters):
    val = {e.get('name'): e.get('value') for e in parameters}

    for param in parameters:
        query = query.replace(f":{param['name']}", f"%({param['name']})s")

    cursor.execute(query, val)

    field_names = [e[0] for e in cursor.description]
    data = []
    for row in cursor.fetchall():
        r = {name: value for name, value in zip(field_names, row)}
        data.append(r)

    return data

def list_to_html(data_list):
    if not data_list:
        return "<table></table>"

    headers = data_list[0].keys()

    html_table = "<table cellpadding=\"5\" border='1' style='border-collapse: collapse;'>\n"
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

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    main()
