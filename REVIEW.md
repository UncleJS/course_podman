# Project Review — 2026-10-03

A pass over every module, example, cheatsheet, exam, and the slide source, checked against Podman 5.8.7 and `podman-systemd.unit(5)` on this host. The teaching sequences that were already right were left in place. The defects below were fixed in this revision.

## Findings

| # | Severity | Area | Finding | Status |
|---|----------|------|---------|--------|
| 1 | High | Modules 00, 01, 12 | Container UID 0 was drawn as the first subuid. It maps to the logged-in UID; subordinate UIDs start at container UID 1 | Resolved |
| 2 | High | Modules 11, 12 | `CapDrop=` / `CapAdd=` are rejected by the Quadlet generator. The keys are `DropCapability=` and `AddCapability=` | Resolved |
| 3 | High | Module 11 | `Restart=unless-stopped` is not a systemd value and the unit fails to load | Resolved |
| 4 | High | Module 06 | `{{.Host.NetworkBackend}}` reports netavark or cni. Pasta vs slirp4netns is `{{.Host.RootlessNetworkCmd}}`, and Podman 5 defaults to pasta | Resolved |
| 5 | High | Capstone units | `capnet` was not internal, Adminer was published on all interfaces, and the backup filename used `${ts}`, which systemd expands to empty | Resolved |
| 6 | High | Module 14 | Rollback was described as a late healthcheck. It follows a failed systemd start, which needs `Notify=healthy` | Resolved |
| 7 | Medium | Modules 02, 03, 04, 05, 08, 10, 13, 90 | Labs and commands that do not do what the text claimed (missing `podman debug`, invalid `registries.conf`, SELinux type, play kube kinds, SOPS recipe, and others) | Resolved |
| 8 | Medium | Modules 06, 08, 13 | Numbered headings used two spaces, so TOC anchors did not match the heading slug | Resolved |
| 9 | Medium | Assessments, cheatsheets, glossary | Exams had no point scale. Security and troubleshooting sheets did not match their README descriptions. Glossary still called pasta optional | Resolved |
| 10 | Low | Slides | A handful of bullets disagreed with the labs (lab path, backend field, 11a service name, capstone backup) | Resolved in `scripts/build_slides.py`; decks regenerated with this revision |

## Verified in this pass

- Quadlet `--dryrun` on this host: `capnet` is created with `--internal`, Adminer publishes `127.0.0.1:8082:8080`, auto-update uses `--sdnotify=healthy`, and the backup `ExecStart` keeps `$$` and `%%` so systemd expands them when the job starts. No `CapDrop=` and no empty `all-.sql`.
- `podman info` on this host reports `NetworkBackend=netavark` and `RootlessNetworkCmd=pasta`. Learner docs point at `RootlessNetworkCmd`.
- Modules 06, 08, and 13 use a single space in numbered headings so the GitHub-style TOC fragments match.
- `dist/course_podman.md` and `dist/course_podman.pdf` were regenerated on 2026-10-03.

## Residual pass (same day)

The Podman 5 and Quadlet fixes above were left in place. This pass closed what that review still had open.

| # | Severity | Area | Finding | Status |
|---|----------|------|---------|--------|
| 11 | Medium | Combined PDF | In-document links missed their targets: em-dash slugs, headings whose ids start with a digit, and repeated titles such as Learning Goals | Resolved in the assembler only. Each source file gets a letter-prefixed heading id, and that file's `](#slug)` links are rewritten to it. Module files are unchanged. The pandoc log from this rebuild reports no undefined references |
| 12 | Medium | Module 9 | The stack lab still created a secret with a literal `printf` password, which lands in shell history | Resolved. The create step uses `read -rs` and `printf '%s' "$p"`, then `unset` |
| 13 | Low | Rootless cheat sheet | The sheet did not mention the UID map, pasta, or the auth file that disappears on reboot | Resolved |
| 14 | Low | Exam A | The rubric scored a container that exits, and the exam never provided one | Resolved. `examples/exams/exam-a.sh` starts it. The prompt does not say why it exits |

`dist/` and `slides/` were regenerated after the Module 9 edit.

## Follow-through (same day)

Labs that failed when followed in order, and slides that disagreed with those labs.

| # | Severity | Area | Finding | Status |
|---|----------|------|---------|--------|
| 15 | Medium | Module 6 | Later port demos reused host port 8080 while `web1` was still up, section 6.2 disconnected a container section 6.1 had already removed, and the section 8 TOC slug dropped a hyphen | Resolved |
| 16 | Medium | Module 7 | The log sidecar mounts nginx's log directory. That image symlinks an empty dir to stdout, so the sidecar never sees an access log | Resolved. Symlinks are replaced with files. `:Z` is omitted on the named volume |
| 17 | Medium | Modules 11, 11a, 14, 80 | nginx verify used `wget` inside an image that has none. Rotation deleted a secret the lab never created. The auto-update intro still described a late healthcheck and `AutoUpdatePolicy=`. The capstone runbook used system `systemctl` and queried MariaDB before it was ready | Resolved |
| 18 | Low | Exams, slides, cheat sheets | Exam A scored a no-container failure its fixture does not create. Exam B said the stack was given. Several slide bullets and three cheat-sheet gaps disagreed with the modules | Resolved |

`dist/` and `slides/` were regenerated after this pass.

## Command mismatches (same day)

A few verify commands still called tools the image does not ship, and a few slide bullets still used short names.

| # | Severity | Area | Finding | Status |
|---|----------|------|---------|--------|
| 19 | Medium | Module 9 | Steps 8 and 9 ran `nc` and `wget` inside Adminer. That PHP image has neither, so the check never printed "DB reachable" | Resolved. Alpine on `stacknet` uses `nc -w 1`. The host uses `curl` on port 8086 |
| 20 | Low | Modules 6, 13 | Section 13.2 and the Module 13 sidecar note still used `nc -zv`, and 13.2 still called `ss` inside images that do not have it. `myapp-net` and `db-internal` were never removed | Resolved |
| 21 | Low | Slides, Module 02 | Lifecycle, Lab 04, Lab 07, and the fully-qualified-name slide still told learners to type short image names | Resolved |

`dist/` and `slides/` were regenerated after this pass.

## Left as written

The tags-vs-digests lesson, the secret threat model, the Quadlet generator explanation, and the Module 13 debug loop were already accurate. They were not rewritten. Module 9's secret create was left as it was; only the Adminer verify commands changed. `examples/stack/stack.sh` only changed its non-interactive hint, which now uses `read -rs`.

---

© 2026 UncleJS — Licensed under CC BY-NC-SA 4.0
