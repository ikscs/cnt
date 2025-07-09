#!/usr/local/bin/python
import sys
import docker
import signal

def main(container_name):
    client = docker.from_env()

    container = client.containers.get(container_name)

    # Send SIGCHLD to PID 1 inside the container
    exit_code, output = container.exec_run("kill -CHLD 1")

    if exit_code == 0:
        result = "SIGCHLD sent to PID 1 successfully."
    else:
        result = "Failed to send SIGCHLD: {output.decode()}"

    return result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <container_name>')
        exit(1)

    result = main(sys.argv[1])
    print(result)
