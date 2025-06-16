#!/usr/local/bin/python
import sys
import json

FOLDER = '/mnt/proc'

processes = {
'meminfo': {'rows': [0, 1, 2], 'cols': [1], 'type': 'int', 'names': {(0,1): 'MemTotal', (1,1): 'MemFree', (2,1): 'MemAvailable'}},
'loadavg': {'rows': [0], 'cols': [0, 1, 2], 'type': 'float', 'names': {(0,0): 'load_avg1', (0,1): 'load_avg5', (0,2): 'load_avg15'}},
}

def get_val(val, val_type):
    try:
        if val_type == 'int':
            res = int(val)
        elif val_type == 'float':
            res = float(val)
        else:
            res = val
    except Exception as err:
        res = val
    return res

def main(proc):
    if proc not in processes:
        return dict()

    with open(f'{FOLDER}/{proc}', 'rt') as f:
        res = f.read().strip().split('\n')

    result = dict()
    for n, row in enumerate(res):
        if n not in processes[proc]['rows']:
            continue

        values = [e.strip() for e in row.split()]
        for c, val in enumerate(values):
            if c not in processes[proc]['cols']:
                continue
            if (n, c) not in processes[proc]['names']:
                continue
            name = processes[proc]['names'][(n, c)]
            result[name] = get_val(val, processes[proc]['type'])

    return result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <proc>')
        exit(1)

    result = main(sys.argv[1])
    print(json.dumps(result))
