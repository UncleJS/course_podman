#!/usr/bin/env bash
set -euo pipefail

NET=stacknet
VOL=dbdata
SECRET_NAME=stack_mariadb_root_password

DB_NAME=stack-db
WEB_NAME=stack-web

cmd=${1:-}

ensure_net() {
  if ! podman network exists "$NET"; then
    podman network create "$NET" >/dev/null
  fi
}

ensure_vol() {
  if ! podman volume exists "$VOL"; then
    podman volume create "$VOL" >/dev/null
  fi
}

ensure_secret() {
  if podman secret exists "$SECRET_NAME"; then
    return 0
  fi

  if [[ -t 0 ]]; then
    local p
    read -r -s -p 'MariaDB root password (for lab stack): ' p
    printf '\n'
    printf '%s' "$p" | podman secret create "$SECRET_NAME" - >/dev/null
    unset p
    return 0
  fi

  echo "secret '$SECRET_NAME' does not exist; create it first" >&2
  echo "example:" >&2
  echo "  printf '%s' 'choose-a-password' | podman secret create $SECRET_NAME -" >&2
  exit 1
}

up() {
  ensure_net
  ensure_vol
  ensure_secret

  if ! podman container exists "$DB_NAME"; then
    podman run -d \
      --name "$DB_NAME" \
      --network "$NET" \
      -v "$VOL":/var/lib/mysql \
      --secret "$SECRET_NAME" \
      -e MARIADB_ROOT_PASSWORD_FILE="/run/secrets/$SECRET_NAME" \
      docker.io/library/mariadb:11 >/dev/null
  fi

  if ! podman container exists "$WEB_NAME"; then
    podman run -d \
      --name "$WEB_NAME" \
      --network "$NET" \
      -p 8086:8080 \
      -e ADMINER_DEFAULT_SERVER="$DB_NAME" \
      docker.io/library/adminer:4 >/dev/null
  fi

  podman start "$DB_NAME" >/dev/null
  podman start "$WEB_NAME" >/dev/null
}

down() {
  podman rm -f "$WEB_NAME" >/dev/null 2>&1 || true
  podman rm -f "$DB_NAME" >/dev/null 2>&1 || true
}

status() {
  podman ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
}

case "$cmd" in
  up) up ;;
  down) down ;;
  status) status ;;
  *)
    echo "usage: $0 {up|down|status}" >&2
    exit 2
    ;;
esac
