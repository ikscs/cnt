#!/usr/local/bin/python
import sys
import os
import psycopg2
import json

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

def main(sql):
    db = DB()
    db.open()

    db.cursor.execute(sql)
    row = db.cursor.fetchone()
    columns = [desc[0] for desc in db.cursor.description]
    if row:
        result_dict = dict(zip(columns, row))
    else:
        result_dict = {key: None for key in columns}

    db.close()

    return result_dict

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <sql>')
        exit(1)

    sql = ' '.join(sys.argv[1:])
    result = main(sql)

    print(json.dumps(result))
