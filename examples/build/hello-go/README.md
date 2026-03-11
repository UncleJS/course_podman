# hello-go (Go multi-stage image build example)

[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../../../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

This example demonstrates a multi-stage build that produces a small runtime image.

<a id="table-of-contents"></a>

## Table of Contents

- [Build](#build)
- [Run](#run)
- [Architecture note](#architecture-note)

## Build

```bash
podman build -t localhost/hello-go:1 examples/build/hello-go  # build an image
```

[↑ Go to TOC](#table-of-contents)

## Run

```bash
podman run --rm -p 8085:8080 localhost/hello-go:1  # run a container
curl -sS http://127.0.0.1:8085/  # verify HTTP endpoint
```

[↑ Go to TOC](#table-of-contents)

## Architecture note

The Containerfile does not force `GOARCH=amd64`.

- On amd64 hosts you will build amd64.
- On arm64 hosts you will build arm64.

If you see `exec format error`, your build architecture and runtime architecture do not match.

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
