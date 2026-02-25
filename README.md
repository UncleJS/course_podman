# Podman Zero-to-Expert Course (Draft)

This is a course-in-a-repo for taking a learner from zero container knowledge to running rootless Podman services with systemd (Quadlet), with strong security and troubleshooting fundamentals.

## How To Use This Repo

- Read the modules in `modules/` in order.
- Do the labs as you go; each module includes a small checklist.
- Keep everything rootless unless the module explicitly says otherwise.

## Structure

- `COURSE_OUTLINE.md`: the full syllabus and learning goals
- `MODULES.md`: reading order
- `modules/`: lesson content (Markdown)
- `cheatsheets/`: quick references
- `examples/`: example YAML and unit files
- `ASSESSMENTS.md`: practical exams and rubrics
- `FAQ.md`: common gotchas and fast fixes

Suggested path:

- Start with `modules/00-setup.md`
- Continue in numeric order

## Safety

- Prefer rootless Podman.
- Never put secret material in images, unit files, or logs.
- If you are on a shared system, treat this repo's lab values as examples only.

## Conventions

- Secrets are delivered as files mounted at runtime (not environment variables).
- Production baseline uses rootless Podman + systemd user services (Quadlet-first).

## Suggested Pacing

See `COURSE_OUTLINE.md` for rough time estimates per module.


# License

This project is licensed under the
Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).

https://creativecommons.org/licenses/by-sa/4.0/
© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
