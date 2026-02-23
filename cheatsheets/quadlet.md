# Quadlet Cheat Sheet

## Files

- put Quadlet files in: `~/.config/containers/systemd/`
- common extensions: `.container`, `.pod`, `.network`, `.volume`

## Workflow

```bash
systemctl --user daemon-reload
systemctl --user start <name>.service
systemctl --user status <name>.service
journalctl --user -u <name>.service -n 100 --no-pager
```

## Boot Start

```bash
sudo loginctl enable-linger "$USER"
systemctl --user enable <name>.service
```
