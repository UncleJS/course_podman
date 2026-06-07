# Podman Zero-to-Expert Course (Draft)

This is a course-in-a-repo for taking a learner from zero container knowledge to running rootless Podman services with systemd (Quadlet), with strong security and troubleshooting fundamentals.

[![CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey)](LICENSE.md)
[![RHEL 10](https://img.shields.io/badge/platform-RHEL%2010-red)](https://access.redhat.com/products/red-hat-enterprise-linux)
[![Podman](https://img.shields.io/badge/Podman-rootless-purple)](https://podman.io)

<a id="table-of-contents"></a>

## Table of Contents

- [How To Use This Repo](#how-to-use-this-repo)
- [Structure](#structure)
- [Safety](#safety)
- [Conventions](#conventions)
- [Suggested Pacing](#suggested-pacing)
- [License](#license)

## How To Use This Repo

- Read the modules in `modules/` in order.
- Do the labs as you go; each module includes a small checklist.
- Keep everything rootless unless the module explicitly says otherwise.

[↑ Go to TOC](#table-of-contents)

## Structure

- `COURSE_OUTLINE.md`: the full syllabus and learning goals
- `MODULES.md`: reading order
- `modules/`: lesson content (Markdown)
- `cheatsheets/`: quick references (see below)
- `examples/`: example YAML and unit files
- `ASSESSMENTS.md`: practical exams and rubrics
- `FAQ.md`: common gotchas and fast fixes

Module numbering:

- `00`–`14`: the core sequence, read in order.
- `11a`: an add-on to Module 11 (secrets with Quadlet + systemd).
- `80`: the capstone project; `90`: an optional elective/survey. The gaps are intentional — they separate the core sequence from the capstone and electives.

Suggested path:

- Start with `modules/00-setup.md`
- Continue in numeric order

Cheatsheets (use alongside the modules, and as a post-course reference):

- [`cheatsheets/podman-cli.md`](cheatsheets/podman-cli.md): everyday `podman` commands (pairs with Modules 02–03)
- [`cheatsheets/rootless.md`](cheatsheets/rootless.md): rootless-specific paths, ranges, and gotchas (Modules 00–01, 05–06)
- [`cheatsheets/quadlet.md`](cheatsheets/quadlet.md): Quadlet unit keys and systemd workflow (Modules 11/11a, 14)
- [`cheatsheets/security.md`](cheatsheets/security.md): hardening flags and SELinux labels (Module 12)
- [`cheatsheets/troubleshooting.md`](cheatsheets/troubleshooting.md): symptom → diagnosis → fix tables (Module 13)

[↑ Go to TOC](#table-of-contents)

## Safety

- Prefer rootless Podman.
- Never put secret material in images, unit files, or logs.
- If you are on a shared system, treat this repo's lab values as examples only.

[↑ Go to TOC](#table-of-contents)

## Conventions

- Secrets are delivered as files mounted at runtime (not environment variables).
- Production baseline uses rootless Podman + systemd user services (Quadlet-first).

[↑ Go to TOC](#table-of-contents)

## Suggested Pacing

See `COURSE_OUTLINE.md` for rough time estimates per module.

[↑ Go to TOC](#table-of-contents)


# License

This project is licensed under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0).

https://creativecommons.org/licenses/by-nc-sa/4.0/

[↑ Go to TOC](#table-of-contents)

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
