#!/bin/bash
# --------------------------------------------
# Deployment Script für Portainer Stack "trashlight"
# Läuft auf Raspberry Pi, zieht das aktuelle GHCR-Image
# Holt automatisch die docker-compose.yml aus GitHub
# --------------------------------------------

# Config
LOCAL_DIR="/home/phri4docker/trashlight"   # Verzeichnis auf dem Pi
REPO_URL="https://github.com/prieffel1/trashlight.git"
COMPOSE_FILE="docker-compose.yml"

# Prüfen ob GHCR_PAT gesetzt ist
if [ -z "$GHCR_PAT" ]; then
  echo "ERROR: GHCR_PAT Environment Variable ist nicht gesetzt!"
  exit 1
fi

# Verzeichnis erstellen, falls nicht existiert
mkdir -p "$LOCAL_DIR"

# docker-compose.yml aus GitHub holen
echo "Fetching latest docker-compose.yml from GitHub..."
curl -L "$REPO_URL/raw/main/$COMPOSE_FILE" -o "$LOCAL_DIR/$COMPOSE_FILE"

if [ $? -ne 0 ]; then
  echo "ERROR: Failed to download docker-compose.yml"
  exit 1
fi

# Docker Login bei GHCR
echo "Logging in to GHCR..."
echo "$GHCR_PAT" | docker login ghcr.io -u prieffel1 --password-stdin

# Pull latest Docker Image
echo "Pulling latest image..."
docker pull ghcr.io/prieffel1/trashlight:latest

# Deploy Stack
echo "Updating stack..."
docker stack deploy -c "$LOCAL_DIR/$COMPOSE_FILE" trashlight

echo "Deployment finished!"
