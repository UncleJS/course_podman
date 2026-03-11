# hello-bun (Bun image build example)

[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

This example builds a tiny HTTP server using Bun with:

- non-root runtime (`USER bun`)
- a small build artifact (`bun build`)
- a built-in `HEALTHCHECK` that calls the service over localhost

<a id="table-of-contents"></a>

## Table of Contents

- [Build](#build)
- [Run](#run)
- [Inspect health](#inspect-health)

## Build

```bash
# NOTE: HEALTHCHECK metadata is not stored in OCI image format.
# Build in docker format so `podman healthcheck run` works.
podman build --format docker -t localhost/hello-bun:1 examples/build/hello-bun  # build an image
```

[↑ Go to TOC](#table-of-contents)

## Run

```bash
podman run --rm -p 8090:3000 localhost/hello-bun:1  # run a container
curl -sS http://127.0.0.1:8090/  # verify HTTP endpoint
curl -sS http://127.0.0.1:8090/healthz  # verify HTTP endpoint
```

[↑ Go to TOC](#table-of-contents)

## Inspect health

```bash
podman run -d --name hb -p 8090:3000 localhost/hello-bun:1  # run a container
podman healthcheck run hb  # run the container healthcheck
podman inspect hb --format '{{json .State.Health}}'  # inspect container/image metadata
podman rm -f hb  # stop and remove the container
```

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
