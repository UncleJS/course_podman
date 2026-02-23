# Module 1: Containers 101

## Learning Goals

- Explain images vs containers in one sentence.
- Understand what an OCI image is (layers + config).
- Understand why rootless containers matter.
- Understand the boundary: containers are isolation, not a VM.

## The Three Things To Get Right

1) Image: the immutable template you pull/build.

2) Container: a running (or stopped) instance of an image with:

- a process
- a writable layer
- mounts
- network settings

3) Runtime boundaries:

- Namespaces: process IDs, networking, mounts
- cgroups: CPU/memory limits

Important: the kernel is shared.

- A container is not a VM.
- Container security is about reducing blast radius and applying least privilege.

## Rootless vs Rootful

Rootless benefits:

- A container breakout is less likely to become full-host root.
- You can run services without handing developers root.

Rootless tradeoffs:

- Some networking and low ports require extra setup.
- File permissions can be confusing until you learn UID mapping.

Rule of thumb:

- Use rootless by default.
- Use rootful only when you can explain why it is required.

## Terminology You Will See

- OCI: the standards that define images and runtimes.
- runtime: software that starts the container process (Podman uses an OCI runtime under the hood).
- registry: where images live (Docker Hub, Quay, your internal registry).
- short name: a shorthand like `alpine` which resolves to a fully qualified name.

## Lab: Compare Host vs Container

Run a container and compare:

```bash
uname -a
podman run --rm docker.io/library/alpine:latest uname -a
```

Look at processes inside the container:

```bash
podman run --rm docker.io/library/alpine:latest ps -ef
```

You will see a small process tree. This is normal.

Inspect the container config (no need to memorize, just recognize the shape):

```bash
podman create --name c101 docker.io/library/alpine:latest sleep 300
podman inspect c101 | less
podman rm c101
```

What to look for in `inspect`:

- the image reference
- mount points
- network mode
- environment variables
- user

## Checkpoint

- You can explain: "An image is a template; a container is a running instance."
- You know rootless is the default for this course.

## Quick Quiz (Answer Without Running Commands)

1) If you delete a container, do you delete its image?

2) If a container runs as UID 0 inside, does that mean it is host root?
