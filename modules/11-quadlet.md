# Module 11: Production Baseline (systemd + Quadlet)

Quadlet lets you define containers/pods as declarative unit files that systemd manages.

## Learning Goals

- Manage containers with systemd user services.
- Use Quadlet `.container`, `.pod`, `.network`, and `.volume` units.
- Make services reboot-safe with predictable restarts.
- Debug generator failures quickly.

## Why Quadlet

- It is the most "Linux-native" way to operate Podman services.
- systemd gives you restart policies, ordering, logs, and boot integration.

## Boot Safety (Rootless)

If you want user services to start on boot:

```bash
sudo loginctl enable-linger "$USER"
```

## Where Quadlet Files Live

- `~/.config/containers/systemd/`

systemd generates units from these files.

## How "Enable" Works for Quadlet

Quadlet units are generated at daemon-reload time.

- You generally do not rely on `systemctl enable` for generated units.
- Instead, include an `[Install]` section in the Quadlet file (like `WantedBy=default.target`).
- After `systemctl --user daemon-reload`, systemd will have the symlinks it needs.

If you remove a Quadlet file, you must reload systemd to remove the generated unit.

## Helpful Podman Commands

List discovered Quadlets:

```bash
podman quadlet list
```

Print the resolved Quadlet file:

```bash
podman quadlet print hello-nginx.container
```

## Lab: Your First Quadlet Container

Use the example unit:

- `examples/quadlet/hello-nginx.container`

Install it:

```bash
mkdir -p ~/.config/containers/systemd
cp examples/quadlet/hello-nginx.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start hello-nginx.service
systemctl --user status hello-nginx.service
curl -sS http://127.0.0.1:8081/ | head
```

Stop and disable:

```bash
systemctl --user stop hello-nginx.service
rm -f ~/.config/containers/systemd/hello-nginx.container
systemctl --user daemon-reload
```

Notes:

- The running container name is typically `systemd-<unit>` unless you set `ContainerName=`.
- Quadlet supports many `podman run` flags via `[Container]` keys.

## Lab: Pre-Create a Network and Volume (Quadlet)

Use the example units:

- `examples/quadlet/labnet.network`
- `examples/quadlet/labdata.volume`

Install them:

```bash
mkdir -p ~/.config/containers/systemd
cp examples/quadlet/labnet.network ~/.config/containers/systemd/
cp examples/quadlet/labdata.volume ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start labnet-network.service
systemctl --user start labdata-volume.service
```

Verify objects exist:

```bash
podman network ls | grep labnet
podman volume ls | grep labdata
```

Cleanup:

```bash
systemctl --user stop labnet-network.service || true
systemctl --user stop labdata-volume.service || true
rm -f ~/.config/containers/systemd/labnet.network
rm -f ~/.config/containers/systemd/labdata.volume
systemctl --user daemon-reload
podman network rm labnet 2>/dev/null || true
podman volume rm labdata 2>/dev/null || true
```

Logs:

```bash
journalctl --user -u hello-nginx.service -n 50 --no-pager
```

## Debugging Quadlet Syntax

If systemd cannot find your generated service, the generator may have failed.

Dry-run the generator:

```bash
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun
```

Show generator verification output:

```bash
systemd-analyze --user --generators=true verify hello-nginx.service
```

When debugging:

- confirm your file is in a searched directory
- confirm keys are spelled correctly (unknown keys can break generation)
- start with a minimal unit and add options incrementally

## Dependencies Between Quadlets

Quadlet can translate dependencies written against `.network`/`.volume`/`.container` files.

Pattern:

- define infra objects (`.network`, `.volume`)
- make containers `Requires=` and `After=` those units

This prevents race conditions on boot.

## Upgrades and Rollback

Baseline approach:

- pin images by digest in production
- upgrade by:
  - pulling a new digest
  - updating the Quadlet unit
  - restarting

Rollback is "switch back to previous digest and restart".

Operational note:

- record the previous digest so rollback is fast

## Secrets

Do not store secret material in unit files.

Use:

- Podman secrets (local-first)
- external systems (survey module)

See:

- `modules/11-quadlet-secrets.md`

## Checkpoint

- You can start/stop a container via systemd user services.
- You can find logs in journald.
- You can debug why a unit did not generate.
