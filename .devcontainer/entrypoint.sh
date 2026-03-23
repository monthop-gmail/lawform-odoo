#!/bin/bash
set -e

echo "=== LawForm Odoo Entrypoint ==="

# Wait for PostgreSQL
echo "Waiting for PostgreSQL..."
export PGPASSWORD=odoo
until pg_isready -h db -U odoo -q; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Create database if not exists
DB_EXISTS=$(psql -h db -U odoo -tAc "SELECT 1 FROM pg_database WHERE datname='lawform'" 2>/dev/null || echo "0")
if [ "$DB_EXISTS" != "1" ]; then
    echo "Creating database 'lawform'..."
    createdb -h db -U odoo lawform
    echo "Initializing Odoo with legal_forms module..."
    exec odoo --config=/workspace/.devcontainer/odoo.conf --init=legal_forms
else
    echo "Database 'lawform' exists. Starting Odoo..."
    exec odoo --config=/workspace/.devcontainer/odoo.conf
fi
