#!/bin/bash
set -e

# Function to create keycloak database if it doesn't exist
# This runs inside the postgres container as the postgres user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE keycloak;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO postgres;
EOSQL

echo "Keycloak database created." 