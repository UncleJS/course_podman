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
sudo dnf install -y podman  # install Podman
```

RHEL (package availability depends on subscription/repos):

```bash
sudo dnf install -y podman  # install Podman
```

Verify:

```bash
podman --version  # show Podman version
podman info  # show Podman host configuration
```

Record your versions (useful for debugging later):

```bash
podman --version  # show Podman version
rpm -q podman 2>/dev/null || true  # show installed package version
uname -r  # show kernel/system info
```

## cgroups v2 Check (Required)

Quadlet requires cgroups v2.

Check:

```bash
podman info --format '{{.Host.CgroupsVersion}}'  # show Podman host configuration
```

Expected: `v2`

## Rootless Prereqs

Rootless Podman uses user namespaces. Your user typically needs subuid/subgid ranges.

Check:

```bash
grep "^$USER:" /etc/subuid /etc/subgid  # filter output
```

If those are missing, create them (example range; coordinate with your admin policy):

```bash
sudo usermod --add-subuids 100000-165535 --add-subgids 100000-165535 "$USER"  # grant subuid/subgid range for rootless
```

Log out and back in after updating subuids/subgids.

## SELinux Quick Check (Fedora/RHEL)

SELinux is usually enabled on these systems. You do not need to understand the full policy model, but you should recognize when it affects bind mounts.

Check status:

```bash
getenforce  # show SELinux mode
```

If SELinux is Enforcing, prefer:

- named volumes for data
- bind mounts with `:Z` (private) or `:z` (shared)

## First Container

```bash
podman run --rm docker.io/library/alpine:latest uname -a  # run a container
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
mkdir -p ~/course_podman-labs  # create directory
cd ~/course_podman-labs  # change directory
```

## Recommended Shell Safety

These are optional but reduce accidents:

```bash
set -o noclobber  # prevent overwriting files with redirects
```

Do not run this in shells where it would surprise you; it changes redirect behavior.

## Checkpoint

- `podman info` runs without errors.
- `podman run --rm ...` works rootless.
- cgroups version reports `v2`.

## Further Reading

- Podman install docs: https://podman.io/docs/installation
- Rootless Podman tutorial: https://github.com/containers/podman/blob/main/docs/tutorials/rootless_tutorial.md
- cgroups v2 (kernel docs): https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html
- `loginctl` (linger for user services): https://www.freedesktop.org/software/systemd/man/latest/loginctl.html
- SELinux with containers (RHEL docs): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/using_selinux/assembly_using-selinux-with-containers_using-selinux
