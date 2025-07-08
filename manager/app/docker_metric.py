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

            result['cpu_percentage'] = calculate_cpu_percentage(stats)
            try:
                result['memory_percentage'] = round(100*stats["memory_stats"]["usage"] / stats["memory_stats"]["limit"], 1)
            except Exception as e:
                result['memory_percentage'] = -1
    return result

def calculate_cpu_percentage(stats):
    try:
        # Extract required fields
        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                    stats['precpu_stats']['cpu_usage']['total_usage']

        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                       stats['precpu_stats']['system_cpu_usage']

        num_cpus = stats['cpu_stats'].get('online_cpus', 1)  # fallback to 1 to avoid division by 0

        # Avoid division by zero
        if system_delta > 0 and cpu_delta > 0:
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
        else:
            cpu_percent = -1

        return round(cpu_percent, 1)

    except (KeyError, ZeroDivisionError, TypeError) as e:
        return -1

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

