# Rootless Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Key Idea](#key-idea)
- [Useful Checks](#useful-checks)
- [Common Paths](#common-paths)
- [Boot Start for systemd User Services](#boot-start-for-systemd-user-services)

## Key Idea

Rootless Podman runs as your user and uses user namespaces.

[↑ Go to TOC](#table-of-contents)

## Useful Checks

```bash
podman info  # show Podman host configuration
grep "^$USER:" /etc/subuid /etc/subgid  # filter output
podman unshare id  # run a command inside the user namespace
```

[↑ Go to TOC](#table-of-contents)

## Common Paths

- storage: `~/.local/share/containers/`
- runtime: `/run/user/<uid>/containers/`

[↑ Go to TOC](#table-of-contents)

## Boot Start for systemd User Services

```bash
sudo loginctl enable-linger "$USER"  # allow user services to start at boot
```

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
