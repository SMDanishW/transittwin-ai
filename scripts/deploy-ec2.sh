#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.production"

echo "=== TransitTwin AI — EC2 deploy ==="

# Check Docker
if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed. Install it with:"
    echo "  curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# Check Docker Compose (plugin form)
if ! docker compose version &>/dev/null; then
    echo "ERROR: Docker Compose plugin not found. Install it with:"
    echo "  sudo apt-get install -y docker-compose-plugin"
    exit 1
fi

# Validate env file
if [[ ! -f "$ENV_FILE" ]]; then
    echo "ERROR: $ENV_FILE not found."
    echo "  cp .env.production.example .env.production"
    echo "  Then fill in GROQ_API_KEY, POSTGRES_PASSWORD, NEXT_PUBLIC_API_URL, etc."
    exit 1
fi

# Warn if placeholder values remain
if grep -q "change_me" "$ENV_FILE"; then
    echo "WARNING: $ENV_FILE still contains placeholder values (change_me)."
    echo "  Update all required fields before deploying to production."
fi

echo "Building and starting containers..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo ""
echo "Done. Check status with:"
echo "  docker compose -f $COMPOSE_FILE ps"
echo "  docker compose -f $COMPOSE_FILE logs -f backend"
