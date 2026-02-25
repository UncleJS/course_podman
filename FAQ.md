# FAQ / Gotchas

This file collects common failure modes and the fastest fixes.

## Rootless: "permission denied" publishing port 80

Rootless users typically cannot bind ports below 1024.

Fix options:

- Use a high port (recommended for labs): `-p 8080:80`
- If you own the system, lower the unprivileged port start:

```bash
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80  # allow low ports for rootless (system-wide)
```

See: `modules/06-networking.md`

## Container name DNS does not work

Container DNS names work on user-defined networks (DNS enabled), not on the default network.

Fix:

```bash
podman network create appnet  # create a network
podman run --network appnet ...  # run a container
```

See: `modules/06-networking.md`

## SELinux: bind mounts fail with permission denied (Fedora/RHEL)

If SELinux is enforcing, bind mounts may require labels.

Fix patterns:

- Private mount: `-v ./dir:/mnt:Z`
- Shared mount: `-v ./dir:/mnt:z`

See: `modules/05-storage.md`

## Local registry lab fails with TLS/HTTPS errors

Some Podman configs treat an HTTP registry as insecure and require explicit configuration.

For the learning lab only:

```bash
podman push --tls-verify=false localhost:5000/alpine:course  # push an image to a registry
```

See: `modules/03-images-registries.md`

## HEALTHCHECK missing after build

Podman warns that `HEALTHCHECK` metadata is not stored in the OCI image format.

Fix options:

- Build in docker format when you need the healthcheck stored in the image:

```bash
podman build --format docker -t localhost/myapp:1 .  # build an image
```

- Or define a runtime healthcheck using `podman run --health-*` flags.

See: `modules/08-building-images.md`, `examples/build/hello-bun/README.md`

## `exec format error`

This almost always means an architecture mismatch (built for amd64, running on arm64, or vice versa).

Fix:

- Build on the target architecture, or
- Use a platform-aware build workflow (advanced topic)

See: `modules/08-building-images.md`, `examples/build/hello-go/README.md`

## Quadlet service does not exist after adding a file

Quadlet units are generated at reload time.

Fix:

```bash
systemctl --user daemon-reload  # regenerate units from files
systemctl --user status <unit>  # show service status
```

See: `modules/11-quadlet.md`

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
