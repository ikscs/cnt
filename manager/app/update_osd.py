#!/usr/local/bin/python
import os
import requests
import psycopg2

OSD_URL = 'http://camera_pooling:8000/set_osd.json'

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

    sql = 'SELECT DISTINCT point_id FROM osd JOIN origin ON origin_id=id;'

    db.cursor.execute(sql)
    for point_id, in db.cursor.fetchall():
        print(f'Update OSD for point_id: {point_id}')
        response = requests.post(OSD_URL, data={'point_id': point_id})

    db.close()
