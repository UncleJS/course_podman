# Security Cheat Sheet

## Baseline

- rootless when possible
- non-root user inside container
- do not pass secrets in env vars
- pin images by digest in production

## Hardening Flags (Examples)

```bash
podman run --read-only --tmpfs /tmp <image>  # read-only root FS + writable temp
```

## SELinux (Fedora/RHEL)

- bind mount with `:Z` (private) or `:z` (shared)

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
