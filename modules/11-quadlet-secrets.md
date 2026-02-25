# Module 11 Add-On: Secrets with Quadlet + systemd (Rootless)

This add-on shows how to run reboot-safe services while keeping secret material out of unit files and environment variables.

## Learning Goals

- Run a rootless systemd user service that consumes a secret as a file.
- Keep secret material out of:
  - unit files
  - `Environment=` lines
  - shell history
- Rotate secrets safely with rollback.

## Recommended Pattern

- Store secret material as a Podman secret (local-first).
- Reference the secret by name in the Quadlet unit.
- The container reads from `/run/secrets/<name>`.

Guidelines:

- Treat secret names as part of your deployment config.
- Prefer versioned secret names for rotation (`db_password_v1`, `db_password_v2`).
- Assume many apps only read secrets at startup.

## Lab: Quadlet Unit Consuming a Secret

Prereqs:

- Rootless Podman installed.
- systemd user session available.

If you want this service to start on boot (common for a server), enable lingering for your user:

```bash
sudo loginctl enable-linger "$USER"  # allow user services to start at boot
```

1) Create the secret (example only):

```bash
printf '%s' 'example-password' | podman secret create db_password -  # print text without trailing newline
```

2) Create a Quadlet `.container` unit.

Location (common):

- `~/.config/containers/systemd/`

Example filename:

- `~/.config/containers/systemd/example-app.container`

Example unit skeleton (adjust image/command to your app):

```ini
[Unit]
Description=Example app with secret

[Container]
Image=docker.io/library/busybox:latest
Secret=db_password
Exec=sh -lc 'test -f /run/secrets/db_password && sleep 3600'

[Service]
Restart=always

[Install]
WantedBy=default.target
```

3) Reload and start:

```bash
systemctl --user daemon-reload          # regenerate units from Quadlet files
systemctl --user start example-app.service   # start the service
systemctl --user status example-app.service  # show status
```

4) Verify logs do not contain secret values:

```bash
journalctl --user -u example-app.service -n 50 --no-pager  # view user-service logs
```

## Rotation

Use versioned secret names and update the Quadlet unit to reference the new secret name, then restart.

Rule: do not delete the old secret until the new service instance is verified.

### Rotation Procedure (Template)

1) Create the new secret:

```bash
printf '%s' 'new-value' | podman secret create db_password_v2 -  # print text without trailing newline
```

2) Update the Quadlet file:

- change `Secret=db_password_v1` to `Secret=db_password_v2`

3) Restart:

```bash
systemctl --user daemon-reload               # regenerate units after editing the Quadlet file
systemctl --user restart example-app.service # restart to pick up new secret reference
```

4) Verify behavior:

```bash
systemctl --user status example-app.service                 # show status
journalctl --user -u example-app.service -n 100 --no-pager  # view logs
```

5) Remove the old secret only after verification:

```bash
podman secret rm db_password_v1  # delete the old secret after verification
```

## Further Reading

- `podman-secret(1)`: https://docs.podman.io/en/latest/markdown/podman-secret.1.html
- Quadlet and Podman systemd integration: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- systemd credentials (service-provisioned files): https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html

## Checkpoint

- You can run a Quadlet-managed service that reads a secret from `/run/secrets/...`.
- You can rotate a secret by switching the referenced secret name and restarting.
- You can verify journald logs do not contain secret values.

## Quick Quiz

1) Why is it safer to mount secrets as files than to pass them in environment variables?

2) Why should you keep the old secret around until after verification?

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
