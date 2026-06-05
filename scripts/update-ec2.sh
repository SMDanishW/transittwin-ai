#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

echo "=== TransitTwin AI — EC2 update ==="

if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found. Run deploy-ec2.sh first."
    exit 1
fi

echo "Pulling latest changes..."
git pull

echo "Rebuilding and restarting containers..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo "Removing dangling images..."
docker image prune -f

echo ""
echo "Update complete. Service status:"
docker compose -f "$COMPOSE_FILE" ps
