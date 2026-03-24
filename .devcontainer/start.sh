#!/bin/bash
# === Every start (postStartCommand) ===
# Runs each time Codespace opens — should be FAST
echo "=== LawForm - Starting services... ==="

# Wait for Docker daemon
for i in $(seq 1 15); do
    if docker info &>/dev/null; then
        break
    fi
    echo "  waiting for Docker... ($i/15)"
    sleep 1
done

# Start containers (no --build, images already cached from setup.sh)
docker compose up -d 2>&1 | tail -5

# Wait for Odoo (DB + modules already cached — just loading)
echo "Waiting for Odoo..."
for i in $(seq 1 90); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login 2>/dev/null | grep -q "200"; then
        echo "Odoo ready! (${i}s)"
        break
    fi
    sleep 1
done

# Set ports public in Codespace
if [ -n "$CODESPACE_NAME" ]; then
    gh codespace ports visibility 8069:public -c "$CODESPACE_NAME" 2>/dev/null || true
fi

echo ""
echo "========================================"
echo "  LawForm - Odoo 19 Dev"
echo "========================================"
if [ -n "$CODESPACE_NAME" ]; then
echo "  Odoo:  https://${CODESPACE_NAME}-8069.app.github.dev"
else
echo "  Odoo:  http://localhost:8069"
fi
echo "  Login: admin / admin"
echo "========================================"
