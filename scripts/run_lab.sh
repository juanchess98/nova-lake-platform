#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="infra/docker-compose.yml"
ENV_FILE=".env"

usage() {
  echo "Usage: ./scripts/run_lab.sh {up|down|logs}"
}

run_compose() {
  MSYS_NO_PATHCONV=1 docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile lab "$@"
}

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing .env file at project root. Create it from .env.example first."
  echo "Example: cp .env.example .env"
  exit 1
fi

case "$1" in
  up)
    run_compose up -d --build
    echo "Notebook Lab available at: http://localhost:8888"
    ;;
  down)
    run_compose down
    ;;
  logs)
    run_compose logs -f notebook-lab
    ;;
  *)
    usage
    exit 1
    ;;
esac
