# Quadlet Cheat Sheet

## Files

- put Quadlet files in: `~/.config/containers/systemd/`
- common extensions: `.container`, `.pod`, `.network`, `.volume`

## Workflow

```bash
systemctl --user daemon-reload  # regenerate units from files
systemctl --user start <name>.service  # start a user service
systemctl --user status <name>.service  # show service status
journalctl --user -u <name>.service -n 100 --no-pager  # view user-service logs
```

## Boot Start

```bash
sudo loginctl enable-linger "$USER"        # allow user services to start at boot
systemctl --user enable <name>.service     # enable the service for your user
```

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
