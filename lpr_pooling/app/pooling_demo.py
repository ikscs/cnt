import uuid
import random
from datetime import datetime, timedelta, timezone

class Demo_runner:
    def __init__(self, db):
        self.db = db

    def run(self, credentials, origin_id, last_dt, params):

        self.origin_id = origin_id

        delta_t = int((datetime.now().astimezone(timezone.utc) - last_dt.astimezone(timezone.utc)).total_seconds())

        cnt = delta_t*params['daily_count']/(24*60*60)

        results = []
        end_time = None
        if cnt > random.random():
            start_time = last_dt + timedelta(seconds=random.randint(1, delta_t-10))
            end_time = start_time + timedelta(seconds=random.randint(0, 10))
            if random.random() > params['chance_match']:
                group = 1
                number = self.get_number_from_base()
                match_number = number
            else:
                group = 3
                number = self.get_number_random()
                match_number = None

            results.append([uuid.uuid4().hex, start_time, end_time, group, number, match_number])

        return results, end_time

    def get_number_from_base(self):
        sql = "SELECT registration_number FROM lpr_demo_camera WHERE origin_id=%s AND registration_number IS NOT NULL AND registration_number NOT IN ('snapshot', 'plate') ORDER BY RANDOM() LIMIT 1;"
        self.db.cursor.execute(sql, [self.origin_id])
        result = self.db.cursor.fetchone()
        if not result:
            return self.get_number_random()

        return result[0]

    def get_number_random(self):
        allow_chars = 'ABEIKMHOPCTX'
        number1 = random.choice(allow_chars) + random.choice(allow_chars)
        number2 = f'{random.randint(0, 9999):04}'
        number3 = random.choice(allow_chars) + random.choice(allow_chars)
        return f'{number1}{number2}{number3}'

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    from db_wrapper import DB

    credentials = {}

    db = DB()

    demo = Demo_runner(db)

    db.open()

    origin_id = 14
    last_dt = datetime.now() + timedelta(seconds=-3600)
    params = {"daily_count": 300, "chance_match": 0.5}

    results, end_time = demo.run(credentials, origin_id, last_dt, params)

    if results:
        for result in results:
            print(result)

    print(end_time)

    db.close()
