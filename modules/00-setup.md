# Module 0: Setup (Fedora/RHEL + systemd)

This course targets Fedora/RHEL-like systems with systemd, using rootless Podman.

## Learning Goals

- Install Podman and verify basic functionality.
- Confirm your system supports rootless containers (subuid/subgid).
- Know where logs and state live for rootless Podman.
- Confirm cgroups v2 is enabled (required for Quadlet).
- Set up a lab workspace and a few safety defaults.

## Install

Fedora:

```bash
sudo dnf install -y podman
```

RHEL (package availability depends on subscription/repos):

```bash
sudo dnf install -y podman
```

Verify:

```bash
podman --version
podman info
```

Record your versions (useful for debugging later):

```bash
podman --version
rpm -q podman 2>/dev/null || true
uname -r
```

## cgroups v2 Check (Required)

Quadlet requires cgroups v2.

Check:

```bash
podman info --format '{{.Host.CgroupsVersion}}'
```

Expected: `v2`

## Rootless Prereqs

Rootless Podman uses user namespaces. Your user typically needs subuid/subgid ranges.

Check:

```bash
grep "^$USER:" /etc/subuid /etc/subgid
```

If those are missing, create them (example range; coordinate with your admin policy):

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"
```

Log out and back in after updating subuids/subgids.

## SELinux Quick Check (Fedora/RHEL)

SELinux is usually enabled on these systems. You do not need to understand the full policy model, but you should recognize when it affects bind mounts.

Check status:

```bash
getenforce
```

If SELinux is Enforcing, prefer:

- named volumes for data
- bind mounts with `:Z` (private) or `:z` (shared)

## First Container

```bash
podman run --rm docker.io/library/alpine:latest uname -a
```

If this works, you have:

- network access to pull images
- a working storage backend
- a working OCI runtime

## Where Things Live (Rootless)

Common locations:

- Container storage: `~/.local/share/containers/`
- Runtime files: `/run/user/<uid>/containers/`
- Quadlet units: `~/.config/containers/systemd/`

Logs:

- `podman logs <name>` for container logs
- `journalctl --user -u <service>` for Quadlet/systemd logs

## Create a Course Workspace

Pick a working directory for labs:

```bash
mkdir -p ~/course_podman-labs
cd ~/course_podman-labs
```

## Recommended Shell Safety

These are optional but reduce accidents:

```bash
set -o noclobber
```

Do not run this in shells where it would surprise you; it changes redirect behavior.

## Checkpoint

- `podman info` runs without errors.
- `podman run --rm ...` works rootless.
- cgroups version reports `v2`.
