#!/usr/local/bin/python
import os
import psycopg2
import shutil
import subprocess

HOST = 'cnt.theweb.place'

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

def get_du_size(path):
    result = subprocess.run(['du', '-s', path], capture_output=True, text=True)
    size, _ = result.stdout.strip().split('\t')
    try:
        size_gb = int(size)/1024/1024
    except Exception as err:
        size_gb = -1
    return size_gb

if __name__ == "__main__":
    stat = shutil.disk_usage('.')
    total = stat.total/1024/1024/1024

    db = DB()
    db.open()

    sql_select = f"SELECT id, disk_path FROM host_disk_usage WHERE host_name='{HOST}';"
    sql_update = f"UPDATE host_disk_usage SET total_size_gb=%s, used_space_gb=%s, collected_at=%s WHERE id=%s;"

    db.cursor.execute(sql_select)
    for id, disk_path in db.cursor.fetchall():
        size = get_du_size(disk_path)
        db.cursor.execute(sql_update, (total, size, 'now()', id))

    db.conn.commit()
    db.close()
