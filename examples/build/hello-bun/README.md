# hello-bun (Bun image build example)

This example builds a tiny HTTP server using Bun with:

- non-root runtime (`USER bun`)
- a small build artifact (`bun build`)
- a built-in `HEALTHCHECK` that calls the service over localhost

## Build

```bash
# NOTE: HEALTHCHECK metadata is not stored in OCI image format.
# Build in docker format so `podman healthcheck run` works.
podman build --format docker -t localhost/hello-bun:1 examples/build/hello-bun  # build an image
```

## Run

```bash
podman run --rm -p 8090:3000 localhost/hello-bun:1  # run a container
curl -sS http://127.0.0.1:8090/  # verify HTTP endpoint
curl -sS http://127.0.0.1:8090/healthz  # verify HTTP endpoint
```

## Inspect health

```bash
podman run -d --name hb -p 8090:3000 localhost/hello-bun:1  # run a container
podman healthcheck run hb  # run the container healthcheck
podman inspect hb --format '{{json .State.Health}}'  # inspect container/image metadata
podman rm -f hb  # stop and remove the container
```
