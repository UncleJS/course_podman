# Project Review — 2026-06-07

A full review of the course: structure and consistency, technical accuracy of all 18 modules and examples, and build tooling. Overall verdict: **technically sound and current**. The findings below were identified; all have been resolved in this revision unless marked otherwise.

## Findings

| # | Severity | Area | Finding | Status |
|---|----------|------|---------|--------|
| 1 | High | `AGENTS.md` | Contained generic AI-tooling routing config unrelated to the course | Resolved — replaced with course-specific agent instructions |
| 2 | High | Module numbering | `modules/11-quadlet-secrets.md` shared prefix `11` with `11-quadlet.md`, while `COURSE_OUTLINE.md` called it "11a" | Resolved — renamed to `modules/11a-quadlet-secrets.md`, heading and references updated |
| 3 | Medium | `dist/` | Combined MD (2026-03-02) and PDF (2026-02-25) were stale vs the 2026-03-26 module rewrite; the rebuild also surfaced a latent break: post-rewrite Unicode (≥, ↑, ✅ …) made the pdflatex build fail | Resolved — assembly step now transliterates LaTeX-unfriendly symbols; both artifacts rebuilt |
| 4 | Medium | Slides | No dedicated deck for the Quadlet-secrets add-on (one slide buried in `11-quadlet.odp`) | Resolved — six-slide `11a-quadlet-secrets.odp` deck added to `build_slides.py` |
| 5 | Medium | Build tooling | `build-course-pdf.sh` bind-mounted the repo into the pandoc container and ran host python3; `build_slides.py` required an undeclared host `odfpy` install | Resolved — both builds now stage the repo into a Podman named volume and run python fully containerized (`scripts/build-slides.sh` added); no bind mounts, nothing installed on the host |
| 6 | Medium | Cheatsheets | Five cheatsheets existed but were orphaned — not linked from README/MODULES learning path | Resolved — listed with descriptions in `README.md` and a Quick References section in `MODULES.md` |
| 7 | Low | Module numbering | Gaps 14 → 80 → 90 unexplained | Resolved — numbering scheme documented in `README.md` and `MODULES.md` |
| 8 | Low | Examples | `examples/quadlet/webpod.yaml` publishes host port 8084 vs 8080 in `examples/kube/webpod.yaml`, with no explanation | Resolved — intent (side-by-side labs without port conflict) documented in the YAML and in Module 10 |
| 9 | Low | Module titles | Modules 80/90 titles lack the "Module N:" prefix used by 00–14 | Accepted — "Capstone:" / "External Secrets Survey:" titles communicate their role better than numbers |
| 10 | Low | Build tooling | `build_slides.py` crashed with a bare traceback when `odfpy` was missing | Resolved — actionable error message pointing at the containerized wrapper |

## Verified clean (no action needed)

- **Licensing** — every Markdown file (including `dist/`) consistently carries CC BY-NC-SA 4.0 badges and footers; no leftover BY-SA wording.
- **TOC navigation** — all 18 modules implement the `<a id="table-of-contents">` anchor and `↑ Go to TOC` links; anchors match headings.
- **Mermaid** — 64 diagram blocks scanned; labels quoted, `<br/>` used correctly, no literal `\n`, no render-breaking syntax.
- **Technical accuracy** — Quadlet section names and keys, `AutoUpdate=registry` semantics, secret handling (tmpfs file mounts, no env vars), `CapDrop`/`CapAdd`, SELinux `:Z`/`:z`, cgroups-v2 requirements, and pasta/slirp4netns guidance are all correct and current.
- **Examples** — Containerfiles (multi-stage Go/Bun), Quadlet units, kube YAML, and systemd units are syntactically sound; every example referenced from a module exists, no orphans.
- **Repo hygiene** — no committed secrets/env files; `.gitignore` covers credential patterns; no oversized binaries (largest artifact ~700 KB).
- **Targeting** — RHEL 10 + rootless Podman messaging is consistent across all modules and badges.

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
