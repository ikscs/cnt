#!/usr/local/bin/python
import os
import psycopg2

class DB:
    def open(self):
        self.conn = psycopg2.connect(host=os.environ['POSTGRES_HOST'], port=os.environ.get('POSTGRES_PORT', 5432),
            user=os.environ['POSTGRES_USER'], password=os.environ['POSTGRES_PASSWORD'], dbname=os.environ['POSTGRES_DB']
        )
        self.cursor = self.conn.cursor()
        self.schema = os.environ['POSTGRES_SCHEMA']
        sql = f'SET search_path = {self.schema}, "$user", public;'
        self.cursor.execute(sql)

    def close(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

def main():
    db = DB()
    db.open()

    sql_select = '''SELECT
point_id, time_slot, face_uuid FROM face_data d
JOIN incoming i using(file_uuid) 
JOIN origin o on origin_id=o.id
WHERE NOT is_checked
AND get_time_slot('day', now()) <> time_slot
'''

    sql_update = 'CALL update_neighbors(%s, %s, %s, %s, %s);'

    db.cursor.execute(sql_select)
    results = db.cursor.fetchall()

    finished = set()
    faces = set()

    for point_id, time_slot, face_uuid in results:
        faces.add(face_uuid)
        if (point_id, time_slot) in finished:
            continue

        finished.add((point_id, time_slot))

        sql_update = 'CALL update_neighbors(%s, %s, %s, %s, %s);'
        db.cursor.execute(sql_update, [point_id, time_slot, 'embedding', 'neighbors', 'cosine'])

    if faces:
        faces_str = "','".join(faces)
        faces_str = "'" + faces_str + "'"
        sql_finalize = f"UPDATE face_data SET is_checked=True WHERE NOT is_checked AND face_uuid IN({faces_str});"
        db.cursor.execute(sql_finalize)

    db.conn.commit()
    db.close()

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
    main()
