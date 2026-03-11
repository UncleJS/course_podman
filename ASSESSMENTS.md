# Assessments
[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](./LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

These assessments focus on practical skills.

<a id="table-of-contents"></a>

## Table of Contents

- [Module Checkpoints](#module-checkpoints)
- [Practical Exam A (Mid-Course)](#practical-exam-a-mid-course)
- [Practical Exam B (Final)](#practical-exam-b-final)

## Module Checkpoints

Each module ends with a checkpoint. Treat it as "must be able to do without notes".

[↑ Go to TOC](#table-of-contents)

## Practical Exam A (Mid-Course)

Scenario:

- You are given a container that exits immediately.

Requirements:

- Determine why it exits.
- Fix it without rebuilding the image.
- Provide a short runbook: commands used, what you observed, final fix.

Rubric:

- Uses `podman ps -a`, `podman logs`, `podman inspect` effectively.
- Fix is minimal and reproducible.
- No secrets printed.

[↑ Go to TOC](#table-of-contents)

## Practical Exam B (Final)

Scenario:

- You are given a two-service stack: web + db.
- The stack must survive reboot.

Requirements:

- Use Quadlet (systemd user service) to run both services.
- Use a named volume for state.
- Use a secret mounted as a file (not env vars).
- DB is private; only web is published.
- Provide backup + restore steps.

Rubric:

- Rootless and reboot-safe (linger configured if required).
- Correct storage and networking.
- Secrets handled safely.
- Clear, testable runbook.

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
