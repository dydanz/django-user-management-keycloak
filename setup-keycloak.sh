#!/bin/bash

# Script to configure Keycloak automatically
# This should be run after all containers are up and running

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is required but not installed. Please install jq first."
    echo "On macOS: brew install jq"
    echo "On Ubuntu/Debian: apt-get install jq"
    echo "On CentOS/RHEL: yum install jq"
    exit 1
fi

# Environment variables
KEYCLOAK_URL="http://localhost:8080"
KEYCLOAK_ADMIN="admin"
KEYCLOAK_ADMIN_PASSWORD="admin"
REALM_NAME="django-app"
CLIENT_ID="django-client"
CLIENT_SECRET="your-client-secret"
REDIRECT_URI="http://localhost:3000/*"
WEB_ORIGIN="http://localhost:3000"

# Wait for Keycloak to be available
echo "Waiting for Keycloak to be available..."
until curl -s "${KEYCLOAK_URL}/realms/master" > /dev/null 2>&1; do
    echo "Keycloak not available yet, waiting..."
    sleep 5
done
echo "Keycloak is available!"

# Get admin token
echo "Getting admin token..."
ADMIN_TOKEN=$(curl -s -X POST "${KEYCLOAK_URL}/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${KEYCLOAK_ADMIN}" \
    -d "password=${KEYCLOAK_ADMIN_PASSWORD}" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r '.access_token')

if [ -z "$ADMIN_TOKEN" ] || [ "$ADMIN_TOKEN" == "null" ]; then
    echo "Failed to get admin token!"
    exit 1
fi

# Create realm
echo "Creating realm '${REALM_NAME}'..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "realm": "'"${REALM_NAME}"'",
        "enabled": true,
        "displayName": "Django Application"
    }'

# Create client
echo "Creating client '${CLIENT_ID}'..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/clients" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "clientId": "'"${CLIENT_ID}"'",
        "enabled": true,
        "redirectUris": ["'"${REDIRECT_URI}"'"],
        "webOrigins": ["'"${WEB_ORIGIN}"'"],
        "publicClient": false,
        "protocol": "openid-connect",
        "directAccessGrantsEnabled": true,
        "standardFlowEnabled": true,
        "implicitFlowEnabled": false,
        "serviceAccountsEnabled": true,
        "authorizationServicesEnabled": true,
        "secret": "'"${CLIENT_SECRET}"'"
    }'

# Create roles
echo "Creating roles..."
for ROLE in "admin" "user"; do
    curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/roles" \
        -H "Authorization: Bearer ${ADMIN_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "'"${ROLE}"'"
        }'
done

# Create test user (optional)
echo "Creating test user..."
curl -s -X POST "${KEYCLOAK_URL}/admin/realms/${REALM_NAME}/users" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "username": "testuser",
        "enabled": true,
        "emailVerified": true,
        "firstName": "Test",
        "lastName": "User",
        "email": "testuser@example.com",
        "credentials": [
            {
                "type": "password",
                "value": "testuser",
                "temporary": false
            }
        ],
        "requiredActions": []
    }'

echo "Keycloak setup completed successfully!" 