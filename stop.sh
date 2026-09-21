#!/bin/bash
# SMM Panel - Stop everything

cd "$(dirname "$0")"

echo "Stopping SMM Panel..."

# Kill ngrok
pkill -f "ngrok http" 2>/dev/null && echo "ngrok stopped" || true

# Stop Docker services
docker-compose down

echo "All services stopped."
