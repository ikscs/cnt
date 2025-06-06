#!/usr/local/bin/python
import os
import requests
import psycopg2
import json

TARGET_URLS = ['http://fair_face:8000/info', ]

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

if __name__ == "__main__":
    db = DB()
    db.open()

    fields = 'name, entry, from_ts, cnt, total_ms, min_ms, max_ms'
    keys = fields.split(', ')
    percent_s = ', '.join('%s' for _ in keys)

    sql = f'INSERT INTO service_info ({fields}) VALUES({percent_s});'

    for url in TARGET_URLS:
        response = requests.get(url)
        result = response.json()
        data = []
        for row in result:
            r = [row[k] for k in keys]
            data.append(r)
        db.cursor.executemany(sql, data)
        db.conn.commit()

    db.close()
