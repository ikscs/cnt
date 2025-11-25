#!/usr/local/bin/python
import signal

class TimeoutError(Exception):
    pass

# Example usage
def long_function(a, b, c):
    print(a, b, c)
    while True:
        pass
    return 9, 12

class Runner():
    def __init__(self, timeout=30):
        signal.signal(signal.SIGALRM, self.handler)
        self.timeout = timeout

    def handler(self, signum, frame):
        raise TimeoutError("Function timed out")

    def run(self, func, *args, **kwargs):
        signal.alarm(self.timeout)
        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)

if __name__ == '__main__':
    r = Runner(3)
    try:
        x, y = r.run(long_function, 33, 22, 1)
        print(x, y)
    except Exception as err:
        print("Error:", err)
