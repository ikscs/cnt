import os
import sys

if __name__ == "__main__":
    SCRIPT = os.path.abspath(sys.argv[1])
    ARGS = [sys.executable, SCRIPT] + sys.argv[2:]

    pid = os.fork()
    if pid > 0:
        # Parent process exits immediately
        sys.exit(0)

    # First child process
    os.setsid()  # Start a new session
    pid = os.fork()
    if pid > 0:
        # First child exits
        sys.exit(0)

    print(ARGS)
    # Second child (daemon)
    with open(os.devnull, 'wb') as devnull:
        os.dup2(devnull.fileno(), sys.stdin.fileno())
        os.dup2(devnull.fileno(), sys.stdout.fileno())
        os.dup2(devnull.fileno(), sys.stderr.fileno())
        os.execvp(ARGS[0], ARGS)
