import os
import sys
import signal
import subprocess

if __name__ == "__main__":
    DIR_PATH = os.path.dirname(os.path.realpath(__file__))

    SCRIPT = os.path.join(DIR_PATH, sys.argv[1])

    rocket = [sys.executable, SCRIPT]
    rocket.extend(sys.argv[2:])

    if os.name != 'nt':
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    try:
        process = subprocess.Popen(rocket, start_new_session=True)
    except Exception as e:
        print(str(e))
