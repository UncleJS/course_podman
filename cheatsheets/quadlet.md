# Quadlet Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Files](#files)
- [Generated unit names](#generated-unit-names)
- [Workflow](#workflow)
- [Boot Start](#boot-start)
- [Keys you will type](#keys-you-will-type)

## Files

Put Quadlet files in `~/.config/containers/systemd/`.

| Extension | Becomes |
|---|---|
| `name.container` | `name.service` |
| `name.pod` | `name-pod.service` |
| `name.kube` | `name.service` |
| `name.image` | `name.service` (pull) |
| `name.network` | `name-network.service` |
| `name.volume` | `name-volume.service` |

[↑ Go to TOC](#table-of-contents)

## Generated unit names

`systemctl --user status` uses the generated name, not the filename stem for networks and volumes:

```bash
systemctl --user status hello-nginx.service
systemctl --user status capnet-network.service
systemctl --user status mariadb-data-volume.service
```

[↑ Go to TOC](#table-of-contents)

## Workflow

```bash
systemctl --user daemon-reload
systemctl --user start <name>.service
systemctl --user status <name>.service
journalctl --user -u <name>.service -n 100 --no-pager
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun
```

[↑ Go to TOC](#table-of-contents)

## Boot Start

Generated Quadlet units are transient. `systemctl --user enable` does not persist them. The generator applies `[Install]` at `daemon-reload`.

```ini
[Install]
WantedBy=default.target
```

```bash
sudo loginctl enable-linger "$USER"
systemctl --user daemon-reload
```

`Restart=unless-stopped` is not a systemd value. Use `Restart=on-failure` or `Restart=always`.

[↑ Go to TOC](#table-of-contents)

## Keys you will type

| Key | Meaning |
|---|---|
| `Image=` | image reference; pin with `@sha256:<hex>` |
| `PublishPort=` | `-p`; use `127.0.0.1:8080:80` for loopback |
| `Network=` | join a `.network` unit |
| `Volume=` | mount a `.volume` unit or a named volume |
| `Secret=` | file mount at `/run/secrets/<name>` (not an env var) |
| `DropCapability=ALL` | `--cap-drop=ALL` (`CapDrop=` is rejected) |
| `AddCapability=` | `--cap-add` |
| `NoNewPrivileges=true` | block setuid escalation |
| `Notify=healthy` | systemd stays `starting` until the healthcheck passes |
| `AutoUpdate=registry` | label for `podman auto-update` |

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
