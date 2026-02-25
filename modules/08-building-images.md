# Module 8: Building Images (Containerfiles)

This module teaches you how to build images you can trust in production:

- reproducible enough to debug
- small enough to ship
- least-privilege by default
- free of secrets

The focus is Podman-first: `podman build`, `podman image`, `podman push`.

---

## Learning Goals

By the end of this module you will be able to:

- Explain what an image layer is and why instruction order matters.
- Write a Containerfile that is secure-by-default (non-root, minimal writes).
- Build, tag, inspect, run, and push images with Podman.
- Use multi-stage builds and `--target` to keep runtime images small.
- Keep secrets out of build layers and out of the build context.
- Debug common build and runtime failures (missing files, permissions, wrong arch).

## Minimum Path (If You Are Short on Time)

- Do Lab A (build + run a tiny image).
- Add a `.containerignore` and switch from `COPY . .` to explicit copies.
- Do the non-root lab (Lab B).
- Build a multi-stage image once (Go example or `examples/build/hello-bun`).

---

## 1  Images, Layers, and the Build Mental Model

An image build is a series of filesystem snapshots.

- Each instruction in a `Containerfile` creates a new **layer**.
- A layer is immutable; rebuilding changes layers above the first changed step.
- `COPY` and `RUN` are the two instructions that most often invalidate caching.

Practical implications:

- Put slow-changing steps early (base image selection, OS packages).
- Put fast-changing steps late (your app source code).
- Keep the build context small so `COPY` does not force expensive rebuilds.

Terminology:

- **Containerfile**: the build recipe (Dockerfile-compatible syntax).
- **Build context**: the directory sent to the builder for `COPY`/`ADD`.
- **Tag**: a mutable pointer (`myapp:1`, `myapp:latest`).
- **Digest**: immutable content address (`sha256:...`).

---

## 2  `podman build` Fundamentals

### 2.1  Basic Build

```bash
podman build -t localhost/myapp:1 .  # build an image
```

Common flags:

```bash
podman build -t localhost/myapp:1 -f Containerfile .  # build an image
podman build --pull=always -t localhost/myapp:1 .  # build an image
podman build --no-cache -t localhost/myapp:1 .  # build an image
podman build --layers -t localhost/myapp:1 .  # build an image
podman build --target runtime -t localhost/myapp:1 .  # build an image
```

Notes:

- `--pull=always` is useful in CI to ensure you build from the newest base.
- `--no-cache` is useful when debugging, but do not make it your default.
- `--target` builds only a named stage from a multi-stage Containerfile.

### 2.2  Naming: Why `localhost/` Is Used in Labs

Using `localhost/<name>` makes it explicit that the tag is local and not in a remote registry namespace.

```bash
podman images | head  # list images
```

You will see `localhost/myapp:1` locally even if you are not logged into a registry.

### 2.3  What Builds What

Podman builds are typically executed by Buildah under the hood.

You do not need to become a Buildah expert, but this matters when you search for docs and flags.

---

## 3  Containerfile Instructions: The Practical Subset

You can build most real images with these instructions:

- `FROM` choose base image (pin versions; consider digest pinning for prod)
- `WORKDIR` avoid brittle `cd` chains
- `COPY` bring in files (prefer explicit paths)
- `RUN` install/build steps
- `ENV` defaults (not secrets)
- `USER` run as non-root
- `EXPOSE` document ports (does not publish)
- `CMD` default command
- `ENTRYPOINT` fixed entry wrapper (use sparingly)
- `LABEL` attach metadata
- `HEALTHCHECK` basic liveness signal (optional)

### 3.1  `COPY` vs `ADD`

Rule of thumb:

- Use `COPY` almost always.
- Use `ADD` only when you specifically need its extra behaviors (such as extracting a local tar archive).

Do not use `ADD` to fetch URLs.

### 3.2  Shell Form vs Exec Form

Exec form (recommended for servers):

```Dockerfile
CMD ["nginx", "-g", "daemon off;"]
```

Shell form:

```Dockerfile
CMD nginx -g 'daemon off;'
```

Why exec form is better:

- Signal handling works as expected.
- Your process becomes PID 1 (no intermediate shell).
- Arguments are not re-parsed by a shell.

### 3.3  `ENTRYPOINT` vs `CMD`

- `CMD` is the default that users commonly override.
- `ENTRYPOINT` is for the command you almost never want overridden.

If you use both:

