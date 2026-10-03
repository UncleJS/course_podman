# Assessments
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](./LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

These assessments focus on practical skills.

Module checkpoints are ungraded self-checks. Sit **Exam A** after Module 10. Sit **Exam B** after the capstone (Module 80). Module 90 is not examined.

<a id="table-of-contents"></a>

## Table of Contents

- [How grading works](#how-grading-works)
- [Module Checkpoints](#module-checkpoints)
- [Practical Exam A (Mid-Course)](#practical-exam-a-mid-course)
- [Practical Exam B (Final)](#practical-exam-b-final)

## How grading works

Each exam is 20 points. A pass is 14. An A+ is 18 or higher, with every item that says "required" present. Partial credit is allowed on a required item only when the runbook shows the command and the observed result.

[↑ Go to TOC](#table-of-contents)

## Module Checkpoints

Each module ends with a checkpoint. Treat it as "must be able to do without notes". Checkpoints are not graded and are not copied into this file.

[↑ Go to TOC](#table-of-contents)

## Practical Exam A (Mid-Course)

Sit this after Module 10. It covers the debug loop from Modules 02 and 13, plus the rule that a fix does not require a new image.

Scenario:

- You are given a container that exits immediately.

Requirements:

- Determine why it exits.
- Fix it without rebuilding the image.
- Provide a short runbook: commands used, what you observed, final fix.

| Points | What an A+ runbook shows |
|---|---|
| 4 | State first: `podman ps -a` and the exit code, named (0, 125, 126, 127, 137, or 143) |
| 4 | Logs next: `podman logs`, including the case where the error was the `podman run` client and no container exists |
| 4 | Inspect next: the field that explains the failure (command, mounts, or ports) |
| 4 | One change that makes the container stay up, without `podman build` |
| 4 | No secret value printed in the runbook or the terminal transcript |

[↑ Go to TOC](#table-of-contents)

## Practical Exam B (Final)

Sit this after Module 80. It is the capstone checklist, graded. Module 90 is out of scope.

Scenario:

- You are given a two-service stack: web + db.
- The stack must survive reboot.

Requirements:

- Use Quadlet (systemd user service) to run both services.
- Use a named volume for state.
- Use a secret mounted as a file (not env vars).
- DB is private; only web is published, and only on loopback.
- Provide backup + restore steps, including a restore onto a clean volume.
- Record image digests and roll one service back.

| Points | What an A+ stack shows |
|---|---|
| 3 | Rootless units, `Linger=yes`, and `WantedBy=default.target`. No `systemctl --user enable` on a Quadlet unit |
| 3 | Named volume for database state. Data survives container replacement |
| 3 | Secret is a file mount. The value is not in `Environment=`, shell history, or logs |
| 3 | Database has no `PublishPort`. The web port is `127.0.0.1:...` |
| 4 | A logical backup restores onto a clean volume, and a query shows the restored rows |
| 4 | `podman image inspect --format '{{.Digest}}'` is recorded before the change, the unit is pinned with `@sha256:<hex>` once, and rollback returns to that digest |

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
