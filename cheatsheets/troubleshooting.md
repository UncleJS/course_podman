# Troubleshooting Cheat Sheet

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
