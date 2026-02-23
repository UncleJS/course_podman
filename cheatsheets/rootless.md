# Rootless Cheat Sheet

## Key Idea

Rootless Podman runs as your user and uses user namespaces.

## Useful Checks

```bash
podman info
grep "^$USER:" /etc/subuid /etc/subgid
podman unshare id
```

## Common Paths

- storage: `~/.local/share/containers/`
- runtime: `/run/user/<uid>/containers/`

## Boot Start for systemd User Services

```bash
sudo loginctl enable-linger "$USER"
```
