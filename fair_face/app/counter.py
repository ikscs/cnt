from datetime import datetime
import time

class AutoDict(dict):
    def __missing__(self, k):
        self[k] = AutoDict()
        return self[k]

class Counter():
    def __init__(self, name):
        self.name = name
        self.count = AutoDict()
        self.start_time = AutoDict()
        self.timer = AutoDict()
        self.min = AutoDict()
        self.max = AutoDict()
        self.total = AutoDict()
        self.from_time = AutoDict()

        self.entry_set = set()
        self.entry_list = []


    def get_idx(self, path, params):
        entry = str((path, params))
        try:
            entry_idx = self.entry_list.index(entry)
        except Exception as err:
            entry_idx = len(self.entry_list)
            self.entry_set.add(entry)
            self.entry_list.append(entry)
            self.min[entry_idx] = float('inf')
            self.max[entry_idx] = 0
            self.total[entry_idx] = 0
            self.from_time[entry_idx] = datetime.now()

        return entry_idx

    def start(self, path, params):
        entry_idx = self.get_idx(path, params)

        self.start_time[entry_idx] = time.time()
        count = self.count[entry_idx]
        if not count:
            count = 0
        self.count[entry_idx] = count + 1

    def stop(self, path, params):
        entry_idx = self.get_idx(path, params)
        t = round((time.time() - self.start_time[entry_idx]) * 1000)
        self.timer[entry_idx] = t

        if t < self.min[entry_idx]:
            self.min[entry_idx] = t
        if t > self.max[entry_idx]:
            self.max[entry_idx] = t
        self.total[entry_idx] += t

    def info(self):
        data = []
        for n, k in enumerate(self.entry_list):
            data.append({'name': self.name, 'entry': k, 'from_ts': self.from_time[n], 'cnt': self.count[n], 'total_ms': self.total[n], 'min_ms': self.min[n], 'max_ms': self.max[n]})
        return data

if __name__ == '__main__':
    from random import randint
    counter = Counter('fair_face')

    for _ in range(7):
        counter.start('/represent.json', ('img', 0.8, 40))
        time.sleep(randint(10, 1500)/1000)
        counter.stop('/represent.json', ('img', 0.8, 40))

    print(counter.info())
