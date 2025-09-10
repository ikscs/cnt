#!/usr/local/bin/python
from croniter import croniter
from datetime import datetime, timedelta
from dateutil import tz
import requests

from db_wrapper import DB

REPORT_URL = 'http://django:8000/api/report/'

def main():
    dt = datetime.now()
    if dt.microsecond == 0:
        dt += timedelta(microseconds=1)
    to_zone = tz.tzlocal()

    db = DB()
    db.open()

    sql_select = '''
SELECT id, customer_id::INTEGER, app_id, report_id::INTEGER, lang, cron, last_dt, maillist, params
FROM report_schedule
WHERE enable
'''

    sql_update = "UPDATE report_schedule SET last_dt=now() WHERE id=%s;"

    db.cursor.execute(sql_select)
    result = db.cursor.fetchall()

    for id, customer_id, app_id, report_id, lang, cron, last_dt, maillist, params in result:

        itr = croniter(cron, dt)
        last_run = itr.get_prev(datetime)
        last_run = last_run.astimezone(to_zone)

        if not maillist or '@' not in maillist:
            continue

        if (last_dt != None) and last_dt >= last_run:
            continue

        parameters = []
        for k, v in params.items():
            parameters.append({'name': k, 'value': v})

        payload = {'lang': lang, 'app_id': app_id, 'report_id': report_id, 'recipient': maillist, 'parameters': parameters}
        headers = {'Authorization': f'{{"customer_id":{customer_id}}}'}
        try:
            response = requests.post(REPORT_URL, json=payload, headers=headers)
        except Exception as err:
            print(str(err))

        db.cursor.execute(sql_update, [id,])
        db.conn.commit()

    db.close()

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    main()
