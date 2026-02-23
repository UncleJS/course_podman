# Module 9: Multi-Service Workflows

This module teaches patterns for running a small stack without jumping straight to a full orchestrator.

## Learning Goals

- Choose between: separate containers, a user-defined network, or a pod.
- Build a repeatable "stack up / stack down" workflow.
- Know the tradeoffs of compose-style tooling.
- Know how to persist data and keep DB private.

## Patterns

1) User-defined network + multiple containers

- Good default for small stacks.
- Clear service discovery (names on the network).

2) Pod (shared localhost)

- Great when sidecars need to hit `127.0.0.1`.

3) Kube YAML locally (`podman play kube`)

- Good when you want the YAML shape.
- Not the full Kubernetes API.

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
bash examples/stack/stack.sh up
bash examples/stack/stack.sh status
bash examples/stack/stack.sh down
```

## Compose-ish Tooling (Context)

If your team already uses compose files, you may encounter helper tools.

Key rule for this course:

- Learn the primitives first (networks, volumes, pods, Quadlet).

If your org already standardized on compose files:

- treat compose as a convenient wrapper
- still learn how it maps to networks/volumes/secrets so you can debug it

## Checkpoint

- You can stand up and tear down a small stack predictably.
- You can explain when you would reach for `podman play kube`.

## Quick Quiz

1) Why should your DB usually not publish a port to the host?

2) What makes a stack script "safe" to run repeatedly?
