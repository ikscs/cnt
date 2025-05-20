import os
import sys
import psutil

def run_once_pid(pid, func, *args, **kwargs):
    fparts = os.path.basename(sys.modules['__main__'].__file__).split('.')
    if len(fparts)>1:
        PID_FILE = '.'.join(fparts[:-1])
    else:
        PID_FILE = '.'.join(fparts)
    PID_FILE = f'{PID_FILE}{pid}.pid'

    if check_pid_file(PID_FILE):
        return

    create_pid_file(PID_FILE)
    func(*args, **kwargs)
    remove_pid_file(PID_FILE)

def run_once(func, *args, **kwargs):
    run_once_pid('', func, *args, **kwargs)

def check_pid_file(PID_FILE):
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
            return is_running(pid)
    return False

def is_running(pid):
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False

def create_pid_file(PID_FILE):
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def remove_pid_file(PID_FILE):
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def main():
    import time
    print("Hello")
    time.sleep(1)

if __name__ == "__main__":
    run_once_pid(1, main)
