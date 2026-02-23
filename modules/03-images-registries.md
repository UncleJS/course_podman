# Module 3: Images and Registries

## Learning Goals

- Pull images by tag and by digest.
- Understand why digests are safer than tags.
- Inspect image metadata (entrypoint/cmd, exposed ports, labels).
- Understand short-name resolution and why fully qualified names matter.

## Tags vs Digests

- A tag (like `:latest`) is a name that can move.
- A digest (like `@sha256:...`) is content-addressed and does not move.

For production, prefer digests.

## Fully Qualified Image Names

Prefer:

- `docker.io/library/alpine:latest`

Avoid relying on ambiguous short names:

- `alpine:latest`

Reason:

- Short-name resolution rules can vary by system policy.
- Fully qualified names are more predictable in automation.

## Lab: Pull by Tag, Record Digest

```bash
podman pull docker.io/library/alpine:latest
podman images | grep alpine
podman inspect docker.io/library/alpine:latest | less
```

Find the digest and re-pull by digest:

```bash
podman images --digests | grep alpine
```

Try running by digest once you have it:

```bash
podman run --rm docker.io/library/alpine@sha256:<digest> echo ok
```

## Registry Authentication

Login stores credentials for your user:

```bash
podman login <registry>
```

Logout:

```bash
podman logout <registry>
```

Do not put registry credentials in shell history.

## Image Metadata: ENTRYPOINT vs CMD

Many images define an ENTRYPOINT and/or CMD.

- ENTRYPOINT: the default program
- CMD: default arguments

Inspect these fields:

```bash
podman image inspect docker.io/library/nginx:stable --format '{{.Config.Entrypoint}} {{.Config.Cmd}}'
```

Practical implication:

- `podman run <image> <args>` appends or replaces depending on ENTRYPOINT.

## Lab (Optional): Push to a Local Registry

This lab teaches the full pull/build/tag/push flow without needing a real external registry.

1) Start a local registry:

```bash
podman run -d --name registry -p 5000:5000 docker.io/library/registry:2
```

2) Tag an image into the local registry namespace and push it:

```bash
podman pull docker.io/library/alpine:latest
podman tag docker.io/library/alpine:latest localhost:5000/alpine:course
podman push localhost:5000/alpine:course
```

3) Remove your local copy and pull from the local registry:

```bash
podman rmi docker.io/library/alpine:latest
podman rmi localhost:5000/alpine:course
podman pull localhost:5000/alpine:course
```

4) Cleanup:

```bash
podman rm -f registry
```

Note:

- A local registry is not "secure by default". Treat it as a learning tool.

## Lab: Local Tagging

```bash
podman pull docker.io/library/nginx:stable
podman tag docker.io/library/nginx:stable localhost/nginx:course
podman images | grep nginx
```

## Lab (Optional): Save and Load

This teaches portable artifacts.

```bash
podman save -o nginx.tar docker.io/library/nginx:stable
podman load -i nginx.tar
```

Note:

- `save/load` are not a registry. They are file-based transport.

## Checkpoint

- You can explain why `:latest` is risky.
- You can find and record an image digest.

## Quick Quiz

1) If you deploy by tag, what can change without you changing your config?

2) What is the advantage of a digest in incident response?
