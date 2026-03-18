#!/bin/bash
set -e

echo "=== LawForm Dev Environment Setup (Odoo 19) ==="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
until pg_isready -h db -U odoo -q; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Initialize database if not exists
DB_EXISTS=$(psql -h db -U odoo -tAc "SELECT 1 FROM pg_database WHERE datname='lawform'" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database 'lawform'..."
    createdb -h db -U odoo lawform
    echo "Initializing Odoo with legal_forms module..."
    odoo --config=/workspace/.devcontainer/odoo.conf \
         --init=legal_forms \
         --stop-after-init \
         --no-http
    echo "Database initialized with legal_forms module!"
else
    echo "Database 'lawform' already exists."
    echo "Updating legal_forms module..."
    odoo --config=/workspace/.devcontainer/odoo.conf \
         --update=legal_forms \
         --stop-after-init \
         --no-http
    echo "Module updated!"
fi

echo ""
echo "=== Setup Complete! ==="
echo ""
echo "To start Odoo:"
echo "  odoo --config=/workspace/.devcontainer/odoo.conf"
echo ""
echo "Then open: http://localhost:8069"
echo "  Login: admin / admin"
echo ""
echo "To update module after code changes:"
echo "  odoo --config=/workspace/.devcontainer/odoo.conf -u legal_forms --stop-after-init --no-http"
echo ""
