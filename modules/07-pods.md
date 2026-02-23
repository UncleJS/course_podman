# Module 7: Pods and Sidecars

Podman pods group multiple containers so they share certain namespaces (especially networking).

## Learning Goals

- Explain what a Podman pod is and when to use it.
- Run a pod with multiple containers.
- Understand the "sidecar" pattern.
- Know what the infra container is.

## Why Pods

Pods are useful when:

- multiple containers need to share localhost networking
- you want a unit of deployment smaller than a full orchestrator

They are not required for most workloads. Use them when they simplify your stack.

## Infra Container

Pods include an "infra" container that holds the shared namespaces.

You will often see it in `podman ps` for a pod.

## Lab: Two Containers, One Pod

1) Create a pod and publish a port:

```bash
podman pod create --name webpod -p 8080:80
```

List pods:

```bash
podman pod ps
podman ps --pod
```

2) Run an HTTP server inside the pod:

```bash
podman run -d --pod webpod --name nginx docker.io/library/nginx:stable
```

3) Add a "debug sidecar" container in the same pod:

```bash
podman run -it --rm --pod webpod docker.io/library/alpine:latest sh
```

Inside the sidecar, verify you can reach nginx on localhost:

```sh
wget -qO- http://127.0.0.1:80/ | head
exit
```

4) Cleanup:

```bash
podman pod rm -f webpod
```

## Pod Lifecycle Notes

- Stopping a pod stops all containers.
- Removing a pod removes the infra container too.

## Checkpoint

## Checkpoint

- You can use a sidecar for debugging without exposing new ports.
- You understand pods are not Kubernetes, but the idea rhymes.

## Quick Quiz

1) Why does a pod show an extra container?

2) When would you prefer a network over a pod?
