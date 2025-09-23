#!/usr/local/bin/python
import os
import psycopg2
import subprocess
from croniter import croniter
from datetime import datetime, timedelta
from dateutil import tz
import json

from info_bot import bot_report

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

def parse_df(txt, template):
    line = txt.strip().split('\n')[-1]
    values = line.split()

    result = dict()
    try:
        result['total'] = round(int(values[1])/1024/1024)
    except Exception as err:
        result['total'] = -1

    try:
        result['used'] = int(values[4].replace('%', ''))
    except Exception as err:
        result['used'] = -1

    return result

def parse_du(txt, template):
    field = 'name'
    line = txt.strip().split('\n')[0]
    values = line.split()

    result = dict()
    name = template['fields'][0]['name']
    try:
        result[name] = int(values[0])/1024/1024
    except Exception as err:
        result[name] = -1
    return result

def parse_regular(txt, template):
    if not txt:
        return {}
    data = json.loads(txt)
    result = dict()
    for row in template['fields']:
        name = row['name']
        result[name] = data.get(name)
    return result

def parse_json(data, template):
    if not data:
        return {}
    result = dict()
    for row in template['fields']:
        name = row['name']
        result[name] = data.get(name)
    return result

def get_status(val, ranges):
    for k, v in ranges.items():
        if isinstance(val, (float, int)):
            if val >= v[0] and val <= v[1]:
                return k
        elif isinstance(val, (str, )):
            if val in v:
                return k
    return None

def main():
    parsers = {
        'df': parse_df, 'du': parse_du,
        './docker_metric.py': parse_regular, './procinfo.py': parse_regular,
        './face_engine.py': parse_json,
        './sql_exec.py': parse_regular,
    }

    dt = datetime.now()
    if dt.microsecond == 0:
        dt += timedelta(microseconds=1)
    to_zone = tz.tzlocal()

    db = DB()
    db.open()

    sql_select = '''
SELECT DISTINCT ON (m.id)
m.id, m.metric_cmd, m.metric_param, m.cron, m.template, h.collected_at
FROM metric m
LEFT JOIN metric_history h ON m.id = h.metric_id
WHERE m.enable
ORDER BY m.id, h.collected_at DESC;
'''

    sql_insert = 'INSERT INTO metric_history (metric_id, "value", status) VALUES (%s, %s, %s)'

    sql_last_values = '''
SELECT mh.metric_id, mh.status, mh.value, m.metric_name
FROM metric_history mh
INNER JOIN (
    SELECT metric_id, MAX(collected_at) AS latest_collected
    FROM metric_history
    GROUP BY metric_id
) latest ON mh.metric_id = latest.metric_id AND mh.collected_at = latest.latest_collected
JOIN metric m ON mh.metric_id=m.id
WHERE m.enable
'''
    db.cursor.execute(sql_last_values)
    last_values = {id: {'status': status, 'value': value, 'name': name} for id, status, value, name in db.cursor.fetchall()}

    db.cursor.execute(sql_select)
    for id, metric_cmd, metric_param, cron, template, collected_at in db.cursor.fetchall():
        itr = croniter(cron, dt)
        last_run = itr.get_prev(datetime)
        last_run = last_run.astimezone(to_zone)

        if (collected_at != None) and collected_at >= last_run:
            continue
        result = subprocess.run(' '.join((metric_cmd, metric_param)), capture_output=True, text=True, shell=True)

        if (not result.stdout) or (metric_cmd not in parsers):
            continue

        txt = result.stdout

        try:
            data = json.loads(txt)
        except Exception as err:
            data = txt

        if isinstance(data, list):
            output = [parsers[metric_cmd](line, template) for line in data]
        else:
            output = [parsers[metric_cmd](txt, template)]

        #Get ranges for status check
        ranges = dict()
        for e in template["fields"]:
            ranges[e["name"]] = e.get("range")

        for row in output:
            value = json.dumps(row) if row else None

            #check status
            status = dict()
            for k, v in row.items():
                if not ranges[k]:
                    continue
                status[k] = get_status(v, ranges[k])
            st = json.dumps(status) if status else None

            db.cursor.execute(sql_insert, (id, value, st))

    db.conn.commit()

    db.cursor.execute(sql_last_values)
    new_values = {id: {'status': status, 'value': value, 'name': name} for id, status, value, name in db.cursor.fetchall()}

    db.close()

    bot_report(last_values, new_values)

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    main()
