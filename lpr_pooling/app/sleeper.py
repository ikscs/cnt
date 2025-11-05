from time import sleep
import os

class Sleeper:
    time_sleep = 10
    time_sleep_min = 10
    time_sleep_max = 10*60

    def update(self, new_val):
        if new_val == None:
            new_val = self.time_sleep_max

#        elif new_val == 0:
#            new_val = 0

        elif new_val < self.time_sleep_min:
            new_val = self.time_sleep_min

        elif new_val > self.time_sleep_max:
            new_val = self.time_sleep_max

        self.time_sleep = new_val

    def sleep(self):
        sleep(self.time_sleep)

    def have_time(self):
        return bool(self.time_sleep > 0)


if __name__ == "__main__":
    sl = Sleeper()

    print('Start')

    sl.sleep()
    print('Stop')

    for t in (0, None, 999, 5, 15):
        sl.update(t)
        print(f'{t} -> {sl.time_sleep} -> {sl.have_time()}')

    sl.sleep()
    print('End')
