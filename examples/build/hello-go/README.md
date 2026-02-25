# hello-go (Go multi-stage image build example)

This example demonstrates a multi-stage build that produces a small runtime image.

## Build

```bash
podman build -t localhost/hello-go:1 examples/build/hello-go  # build an image
```

## Run

```bash
podman run --rm -p 8085:8080 localhost/hello-go:1  # run a container
curl -sS http://127.0.0.1:8085/  # verify HTTP endpoint
```

## Architecture note

The Containerfile does not force `GOARCH=amd64`.

- On amd64 hosts you will build amd64.
- On arm64 hosts you will build arm64.

If you see `exec format error`, your build architecture and runtime architecture do not match.

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
