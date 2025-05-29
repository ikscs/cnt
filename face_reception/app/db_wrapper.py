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

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    db = DB()
    db.open()
    db.cursor.execute('SELECT VERSION();')
    result = db.cursor.fetchone()
    print(result[0])
    db.close()
