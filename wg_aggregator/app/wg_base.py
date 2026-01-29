#!/usr/bin/env python3
import os
from datetime import datetime
import subprocess

from db_wrapper import DB

class WG():
    conf_folder = '/config/wg_confs'
    data = dict()

    def exec_cmd(self, cmd):
        cmd = cmd.split()
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            txt = result.stdout
        except Exception as err:
            txt = f'exception: {err}'
        return txt

    def __init__(self, cursor):
        sql = 'SELECT id, conf FROM public.wireguard_conf WHERE enabled;'
        cursor.execute(sql)
        for id, conf in cursor.fetchall():
            self.data[id] = {'conf': conf, 'route': []}

        sql = 'SELECT conf_id, listen_port, host, port FROM public.wireguard_port p JOIN public.wireguard_conf c ON p.conf_id=c.id WHERE c.enabled AND p.enabled;'
        cursor.execute(sql)
        for conf_id, listen_port, host, port in cursor.fetchall():
            self.data[conf_id]['route'].append({'listen_port': listen_port, 'host': host, 'port': port})

#        print(self.data)

    def load_ifaces(self):
        for root, dirs, files in os.walk(self.conf_folder):
            break

        for file in files:
            if not file.endswith('.conf'):
                #ignore not conf
                continue
            id = file.split('.conf', 1)[0]
            if not id.isnumeric():
                #ignore not numeric ids
                continue

            #Down running ifaces
            self.exec_cmd(f'wg-quick down {id}')

            if int(id) not in self.data.keys():
                #Delete unnessesary ifaces
                os.unlink(f'{self.conf_folder}/{file}')

        result_show = self.exec_cmd('wg show')
#        print(result_show)

        for k, v in self.data.items():
            with open(f'{self.conf_folder}/{k}.conf', 'wt') as f:
                f.write(v['conf'])

            if f'interface: {k}' not in result_show:
                result = self.exec_cmd(f'wg-quick up {k}')
                print(result)

    def sync_routing(self, key=None):
        keys = [key] if key else self.data.keys()
        for k in keys:
            id = f'{k}'

            cmd1 = f'ip rule del fwmark {id} table {id}'
            result1 = self.exec_cmd(cmd1)

            cmd2 = f'ip rule add fwmark {id} table {id}'
            result2 = self.exec_cmd(cmd2)

            cmd3 = f'ip route replace default dev {id} table {id}'
            result3 = self.exec_cmd(cmd3)

    def sync_table(self, key=None):
        items = (key, self.data[key]) if key else self.data.items()
        for k, v in items:
            id = f'{k}'
            for route in v['route']:
                lport = str(route['listen_port'])
                dport = str(route['port'])
                dip = str(route['host'])

                cmd = f'iptables -t nat -A PREROUTING -p tcp --dport {lport} -j DNAT --to-destination {dip}:{dport}'
                result = self.exec_cmd(cmd)

                cmd = f'iptables -t nat -A OUTPUT -p tcp --dport {lport} -j DNAT --to-destination {dip}:{dport}'
                result = self.exec_cmd(cmd)

                cmd = f'iptables -t nat -A POSTROUTING -d {dip} -p tcp --dport {dport} -j MASQUERADE'
                result = self.exec_cmd(cmd)

                cmd = f'iptables -A FORWARD -p tcp -d {dip} --dport {dport} -j ACCEPT'
                result = self.exec_cmd(cmd)

                cmd = f'iptables -t mangle -A PREROUTING -p tcp --dport {lport} -j MARK --set-mark {id}'
                result = self.exec_cmd(cmd)

    def sync_tables(self):
        cleanup_list = [
'iptables -t nat -F PREROUTING',
'iptables -t nat -F POSTROUTING',
'iptables -t mangle -F PREROUTING',
'iptables -F FORWARD',
]
        for cmd in cleanup_list:
            result = self.exec_cmd(cmd)

        cmd = 'iptables -P FORWARD ACCEPT'
        result = self.exec_cmd(cmd)

        forward_list = [
'iptables -A FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT',
'iptables -A FORWARD -j ACCEPT',
]
        for cmd in forward_list:
            result = self.exec_cmd(cmd)

        self.sync_table()

def main(cursor):
    wg = WG(cursor)
    wg.load_ifaces()
    wg.sync_routing()
    wg.sync_tables()
    result_show = wg.exec_cmd('wg show')
    print(result_show)

if __name__ == "__main__":
    from dotenv import load_dotenv, dotenv_values
    load_dotenv()

    db = DB()
    db.open()

    main(db.cursor)

    db.close()