```Dockerfile
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["/app/server"]
```

### 3.4  `EXPOSE` Does Not Publish Ports

`EXPOSE 8080` is documentation inside the image.

Publishing is runtime:

```bash
podman run -p 8080:8080 localhost/myapp:1  # run a container
```

---

## 4  Lab A: Build a Tiny HTTP Image (Warm-Up)

Create a new directory:

```bash
mkdir -p ./image-lab  # create directory
cd ./image-lab  # change directory
```

Create `index.html`:

```bash
printf '%s\n' '<h1>Hello from Podman</h1>' > index.html  # print text without trailing newline
```

Create `Containerfile`:

```Dockerfile
FROM docker.io/library/nginx:stable
COPY index.html /usr/share/nginx/html/index.html
```

Build and run:

```bash
podman build -t localhost/hello-nginx:1 .  # build an image
podman run --rm -p 8080:80 localhost/hello-nginx:1  # run a container
```

Verify in another terminal:

```bash
curl -sS http://127.0.0.1:8080/  # verify HTTP endpoint
```

Inspect the image:

```bash
podman image inspect localhost/hello-nginx:1 | less  # inspect image metadata
podman image history localhost/hello-nginx:1  # show image layer history
```

Cleanup:

```bash
podman rmi localhost/hello-nginx:1  # remove the image from local storage
cd ..  # change directory
rm -rf ./image-lab                 # delete the lab directory
```

---

## 5  Build Context Hygiene (The Most Common Image Leak)

Your build context is everything in the directory you pass to `podman build`.

If your directory contains:

- `.env`
- SSH keys
- kubeconfigs
- `node_modules`
- build artifacts

...then a sloppy `COPY . .` can accidentally ship them inside your image.

### 5.1  Use `.containerignore`

Create `.containerignore` next to your `Containerfile`:

```text
.git
.github
.env
*.key
*.pem
node_modules
dist
build
tmp
*.log
```

Podman commonly supports `.containerignore` and often also `.dockerignore`.

### 5.2  Prefer Explicit Copies

Instead of:

```Dockerfile
COPY . /app
```

Prefer:

```Dockerfile
COPY package.json bun.lockb /app/
COPY src/ /app/src/
```

This prevents accidental inclusion and improves caching.

---

## 6  Running as Non-Root (Image-Level Least Privilege)

Rootless Podman protects the host.

Running as non-root inside the container protects you from:

- container escape bugs that still require privileges inside the container
- accidental writes to system locations in the image
- overly-permissive defaults (root can write almost anywhere)

### 6.1  The Three Places You Usually Need Write Access

- `/tmp`
- an app state directory (like `/var/lib/myapp`)
- log directory (often better to log to stdout/stderr)

Best practice:

- treat the root filesystem as read-only when possible (Module 12)
- use a dedicated volume or tmpfs for the few paths that must be writable

### 6.2  Pattern: Create a User and Own the App Directory

```Dockerfile
FROM docker.io/library/alpine:3.20

RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --chown=app:app . /app
USER app
CMD ["sh", "-lc", "id && ls -la"]
```

Notes:

- `COPY --chown=...` is often cleaner than `RUN chown -R ...`.
- Some minimal images do not include `adduser`/`addgroup` (use their native tools).

### 6.3  Lab B: Verify Non-Root Actually Works

```bash
mkdir -p ./nonroot-lab  # create directory
cd ./nonroot-lab  # change directory

cat > Containerfile <<'EOF'
FROM docker.io/library/alpine:3.20

RUN addgroup -S app && adduser -S -G app app
WORKDIR /app
COPY --chown=app:app . /app
USER app
CMD ["sh", "-lc", "echo user=$(id -u) group=$(id -g); touch /app/ok; ls -la /app"]
EOF

podman build -t localhost/nonroot:1 .  # build an image
podman run --rm localhost/nonroot:1  # run a container
podman rmi localhost/nonroot:1  # remove the image from local storage
cd ..  # change directory
rm -rf ./nonroot-lab            # delete the lab directory
```

If `touch /app/ok` fails, you did not set ownership correctly.

---

## 7  Multi-Stage Builds (Small Images, Fast Builds)

Multi-stage builds let you:

- compile/build in a stage that has toolchains
- copy only the runtime artifacts into a final minimal image

Key properties:

- stages have names: `FROM ... AS build`
- later stages can `COPY --from=build ...`
- `podman build --target <stage>` stops early (useful for debugging)

