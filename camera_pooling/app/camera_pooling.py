import logging

from service_exchange import Service_exchange
from db_wrapper import DB
from sleeper import Sleeper

from pooling_hik import hik_runner
from pooling_dah import dah_runner

ORIGIN_PROTOCOL = 'ISAPI'
runners = {'Hikvision': hik_runner, 'Dahua': dah_runner}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    logging.info("Start service")
    db = DB()
    se = Service_exchange()
    sl = Sleeper()

    sql_jobs = f'''
SELECT o.point_id, o.id, o.origin, o.credentials, s.poling_period_s, t.params, t.vendor
FROM origin o
LEFT JOIN origin_schedule s ON o.id=s.origin_id
LEFT JOIN origin_type t using(origin_type_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled AND s.is_enabled
AND CURRENT_TIME between start_time AND end_time
AND NOW() >= next_dt
ORDER BY next_dt ASC
LIMIT 1
'''

    sql_last_dt = f"SELECT get_last_dt(%s)"

    sql_next = f"UPDATE origin_schedule SET next_dt=NOW()+INTERVAL '%s SECOND' WHERE origin_id=%s"

    sql_seconds = f'''
SELECT EXTRACT(EPOCH FROM s.next_dt - NOW())::INT AS seconds_until_next
FROM origin o
LEFT JOIN origin_schedule s ON o.id=s.origin_id
LEFT JOIN origin_type t using(origin_type_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled AND s.is_enabled
AND CURRENT_TIME between start_time AND end_time
AND NOW() < next_dt
ORDER BY next_dt ASC
LIMIT 1
'''

    while True:
        if sl.have_time():
            db.open()

        point_ids = set()
        while True:
            db.cursor.execute(sql_jobs)
            res = db.cursor.fetchone()
            if not res:
                break

            point_id, id, origin, credentials, poling_period_s, params, vendor = res
            point_ids.add(point_id)

            db.cursor.execute(sql_last_dt, [origin])
            res = db.cursor.fetchone()
            last_dt = res[0]

            try:
                count, end_time = runners[vendor](credentials, origin, last_dt, params)
            except Exception as e:
                logging.exception("Error while running job")

            db.cursor.execute(sql_next, [poling_period_s, id])
            db.conn.commit()

        db.cursor.execute(sql_seconds)

        res = db.cursor.fetchone()
        sl.update(res[0] if res else None)

#        logging.info(f"New time_sleep: {sl.time_sleep}")
        if not sl.have_time():
            continue

        db.close()

        for point_id in point_ids:
            if point_id:
                pass
                se.update_osd(point_id)

        logging.info(f"Sleep {sl.time_sleep}s")
        sl.sleep()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    main()
