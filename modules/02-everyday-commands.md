# Module 2: Everyday Podman Commands

## Learning Goals

- Run containers interactively and in the background.
- Use `logs` and `exec` to debug.
- Clean up containers and images safely.
- Understand naming, exit codes, and restart behavior.

## Core Commands

Run and remove when done:

```bash
podman run --rm docker.io/library/alpine:latest echo hello  # run a container
```

Notes:

- `--rm` removes the container after it exits.
- Prefer `--rm` for short experiments to avoid clutter.

Run a long-lived container:

```bash
podman run -d --name sleep1 docker.io/library/alpine:latest sleep 600  # run a container
podman ps  # list containers
```

Inspect exit codes:

```bash
podman wait sleep1  # wait for a container to exit
podman inspect sleep1 --format '{{.State.ExitCode}}'  # inspect container/image metadata
```

View logs:

```bash
podman logs sleep1  # show container logs
```

Execute a command in a running container:

```bash
podman exec -it sleep1 sh  # run a command in a running container
```

Tip:

- If an image does not have `sh`, try `bash` or use a debug container on the same network/pod.

Stop/start/remove:

```bash
podman stop sleep1  # stop a running container
podman start sleep1  # start an existing container
podman rm -f sleep1  # stop (if needed) and force remove the container
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
podman run -it --name scratch docker.io/library/alpine:latest sh  # run a container
```

Inside the container:

```sh
echo hi > /tmp/hello.txt  # print text
exit  # exit the shell
```

2) Remove and recreate:

```bash
podman rm scratch  # remove the container
podman run -it --name scratch docker.io/library/alpine:latest sh  # run a container
```

Inside:

```sh
ls -la /tmp/hello.txt  # list files
```

Expected: the file is gone.

## Lab: Name Your Containers

1) Run the same image twice with different names:

```bash
podman run -d --name a1 docker.io/library/alpine:latest sleep 300  # run a container
podman run -d --name a2 docker.io/library/alpine:latest sleep 300  # run a container
podman ps  # list containers
podman rm -f a1 a2  # cleanup both containers
```

2) Try to reuse a name and observe the error.

This teaches you why stable naming matters.

## Cleaning Up Without Nuking Your System

List containers and images:

```bash
podman ps -a  # list containers
podman images  # list images
```

Remove stopped containers:

```bash
podman container prune  # remove all stopped containers
```

Remove unused images (be careful; it can remove bases you need):

```bash
podman image prune  # remove unused images (frees disk)
```

## Checkpoint

- You can use `podman logs` and `podman exec` without guessing.
- You understand why volumes exist.

## Quick Quiz

1) What is the difference between `podman run` and `podman start`?

2) Where do you look first if a container exits immediately?

## Further Reading

- `podman-run(1)`: https://docs.podman.io/en/latest/markdown/podman-run.1.html
- `podman-ps(1)`: https://docs.podman.io/en/latest/markdown/podman-ps.1.html
- `podman-logs(1)`: https://docs.podman.io/en/latest/markdown/podman-logs.1.html
- `podman-exec(1)`: https://docs.podman.io/en/latest/markdown/podman-exec.1.html
- `podman-inspect(1)`: https://docs.podman.io/en/latest/markdown/podman-inspect.1.html

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
