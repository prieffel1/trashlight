#!/bin/bash
# --------------------------------------------
# Automatisches Deployment für Trashlight-Stack
# Läuft auf Raspberry Pi
# --------------------------------------------

# Konfiguration
LOCAL_DIR="/home/phri4docker/trashlight"
REPO_URL="https://github.com/prieffel1/trashlight.git"
COMPOSE_FILE="docker-compose.yml"
STACK_NAME="trashlight"
SERVICE_NAME="${STACK_NAME}_trashlight"

# Prüfen ob GHCR_PAT gesetzt ist
if [ -z "$GHCR_PAT" ]; then
  echo "ERROR: GHCR_PAT Environment Variable ist nicht gesetzt!"
  exit 1
fi

# Verzeichnis erstellen
mkdir -p "$LOCAL_DIR"

# Alte Compose-Datei sichern
if [ -f "$LOCAL_DIR/$COMPOSE_FILE" ]; then
  cp "$LOCAL_DIR/$COMPOSE_FILE" "$LOCAL_DIR/${COMPOSE_FILE}.bak"
fi

# Neue Compose-Datei aus GitHub laden
curl -L "$REPO_URL/raw/main/$COMPOSE_FILE" -o "$LOCAL_DIR/$COMPOSE_FILE"
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to download docker-compose.yml"
  exit 1
fi

# Prüfen, ob Compose-Datei geändert wurde
if [ -f "$LOCAL_DIR/${COMPOSE_FILE}.bak" ]; then
  if cmp -s "$LOCAL_DIR/$COMPOSE_FILE" "$LOCAL_DIR/${COMPOSE_FILE}.bak"; then
    COMPOSE_CHANGED=false
    echo "No changes in docker-compose.yml detected."
  else
    COMPOSE_CHANGED=true
    echo "docker-compose.yml changed!"
  fi
else
  COMPOSE_CHANGED=true
fi

# Docker Login
echo "$GHCR_PAT" | docker login ghcr.io -u prieffel1 --password-stdin

# Pull latest Image
docker pull ghcr.io/prieffel1/trashlight:latest

# Deployment-Entscheidung
if [ "$COMPOSE_CHANGED" = true ]; then
  echo "Performing full stack deploy..."
  docker stack deploy -c "$LOCAL_DIR/$COMPOSE_FILE" "$STACK_NAME"
else
  echo "Only updating service image..."
  docker service update --image ghcr.io/prieffel1/trashlight:latest "$SERVICE_NAME"
fi

echo "Deployment finished!"
