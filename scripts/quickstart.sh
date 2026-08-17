#!/bin/sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example. Add ZEP_API_KEY, then rerun this script."
  exit 1
fi

docker compose build
docker compose up -d redis qdrant
docker compose run --rm app python -m src.smoke
docker compose run --rm app python -m src.seed

echo "Ready. After editing src/memory_student.py, rebuild first:"
echo "  docker compose build app"
echo "  docker compose run --rm app python -m src.evaluate --impl student --reuse-seeded"
