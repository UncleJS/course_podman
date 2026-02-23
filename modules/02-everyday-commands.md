# Module 2: Everyday Podman Commands

## Learning Goals

- Run containers interactively and in the background.
- Use `logs` and `exec` to debug.
- Clean up containers and images safely.
- Understand naming, exit codes, and restart behavior.

## Core Commands

Run and remove when done:

```bash
podman run --rm docker.io/library/alpine:latest echo hello
```

Notes:

- `--rm` removes the container after it exits.
- Prefer `--rm` for short experiments to avoid clutter.

Run a long-lived container:

```bash
podman run -d --name sleep1 docker.io/library/alpine:latest sleep 600
podman ps
```

Inspect exit codes:

```bash
podman wait sleep1
podman inspect sleep1 --format '{{.State.ExitCode}}'
```

View logs:

```bash
podman logs sleep1
```

Execute a command in a running container:

```bash
podman exec -it sleep1 sh
```

Tip:

- If an image does not have `sh`, try `bash` or use a debug container on the same network/pod.

Stop/start/remove:

```bash
podman stop sleep1
podman start sleep1
podman rm -f sleep1
```

## Useful Flags (Learn These Early)

- `--name <name>`: stable name for scripts
- `-e KEY=VALUE`: environment variables (avoid for secrets)
- `-v name:/path`: volumes
- `-p host:container`: publish ports
- `--network <net>`: connect to network
- `--user <uid[:gid]>`: run as a specific user

## Lab: The Writable Layer Is Not Persistence

1) Start a container and create a file:

```bash
podman run -it --name scratch docker.io/library/alpine:latest sh
```

Inside the container:

```sh
echo hi > /tmp/hello.txt
exit
```

2) Remove and recreate:

```bash
podman rm scratch
podman run -it --name scratch docker.io/library/alpine:latest sh
```

Inside:

```sh
ls -la /tmp/hello.txt
```

Expected: the file is gone.

## Lab: Name Your Containers

1) Run the same image twice with different names:

```bash
podman run -d --name a1 docker.io/library/alpine:latest sleep 300
podman run -d --name a2 docker.io/library/alpine:latest sleep 300
podman ps
podman rm -f a1 a2
```

2) Try to reuse a name and observe the error.

This teaches you why stable naming matters.

## Cleaning Up Without Nuking Your System

List containers and images:

```bash
podman ps -a
podman images
```

Remove stopped containers:

```bash
podman container prune
```

Remove unused images (be careful; it can remove bases you need):

```bash
podman image prune
```

## Checkpoint

- You can use `podman logs` and `podman exec` without guessing.
- You understand why volumes exist.

## Quick Quiz

1) What is the difference between `podman run` and `podman start`?

2) Where do you look first if a container exits immediately?