### 7.1  Lab C (Optional): Provided Go Multi-Stage Example

This repository includes:

- `examples/build/hello-go/Containerfile`
- `examples/build/hello-go/main.go`

Build and run:

```bash
podman build -t localhost/hello-go:1 examples/build/hello-go  # build an image
podman run --rm -p 8085:8080 localhost/hello-go:1  # run a container
curl -sS http://127.0.0.1:8085/  # verify HTTP endpoint
```

Inspect size:

```bash
podman images | head  # list images
podman image history localhost/hello-go:1  # show image layer history
```

### 7.2  Pattern: Build Dependencies First, Copy Source Later

This pattern maximizes cache reuse:

1. copy dependency manifests
2. install dependencies
3. copy application source
4. build

Even if you do not use multi-stage, the order still matters.

### 7.3  Example Pattern: Bun App (Build + Runtime)

This is an example Containerfile shape for Bun-based services. Adapt it to your project.

Try the repo-backed example:

- `examples/build/hello-bun/Containerfile`
- `examples/build/hello-bun/server.ts`

```Dockerfile
FROM docker.io/oven/bun:1.2.0 AS build
WORKDIR /app

# Install deps separately for caching
COPY package.json bun.lockb ./
RUN bun install --frozen-lockfile

COPY . ./
RUN bun run build

FROM docker.io/oven/bun:1.2.0 AS runtime
WORKDIR /app
ENV NODE_ENV=production

# Copy only the runtime artifacts you need
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./package.json

USER bun
EXPOSE 3000
CMD ["bun", "dist/server.js"]
```

Notes:

- If your build outputs different paths, adjust `COPY --from=build`.
- If you need native modules, your runtime base must be compatible.

### 7.4  Example Pattern: Static Web Build (Build Stage + nginx)

```Dockerfile
FROM docker.io/library/node:22-alpine AS build
WORKDIR /src
COPY package.json package-lock.json ./
RUN npm ci
COPY . ./
RUN npm run build

FROM docker.io/library/nginx:stable
COPY --from=build /src/dist/ /usr/share/nginx/html/
```

This keeps Node and build tools out of the runtime image.

---

## 8  Caching: Make Rebuilds Fast

Most slow builds are slow because caching is accidentally disabled.

### 8.1  Common Cache-Busters

- `COPY . .` early in the file
- including `node_modules/` or `target/` in the context
- running `apt-get update` in a separate layer from `apt-get install`
- using floating package versions

### 8.2  Linux Packages: One Layer, Clean Up

For Debian/Ubuntu bases:

```Dockerfile
RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl \
  && rm -rf /var/lib/apt/lists/*
```

For Alpine:

```Dockerfile
RUN apk add --no-cache ca-certificates curl
```

### 8.3  Use Stage Targets for Faster Debugging

If a multi-stage build fails late, rebuild only to the stage you care about:

```bash
podman build --target build -t localhost/myapp:build .  # build an image
```

Then you can run that stage as an image to inspect the filesystem:

```bash
podman run --rm -it localhost/myapp:build sh  # run a container
```

---

## 9  `ARG`, `ENV`, and Configuration

### 9.1  `ARG` Is Build-Time

`ARG` values exist during build, and can influence caching.

```Dockerfile
ARG APP_VERSION
LABEL org.opencontainers.image.version=$APP_VERSION
```

Build:

```bash
podman build --build-arg APP_VERSION=1.2.3 -t localhost/myapp:1 .  # build an image
```

### 9.2  `ENV` Is Runtime Default

```Dockerfile
ENV PORT=3000
EXPOSE 3000
CMD ["/app/server"]
```

Override at runtime:

```bash
podman run --rm -e PORT=8080 localhost/myapp:1  # run a container
```

### 9.3  Do Not Put Secrets in `ARG` or `ENV`

If you do this:

```Dockerfile
ARG API_KEY
RUN curl -H "Authorization: Bearer $API_KEY" ...
```

You risk leaking secrets into:

- image history
- build logs
- intermediate layers

Use runtime secrets (Module 4) or build-time secret mechanisms (next section).

---

## 10  Secrets and Private Dependencies (Build-Time)

Rules you can rely on:

- never `COPY` secret files into the image
- never commit secrets into the build context
- prefer fetching private dependencies outside the build and copying only artifacts

### 10.1  If Your Podman Supports Build Secrets

