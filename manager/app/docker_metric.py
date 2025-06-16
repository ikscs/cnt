#!/usr/local/bin/python
import sys
import docker
import json
from datetime import datetime, timezone

def main(mode, container_name):
    client = docker.from_env()

    result = dict()
    for container in client.containers.list(all=True):
        if container_name != container.name:
            continue
        if mode == 'info':
            state = container.attrs["State"]
            result['status'] = state['Status']
            result['health'] = state.get("Health", {}).get("Status", "no health check")
            start_time = state["StartedAt"].replace('Z', '+00:00')
            started_dt = datetime.fromisoformat(start_time)
            result['uptime'] = str(datetime.now(timezone.utc) - started_dt)
            result['exit_code'] = state.get('ExitCode')
        elif mode == 'stats':
            stats = container.stats(stream=False)
            result['cpu_usage'] = stats["cpu_stats"]["cpu_usage"]["total_usage"]
            result['memory_usage'] = stats["memory_stats"]["usage"]
    return result

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} mode <container_name>')
        exit(1)

    mode = sys.argv[1]
    if mode not in ('info', 'stats'):
        print(f'Usage: {sys.argv[0]} mode <container_name>')
        exit(1)

    result = main(mode, sys.argv[2])
    print(json.dumps(result))

