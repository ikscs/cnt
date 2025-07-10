#!/usr/bin/python3
import os
import psycopg2
from run_once import run_once, run_once_pid
#from dotenv import load_dotenv

def main(src='embedding', dst='neighbors', method='cosine', demography='demography'):
    conn = psycopg2.connect(
        host=os.environ['POSTGRES_HOST'],
        port=os.environ.get('POSTGRES_PORT'),
        user=os.environ['POSTGRES_USER'],
        password=os.environ['POSTGRES_PASSWORD'],
        dbname=os.environ['POSTGRES_DB']
    )
    cur = conn.cursor()
    schema = os.environ['POSTGRES_SCHEMA']

    sql1 = f'''
SELECT DISTINCT p.point_id, d.time_slot
FROM {schema}.face_data d
LEFT JOIN {schema}.incoming i using(file_uuid)
LEFT JOIN {schema}.origin o using(origin)
LEFT JOIN {schema}.point p using(point_id)
WHERE point_id IS NOT NULL
AND time_slot IS NOT NULL
AND {demography} IS NOT NULL
AND {src} IS NOT NULL
AND {dst} IS NULL
ORDER BY time_slot ASC
LIMIT 1
'''

    sql2 = f"CALL {schema}.update_neighbors(%s, %s, %s, %s, %s);"

    while True:
        cur.execute(sql1)
        res = cur.fetchone()
        if not res: break
        point_id = res[0]
        time_slot = res[1]

#        print(point_id, time_slot)

        cur.execute(sql2, [point_id, time_slot, src, dst, method])
        conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
    import sys
#    load_dotenv()

    if len(sys.argv) == 1:
        run_once(main)
    else:
        run_once_pid(sys.argv[1], main, src=sys.argv[2], dst=sys.argv[3], method=sys.argv[4], demography=sys.argv[5])
