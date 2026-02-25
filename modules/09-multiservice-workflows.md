# Module 9: Multi-Service Workflows

<a id="table-of-contents"></a>

## Table of Contents

- [Learning Goals](#learning-goals)
- [Patterns](#patterns)
- [Lab: A Two-Service Stack (Network + Volumes)](#lab-a-two-service-stack-network-volumes)
- [Make It Repeatable (Script)](#make-it-repeatable-script)
- [Compose-ish Tooling (Context)](#compose-ish-tooling-context)
- [Checkpoint](#checkpoint)
- [Quick Quiz](#quick-quiz)
- [Further Reading](#further-reading)

This module teaches patterns for running a small stack without jumping straight to a full orchestrator.


[↑ Go to TOC](#table-of-contents)

## Learning Goals

- Choose between: separate containers, a user-defined network, or a pod.
- Build a repeatable "stack up / stack down" workflow.
- Know the tradeoffs of compose-style tooling.
- Know how to persist data and keep DB private.


[↑ Go to TOC](#table-of-contents)

## Patterns

1) User-defined network + multiple containers

- Good default for small stacks.
- Clear service discovery (names on the network).

2) Pod (shared localhost)

- Great when sidecars need to hit `127.0.0.1`.

3) Kube YAML locally (`podman play kube`)

- Good when you want the YAML shape.
- Not the full Kubernetes API.


[↑ Go to TOC](#table-of-contents)

## Lab: A Two-Service Stack (Network + Volumes)

Goal:

- DB: private, persistent volume
- App: published port

Checklist:

- Create network `appnet`
- Create volume `dbdata`
- Start DB on `appnet` with `dbdata`
- Start web app on `appnet` and publish 8080
- Confirm web app can resolve DB by container name

Suggested validation steps:

- `podman ps` shows both containers
- `podman network inspect appnet` shows both attached
- DB has no published ports (`podman port <db>` shows nothing)


[↑ Go to TOC](#table-of-contents)

## Make It Repeatable (Script)

Use the provided example:

- `examples/stack/stack.sh`

It demonstrates:

- idempotent create of network/volume
- start/stop with stable names
- separate concerns: infra objects vs containers

Notes:

- The script uses Podman secrets and prompts for a DB password if missing.
- Treat it as a learning tool, not a production deploy mechanism.

Run:

```bash
bash examples/stack/stack.sh up  # run a shell script
bash examples/stack/stack.sh status  # run a shell script
bash examples/stack/stack.sh down  # run a shell script
```


[↑ Go to TOC](#table-of-contents)

## Compose-ish Tooling (Context)

If your team already uses compose files, you may encounter helper tools.

Key rule for this course:

- Learn the primitives first (networks, volumes, pods, Quadlet).

If your org already standardized on compose files:

- treat compose as a convenient wrapper
- still learn how it maps to networks/volumes/secrets so you can debug it


[↑ Go to TOC](#table-of-contents)

## Checkpoint

- You can stand up and tear down a small stack predictably.
- You can explain when you would reach for `podman play kube`.


[↑ Go to TOC](#table-of-contents)

## Quick Quiz

1) Why should your DB usually not publish a port to the host?

2) What makes a stack script "safe" to run repeatedly?


[↑ Go to TOC](#table-of-contents)

## Further Reading

- `podman-network(1)`: https://docs.podman.io/en/latest/markdown/podman-network.1.html
- `podman-pod(1)`: https://docs.podman.io/en/latest/markdown/podman-pod.1.html
- `podman-play-kube(1)`: https://docs.podman.io/en/latest/markdown/podman-play-kube.1.html
- Compose Specification (for mapping concepts): https://compose-spec.io/


[↑ Go to TOC](#table-of-contents)

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
