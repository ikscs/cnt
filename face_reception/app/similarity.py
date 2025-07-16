#!/usr/bin/python3
from db_wrapper import DB
from singleton import SingletonMeta

class Similarity(metaclass=SingletonMeta):
    sql1 = f'''SELECT DISTINCT p.point_id, d.time_slot
FROM face_data d
LEFT JOIN incoming i using(file_uuid)
LEFT JOIN origin o using(origin)
LEFT JOIN point p using(point_id)
WHERE point_id IS NOT NULL
AND time_slot IS NOT NULL
AND demography IS NOT NULL
AND embedding IS NOT NULL
AND neighbors IS NULL
ORDER BY time_slot ASC
LIMIT 1;
'''
    sql2 = f"CALL update_neighbors(%s, %s, %s, %s, %s);"

    def __init__(self):
        self.db = DB()
        self.lock = False

    def execute(self):
        if self.lock: return
        self.lock = True

        self.db.open()

        while True:
            self.db.cursor.execute(self.db.sql1)
            res = self.db.cursor.fetchone()
            if not res: break
            point_id = res[0]
            time_slot = res[1]

            self.db.cursor.execute(self.db.sql2, [point_id, time_slot, 'embedding', 'neighbors', 'cosine'])
            self.db.conn.commit()

        self.db.close()

        self.lock = False

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()

    similarity = Similarity()
    similarity.execute()
