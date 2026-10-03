# Troubleshooting Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Debug loop](#debug-loop)
- [Exit codes](#exit-codes)
- [Symptom to fix](#symptom-to-fix)
- [Quadlet](#quadlet)

## Debug loop

1. What state is it in? `podman ps -a`
2. What did it print? `podman logs <name>` (journald still has logs after `--rm`)
3. What was it told to do? `podman inspect <name>`
4. Change one thing and repeat.

```bash
podman ps -a
podman logs <name>
podman inspect <name> --format '{{.State.Status}} {{.State.ExitCode}}'
journalctl --user -u <service>.service -n 100 --no-pager
```

[↑ Go to TOC](#table-of-contents)

## Exit codes

| Code | Meaning |
|---|---|
| 0 | clean exit |
| 125 | Podman itself failed (the container may not exist) |
| 126 | command found, not executable |
| 127 | command not found |
| 137 | SIGKILL, often OOM |
| 143 | SIGTERM (`podman stop`) |

A port conflict fails in the `podman run` client. There is no container to `podman logs`.

[↑ Go to TOC](#table-of-contents)

## Symptom to fix

| Symptom | Look at | Fix |
|---|---|---|
| name does not resolve | default `podman` network | user-defined network (DNS is off on the default network) |
| published port, curl fails | `HostIp` in inspect | `127.0.0.1` binds are local-only; firewalld: `firewall-cmd --list-all` |
| permission denied on a bind mount | `sudo ausearch -m avc -ts recent` | `:Z` or `:z`. `:Z` relabels the whole tree |
| data gone after `podman rm` | writable layer | named volume. Anonymous volumes survive `rm` and go away with `rm -v` |
| Quadlet unit missing | generator dry-run | file under `~/.config/containers/systemd/`, then `daemon-reload` |
| service not up at boot | `Linger=` | `loginctl enable-linger` and `WantedBy=default.target`. Do not `systemctl enable` a Quadlet unit |

[↑ Go to TOC](#table-of-contents)

## Quadlet

```bash
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun
systemctl --user daemon-reload
systemctl --user status <name>.service
journalctl --user -u <name>.service -n 200 --no-pager
```

Network and volume units are `<name>-network.service` and `<name>-volume.service`.

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
