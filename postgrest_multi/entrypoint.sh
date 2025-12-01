#!/bin/bash
set -e

IFS=',' read -ra INSTANCES <<< "$APIS"

for api in "${INSTANCES[@]}"; do
  # Uppercase variable names for Bash substitution
  var_uri=$(echo "${api}_DB_URI" | tr '[:lower:]' '[:upper:]')
  var_port=$(echo "${api}_PORT" | tr '[:lower:]' '[:upper:]')
  var_schemas=$(echo "${api}_DB_SCHEMAS" | tr '[:lower:]' '[:upper:]')
  var_anon_role=$(echo "${api}_DB_ANON_ROLE" | tr '[:lower:]' '[:upper:]')
  var_jwt_secret=$(echo "${api}_JWT_secret" | tr '[:lower:]' '[:upper:]')
  var_jwt_role_claim_key=$(echo "${api}_JWT_ROLE_CLAIM_KEY" | tr '[:lower:]' '[:upper:]')
  var_db_pre_config=$(echo "${api}_DB_PRE_CONFIG" | tr '[:lower:]' '[:upper:]')
  var_db_pre_request=$(echo "${api}_DB_PRE_REQUEST" | tr '[:lower:]' '[:upper:]')

  # Expand environment variables
  db_uri="${!var_uri}"
  port="${!var_port}"
  schemas="${!var_schemas}"
  anon_role="${!var_anon_role}"
  jwt_secret="${!var_jwt_secret}"
  jwt_role_claim_key="${!var_jwt_role_claim_key}"
  db_pre_config="${!var_db_pre_config}"
  db_pre_request="${!var_db_pre_request}"

  # Generate config
  conf_file="/etc/postgrest/${api}.conf"
  echo "Generating config for $api (port $port) (schemas $schemas)"
  DB_URI="$db_uri" DB_SCHEMAS="$schemas" DB_ANON_ROLE="$anon_role" JWT_ROLE_CLAIM_KEY="$jwt_role_claim_key" JWT_SECRET="$jwt_secret" DB_PRE_CONFIG="$db_pre_config" DB_PRE_REQUEST="$db_pre_request" SERVER_PORT="$port" envsubst < /etc/postgrest/api.template.conf > "$conf_file"

  # Start PostgREST instance
  postgrest "$conf_file" &
done

wait
