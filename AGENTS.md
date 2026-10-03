# Agent instructions — course_podman

This repository is a self-paced Podman training course (Markdown modules + generated slides/PDF). There is no application code; "building" means regenerating course artifacts.

## Layout

| Path | Purpose |
|------|---------|
| `modules/` | Course content, one Markdown file per module (source of truth) |
| `cheatsheets/` | Quick references (CLI, Quadlet, rootless, security, troubleshooting) |
| `examples/` | Lab files referenced by modules: Containerfiles, Quadlet units, kube YAML, systemd units, stack script |
| `slides/` | Generated ODP decks — do not hand-edit; regenerate via `scripts/build-slides.sh` |
| `dist/` | Generated combined course (`course_podman.md` + `.pdf`) — do not hand-edit; regenerate via `scripts/build-course-pdf.sh` |
| `scripts/` | Build tooling (containerized; nothing runs on the host except `podman` and POSIX shell) |
| `MODULES.md` | Canonical ordered module list — the PDF build parses this file |

## Module numbering

- `00`–`14`: core sequence, in order.
- `11a`: add-on to Module 11 (Quadlet + secrets).
- `80`: capstone project. `90`: optional elective/survey. The gaps are intentional.

## Builds

- PDF: `scripts/build-course-pdf.sh` — stages the repo into a Podman named volume, assembles `dist/course_podman.md` with containerized Python, renders the PDF with the `pandoc/latex` container.
- Slides: `scripts/build-slides.sh` — runs `scripts/build_slides.py` in a Python container (installs `odfpy` inside the container) and extracts the `.odp` files.
- No bind mounts; named volumes only. No Python/pip on the host.
- After editing any module, rebuild both `dist/` and `slides/` and commit the regenerated artifacts.

## Conventions to preserve

- Every module starts with the title, the CC BY-NC-SA 4.0 + RHEL 10 + Podman badges, then `<a id="table-of-contents"></a>` and a Table of Contents; sections end with `[↑ Go to TOC](#table-of-contents)`.
- Every Markdown file ends with the standard CC BY-NC-SA 4.0 footer. Keep the license consistent everywhere (including `dist/`).
- Mermaid diagrams: quote labels containing special characters, use `<br/>` (not literal `\n`) for line breaks.
- A new module must be added to `MODULES.md` (PDF build input), `COURSE_OUTLINE.md`, and the `SLIDES` list in `scripts/build_slides.py`.
- Target platform is RHEL 10 with rootless Podman + systemd/Quadlet; keep commands and paths consistent with that.
- Timestamps/dates in content use `yyyy-MM-dd`.

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
