# Module 12: Security Deep Dive

This module focuses on reducing blast radius and making your container posture auditable.

## Learning Goals

- Apply least privilege inside and outside containers.
- Use read-only filesystems and drop capabilities.
- Understand SELinux and why it matters on Fedora/RHEL.
- Understand image trust at a practical level.
- Build a secure-by-default run configuration.

## Baseline Hardening Checklist

- Run rootless when possible.
- Run as non-root inside the container.
- Drop capabilities you do not need.
- Use a read-only root filesystem when possible.
- Use `tmpfs` for writable scratch.
- Limit resources (memory/CPU).
- Avoid mounting the Docker socket equivalent (do not give containers control of Podman).

Also consider:

- `--security-opt no-new-privileges`
- minimal mounts (avoid mounting home directories)
- immutable config (mount config read-only)

## Lab: Drop Capabilities

Start with a simple container and drop all Linux capabilities:

```bash
podman run --rm --cap-drop=ALL docker.io/library/alpine:latest id  # run a container
```

If your workload breaks, add only the specific capabilities required.

Avoid using `--privileged` as a workaround.

## Resource Limits

Example:

```bash
podman run --rm --memory 256m --pids-limit 200 docker.io/library/alpine:latest sh -lc 'echo ok'  # run a container
```

## Lab: No-New-Privileges

```bash
podman run --rm --security-opt no-new-privileges docker.io/library/alpine:latest id  # run a container
```

## Lab: Read-Only Root FS

Run nginx with a read-only root filesystem (this may require a writable temp location depending on image behavior):

```bash
podman run --rm -p 8080:80 --read-only --tmpfs /var/cache/nginx --tmpfs /var/run docker.io/library/nginx:stable  # run a container
```

If it fails:

- read the error
- identify the write path
- add a targeted `tmpfs` or volume

Try pairing with "drop everything":

```bash
podman run --rm -p 8080:80 --read-only --cap-drop=ALL --security-opt no-new-privileges --tmpfs /var/cache/nginx --tmpfs /var/run docker.io/library/nginx:stable  # run a container
```

If it fails, treat the error as a map of required writes/capabilities and add back only what is necessary.

## SELinux (Fedora/RHEL)

If SELinux is enforcing:

- prefer `:Z` for private bind mounts
- prefer volumes when possible

Do not disable SELinux to "fix" containers in production.

If you see mount permission errors with bind mounts:

- try `:Z`
- prefer volumes

## Image Trust (Practical)

Minimum viable practices:

- pin by digest
- use minimal base images when possible
- track upstream sources
- scan images (tooling varies by org)

Supply chain habits:

- prefer official images or your organization's curated base images
- avoid running unverified installer scripts in builds

## Checkpoint

- You can explain the difference between rootless and non-root-in-container.
- You can make a service run read-only (or explain why it cannot).

## Quick Quiz

1) Why is `--privileged` almost always the wrong answer?

2) Why is digest pinning useful even if you trust the upstream?

## Further Reading

- Linux capabilities (man7): https://man7.org/linux/man-pages/man7/capabilities.7.html
- `seccomp(2)` (man7): https://man7.org/linux/man-pages/man2/seccomp.2.html
- SELinux with containers (RHEL docs): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/assembly_using-selinux-with-containers_using-selinux
- Podman security docs: https://github.com/containers/podman/blob/main/docs/tutorials/security.md

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
