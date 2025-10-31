#!/bin/bash
set -e

# Default API list from env
IFS=',' read -ra INSTANCES <<< "${APIS:-api1,api2}"

# Check each instance port
for api in "${INSTANCES[@]}"; do
  var_port=$(echo "${api}_PORT" | tr '[:lower:]' '[:upper:]')
  port="${!var_port}"

  if ! curl -fs "http://localhost:${port}/" > /dev/null; then
    echo "❌ $api on port $port is unhealthy"
    exit 1
  fi
done

echo "✅ All PostgREST instances are healthy"
