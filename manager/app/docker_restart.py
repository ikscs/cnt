#!/usr/local/bin/python
import sys
import docker

def main(container_name):
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        container.restart()
        result = f"Container '{container.name}' restarted successfully."

    except docker.errors.NotFound:
        result = f"Container '{container_name}' not found."
    except docker.errors.APIError as e:
        result = f"Docker API error: {e.explanation}"

    return result

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <container_name>')
        exit(1)

    result = main(sys.argv[1])
    print(result)
