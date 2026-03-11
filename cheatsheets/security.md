# Security Cheat Sheet
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](../LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Baseline](#baseline)
- [Hardening Flags (Examples)](#hardening-flags-examples)
- [SELinux (Fedora/RHEL)](#selinux-fedorarhel)

## Baseline

- rootless when possible
- non-root user inside container
- do not pass secrets in env vars
- pin images by digest in production

[↑ Go to TOC](#table-of-contents)

## Hardening Flags (Examples)

```bash
podman run --read-only --tmpfs /tmp <image>  # read-only root FS + writable temp
```

[↑ Go to TOC](#table-of-contents)

## SELinux (Fedora/RHEL)

- bind mount with `:Z` (private) or `:z` (shared)

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