Some Podman/Buildah versions support `podman build --secret ...`.

Example shape (do not assume your version supports it):

```bash
podman build --secret id=npmrc,src=$HOME/.npmrc -t localhost/private-build:1 .  # build an image
```

In a Containerfile, the secret is mounted at build time (not copied into layers).

If your version does not support it, use the safe fallback below.

### 10.2  Safe Fallback: Fetch in CI, Copy Artifacts

Instead of cloning or downloading private content during image build:

1. fetch private deps in CI with credentials
2. produce a build artifact (binary, bundle, wheel)
3. copy only the artifact into the build context
4. build a runtime image that contains only that artifact

This keeps secrets entirely out of the image build process.

---

## 11  Labels, Metadata, and Image Introspection

Labels help you operate images later.

Recommended OCI labels:

- `org.opencontainers.image.title`
- `org.opencontainers.image.description`
- `org.opencontainers.image.source`
- `org.opencontainers.image.revision`
- `org.opencontainers.image.version`
- `org.opencontainers.image.licenses`

Example:

```Dockerfile
LABEL org.opencontainers.image.title="hello"
LABEL org.opencontainers.image.source="https://example.com/repo"
LABEL org.opencontainers.image.version="1.0.0"
```

Inspect labels:

```bash
podman image inspect localhost/myapp:1 --format '{{json .Labels}}'  # inspect image metadata
```

---

## 12  Tagging, Digests, and Promotion

### 12.1  Tags Are Mutable

`myapp:latest` can point to different content over time.

This is convenient, but it is not auditable.

### 12.2  Digests Are Immutable

Pull and run by digest:

```bash
podman pull docker.io/library/nginx@sha256:<digest>  # pull an image
podman run --rm docker.io/library/nginx@sha256:<digest>  # run a container
```

For production:

- build from pinned bases when you need repeatability
- promote images by digest (not by tag) when you need audit trails

### 12.3  A Simple Promotion Flow

1. build locally or in CI as `myapp:git-<sha>`
2. run tests
3. re-tag as `myapp:staging`
4. re-tag as `myapp:prod`

Commands:

```bash
podman tag localhost/myapp:git-abc123 localhost/myapp:staging  # add another tag/name
podman tag localhost/myapp:git-abc123 localhost/myapp:prod  # add another tag/name
```

---

## 13  Pushing Images to a Registry

### 13.1  Login

```bash
podman login <registry>  # log into a container registry
```

### 13.2  Tag for the Registry Namespace

```bash
podman tag localhost/myapp:1 registry.example.com/team/myapp:1  # add another tag/name
```

### 13.3  Push

```bash
podman push registry.example.com/team/myapp:1  # push an image to a registry
```

### 13.4  Pull and Verify

```bash
podman pull registry.example.com/team/myapp:1  # pull an image
podman image inspect registry.example.com/team/myapp:1 | less  # inspect image metadata
```

Production habit:

- record the digest you deployed
- configure your runtime (Quadlet, Kubernetes YAML) to pull by digest

---

## 14  Testing the Image You Built

Your build is not done when `podman build` finishes.

Minimum checks:

1. container starts
2. correct ports are exposed/published
3. process responds to a health endpoint
4. container runs as non-root (if intended)
5. container writes only to intended paths

### 14.1  Smoke Test

```bash
podman run --rm -p 8080:8080 localhost/myapp:1  # run a container
```

### 14.2  Confirm Effective User

```bash
podman run --rm localhost/myapp:1 id  # run a container
```

### 14.3  Healthcheck (If You Define One)

If your Containerfile includes `HEALTHCHECK`:

- You may see warnings that `HEALTHCHECK` is ignored in OCI image format.
- If you need the healthcheck stored in the image, build using docker format:

```bash
podman build --format docker -t localhost/myapp:1 .  # build an image
```

Alternative: define a healthcheck at runtime with `podman run --health-*` flags.

```bash
podman run -d --name hc localhost/myapp:1  # run a container
podman healthcheck run hc  # run the container healthcheck
podman inspect hc --format '{{json .State.Health}}'  # inspect container/image metadata
podman rm -f hc  # stop and remove the container
```

---

## 15  Troubleshooting Builds (Common Failures)

### 15.1  `COPY failed: file not found in build context`

Causes:

- wrong path (relative paths are relative to the build context)
- file excluded by `.containerignore`
- building from the wrong directory

Fix:

