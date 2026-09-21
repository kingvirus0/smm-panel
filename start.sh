#!/bin/bash
# SMM Panel - Start everything
# Usage: ./start.sh

set -e

cd "$(dirname "$0")"

echo "Starting SMM Panel..."

# Start Docker services (PostgreSQL, Redis, Backend, Celery, Bot, Frontend)
echo "[1/3] Starting Docker services..."
docker-compose up -d postgres redis

echo "Waiting for database..."
sleep 5

docker-compose up -d backend celery-worker celery-beat bot

echo "[2/3] Starting ngrok tunnel..."
ngrok http 8000 --log=stdout > /tmp/ngrok.log &
NGROK_PID=$!
sleep 3

# Get ngrok URL
NGROK_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "")

if [ -n "$NGROK_URL" ]; then
    echo ""
    echo "============================================"
    echo "  ngrok tunnel active: $NGROK_URL"
    echo "============================================"
    echo ""
    echo "Set these webhook URLs in your dashboards:"
    echo "  Paystack:     $NGROK_URL/api/webhooks/paystack"
    echo "  Flutterwave:  $NGROK_URL/api/webhooks/flutterwave"
    echo ""
    echo "Backend API:   $NGROK_URL"
    echo "ngrok panel:   http://127.0.0.1:4040"
    echo ""
else
    echo "ngrok failed to start. Check /tmp/ngrok.log"
fi

echo "[3/3] All services running!"
echo ""
echo "Services:"
echo "  Backend API:  http://localhost:8000"
echo "  Frontend:     http://localhost:5173"
echo "  Bot:          @justgrowmeBot"
echo ""
echo "To stop: ./stop.sh"
