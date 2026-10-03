# Glossary
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](./LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [Terms](#terms)

## Terms

- container: a running (or stopped) instance of an image with its own writable layer and runtime config
- image: an OCI artifact composed of layers + config; used as a template for containers
- OCI: Open Container Initiative. The image, runtime, and distribution specs that let Podman images run on other OCI tools
- registry: a service that stores and distributes images
- tag: a movable name that points to an image (example: `:latest`)
- digest: a content-addressed identifier for an image (example: `@sha256:...`)
- rootless: running Podman as a normal user using user namespaces
- Quadlet: systemd integration that generates service units from `.container`, `.pod`, `.kube`, `.image`, `.volume`, and `.network` files
- pod: a group of containers that share a network namespace (and usually localhost). Quadlet `.pod` files describe one
- Secret=: Quadlet key that mounts a Podman secret as a file (default `/run/secrets/<name>`), not as an environment variable
- SELinux: a Linux MAC system; on Fedora/RHEL it can affect mounts and container permissions
- namespace: a Linux kernel isolation feature; containers commonly use PID, mount, and network namespaces
- cgroups v2: the kernel resource-control mechanism used for CPU/memory limits and systemd integration
- user namespace: a namespace that remaps UIDs/GIDs; enables rootless containers to have "root" inside without host root
- subuid/subgid: per-user UID/GID ranges used for user namespace mappings (rootless)
- writable layer: the per-container filesystem layer on top of the image; it is not durable persistence
- volume: Podman-managed persistent storage intended for stateful data
- tmpfs: an in-memory filesystem. Used for scratch paths and for secret files that must not hit the writable layer
- bind mount: a host path mounted into a container; often used for config and source code
- network (user-defined): a named bridge network with DNS enabled for container name resolution
- aardvark-dns: Podman’s embedded DNS service for user-defined networks
- netavark: Podman’s networking stack used to configure networks and DNS (modern Podman)
- slirp4netns: the previous default rootless network helper. Still used when `default_rootless_network_cmd` is set to it
- pasta: the Podman 5 / RHEL 10 default rootless network helper. It connects the rootless network namespace to the host. Check with `podman info --format '{{.Host.RootlessNetworkCmd}}'`
- healthcheck: an image or runtime-defined command that reports container health. With Quadlet `Notify=healthy`, a failed healthcheck fails the systemd start so auto-update can roll back
- AutoUpdate: Quadlet key (`AutoUpdate=registry` or `local`) that labels a container for `podman auto-update`. A digest-pinned `Image=` has nothing to move
- seccomp: syscall filter. Podman's default profile denies by default and allows a few hundred common syscalls
- linger: systemd feature that allows user services to run at boot without an interactive login

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
