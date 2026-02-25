# Module 11: Production Baseline (systemd + Quadlet)

<a id="table-of-contents"></a>

## Table of Contents

- [Learning Goals](#learning-goals)
- [Why Quadlet](#why-quadlet)
- [Boot Safety (Rootless)](#boot-safety-rootless)
- [Where Quadlet Files Live](#where-quadlet-files-live)
- [How "Enable" Works for Quadlet](#how-enable-works-for-quadlet)
- [Helpful Podman Commands](#helpful-podman-commands)
- [Lab: Your First Quadlet Container](#lab-your-first-quadlet-container)
- [Lab: Pre-Create a Network and Volume (Quadlet)](#lab-pre-create-a-network-and-volume-quadlet)
- [Debugging Quadlet Syntax](#debugging-quadlet-syntax)
- [Dependencies Between Quadlets](#dependencies-between-quadlets)
- [Upgrades and Rollback](#upgrades-and-rollback)
- [Secrets](#secrets)
- [Checkpoint](#checkpoint)
- [Further Reading](#further-reading)

Quadlet lets you define containers/pods as declarative unit files that systemd manages.


[↑ Go to TOC](#table-of-contents)

## Learning Goals

- Manage containers with systemd user services.
- Use Quadlet `.container`, `.pod`, `.network`, and `.volume` units.
- Make services reboot-safe with predictable restarts.
- Debug generator failures quickly.


[↑ Go to TOC](#table-of-contents)

## Why Quadlet

- It is the most "Linux-native" way to operate Podman services.
- systemd gives you restart policies, ordering, logs, and boot integration.


[↑ Go to TOC](#table-of-contents)

## Boot Safety (Rootless)

If you want user services to start on boot:

```bash
sudo loginctl enable-linger "$USER"  # allow user services to start at boot
```


[↑ Go to TOC](#table-of-contents)

## Where Quadlet Files Live

- `~/.config/containers/systemd/`

systemd generates units from these files.


[↑ Go to TOC](#table-of-contents)

## How "Enable" Works for Quadlet

Quadlet units are generated at daemon-reload time.

- You generally do not rely on `systemctl enable` for generated units.
- Instead, include an `[Install]` section in the Quadlet file (like `WantedBy=default.target`).
- After `systemctl --user daemon-reload`, systemd will have the symlinks it needs.

If you remove a Quadlet file, you must reload systemd to remove the generated unit.


[↑ Go to TOC](#table-of-contents)

## Helpful Podman Commands

List discovered Quadlets:

```bash
podman quadlet list  # list discovered Quadlet definitions
```

Print the resolved Quadlet file:

```bash
podman quadlet print hello-nginx.container  # show the resolved Quadlet file
```


[↑ Go to TOC](#table-of-contents)

## Lab: Your First Quadlet Container

Use the example unit:

- `examples/quadlet/hello-nginx.container`

Install it:

```bash
mkdir -p ~/.config/containers/systemd                   # Quadlet search path
cp examples/quadlet/hello-nginx.container ~/.config/containers/systemd/  # install unit
systemctl --user daemon-reload                          # regenerate units from Quadlet files
systemctl --user start hello-nginx.service              # start the service
systemctl --user status hello-nginx.service             # show status
curl -sS http://127.0.0.1:8081/ | head                  # verify HTTP response
```

Stop and disable:

```bash
systemctl --user stop hello-nginx.service               # stop the service
rm -f ~/.config/containers/systemd/hello-nginx.container  # remove the Quadlet definition file
systemctl --user daemon-reload                          # remove generated unit from systemd
```

Notes:

- The running container name is typically `systemd-<unit>` unless you set `ContainerName=`.
- Quadlet supports many `podman run` flags via `[Container]` keys.


[↑ Go to TOC](#table-of-contents)

## Lab: Pre-Create a Network and Volume (Quadlet)

Use the example units:

- `examples/quadlet/labnet.network`
- `examples/quadlet/labdata.volume`

Install them:

```bash
mkdir -p ~/.config/containers/systemd                   # Quadlet search path
cp examples/quadlet/labnet.network ~/.config/containers/systemd/        # install network unit
cp examples/quadlet/labdata.volume ~/.config/containers/systemd/        # install volume unit
systemctl --user daemon-reload                          # regenerate units
systemctl --user start labnet-network.service           # create network
systemctl --user start labdata-volume.service           # create volume
```

Verify objects exist:

```bash
podman network ls | grep labnet  # list networks
podman volume ls | grep labdata  # list volumes
```

Cleanup:

```bash
systemctl --user stop labnet-network.service || true    # stop unit (ignore if missing)
systemctl --user stop labdata-volume.service || true    # stop unit (ignore if missing)
rm -f ~/.config/containers/systemd/labnet.network   # remove the Quadlet definition file
rm -f ~/.config/containers/systemd/labdata.volume   # remove the Quadlet definition file
systemctl --user daemon-reload                          # regenerate units
podman network rm labnet 2>/dev/null || true        # remove the network object
podman volume rm labdata 2>/dev/null || true        # remove the volume object (data loss)
```

Logs:

```bash
journalctl --user -u hello-nginx.service -n 50 --no-pager  # view user-service logs
```


[↑ Go to TOC](#table-of-contents)

## Debugging Quadlet Syntax

If systemd cannot find your generated service, the generator may have failed.

Dry-run the generator:

```bash
/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun
```

Show generator verification output:

```bash
systemd-analyze --user --generators=true verify hello-nginx.service  # analyze/verify systemd units
```

When debugging:

- confirm your file is in a searched directory
- confirm keys are spelled correctly (unknown keys can break generation)
- start with a minimal unit and add options incrementally


[↑ Go to TOC](#table-of-contents)

## Dependencies Between Quadlets

Quadlet can translate dependencies written against `.network`/`.volume`/`.container` files.

Pattern:

- define infra objects (`.network`, `.volume`)
- make containers `Requires=` and `After=` those units

This prevents race conditions on boot.


[↑ Go to TOC](#table-of-contents)

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


[↑ Go to TOC](#table-of-contents)

## Secrets

Do not store secret material in unit files.

Use:

- Podman secrets (local-first)
- external systems (survey module)

See:

- `modules/11-quadlet-secrets.md`


[↑ Go to TOC](#table-of-contents)

## Checkpoint

- You can start/stop a container via systemd user services.
- You can find logs in journald.
- You can debug why a unit did not generate.


[↑ Go to TOC](#table-of-contents)

## Further Reading

- Quadlet and Podman systemd integration: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- `podman-quadlet(1)`: https://docs.podman.io/en/latest/markdown/podman-quadlet.1.html
- systemd unit basics: https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html
- systemd user services: https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html
- journald: https://www.freedesktop.org/software/systemd/man/latest/journald.html


[↑ Go to TOC](#table-of-contents)

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
