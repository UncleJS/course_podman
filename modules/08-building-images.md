# Module 8: Building Images (Containerfiles)

## Learning Goals

- Write a simple `Containerfile`.
- Build, tag, and run your own image.
- Use multi-stage builds to keep images small.
- Run as a non-root user inside the container.
- Keep secrets out of builds and images.

## Containerfile Basics

Common instructions:

- `FROM` base image
- `WORKDIR` working directory
- `COPY` add files
- `RUN` build steps
- `USER` drop privileges
- `EXPOSE` document ports
- `CMD` default command

Also useful:

- `LABEL` for metadata
- `HEALTHCHECK` for basic liveness signals

## Lab A: Build a Tiny HTTP Image

Create a new directory:

```bash
mkdir -p ./image-lab
cd ./image-lab
```

Create `index.html`:

```bash
printf '%s\n' '<h1>Hello from Podman</h1>' > index.html
```

Create `Containerfile`:

```Dockerfile
FROM docker.io/library/nginx:stable
COPY index.html /usr/share/nginx/html/index.html
```

Build and run:

```bash
podman build -t localhost/hello-nginx:1 .
podman run --rm -p 8080:80 localhost/hello-nginx:1
```

Verify in another terminal:

```bash
curl -sS http://127.0.0.1:8080/
```

Inspect what you built:

```bash
podman image inspect localhost/hello-nginx:1 | less
```

## Lab B: Run as Non-Root (Concept)

Many vendor images already run as non-root. If you build your own:

- create a user
- ensure writable paths are owned correctly
- set `USER`

Example patterns:

- if your app writes to `/tmp`, mount a `tmpfs` or keep `/tmp` writable
- if your app needs a state directory, use a volume and chown it in the image build (or on first start)

Checkpoint:

- Your container still starts.
- Writable paths (if any) are writable by the configured user.

## Lab C (Optional): Multi-Stage Build Pattern

Multi-stage builds let you compile/build in one stage and copy only the runtime artifacts into a smaller final image.

Goal:

- demonstrate "build tools stay behind"

Checklist:

- stage 1 installs build tooling and produces an artifact
- stage 2 copies only that artifact

Try the provided example (Go static binary):

- `examples/build/hello-go/Containerfile`
- `examples/build/hello-go/main.go`

Build and run:

```bash
podman build -t localhost/hello-go:1 examples/build/hello-go
podman run --rm -p 8085:8080 localhost/hello-go:1
```

Verify:

```bash
curl -sS http://127.0.0.1:8085/
```

## Build Context Hygiene

Add an ignore file to keep junk out of the build context.

Podman commonly supports `.containerignore` and often also `.dockerignore`.

Example:

```text
.git
node_modules
*.log
```

## Secrets and Builds

Rules:

- do not `COPY` secret files into an image
- do not use `ARG`/`ENV` for secret material
- use runtime file-mounted secrets (Module 4)

If you must access private dependencies:

- prefer build-time secrets support if available
- otherwise fetch in CI and copy only the resulting artifacts into the build context

## Image Hygiene

- Pin critical production images by digest.
- Keep build context small.
- Do not put secrets in:
  - `ARG`
  - `ENV`
  - build context

## Checkpoint

- You can build and run a custom image.
- You can explain why multi-stage builds exist.
- You can explain how secrets accidentally leak into image layers.
