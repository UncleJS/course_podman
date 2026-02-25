# Module 7: Pods and Sidecars

<a id="table-of-contents"></a>

## Table of Contents

- [Learning Goals](#learning-goals)
- [Why Pods](#why-pods)
- [Infra Container](#infra-container)
- [Lab: Two Containers, One Pod](#lab-two-containers-one-pod)
- [Pod Lifecycle Notes](#pod-lifecycle-notes)
- [Checkpoint](#checkpoint)
- [Quick Quiz](#quick-quiz)
- [Further Reading](#further-reading)

Podman pods group multiple containers so they share certain namespaces (especially networking).


[↑ Go to TOC](#table-of-contents)

## Learning Goals

- Explain what a Podman pod is and when to use it.
- Run a pod with multiple containers.
- Understand the "sidecar" pattern.
- Know what the infra container is.


[↑ Go to TOC](#table-of-contents)

## Why Pods

Pods are useful when:

- multiple containers need to share localhost networking
- you want a unit of deployment smaller than a full orchestrator

They are not required for most workloads. Use them when they simplify your stack.


[↑ Go to TOC](#table-of-contents)

## Infra Container

Pods include an "infra" container that holds the shared namespaces.

You will often see it in `podman ps` for a pod.


[↑ Go to TOC](#table-of-contents)

## Lab: Two Containers, One Pod

1) Create a pod and publish a port:

```bash
podman pod create --name webpod -p 8080:80  # create a pod
```

List pods:

```bash
podman pod ps  # list pods
podman ps --pod  # list containers
```

2) Run an HTTP server inside the pod:

```bash
podman run -d --pod webpod --name nginx docker.io/library/nginx:stable  # run a container
```

3) Add a "debug sidecar" container in the same pod:

```bash
podman run -it --rm --pod webpod docker.io/library/alpine:latest sh  # run a container
```

Inside the sidecar, verify you can reach nginx on localhost:

```sh
wget -qO- http://127.0.0.1:80/ | head  # fetch a URL
exit  # exit the shell
```

4) Cleanup:

```bash
podman pod rm -f webpod  # stop and remove the pod and its containers
```


[↑ Go to TOC](#table-of-contents)

## Pod Lifecycle Notes

- Stopping a pod stops all containers.
- Removing a pod removes the infra container too.


[↑ Go to TOC](#table-of-contents)

## Checkpoint

- You can use a sidecar for debugging without exposing new ports.
- You understand pods are not Kubernetes, but the idea rhymes.


[↑ Go to TOC](#table-of-contents)

## Quick Quiz

1) Why does a pod show an extra container?

2) When would you prefer a network over a pod?


[↑ Go to TOC](#table-of-contents)

## Further Reading

- `podman-pod(1)`: https://docs.podman.io/en/latest/markdown/podman-pod.1.html
- Kubernetes Pods concept: https://kubernetes.io/docs/concepts/workloads/pods/
- Sidecar containers (Kubernetes): https://kubernetes.io/docs/concepts/workloads/pods/sidecar-containers/


[↑ Go to TOC](#table-of-contents)

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
