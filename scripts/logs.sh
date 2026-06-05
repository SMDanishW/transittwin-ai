#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="docker-compose.prod.yml"

# Accept an optional service name argument; default to all four main services
SERVICE="${1:-}"

if [[ -n "$SERVICE" ]]; then
    docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE"
else
    docker compose -f "$COMPOSE_FILE" logs -f backend worker frontend nginx
fi
