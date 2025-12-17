#!/usr/bin/python3
from db_wrapper import DB
from singleton import SingletonMeta

from service_exchange import Service_exchange

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
    sql3 = "CREATE TABLE IF NOT EXISTS person_match (ts TIMESTAMPTZ, face_uuid TEXT, parent_uuid TEXT, group_id INTEGER, point_id INTEGER);"
    sql4 = """SELECT t.name AS reaction_name, m.face_uuid, m.parent_uuid, ts, p.name, common_param, param
FROM person_match m
JOIN person_group_reaction r USING(group_id)
JOIN reaction_type t USING(reaction_id)
JOIN face_referer_data f ON f.face_uuid=parent_uuid
JOIN person p USING(person_id)
ORDER BY point_id, reaction_id;"""
    sql5 = "TRUNCATE person_match;"

    def __init__(self):
        self.se = Service_exchange()
        self.db = DB()
        self.lock = False

    def execute(self):
        if self.lock: return
        self.lock = True

        self.db.open()
        self.db.cursor.execute(self.sql3)

        while True:
            self.db.cursor.execute(self.sql1)
            res = self.db.cursor.fetchone()
            if not res: break
            point_id = res[0]
            time_slot = res[1]

            self.db.cursor.execute(self.sql2, [point_id, time_slot, 'embedding', 'neighbors', 'cosine'])

            self.db.cursor.execute(self.sql4)
            res = self.db.cursor.fetchall()
            if res:
                self.se.reaction(res)
                #self.db.cursor.execute(self.sql5)

            self.db.conn.commit()

        self.db.close()

        self.lock = False

if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()

    similarity = Similarity()
    similarity.execute()
