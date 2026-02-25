# Module 13: Troubleshooting and Ops

This module is about turning "it doesn't work" into a short checklist.

## Learning Goals

- Diagnose startup failures quickly.
- Know where to look: logs, inspect, events, journald.
- Debug networking and storage issues.
- Do failure drills and recover.

## The Debug Loop

1) Confirm container state:

```bash
podman ps -a  # state, exit codes, recent failures
```

2) Read logs:

```bash
podman logs <name>  # app output / crash reason
```

3) Inspect config:

```bash
podman inspect <name> | less  # ports, mounts, env, command
```

4) Reproduce interactively:

```bash
podman run --rm -it <image> sh  # reproduce interactively
```

If the container exits too fast to exec into it:

- run the same image with an interactive shell
- or override command to `sleep 3600` and then `exec` in

## More Tools

Events (what Podman is doing):

```bash
podman events  # see Podman lifecycle events
```

Live resource stats:

```bash
podman stats  # live CPU/mem/io stats
```

Show processes in a container:

```bash
podman top <name>  # processes inside the container
```

Disk usage:

```bash
podman system df  # disk usage summary
```

Cleanup (be careful on shared systems):

```bash
podman system prune  # remove unused objects (be careful)
```

## Failure Drills (With Expected Observations)

Do these on purpose; they make you faster in real incidents.

1) Port conflict

- symptom: container fails to start, error mentions bind/listen
- check: `podman port <name>` or the error in logs
- fix: change host port

2) Bad command

- symptom: container exits immediately with non-zero
- check: `podman logs <name>` shows "not found" or usage
- fix: correct command/entrypoint/args

3) Permissions

- symptom: "permission denied" writing to mounted path
- check: `podman inspect <name> --format '{{json .Mounts}}'`
- fix: prefer volume or correct ownership in user namespace; add `:Z` for bind mounts on Fedora/RHEL

4) DNS

- symptom: app cannot resolve service name
- check: `podman network inspect <net>`; run a debug container and `getent hosts <name>`
- fix: ensure both containers are on the same user-defined network

## systemd/Quadlet Troubleshooting

Check status:

```bash
systemctl --user status <service>  # systemd view: active/failed
```

Logs:

```bash
journalctl --user -u <service> -n 200 --no-pager  # service logs from journald
```

Reload after unit changes:

```bash
systemctl --user daemon-reload           # reload unit changes
systemctl --user restart <service>       # restart the service
```

## Networking Checklist

- Is the port published to the host?
- Is the service listening on the expected interface?
- Are containers on the same network?
- Does DNS resolve container names?

## Storage Checklist

- Is the correct volume mounted?
- Are permissions correct for the container user?
- On Fedora/RHEL: is SELinux labeling correct (`:Z`/`:z`)?

## Failure Drills (Do These)

1) Port conflict

- start a service on 8080
- try to start another service on 8080
- fix by changing published port

2) Permission denied

- mount a directory your container cannot write
- fix with ownership/permissions or a different storage approach

3) Bad image tag

- deploy with a tag that gets replaced upstream
- fix by pinning to digest

## Checkpoint

- You can debug a failed service without guessing.
- You have a repeatable recovery flow.

## Quick Quiz

1) What is the difference between `podman logs` and `journalctl --user -u ...`?

2) What do you do when a container exits too quickly to exec into it?

## Further Reading

- `podman-events(1)`: https://docs.podman.io/en/latest/markdown/podman-events.1.html
- `podman-stats(1)`: https://docs.podman.io/en/latest/markdown/podman-stats.1.html
- systemd journalctl: https://www.freedesktop.org/software/systemd/man/latest/journalctl.html
- `systemd-analyze(1)` (verify, generators): https://www.freedesktop.org/software/systemd/man/latest/systemd-analyze.html

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
