#!/bin/bash
# === First-time setup (postCreateCommand) ===
# Runs ONCE when Codespace is created (or prebuild) — cached for subsequent starts
echo "=== LawForm - Building Odoo environment... ==="

# Wait for Docker daemon
for i in $(seq 1 30); do
    if docker info &>/dev/null; then
        break
    fi
    echo "  waiting for Docker... ($i/30)"
    sleep 2
done

# Build and start (first time — includes image build + module install)
echo "Building Docker images (one-time, will be cached)..."
docker compose build 2>&1 | tail -10

echo "Starting services for initial setup..."
docker compose up -d 2>&1 | tail -10

# Wait for Odoo to finish init (first boot installs legal_forms)
echo "Waiting for Odoo first-time init (installing legal_forms)..."
for i in $(seq 1 120); do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login 2>/dev/null | grep -q "200"; then
        echo "Odoo ready! (took ~$((i*2))s)"
        break
    fi
    if [ "$i" -eq 120 ]; then
        echo "Odoo not ready yet. Check: docker compose logs odoo"
    fi
    sleep 2
done

# Stop containers cleanly — so they restart fast from prebuild cache
echo "Stopping containers (clean state for fast restart)..."
docker compose stop 2>&1 | tail -5

echo ""
echo "=== First-time setup complete! ==="
echo "    Prebuild cached. Next start will be fast (~30-60s)."