- confirm your build context: `podman build ... <context-dir>`
- list files in the context dir

### 15.2  Permission Errors in `RUN` Steps

Typical in rootless builds when scripts assume root-only locations.

Fix patterns:

- write into `$HOME` or your work directory, not `/root`
- ensure `WORKDIR` exists
- if you switch to `USER app`, do it after you finish root-only install steps

### 15.3  Container Starts Then Exits Immediately

Causes:

- `CMD` is missing or wrong
- app binary not executable
- wrong working directory

Debug:

```bash
podman run --rm -it --entrypoint sh localhost/myapp:1  # run a container
```

### 15.4  `exec format error`

Cause:

- architecture mismatch (built for amd64, running on arm64, or vice versa)

Fix:

- build for the target platform (if your environment supports it):

```bash
podman build --platform linux/amd64 -t localhost/myapp:amd64 .  # build an image
```

Cross-building often requires extra host setup (emulation). Treat it as an advanced topic.

### 15.5  Huge Images

Causes:

- build tools included in the runtime stage
- caches kept (package manager caches, build artifacts)
- copying your entire repo including junk

Fix:

- multi-stage builds
- `.containerignore`
- copy only artifacts into the final stage

Inspect what grew:

```bash
podman image history localhost/myapp:1  # show image layer history
```

---

## 16  Cleanup: Keep Your Machine Healthy

Image builds create intermediate images and caches.

Useful commands:

```bash
podman images  # list images
podman ps -a  # list containers

podman image prune        # remove unused images (frees disk)
podman container prune    # remove stopped containers
podman system prune       # remove unused objects (be careful)

# builder-specific cache (if supported)
podman builder prune      # remove build cache (if supported)
```

Be careful:

- `podman system prune` can delete data you care about if you store it in unnamed volumes.

---

## 17  Extended Lab: A Small "Real" Service Image

This lab builds a service image with:

- non-root runtime
- explicit copies
- reasonable labels
- a predictable port

It uses only shell + Python standard library so you do not need extra tooling.

### 17.1  Create a Small App

```bash
mkdir -p ./svc-lab  # create directory
cd ./svc-lab  # change directory
```

Create `server.py`:

```bash
cat > server.py <<'EOF'
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "8080"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok\n")

HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
EOF
```

Create a `.containerignore`:

```bash
cat > .containerignore <<'EOF'
.git
.env
*.log
__pycache__
EOF
```

Create `Containerfile`:

```bash
cat > Containerfile <<'EOF'
FROM docker.io/library/python:3.13-alpine

LABEL org.opencontainers.image.title="svc-lab"
LABEL org.opencontainers.image.description="tiny HTTP server lab"

RUN addgroup -S app && adduser -S -G app app

WORKDIR /app
COPY --chown=app:app server.py /app/server.py

ENV PORT=8080
USER app
EXPOSE 8080

CMD ["python", "/app/server.py"]
EOF
```

Build and run:

```bash
podman build -t localhost/svc-lab:1 .  # build an image
podman run --rm -p 8088:8080 localhost/svc-lab:1  # run a container
```

Verify:

```bash
curl -sS http://127.0.0.1:8088/  # verify HTTP endpoint
```

Cleanup:

```bash
podman rmi localhost/svc-lab:1  # remove the image from local storage
cd ..  # change directory
rm -rf ./svc-lab               # delete the lab directory
```

---

## Checkpoint

- You can explain what a build context is and why `.containerignore` matters.
- You can write a Containerfile that runs as non-root.
- You can explain why multi-stage builds keep runtime images small.
- You can inspect image history to understand what changed.
- You can explain why secrets do not belong in `ARG`, `ENV`, or `COPY`.

---

## Quick Quiz

1) Your build works, but rebuilds are always slow even when nothing changes. What Containerfile patterns usually cause cache misses?

2) Why is `COPY . .` risky even when you think your repo contains no secrets?

3) You want to build a Go binary and ship it in a small runtime image. What key multi-stage instruction copies the artifact into the final image?

4) You set `EXPOSE 8080` in the image but the service is not reachable from the host. What did you forget?

5) An auditor asks you to prove exactly which base image you shipped. Why does pinning by digest help?

---

## Further Reading

- `man podman-build`
- `man podman-image`
- `man Containerfile` (often via Buildah docs)
- OCI image spec labels: https://github.com/opencontainers/image-spec/blob/main/annotations.md

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
