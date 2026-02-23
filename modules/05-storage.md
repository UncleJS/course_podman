# Module 5: Storage (Volumes, Bind Mounts, Permissions)

## Learning Goals

- Use volumes for persistent state.
- Use bind mounts for source code and config.
- Debug rootless permission issues (UID/GID mapping).
- Understand SELinux labeling at a high level.
- Know when to use `podman unshare`.

## The Three Storage Types You Will Use

1) Writable layer (per-container, not persistence)

2) Named volume (Podman-managed path, best default for data)

3) Bind mount (you pick the host path)

Practical guidance:

- Use volumes for databases and state.
- Use bind mounts for configuration and source code.
- Avoid writing important data into the writable layer.

## Volumes

Create/list/inspect:

```bash
podman volume create dbdata
podman volume ls
podman volume inspect dbdata
```

Use a volume:

```bash
podman run --rm -v dbdata:/data docker.io/library/alpine:latest sh -lc 'echo hi > /data/x'
podman run --rm -v dbdata:/data docker.io/library/alpine:latest sh -lc 'cat /data/x'
```

Clean up (be careful; this deletes data):

```bash
podman volume rm dbdata
```

## Bind Mounts

Bind mounts are great for:

- configs
- certificates
- local source code in development

Example:

```bash
mkdir -p ./mnt-demo
echo hi > ./mnt-demo/hello.txt
podman run --rm -v ./mnt-demo:/mnt:Z docker.io/library/alpine:latest cat /mnt/hello.txt
```

Read-only bind mount:

```bash
podman run --rm -v ./mnt-demo:/mnt:Z,ro docker.io/library/alpine:latest sh -lc 'cat /mnt/hello.txt; echo nope > /mnt/x'
```

SELinux note (Fedora/RHEL):

- `:Z` relabels the content for private container use.
- `:z` relabels for shared use.

If SELinux is enforcing and you omit labels, mounts can fail with "permission denied".

## Inspect Mounts

```bash
podman run -d --name mount1 -v ./mnt-demo:/mnt:Z docker.io/library/alpine:latest sleep 300
podman inspect mount1 --format '{{json .Mounts}}' | less
podman rm -f mount1
```

## Rootless Permission Pitfalls

Common symptom:

- container process cannot write a mounted directory

Common causes:

- host path is owned by root and not writable by your user
- image runs as a non-root user and needs a matching UID

Debug steps:

```bash
podman unshare id
podman unshare ls -la <path>
```

Fix patterns:

- If the container runs as your UID, bind mounts are usually easiest.
- If the image runs as a dedicated user, prefer a named volume and let the image initialize ownership.
- If you must, adjust ownership inside the user namespace:

```bash
podman unshare chown -R 1000:1000 <path>
```

Do not blindly `chmod 777`.

## SELinux Drill (Fedora/RHEL)

If SELinux is Enforcing, try this to learn the failure mode:

1) Attempt a bind mount without labels:

```bash
podman run --rm -v ./mnt-demo:/mnt docker.io/library/alpine:latest cat /mnt/hello.txt
```

2) If you get permission denied, fix it by adding `:Z`:

```bash
podman run --rm -v ./mnt-demo:/mnt:Z docker.io/library/alpine:latest cat /mnt/hello.txt
```

Do not disable SELinux as a workaround.

## Lab: Persistent DB Data (Conceptual)

Run a database with a named volume (choose an image you are comfortable with). The key learning is:

- container can be replaced
- data remains

Checklist:

- Create a named volume
- Start the DB with that volume
- Create a table/record
- Remove the container
- Start a new container with the same volume
- Verify the record is still there

Stretch:

- show where the volume lives (`podman volume inspect`)
- document a backup and restore method (logical dump)

## Checkpoint

- You can choose volume vs bind mount intentionally.
- You can explain when `:Z` matters on Fedora/RHEL.
- You can use `podman unshare` to debug permission issues.

## Further Reading

- `podman-volume(1)`: https://docs.podman.io/en/latest/markdown/podman-volume.1.html
- Rootless storage and UID mapping: https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md
- SELinux mount labeling for containers (RHEL docs): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/assembly_using-selinux-with-containers_using-selinux
- `subuid(5)` and `subgid(5)` (man7): https://man7.org/linux/man-pages/man5/subuid.5.html
