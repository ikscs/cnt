#!/usr/local/bin/python
import os
import psycopg2
from datetime import datetime, timedelta, timezone
from dateutil import tz

from telegram_bot import TBot

emoji = {'red': '🔴', 'yellow': '🟡', 'green': '🟢', 'grey': '⚪️'}

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

    dt_now = datetime.now()

    db = DB()
    db.open()

    sql_last_values = '''
SELECT mh.metric_id, m.metric_name, mh.collected_at, mh.status, mh.value
FROM metric_history mh
INNER JOIN (
    SELECT metric_id, MAX(collected_at) AS latest_collected
    FROM metric_history
    GROUP BY metric_id
) latest ON mh.metric_id = latest.metric_id AND mh.collected_at = latest.latest_collected
JOIN metric m ON mh.metric_id=m.id
WHERE m.enable
ORDER BY m.id
'''

    rez = dict()
    report = ''
    db.cursor.execute(sql_last_values)
    for id, metric_name, dt, status, value in db.cursor.fetchall():
        rez[id] = set()

        delta_t = dt_now.astimezone(timezone.utc) - dt.astimezone(timezone.utc)
        if delta_t > timedelta(days=1):
            rez[id].add('outdated')

        if 'outdated' not in rez:
            for e in status.values():
                e = e.lower() if e else ''
                if e in ('error', 'unhealthy'):
                    rez[id].add('error')
                    break
                elif e == 'warning':
                    rez[id].add('warning')
                elif e in ('ok', 'healthy', 'running'):
                    rez[id].add('ok')

        if 'outdated' in rez[id]:
            status = emoji['grey']
        elif 'error' in rez[id]:
            status = emoji['red']
        elif 'warning' in rez[id]:
            status = emoji['yellow']
        elif 'ok' in rez[id]:
            status = emoji['green']
        else:
            status = ' '

        report += f'{status} <b>{metric_name}</b>: {dt:%Y-%m-%d %H:%M:%S}\n'
        if ('error' in rez[id]) or ('warning' in rez[id]):
            report += f'{value}\n'
        report += '\n'

    total_set = set()
    for s in rez.values():
        total_set = total_set | s

    if 'error' in total_set:
        status = emoji['red']
    elif 'warning' in total_set:
        status = emoji['yellow']
    elif 'ok' in total_set:
        status = emoji['green']
    else:
        status = emoji['grey']

    report = f'{status} <b>Daily report</b>\n\n{report}'

    db.close()

    if len(report) > 4096:
        report = f'{report[:4080]} --skipped--'

#    with open('report.txt', 'wt', encoding='utf-8') as f:
#        f.write(report)

    bot = TBot()
    bot.send_message(report)

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    main()
