#!/bin/sh

INTERVAL=300

echo "Starting Docker health monitor (interval: $INTERVAL sec)"

while true; do
    for cid in $(docker ps --format '{{.ID}}'); do

        health=$(docker inspect --format '{{json .State.Health}}' $cid 2>/dev/null)

        # Skip containers without a healthcheck
        if [ "$health" = "null" ] || [ -z "$health" ]; then
            continue
        fi

        status=$(docker inspect --format '{{.State.Health.Status}}' $cid 2>/dev/null)

        if [ "$status" = "unhealthy" ]; then
            name=$(docker inspect --format '{{.Name}}' $cid | sed 's#/##')
            echo "$(date) - Restarting unhealthy container: $name ($cid)"
            docker restart "$cid" >/dev/null 2>&1
        fi
    done

    sleep "$INTERVAL"
done
