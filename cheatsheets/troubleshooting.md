# Troubleshooting Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

## Fast Triage

```bash
podman ps -a                 # is it running? exit code?
podman logs <name>           # app output / crash reason
podman inspect <name> | less # config: mounts, ports, command, env
```

## systemd/Quadlet

```bash
systemctl --user status <service>                    # systemd view: active/failed
journalctl --user -u <service> -n 200 --no-pager     # service logs from journald
```

## Network Checks

- verify ports: `-p host:container`
- verify container name DNS on the network

## Storage Checks

- volume mounted where the app expects
- permissions for the container user
- on Fedora/RHEL: use `:Z` for private bind mounts

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
