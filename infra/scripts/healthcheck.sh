#!/bin/bash
# ==============================================================================
# KnowDoc Services Healthcheck Probe
# ==============================================================================
set -e

BACKEND_URL="${BACKEND_URL:-http://localhost:5000/api/v1/health}"
AI_SERVICE_URL="${AI_SERVICE_URL:-http://localhost:8000/internal/v1/health}"
INTERNAL_KEY="${INTERNAL_SERVICE_KEY:-dev-internal-secret-change-in-production}"

echo "Checking Express Backend Health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL" || echo "failed")
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✓ Express Backend is Healthy (HTTP 200)"
else
    echo "✗ Express Backend check failed (Status: $BACKEND_STATUS)"
fi

echo "Checking FastAPI AI Service Health..."
AI_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -H "X-Internal-Service-Key: $INTERNAL_KEY" "$AI_SERVICE_URL" || echo "failed")
if [ "$AI_STATUS" = "200" ]; then
    echo "✓ FastAPI AI Service is Healthy (HTTP 200)"
else
    echo "✗ FastAPI AI Service check failed (Status: $AI_STATUS)"
fi

