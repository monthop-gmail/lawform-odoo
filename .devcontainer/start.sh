#!/bin/bash
# === Every start (postStartCommand) ===
echo "=== LawForm - Starting services... ==="

# Wait for Docker daemon
for i in $(seq 1 30); do
    if docker info &>/dev/null; then
        break
    fi
    echo "  waiting for Docker... ($i/30)"
    sleep 2
done

# Start all services
echo "Starting Docker Compose..."
docker compose up -d --build 2>&1 | tail -20

# Wait for Odoo to be ready
echo "Waiting for Odoo..."
for i in $(seq 1 60); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login 2>/dev/null | grep -q "200"; then
        echo "Odoo ready!"
        break
    fi
    if [ "$i" -eq 60 ]; then
        echo "Odoo not ready yet. Check: docker compose logs odoo"
    fi
    sleep 5
done

# Set ports public in Codespace
if [ -n "$CODESPACE_NAME" ]; then
    echo "Setting ports public..."
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
echo ""
echo "  Login: admin / admin"
echo ""
echo "  Update module:"
echo "    docker compose exec odoo odoo --config=/workspace/.devcontainer/odoo.conf -u legal_forms --stop-after-init --no-http"
echo "========================================"
