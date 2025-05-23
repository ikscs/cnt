#!/usr/local/bin/python
import os
import subprocess
import psycopg2

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

def run_shell_script(script_path, *args):
    try:
        result = subprocess.run([script_path, *args], check=True, capture_output=True, text=True)
        print(f'Success: {script_path}')
        print(result.stdout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f'Error: {script_path}')
        print(e.stderr)
        return e.returncode, e.output, e.stderr
    except FileNotFoundError:
        print(f'Error: {script_path}')
        print(f'Not found: {script_path}')
        return -1, None, f'Not found: {script_path}'

if __name__ == "__main__":
    db = DB()
    db.open()

    sql = f'SELECT order_id, cmd, param FROM manager_order WHERE return_code IS NULL ORDER BY ts ASC;'
    db.cursor.execute(sql)

    sql = f'UPDATE manager_order SET return_code=%s, stdout=%s, stderr=%s WHERE order_id=%s;'
    for res in db.cursor.fetchall():
        order_id = res[0]
        cmd = res[1]
        param = res[2]

        if os.path.exists(f'/app/{cmd}'):
            cmd = f'/app/{cmd}'

        if param == None:
            code, output, error = run_shell_script(cmd)
        else:
            params = param.split(' ')
            code, output, error = run_shell_script(cmd, *params)

        db.cursor.execute(sql, (code, output, error, order_id))
        db.conn.commit()

    db.close()
