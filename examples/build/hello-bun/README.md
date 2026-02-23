# hello-bun (Bun image build example)

This example builds a tiny HTTP server using Bun with:

- non-root runtime (`USER bun`)
- a small build artifact (`bun build`)
- a built-in `HEALTHCHECK` that calls the service over localhost

## Build

```bash
# NOTE: HEALTHCHECK metadata is not stored in OCI image format.
# Build in docker format so `podman healthcheck run` works.
podman build --format docker -t localhost/hello-bun:1 examples/build/hello-bun
```

## Run

```bash
podman run --rm -p 8090:3000 localhost/hello-bun:1
curl -sS http://127.0.0.1:8090/
curl -sS http://127.0.0.1:8090/healthz
```

## Inspect health

```bash
podman run -d --name hb -p 8090:3000 localhost/hello-bun:1
podman healthcheck run hb
podman inspect hb --format '{{json .State.Health}}'
podman rm -f hb
```
