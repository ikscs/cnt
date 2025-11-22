import logging

from service_exchange import Service_exchange
from db_wrapper import DB
from sleeper import Sleeper

from pooling_hik import hik_runner
from pooling_dah import dah_runner

from runner import Runner

ORIGIN_PROTOCOL = 'ISAPI'
ZERO_DAY = '2025-04-26 00:00:00+03'

runners = {'Hikvision': hik_runner, 'Dahua': dah_runner}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    logging.info("Start service")
    db = DB()
    se = Service_exchange()
    sl = Sleeper()

    sql_jobs = f'''
SELECT o.point_id, o.id, o.origin, o.credentials, o.poling_period_s, t.params, t.vendor
FROM origin o
LEFT JOIN origin_next_pooling n ON o.id=n.origin_id
LEFT JOIN origin_type t using(origin_type_id)
LEFT JOIN point p using(point_id)
LEFT JOIN billing.balance b using(customer_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled
AND CURRENT_TIME between p.start_time AND p.end_time
AND NOW() <= b.end_date
AND NOW() >= COALESCE(n.next_dt, '{ZERO_DAY}')
ORDER BY n.next_dt ASC
LIMIT 1
'''

    sql_last_dt = f"SELECT get_last_dt(%s)"

    sql_next = f"INSERT INTO origin_next_pooling (origin_id, next_dt) VALUES (%s, NOW()+INTERVAL '%s SECOND') ON CONFLICT (origin_id) DO UPDATE SET next_dt=NOW()+INTERVAL '%s SECOND'"

    sql_seconds = f'''
SELECT EXTRACT(EPOCH FROM COALESCE(n.next_dt, '{ZERO_DAY}') - NOW())::INT AS seconds_until_next
FROM origin o
LEFT JOIN origin_next_pooling n ON o.id=n.origin_id
LEFT JOIN origin_type t using(origin_type_id)
LEFT JOIN point p using(point_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled
AND CURRENT_TIME between p.start_time AND p.end_time
AND NOW() < COALESCE(n.next_dt, '{ZERO_DAY}')
ORDER BY n.next_dt ASC
LIMIT 1
'''

    sql_status = 'INSERT INTO origin_status (id, success, dt, description) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s) ON CONFLICT (id) DO UPDATE SET success=%s, dt=COALESCE(%s, CURRENT_TIMESTAMP), description=%s'

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

            runner = Runner(60)
            try:
                count, end_time = runner.run(runners[vendor], credentials, origin, id, last_dt, params)
                err = None
            except Exception as error:
                count, end_time, err = 0, None, str(error)
                logging.exception("Error while running job")
            success = bool(end_time != None)

            db.cursor.execute(sql_status, [id, success, end_time, err, success, end_time, err])

            db.cursor.execute(sql_next, [id, poling_period_s, poling_period_s])
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
