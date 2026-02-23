# Module 6: Networking (Ports, DNS, User-Defined Networks)

## Learning Goals

- Publish container ports to the host.
- Create user-defined networks and connect containers.
- Use container DNS names for service discovery.

## Port Publishing

Run an HTTP server and publish to the host:

```bash
podman run -d --name web1 -p 8080:80 docker.io/library/nginx:stable
curl -sS http://127.0.0.1:8080/ | head
podman rm -f web1
```

Rootless note:

- Publishing low ports (like 80) may require additional system config.
- Use high ports (8080, 8443) in labs.

## Rootless Networking (What To Know)

In rootless mode, Podman typically uses user-mode networking.

Practical implications:

- some protocols behave differently than rootful bridge networking
- performance may differ

If your environment supports it, you may see references to helpers like slirp4netns or pasta.
You do not need to memorize internals, but you should recognize that "rootless networking" is a distinct mode.

Check what Podman is using:

```bash
podman info --format '{{.Host.NetworkBackend}}'
```

## Debug Ports

List how a running container is published:

```bash
podman port <name>
```

Show port publishing in `inspect`:

```bash
podman inspect <name> --format '{{json .NetworkSettings.Ports}}'
```

## User-Defined Networks

Create a network:

```bash
podman network create appnet
podman network ls
```

Run containers on that network:

```bash
podman run -d --name net-a --network appnet docker.io/library/alpine:latest sleep 600
podman run --rm --network appnet docker.io/library/alpine:latest sh -lc 'getent hosts net-a'
podman rm -f net-a
```

Inspect the network:

```bash
podman network inspect appnet | less
```

Cleanup:

```bash
podman network rm appnet
```

## Lab: App Talks to DB Over Private Network

Goal:

- DB is not published to the host.
- App can reach DB by name over a private network.

Checklist:

- Create a user-defined network
- Start DB container on that network (no `-p`)
- Start app container on that network
- Verify app resolves `db` name and can connect

Debug tip:

- use a temporary debug container on the same network to test DNS and TCP connectivity

Example:

```bash
podman run --rm --network appnet docker.io/library/alpine:latest sh -lc 'getent hosts db || true'
```

## Checkpoint

- You can explain "publish to host" vs "private network".
- You can use `podman network create` and container DNS names.

## Quick Quiz

1) Why might a container be reachable from another container but not from the host?

2) What is the first command you run to confirm ports are published correctly?
