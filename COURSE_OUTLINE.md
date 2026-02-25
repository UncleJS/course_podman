# Course Outline

Goal: take an absolute beginner to an operator who can build, run, secure, and troubleshoot rootless Podman workloads, including systemd (Quadlet) production patterns.

Assumptions:

- Learners have basic command line familiarity by the end of Module 2.
- Labs target Fedora/RHEL-like systems with systemd. Where commands differ across distros, modules call it out.

## Modules

0. Setup (install, rootless prerequisites, verification)
1. Containers 101 (images vs containers, OCI, rootless)
2. Everyday Podman commands (`run`, `exec`, `logs`, lifecycle)
3. Images and registries (tags vs digests, inspect, provenance basics)
4. Secrets (local-first with Podman secrets; rotation patterns)
5. Storage basics (volumes, bind mounts, permissions, SELinux notes)
6. Networking (ports, DNS, user-defined networks)
7. Pods and sidecars (Podman pods, shared network namespace)
8. Building images (Containerfiles, multi-stage, non-root)
9. Multi-service workflows (scripted, compose-ish patterns, `play kube` preview)
10. `podman play kube` (Kubernetes YAML locally, parity concepts; YAML secrets caveats)
11. Production baseline: systemd + Quadlet (rootless services, restart, upgrades; secrets add-on)
11a. Quadlet secrets add-on (runtime file secrets + rotation)
12. Security deep dive (capabilities, seccomp/SELinux, read-only FS)
13. Troubleshooting and ops (events, logs, journald, failure drills)
14. Maintenance and auto-updates (policy, `podman auto-update`, safe rollouts)
80. Capstone (Quadlet stack with secrets, backups, upgrades, rollback)
90. External secrets survey (thorough intro; optional implementation paths)

## Suggested Pacing (Rough Estimates)

These are rough time boxes for a first pass (reading + doing the labs).

- Module 0: 30-60 min
- Module 1: 30-45 min
- Module 2: 60-90 min
- Module 3: 60-90 min
- Module 4: 60-90 min
- Module 5: 60-90 min
- Module 6: 2-3 hours
- Module 7: 45-60 min
- Module 8: 2-3 hours
- Module 9: 60-90 min
- Module 10: 45-75 min
- Module 11: 2-3 hours
- Module 11a: 45-75 min
- Module 12: 60-120 min
- Module 13: 60-120 min
- Module 14: 45-75 min
- Module 80 (Capstone): 3-6 hours
- Module 90 (Survey): 45-90 min

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
