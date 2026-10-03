# Security Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Baseline](#baseline)
- [Hardening Flags (Examples)](#hardening-flags-examples)
- [Quadlet keys](#quadlet-keys)
- [SELinux (Fedora/RHEL)](#selinux-fedorarhel)

## Baseline

- rootless when possible
- non-root user inside the container
- secrets as files (`--secret` / `Secret=`), not environment variables
- pin images by digest in production
- do not use `--privileged`

[↑ Go to TOC](#table-of-contents)

## Hardening Flags (Examples)

```bash
podman run \
  --read-only --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  --memory 256m --memory-swap 256m \
  --pids-limit 200 \
  <image>
```

Add `--cap-add=NET_BIND_SERVICE` only when the process binds a port below 1024. Publishing `-p 8080:80` still means the process inside binds port 80.

[↑ Go to TOC](#table-of-contents)

## Quadlet keys

```ini
[Container]
DropCapability=ALL
NoNewPrivileges=true
ReadOnly=true
Notify=healthy
SecurityLabelDisable=false
```

`CapDrop=` is not a Quadlet key. `SecurityLabelDisable=false` keeps SELinux on. `NoNewPrivileges=true` is the setuid control. `Notify=healthy` is what lets auto-update roll back a failed start.

[↑ Go to TOC](#table-of-contents)

## SELinux (Fedora/RHEL)

- `:Z` relabels the host directory for one container (`container_file_t` plus an MCS category).
- `:z` shares that label across containers.
- `:Z` relabels the whole tree. Never use it on `$HOME` or `/`.
- Audit denials: `sudo ausearch -m avc -ts recent` (the audit log is not readable rootless).

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
