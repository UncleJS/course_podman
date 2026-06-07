#!/usr/bin/env bash
set -euo pipefail

# Generate the ODP slide decks using a Podman container only:
# no host python/pip, no bind mounts (named-volume staging).
# odfpy is installed inside the throwaway container, never on the host.
# Output: slides/*.odp (one per module + intro/closing + combined deck)

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT_DIR="$ROOT_DIR/slides"
VOLUME="course-build-slides"
PYTHON_IMAGE="docker.io/library/python:3-alpine"

mkdir -p "$OUT_DIR"

cleanup() {
  podman rm -f course-slides-stage course-slides-extract >/dev/null 2>&1 || true
  podman volume rm -f "$VOLUME" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

# Stage the build script into a named volume (no bind mounts).
podman volume create "$VOLUME" >/dev/null
podman create --name course-slides-stage -v "$VOLUME":/work "$PYTHON_IMAGE" true >/dev/null
podman cp "$ROOT_DIR/scripts" course-slides-stage:/work/
podman rm course-slides-stage >/dev/null

# Build all decks inside the container.
podman run --rm -v "$VOLUME":/work -w /work "$PYTHON_IMAGE" \
  sh -ec 'pip install --quiet --root-user-action=ignore odfpy && python3 scripts/build_slides.py slides'

# Extract the generated .odp files back out of the volume.
podman create --name course-slides-extract -v "$VOLUME":/work "$PYTHON_IMAGE" true >/dev/null
podman cp course-slides-extract:/work/slides/. "$OUT_DIR/"

printf 'Wrote ODP decks to: %s\n' "$OUT_DIR"
