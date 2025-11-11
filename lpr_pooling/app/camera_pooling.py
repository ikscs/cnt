import logging

from db_wrapper import DB
from sleeper import Sleeper

from pooling_tyto import tyto_runner

ORIGIN_PROTOCOL = 'ISAPI'
ZERO_DAY = '2025-10-29 00:00:00+02'

runners = {'Tyto': tyto_runner}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    logging.info("Start service")
    db = DB()
    sl = Sleeper()

    sql_jobs = f'''
SELECT o.entity_id, o.credentials, o.poling_period_s, t.params, t.vendor
FROM lpr_origin o
LEFT JOIN lpr_origin_next_pooling n using(entity_id)
LEFT JOIN lpr_entity e using(entity_id)
LEFT JOIN lpr_origin_type t USING(origin_type_id)
LEFT JOIN billing.balance b using(customer_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled
-- AND CURRENT_TIME between p.start_time AND p.end_time
AND NOW() <= b.end_date
AND NOW() >= COALESCE(n.next_dt, '{ZERO_DAY}')
ORDER BY n.next_dt ASC
LIMIT 1
'''

    sql_last_dt = f"SELECT get_last_dt(%s)"

    sql_next = f"INSERT INTO lpr_origin_next_pooling (entity_id, next_dt) VALUES (%s, NOW()+INTERVAL '%s SECOND') ON CONFLICT (entity_id) DO UPDATE SET next_dt=NOW()+INTERVAL '%s SECOND'"

    sql_seconds = f'''
SELECT EXTRACT(EPOCH FROM COALESCE(n.next_dt, '{ZERO_DAY}') - NOW())::INT AS seconds_until_next
FROM lpr_origin o
LEFT JOIN lpr_origin_next_pooling n using(entity_id)
LEFT JOIN lpr_origin_type t USING(origin_type_id)
WHERE
t.protocol = '{ORIGIN_PROTOCOL}'
AND o.is_enabled
--AND CURRENT_TIME between p.start_time AND p.end_time
AND NOW() < COALESCE(n.next_dt, '2025-10-29 00:00:00+02')
ORDER BY n.next_dt ASC
LIMIT 1
'''

    sql_status = 'INSERT INTO lpr_entity_status (entity_id, success, dt, description) VALUES (%s, %s, COALESCE(%s, CURRENT_TIMESTAMP), %s) ON CONFLICT (entity_id) DO UPDATE SET success=%s, dt=COALESCE(%s, CURRENT_TIMESTAMP), description=%s'

    sql_write_events = 'INSERT INTO lpr_event (entity_id, uuid, ts_start, ts_end, group_id, registration_number, matched_number) VALUES (_ENTITY_ID_, %s, %s, %s, %s, %s, %s) ON CONFLICT (entity_id, uuid) DO NOTHING'

    while True:
        if sl.have_time():
            db.open()

        while True:
            db.cursor.execute(sql_jobs)
            res = db.cursor.fetchone()
            if not res:
                break

            entity_id, credentials, poling_period_s, params, vendor = res

            db.cursor.execute(sql_last_dt, [entity_id])
            res = db.cursor.fetchone()
            last_dt = res[0]

            try:
                results, end_time = runners[vendor](credentials, entity_id, last_dt, params)
                err = None
            except Exception as error:
                end_time, err = None, str(error)
                logging.exception("Error while running job")
            success = bool(end_time != None)

            if success:
                db.cursor.executemany(sql_write_events.replace('_ENTITY_ID_', f'{entity_id}'), results)

            db.cursor.execute(sql_status, [entity_id, success, end_time, err, success, end_time, err])

            db.cursor.execute(sql_next, [entity_id, poling_period_s, poling_period_s])
            db.conn.commit()

        db.cursor.execute(sql_seconds)

        res = db.cursor.fetchone()
        sl.update(res[0] if res else None)

#        logging.info(f"New time_sleep: {sl.time_sleep}")
        if not sl.have_time():
            continue

        db.close()

        logging.info(f"Sleep {sl.time_sleep}s")
        sl.sleep()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    main()
