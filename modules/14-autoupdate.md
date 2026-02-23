# Module 14: Maintenance and Auto-Updates

Auto-updates can be useful, but they are a policy decision.

## Learning Goals

- Understand what Podman auto-update does.
- Configure a Quadlet-managed container for registry-based auto-update.
- Build a safe rollout + rollback plan.

## What Auto-Update Is

Podman auto-update can:

- check for new images in a registry
- pull updates
- restart the systemd unit that runs the container

What it cannot do by itself:

- perform multi-step migrations safely
- coordinate multiple hosts without additional tooling
- guarantee compatibility between versions

## Tags, Digests, and Policy

Auto-update works best with tags (because tags can move).

Digest pinning works best for reproducibility.

Choose intentionally:

- If you need "always latest patch": use a stable tag + auto-update, and invest in monitoring + rollback.
- If you need "always reproducible": pin digests and upgrade with a controlled change.

In regulated environments, digest pinning is often the default.

## Lab: Enable Registry Auto-Update (Single Service)

Use:

- `examples/quadlet/autoupdate-nginx.container`

Install:

```bash
mkdir -p ~/.config/containers/systemd  # create directory
cp examples/quadlet/autoupdate-nginx.container ~/.config/containers/systemd/  # copy file
systemctl --user daemon-reload                   # regenerate units from Quadlet files
systemctl --user start autoupdate-nginx.service  # start the service
```

Run auto-update manually:

```bash
podman auto-update  # pull updates and restart labeled units
```

Watch what changed:

```bash
systemctl --user status autoupdate-nginx.service                 # show status
journalctl --user -u autoupdate-nginx.service -n 100 --no-pager  # view logs
```

On many systems there is also a timer unit you can enable (name varies by distro). If present:

```bash
systemctl --user list-unit-files | grep auto-update  # look for an auto-update timer
```

If a timer exists and you choose to use it, enable it like a normal systemd unit.

## Rollback Plan (Required If You Auto-Update)

Minimum rollback plan:

- know the previous working image reference
- be able to restart the service back to that version
- have monitoring to detect restart loops quickly

If you rely on tags:

- you may need to pin to a specific digest during rollback
- you may need a local cache/registry to keep old versions available

## Safe Rollout Rules

- Prefer digest-pinned images for production unless you explicitly accept the risk.
- If you use auto-update:
  - add healthchecks
  - alert on restart loops
  - document rollback

Treat auto-update as an operational feature, not a convenience hack.

## Checkpoint

- You can explain why auto-update is optional, not mandatory.
- You can trigger and observe an auto-update.

## Quick Quiz

1) Why can auto-update increase risk for stateful services?

2) What must exist before you turn on auto-update in production?

## Further Reading

- `podman-auto-update(1)`: https://docs.podman.io/en/latest/markdown/podman-auto-update.1.html
- systemd timers: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html
- systemd service restart policies: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
