# Troubleshooting Cheat Sheet

## Fast Triage

```bash
podman ps -a
podman logs <name>
podman inspect <name> | less
```

## systemd/Quadlet

```bash
systemctl --user status <service>
journalctl --user -u <service> -n 200 --no-pager
```

## Network Checks

- verify ports: `-p host:container`
- verify container name DNS on the network

## Storage Checks

- volume mounted where the app expects
- permissions for the container user
- on Fedora/RHEL: use `:Z` for private bind mounts
