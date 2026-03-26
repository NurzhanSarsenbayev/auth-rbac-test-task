#!/usr/bin/env bash

set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "==> Demo started"
echo "BASE_URL=${BASE_URL}"
echo

echo "==> 1. Login as regular user"
USER_LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}')

USER_TOKEN=$(echo "${USER_LOGIN_RESPONSE}" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "User token acquired"
echo

echo "==> 2. Regular user can access /mock/projects"
USER_PROJECTS_STATUS=$(curl -s -o /tmp/user_projects.json -w "%{http_code}" \
  -X GET "${BASE_URL}/mock/projects" \
  -H "Authorization: Bearer ${USER_TOKEN}")

echo "Status: ${USER_PROJECTS_STATUS}"
cat /tmp/user_projects.json
echo
echo

echo "==> 3. Regular user cannot access /mock/reports by default"
USER_REPORTS_STATUS_BEFORE=$(curl -s -o /tmp/user_reports_before.json -w "%{http_code}" \
  -X GET "${BASE_URL}/mock/reports" \
  -H "Authorization: Bearer ${USER_TOKEN}")

echo "Status: ${USER_REPORTS_STATUS_BEFORE}"
cat /tmp/user_reports_before.json
echo
echo

echo "==> 4. Login as admin"
ADMIN_LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}')

ADMIN_TOKEN=$(echo "${ADMIN_LOGIN_RESPONSE}" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "Admin token acquired"
echo

echo "==> 5. Admin grants reports read access to regular user"
PATCH_STATUS=$(curl -s -o /tmp/patch_permission.json -w "%{http_code}" \
  -X PATCH "${BASE_URL}/admin/permissions/6" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -d '{"can_read": true, "scope": "all"}')

echo "Status: ${PATCH_STATUS}"
cat /tmp/patch_permission.json
echo
echo

echo "==> 6. Login as regular user again"
USER_LOGIN_RESPONSE_2=$(curl -s -X POST "${BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"user123"}')

USER_TOKEN_2=$(echo "${USER_LOGIN_RESPONSE_2}" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "New user token acquired"
echo

echo "==> 7. Regular user can now access /mock/reports"
USER_REPORTS_STATUS_AFTER=$(curl -s -o /tmp/user_reports_after.json -w "%{http_code}" \
  -X GET "${BASE_URL}/mock/reports" \
  -H "Authorization: Bearer ${USER_TOKEN_2}")

echo "Status: ${USER_REPORTS_STATUS_AFTER}"
cat /tmp/user_reports_after.json
echo
echo

echo "==> 8. Logout regular user"
LOGOUT_STATUS=$(curl -s -o /tmp/logout.json -w "%{http_code}" \
  -X POST "${BASE_URL}/auth/logout" \
  -H "Authorization: Bearer ${USER_TOKEN_2}")

echo "Status: ${LOGOUT_STATUS}"
cat /tmp/logout.json
echo
echo

echo "==> 9. Reuse revoked token"
REVOKED_TOKEN_STATUS=$(curl -s -o /tmp/revoked_me.json -w "%{http_code}" \
  -X GET "${BASE_URL}/users/me" \
  -H "Authorization: Bearer ${USER_TOKEN_2}")

echo "Status: ${REVOKED_TOKEN_STATUS}"
cat /tmp/revoked_me.json
echo
echo

echo "==> Demo finished"