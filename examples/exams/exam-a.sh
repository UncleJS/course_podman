#!/usr/bin/env bash
# Exam A fixture. Starts a named container that exits.
# Diagnose it with the four-step loop. Do not rebuild the image.
set -euo pipefail

podman rm -f exam-a >/dev/null 2>&1 || true
podman run -d --name exam-a docker.io/library/alpine:latest not-a-command || true
