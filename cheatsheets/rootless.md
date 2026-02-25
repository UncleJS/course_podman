# Rootless Cheat Sheet

## Key Idea

Rootless Podman runs as your user and uses user namespaces.

## Useful Checks

```bash
podman info  # show Podman host configuration
grep "^$USER:" /etc/subuid /etc/subgid  # filter output
podman unshare id  # run a command inside the user namespace
```

## Common Paths

- storage: `~/.local/share/containers/`
- runtime: `/run/user/<uid>/containers/`

## Boot Start for systemd User Services

```bash
sudo loginctl enable-linger "$USER"  # allow user services to start at boot
```

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
