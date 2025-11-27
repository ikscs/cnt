#!/bin/bash
set -e

# Default API list from env
IFS=',' read -ra INSTANCES <<< "${APIS:-api1,api2}"

# Check each instance port
for api in "${INSTANCES[@]}"; do
  var_port=$(echo "${api}_PORT" | tr '[:lower:]' '[:upper:]')
  port="${!var_port}"

  status=$(curl -o /dev/null -s -w "%{http_code}" "http://localhost:${port}/")
  if [ "$status" -eq 000 ]; then
    echo "❌ $api on port $port unreachable"
    exit 1
  fi

  if [ "$status" -ge 500 ]; then
    echo "❌ $api on port $port server error: $status"
    exit 1
  fi

done

echo "✅ All PostgREST instances are healthy"
