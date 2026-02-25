#!/usr/bin/env python3
"""
build_slides.py — Generate one ODP per module from course content.

Uses the odfpy library (python-odf) to produce valid OpenDocument Presentation
files with a dark theme and full instructor notes on every slide.

Run:
    python3 scripts/build_slides.py
Output (one file per module):
    slides/00-setup.odp
    slides/01-containers-101.odp
    slides/02-everyday-commands.odp
    ... (one file per module + intro + closing)
    slides/podman-course.odp  (full combined deck)
"""

import os
import textwrap
from odf.opendocument import OpenDocumentPresentation
from odf.style import (
    Style, MasterPage, PageLayout, PageLayoutProperties,
    TextProperties, GraphicProperties, DrawingPageProperties,
)
from odf.text import P, Span
from odf.draw import Frame, TextBox, Page
from odf.presentation import Notes
from odf.namespaces import PRESENTATIONNS


# ---------------------------------------------------------------------------
# Colour palette (dark theme)
# ---------------------------------------------------------------------------
BG_DARK      = "#1a1a2e"   # default slide background
BG_SECTION   = "#16213e"   # section title slide bg
BG_LAB       = "#0f3460"   # lab/demo slide bg
ACCENT       = "#e94560"   # headings accent
TEXT_PRIMARY = "#eaeaea"   # body text
TEXT_DIM     = "#a0a0b0"   # secondary text / subtitle
WHITE        = "#ffffff"

SLIDE_W = "25.4cm"
SLIDE_H = "14.29cm"


# ---------------------------------------------------------------------------
# Slide content
# ---------------------------------------------------------------------------

SLIDES = [

    # ──────────────────────────────────────────────────────────────
    # TITLE SLIDE
    # ──────────────────────────────────────────────────────────────
    {
        "module": "intro",
        "type": "title",
        "title": "Podman: Zero to Production",
        "subtitle": "Rootless Containers · systemd · Quadlet · Security",
        "notes": (
            "Welcome everyone. This course takes you from never having typed 'podman' "
            "all the way to running reboot-safe, secret-aware production services on a "
            "Fedora or RHEL system. We use rootless Podman throughout — that means you "
            "never need root to run containers, which is both safer and more practical "
            "for most teams. By the end you will be able to deploy a multi-service stack "
            "that survives reboots, handles secrets securely, and can be upgraded or "
            "rolled back with a documented procedure. Let's get started."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # COURSE OVERVIEW
    # ──────────────────────────────────────────────────────────────
    {
        "module": "intro",
        "type": "content",
        "title": "Course Map",
        "bullets": [
            "Foundations  (Modules 00-03):  setup, concepts, commands, images",
            "Intermediate (Modules 04-07):  secrets, storage, networking, pods",
            "Production   (Modules 08-11):  building images, Quadlet, multi-service",
            "Operations   (Modules 12-14):  security, troubleshooting, auto-updates",
            "Capstone     (Module 80):      full stack with backups & upgrades",
            "Optional     (Module 90):      external secrets survey",
        ],
        "notes": (
            "Here is the shape of the course. We move from the bare minimum to get "
            "Podman running all the way to a production-quality deployment workflow. "
            "Each module has labs — hands-on commands you run yourself. There is also "
            "a capstone project that ties everything together into a reboot-safe stack "
            "with real secrets, backups, and a documented upgrade procedure. "
            "Module 90 on external secrets is optional but recommended if your team "
            "will eventually use Vault or SOPS. Total course time is roughly 30-50 hours "
            "including all labs."
        ),
    },
    {
        "module": "intro",
        "type": "content",
        "title": "What We Cover (and What We Don't)",
        "bullets": [
            "YES:  Single-host rootless Podman on Fedora / RHEL",
            "YES:  systemd integration via Quadlet (production baseline)",
            "YES:  Secrets, volumes, networking, security hardening",
            "YES:  Troubleshooting methodology + failure drills",
            "NO:   Kubernetes / OpenShift orchestration",
            "NO:   CI/CD pipelines (only image build patterns)",
            "NO:   Cloud-provider-specific tooling",
        ],
        "notes": (
            "Be explicit with students about scope. This is a single-host Podman course. "
            "If someone asks how this maps to Kubernetes — the concepts map well "
            "(images, volumes, secrets, health checks) but the tooling is different. "
            "We deliberately skip CI/CD pipelines; the course teaches you how to build "
            "and tag images correctly so that any pipeline can pick them up. "
            "The Quadlet + systemd approach is the Linux-native alternative to Docker Compose "
            "and is the right baseline for RHEL-family systems."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 00 — SETUP
    # ──────────────────────────────────────────────────────────────
    {
        "module": "00-setup",
        "type": "section",
        "title": "Module 00",
        "subtitle": "Setup — Fedora / RHEL + systemd   (30-60 min)",
        "notes": (
            "Module 00 is pure setup. Its only job is to get everyone to a working "
            "rootless Podman before the real learning begins. The three hard blockers "
            "are: cgroups v2 not enabled, missing subuid/subgid ranges, and SELinux "
            "in enforcing mode causing unexpected permission denials. Walk through each "
            "check as a group so no one falls behind."
        ),
    },
    {
        "module": "00-setup",
        "type": "content",
        "title": "Install and Verify",
        "bullets": [
            "sudo dnf install -y podman",
            "podman --version        (record it)",
            "podman info             (verify host config)",
            "podman info --format '{{.Host.CgroupsVersion}}'   must be: v2",
            "cgroups v2 is required for Quadlet — check before anything else",
        ],
        "notes": (
            "On Fedora 40+ and RHEL 9+ cgroups v2 is the default. On older systems "
            "you may need to add systemd.unified_cgroup_hierarchy=1 to the kernel "
            "command line and reboot. Quadlet will not work without cgroups v2, so "
            "this check is mandatory. Record the Podman version now — it is the first "
            "thing to share when filing a bug report or asking for help."
        ),
    },
    {
        "module": "00-setup",
        "type": "content",
        "title": "Rootless Prerequisites",
        "bullets": [
            "grep \"^$USER:\" /etc/subuid /etc/subgid   (need 65536+ UIDs)",
            "If missing:  sudo usermod --add-subuids 100000-165535 $USER",
            "Log out and back in after adding subuid/subgid ranges",
            "SELinux check:  getenforce   (Enforcing is fine — don't disable it)",
            "First container: podman run --rm docker.io/library/alpine:latest uname -a",
        ],
        "notes": (
            "Rootless containers rely on user namespaces. The kernel needs a range of "
            "subordinate UIDs/GIDs mapped to your user so that processes inside the "
            "container can have their own UID space. Without these ranges, Podman will "
            "fail with a cryptic namespace error. The range 100000-165535 gives 65536 "
            "UIDs which is the minimum Podman expects. "
            "SELinux: never tell students to set it to permissive. Instead teach them "
            "the :Z bind-mount label which is covered in Module 05."
        ),
    },
    {
        "module": "00-setup",
        "type": "lab",
        "title": "Lab 00: Workspace Setup",
        "bullets": [
            "mkdir -p ~/course_podman-labs && cd ~/course_podman-labs",
            "podman run --rm docker.io/library/alpine:latest uname -a",
            "Checkpoint: 'podman info' runs without errors",
            "Checkpoint: cgroups version reports v2",
            "Checkpoint: first container runs without sudo",
        ],
        "notes": (
            "Give students 10 minutes for this lab. The most common failure is a "
            "missing network connection to docker.io — if the pull hangs, check proxy "
            "settings or try 'podman pull docker.io/library/alpine:latest' explicitly "
            "to see the error. Second most common: missing subuid entries. Have the "
            "fix command ready on screen. Once everyone has a working uname -a output "
            "from inside a container, the group is ready for Module 01."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 01 — CONTAINERS 101
    # ──────────────────────────────────────────────────────────────
    {
        "module": "01-containers-101",
        "type": "section",
        "title": "Module 01",
        "subtitle": "Containers 101 — Concepts   (30-45 min)",
        "notes": (
            "Module 01 is intentionally conceptual. Resist the urge to rush through it "
            "to get to commands. The mental model built here — image vs container, "
            "namespaces vs cgroups, rootless vs rootful — pays off every time a student "
            "debugs a weird permission issue in module 05 or a network issue in module 06."
        ),
    },
    {
        "module": "01-containers-101",
        "type": "content",
        "title": "Image vs Container vs Registry",
        "bullets": [
            "Image — immutable template (layers + config)",
            "Container — running (or stopped) instance of an image",
            "Registry — where images live (Docker Hub, Quay, internal)",
            "Container has: a process, writable layer, mounts, network settings",
            "The kernel is shared — a container is NOT a VM",
        ],
        "notes": (
            "The 'not a VM' point is crucial and comes up in security discussions later. "
            "A container shares the host kernel. If the kernel has a privilege-escalation "
            "bug and the container is running as root with extra capabilities, that is a "
            "real threat. This is exactly why rootless plus non-root-inside-container matters. "
            "Common analogy: an image is a class definition; a container is an instance. "
            "Deleting the container does not delete the image, just like deleting an object "
            "does not delete the class."
        ),
    },
    {
        "module": "01-containers-101",
        "type": "content",
        "title": "Rootless vs Rootful",
        "bullets": [
            "Rootless: container daemon and processes run as your user account",
            "A breakout gains your user's privileges — not host root",
            "Developers can run containers without handing them sudo",
            "Tradeoff: ports below 1024 need extra setup, UID mapping can confuse",
            "Rule: rootless by default; rootful only when you can explain why",
        ],
        "notes": (
            "This slide is the security foundation of the whole course. Every time "
            "a student asks why they can not just use sudo, refer back here. "
            "The threat model: if an attacker can escape the container (kernel CVE, "
            "misconfigured volume), rootless limits blast radius to your user account "
            "rather than full host root. "
            "For the low-port question: the recommended production pattern is a high port "
            "for the container plus a reverse proxy (nginx, Caddy) in front. This is covered "
            "in Module 06. The sysctl approach is a last resort."
        ),
    },
    {
        "module": "01-containers-101",
        "type": "lab",
        "title": "Lab 01: Compare Host vs Container",
        "bullets": [
            "uname -a                                        (host kernel)",
            "podman run --rm alpine:latest uname -a          (same kernel!)",
            "podman run --rm alpine:latest ps -ef             (tiny process tree)",
            "podman create --name c101 alpine:latest sleep 300",
            "podman inspect c101 | less   (note: image, mounts, network, user)",
            "podman rm c101",
        ],
        "notes": (
            "The key learning moment is the uname output being identical — same kernel "
            "version on host and container. This makes the 'not a VM' point visceral. "
            "The inspect exercise teaches students where to look when debugging: the JSON "
            "blob from podman inspect contains everything Podman knows about a container. "
            "Ask students: what user is the container running as? They should find it "
            "in the Config.User field. If it is empty string, that means root inside "
            "the container — a problem fixed in Module 08."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 02 — EVERYDAY COMMANDS
    # ──────────────────────────────────────────────────────────────
    {
        "module": "02-everyday-commands",
        "type": "section",
        "title": "Module 02",
        "subtitle": "Everyday Podman Commands   (60-90 min)",
        "notes": (
            "Module 02 is muscle memory. Students will type these commands hundreds of "
            "times. The goal is fluency: run, ps, logs, exec, stop, rm — and knowing "
            "when to use each. The writable-layer lab is the single most important "
            "concept in this module: data written to the container filesystem is gone "
            "when the container is removed."
        ),
    },
    {
        "module": "02-everyday-commands",
        "type": "content",
        "title": "Core Lifecycle Commands",
        "bullets": [
            "podman run --rm alpine echo hello             # run and auto-remove",
            "podman run -d --name web nginx:stable         # detached, named",
            "podman ps / podman ps -a                      # list running / all",
            "podman logs web                               # app stdout/stderr",
            "podman exec -it web sh                        # shell inside container",
            "podman stop web / podman rm -f web            # stop / force remove",
        ],
        "notes": (
            "Emphasise --rm for ephemeral containers. Every lab should use --rm "
            "unless you specifically want to inspect the stopped state. Students who "
            "skip --rm end up with dozens of stopped containers clogging podman ps -a. "
            "podman exec -it is the single most-used debug tool. Ask: what do you do "
            "if the container has no shell? Answer: use a sidecar on the same network "
            "(Module 07) or --network container:<name> to share the namespace. "
            "Exit codes: podman inspect --format {{.State.ExitCode}} is how you "
            "programmatically check why a container died."
        ),
    },
    {
        "module": "02-everyday-commands",
        "type": "lab",
        "title": "Lab 02: The Writable Layer Is Not Persistence",
        "bullets": [
            "1.  podman run -it --name scratch alpine sh",
            "    Inside: echo hi > /tmp/hello.txt && exit",
            "2.  podman rm scratch",
            "3.  podman run -it --name scratch alpine sh",
            "    Inside: ls -la /tmp/hello.txt   ->  file is GONE",
            "Key insight: use volumes for anything you need to keep",
        ],
        "notes": (
            "This lab creates a memorable aha moment. Students who have used Docker "
            "with bind mounts may already know this, but it is worth reinforcing. "
            "The correct mental model: the writable layer is scratch space for the container. "
            "It is gone when the container is gone. "
            "Follow up with the naming lab: run two containers with names a1 and a2, "
            "then try to create a third container called a1 — the error teaches why "
            "stable naming matters for scripts and automation."
        ),
    },
    {
        "module": "02-everyday-commands",
        "type": "content",
        "title": "Cleanup Commands",
        "bullets": [
            "podman container prune     # remove all stopped containers",
            "podman image prune         # remove dangling images",
            "podman system df           # see disk usage at a glance",
            "podman system prune        # remove ALL unused objects — use with care",
            "Tip: know what prune will remove before running it",
        ],
        "notes": (
            "Production tip: add podman container prune to a weekly cron/timer to "
            "keep stopped containers from accumulating. podman system prune can "
            "delete unnamed volumes containing data you care about — always check "
            "podman volume ls first. "
            "Common interview question: how do you free up disk space from containers? "
            "Correct answer: check df first, then prune images (largest savings), "
            "then containers, and never blindly prune volumes."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 03 — IMAGES & REGISTRIES
    # ──────────────────────────────────────────────────────────────
    {
        "module": "03-images-registries",
        "type": "section",
        "title": "Module 03",
        "subtitle": "Images and Registries   (60-90 min)",
        "notes": (
            "Module 03 teaches image hygiene. The two big ideas: always use fully "
            "qualified image names, and prefer digests over tags for anything that "
            "matters. Both habits prevent whole categories of bugs and security incidents."
        ),
    },
    {
        "module": "03-images-registries",
        "type": "content",
        "title": "Tags vs Digests",
        "bullets": [
            "Tag (:latest, :stable) — mutable pointer, can change silently",
            "Digest (@sha256:...) — content-addressed, immutable",
            "Production rule: pin by digest for reproducibility and audit",
            "podman images --digests | grep nginx",
            "podman run docker.io/library/nginx@sha256:<digest>",
        ],
        "notes": (
            "Classic failure mode: deploy with :latest, it works. Three weeks later "
            "upstream publishes a new :latest with a breaking change. Your next deploy "
            "silently picks up the new image and the service breaks. Digest pinning "
            "prevents this entirely. The trade-off is that you have to actively update "
            "digests to get security patches — that is the auto-update topic in Module 14. "
            "For incident response: if you record the digest you deployed, you can always "
            "reproduce the exact image that was running, even if tags have moved."
        ),
    },
    {
        "module": "03-images-registries",
        "type": "content",
        "title": "Fully Qualified Image Names",
        "bullets": [
            "Avoid: alpine:latest             (ambiguous — which registry?)",
            "Prefer: docker.io/library/alpine:latest",
            "Short-name resolution rules vary by /etc/containers/registries.conf",
            "ENTRYPOINT vs CMD: podman image inspect nginx:stable --format '{{.Config.Entrypoint}}'",
            "In scripts and unit files: always use fully qualified names",
        ],
        "notes": (
            "Short names are convenient interactively but dangerous in automation. "
            "On Fedora the default short-name aliases list is in /etc/containers/registries.conf.d/. "
            "Different distros or custom configs can resolve 'alpine' to a completely different "
            "registry. In scripts, Containerfiles, and Quadlet units: always use the fully "
            "qualified form. The ENTRYPOINT vs CMD distinction matters when you try to "
            "override the command at runtime — if an image has ENTRYPOINT set, "
            "podman run image mycommand appends to the entrypoint rather than replacing it."
        ),
    },
    {
        "module": "03-images-registries",
        "type": "lab",
        "title": "Lab 03: Pull, Inspect, Digest",
        "bullets": [
            "podman pull docker.io/library/nginx:stable",
            "podman images --digests | grep nginx     (record the sha256)",
            "podman run --rm docker.io/library/nginx@sha256:<digest> nginx -v",
            "Optional: local registry -> tag -> push -> rmi -> pull back",
            "Checkpoint: can run an image by digest without specifying a tag",
        ],
        "notes": (
            "Walk students through finding the digest in the podman images --digests output. "
            "The format is sha256: followed by 64 hex characters. Copy it to a file — "
            "they will need it again when they do digest pinning in the capstone. "
            "The optional local registry lab is valuable for teams that have a private "
            "registry. The push/pull flow (tag, push, rmi, pull) teaches the full "
            "promotion pipeline in miniature. Flag: --tls-verify=false is only for "
            "this lab; never use it in production."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 04 — SECRETS
    # ──────────────────────────────────────────────────────────────
    {
        "module": "04-secrets",
        "type": "section",
        "title": "Module 04",
        "subtitle": "Secrets (Local-First)   (60-90 min)",
        "notes": (
            "Module 04 breaks one of the most deeply ingrained bad habits in container "
            "deployments: putting passwords in environment variables. Once students do "
            "Lab A2 (proving the secret is not in the environment), the correct pattern "
            "becomes intuitive. The rotation lab is equally important — secrets that "
            "cannot be rotated become permanent liabilities."
        ),
    },
    {
        "module": "04-secrets",
        "type": "content",
        "title": "Why Not Environment Variables?",
        "bullets": [
            "Env vars appear in: process listings, podman inspect, crash dumps, logs",
            "'-e DB_PASSWORD=...' is visible to any user who can run ps",
            "'.env' files get accidentally committed to git",
            "Podman secrets: named blob mounted as a file at /run/secrets/<name>",
            "App reads the file — never an environment variable",
        ],
        "notes": (
            "Show students how to find env vars on a running system: "
            "cat /proc/<pid>/environ (as root). Then show that with secrets as files "
            "the password does not appear there. The process listing visibility is "
            "the most compelling demo: run a container with -e DB_PASSWORD=supersecret "
            "then from another terminal do podman inspect and search for PASSWORD. "
            "It is right there in the JSON. Then do the same with a mounted secret — it "
            "is completely absent from the inspect output."
        ),
    },
    {
        "module": "04-secrets",
        "type": "content",
        "title": "Podman Secret Commands",
        "bullets": [
            "printf '%s' 'mypassword' | podman secret create db_password -",
            "podman secret ls / podman secret inspect db_password",
            "podman run --rm --secret db_password alpine sh -lc 'ls /run/secrets'",
            "Custom path: --secret db_password,target=db.pass",
            "Rotation: versioned names — db_password_v1 -> db_password_v2",
        ],
        "notes": (
            "The printf %s idiom avoids a trailing newline which would corrupt the "
            "secret value. Some apps are strict about newlines in passwords. "
            "Never use 'echo password' — it adds a newline. "
            "Teach the rotation pattern by name: create v2, update the consumer to "
            "reference v2, restart, verify, then delete v1. This is the only safe "
            "rotation flow. Deleting v1 before verifying v2 works means you cannot "
            "roll back. The rule: keep the old secret until rollback is no longer needed."
        ),
    },
    {
        "module": "04-secrets",
        "type": "lab",
        "title": "Lab 04: Create, Mount, and Rotate a Secret",
        "bullets": [
            "1.  printf '%s' 'correct-horse-battery' | podman secret create db_password -",
            "2.  podman run --rm --secret db_password busybox sh -lc 'test -f /run/secrets/db_password && echo OK'",
            "3.  Prove not env var: podman run ... busybox env | grep -i password   (nothing!)",
            "4.  Rotation: create db_password_v2, switch container, verify, remove v1",
        ],
        "notes": (
            "Lab step 3 is the most important: asking students to prove the absence of "
            "the secret from the environment builds the 'verify, don't assume' habit. "
            "For the rotation lab, have students explicitly run a container with v1, "
            "then switch to v2 and run again. Ask: what would happen if v2 was wrong? "
            "Answer: the app would fail to start and they could roll back by switching "
            "back to v1 — which is still there. This is why we keep v1 around."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 05 — STORAGE
    # ──────────────────────────────────────────────────────────────
    {
        "module": "05-storage",
        "type": "section",
        "title": "Module 05",
        "subtitle": "Storage — Volumes, Bind Mounts, Permissions   (60-90 min)",
        "notes": (
            "Storage is where rootless Podman trips up most new users. The UID mapping "
            "inside user namespaces makes permissions behave unexpectedly. 'podman unshare' "
            "is the key debugging tool — teach it early and students can self-diagnose. "
            "SELinux on Fedora/RHEL is the other common friction point: :Z is the fix "
            "for bind mounts, volumes usually just work."
        ),
    },
    {
        "module": "05-storage",
        "type": "content",
        "title": "Three Storage Types",
        "bullets": [
            "Writable layer — per container, gone when container is removed",
            "Named volume — Podman-managed, persists independently of containers",
            "Bind mount — you specify the exact host path",
            "Rule: volumes for databases/state, bind mounts for config/source code",
            "Never write important data into the writable layer",
        ],
        "notes": (
            "For named volumes: Podman stores them in ~/.local/share/containers/storage/volumes/. "
            "Find the actual path with: podman volume inspect dbdata --format {{.Mountpoint}}. "
            "Key advantage of named volumes over bind mounts: the container initialises "
            "ownership when it first writes to the volume. With bind mounts you have to "
            "manually ensure permissions match what the container process expects. "
            "For databases: always use a named volume. Never a bind mount for DB data "
            "in production — ownership problems are too common."
        ),
    },
    {
        "module": "05-storage",
        "type": "content",
        "title": "SELinux and Rootless Permissions",
        "bullets": [
            "Bind mount without label: may fail with permission denied on Fedora/RHEL",
            "Fix private:  -v ./data:/mnt:Z   (relabelled for this container only)",
            "Fix shared:   -v ./data:/mnt:z   (shared across containers)",
            "Never: chmod 777 or setenforce 0 — fix the root cause",
            "Debug: podman unshare ls -la <path>   (view inside user namespace)",
        ],
        "notes": (
            "The :Z vs :z distinction: uppercase Z means private — only this container "
            "can access this mount. Lowercase z means shared — multiple containers can "
            "access it. In most cases use uppercase Z. "
            "podman unshare is magical for debugging: it opens a shell inside the same "
            "user namespace that containers use. Run podman unshare ls -la /path to see "
            "what the container process actually sees. "
            "Common failure: host path is owned by root:root mode 700. The container "
            "process runs as UID 0 inside (mapped to your user outside) but has no write "
            "access. Fix: podman unshare chown -R 1000:1000 /path where 1000 is the "
            "UID the container runs as."
        ),
    },
    {
        "module": "05-storage",
        "type": "lab",
        "title": "Lab 05: Persistent Volume Demo",
        "bullets": [
            "podman volume create dbdata",
            "podman run --rm -v dbdata:/data alpine sh -lc 'echo hi > /data/x'",
            "podman run --rm -v dbdata:/data alpine sh -lc 'cat /data/x'     ->  hi",
            "Remove the container — then re-run the cat — data is STILL there",
            "SELinux drill: try bind mount without :Z, observe error, add :Z",
        ],
        "notes": (
            "This lab makes volume persistence concrete in one minute. "
            "Run the echo, destroy the container, run the cat — data survives. "
            "This is the fundamental difference between a volume and the writable layer. "
            "The SELinux drill is optional but highly recommended on Fedora/RHEL. "
            "Tell students: trigger the error on purpose, read the error message, then "
            "fix it. Building the habit of reading errors rather than immediately "
            "Googling is one of the most valuable meta-skills in this course."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 06 — NETWORKING
    # ──────────────────────────────────────────────────────────────
    {
        "module": "06-networking",
        "type": "section",
        "title": "Module 06",
        "subtitle": "Networking — Ports, DNS, Networks   (2-3 hours)",
        "notes": (
            "Module 06 is the largest module in the course and the most common source "
            "of production bugs. The key insight is that user-defined networks enable "
            "DNS-based service discovery; the default network does not. Build that "
            "intuition early and the rest of the module flows naturally."
        ),
    },
    {
        "module": "06-networking",
        "type": "content",
        "title": "How Container Networking Works",
        "bullets": [
            "Each container gets its own network namespace",
            "Virtual ethernet pair (veth) connects container to bridge",
            "User-defined network: DNS enabled — containers find each other by name",
            "Default 'podman' bridge: NO automatic DNS (use named networks!)",
            "Rootless helpers: pasta (preferred, modern) or slirp4netns",
        ],
        "notes": (
            "Mental model: think of a user-defined network as a private LAN segment. "
            "Every container on that segment gets a private IP and a DNS entry matching "
            "its container name. The Podman DNS resolver (aardvark-dns) handles the DNS. "
            "The default network is a legacy artifact — it has no DNS, so containers "
            "cannot find each other by name. Always create explicit named networks. "
            "Check your rootless backend: podman info --format {{.Host.NetworkBackend}}. "
            "Pasta is newer and handles UDP/ICMP more cleanly than slirp4netns."
        ),
    },
    {
        "module": "06-networking",
        "type": "content",
        "title": "Port Publishing Patterns",
        "bullets": [
            "-p 8080:80              all interfaces (0.0.0.0) — default",
            "-p 127.0.0.1:8080:80   loopback only — safer for internal services",
            "-p 8080:80 -p 8443:443  multiple ports",
            "-p 80                   random host port (ephemeral)",
            "podman port <name>      see what is published",
        ],
        "notes": (
            "Security principle: bind to the most restrictive address that still meets "
            "your requirements. Internal APIs should bind to 127.0.0.1. "
            "Only the reverse proxy should bind to 0.0.0.0. "
            "In production: DB never publishes a port at all — it lives on an internal "
            "network only accessible to the app tier. This is the network segmentation "
            "pattern covered in the three-tier lab. "
            "Rootless note: ports below 1024 need sysctl net.ipv4.ip_unprivileged_port_start "
            "or a reverse proxy. The reverse proxy approach is always preferred."
        ),
    },
    {
        "module": "06-networking",
        "type": "content",
        "title": "User-Defined Networks and DNS",
        "bullets": [
            "podman network create appnet",
            "podman run -d --name db --network appnet postgres:16-alpine",
            "podman run -d --name app --network appnet myapp:latest",
            "Inside 'app': getent hosts db   ->  resolves to db container's IP",
            "Network aliases: --network-alias db   (role-based names)",
        ],
        "notes": (
            "Key demo: create a network, start two containers on it, exec into one and "
            "resolve the other by container name. When this works, students understand "
            "why user-defined networks are mandatory for multi-service stacks. "
            "Network aliases: --network-alias db means you can have two containers share "
            "the alias db for a blue/green rotation. When you cut over, the alias switches — "
            "downstream services need no config change. "
            "Custom subnets: only needed when avoiding VPN subnet conflicts."
        ),
    },
    {
        "module": "06-networking",
        "type": "content",
        "title": "Multi-Network Segmentation",
        "bullets": [
            "[internet] -> [frontend-net] -> [proxy] -> [app] -> [backend-net] -> [db]",
            "proxy: only on frontend-net",
            "app: on BOTH frontend-net AND backend-net",
            "db: only on backend-net (--internal, no outbound access)",
            "podman network connect backend-net app   # add second network live",
        ],
        "notes": (
            "This is the production architecture pattern for the course. "
            "Walk through the logic: the proxy cannot reach the db (different network), "
            "the app can reach both, and the db cannot reach the internet (--internal). "
            "--internal is important: an internal network has no default route, so a "
            "compromised DB container cannot exfiltrate data to the internet. "
            "This is a concrete, verifiable security control. "
            "Key command: podman network connect adds a running container to a second "
            "network without restart."
        ),
    },
    {
        "module": "06-networking",
        "type": "lab",
        "title": "Lab 06: Three-Tier Isolated Stack",
        "bullets": [
            "Create: frontend-net, app-net (--internal)",
            "Start: db on app-net, app on app-net (--network-alias api), proxy on frontend-net",
            "podman network connect frontend-net app",
            "Verify: app resolves db (YES), proxy resolves api (YES)",
            "Verify: proxy cannot resolve db (ISOLATED), db cannot reach internet (BLOCKED)",
        ],
        "notes": (
            "This is the most important lab in Module 06. Run each verification step "
            "explicitly and ask students to predict the result before running it. "
            "Check proxy isolation: podman exec proxy sh -lc 'getent hosts db 2>&1 || echo ISOLATED'. "
            "If it says ISOLATED the segmentation works. "
            "Check db internet access: podman exec db wget --timeout=3 http://example.com 2>&1 || echo BLOCKED. "
            "These two verification commands should become part of every student's deployment checklist."
        ),
    },
    {
        "module": "06-networking",
        "type": "content",
        "title": "Networking Troubleshooting Checklist",
        "bullets": [
            "Cannot reach by name? -> are both on the same user-defined network?",
            "DNS works, TCP fails? -> service not listening, wrong port, firewall",
            "Port published but unreachable? -> check HostIp binding, check ss -tlnp inside",
            "Cannot reach internet? -> check if --internal flag is set on the network",
            "Debug sidecar: podman run --rm --network <net> alpine sh",
        ],
        "notes": (
            "Teach the systematic approach: DNS first, then TCP, then firewall, then binding. "
            "Students who skip steps waste time. The most common mistake is checking "
            "the wrong thing first: they try curl before checking if DNS resolves. "
            "The debug sidecar pattern: run an ephemeral alpine container on the same "
            "network and use it as your network debug tool. "
            "For containers that lack networking tools, point to nicolaka/netshoot — "
            "it is a purpose-built debug image with curl, dig, tcpdump, and nmap."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 07 — PODS
    # ──────────────────────────────────────────────────────────────
    {
        "module": "07-pods",
        "type": "section",
        "title": "Module 07",
        "subtitle": "Pods and Sidecars   (45-60 min)",
        "notes": (
            "Module 07 is short but important for students who will use Kubernetes later. "
            "Podman pods share a network namespace, so containers inside a pod reach "
            "each other on localhost. The infra container holds the namespaces. "
            "Pods are not required for most Podman workloads — use a user-defined network "
            "instead unless you specifically need localhost sharing."
        ),
    },
    {
        "module": "07-pods",
        "type": "content",
        "title": "What Is a Podman Pod?",
        "bullets": [
            "A pod groups containers that share network namespace",
            "Infra container: holds the shared namespaces, always present",
            "All containers share the same IP and port space",
            "Port published on pod -> available to all containers inside",
            "Mirrors the Kubernetes pod concept (same design intent)",
        ],
        "notes": (
            "The infra container shows up in podman ps. Students sometimes try to delete "
            "it — remind them it is infrastructure, not garbage. "
            "podman pod rm -f webpod cleans up the pod and all its containers including "
            "the infra container. "
            "When to use pods vs networks: use a pod when containers need to communicate "
            "via localhost (e.g., a sidecar logging agent that reads a socket file). "
            "Use a user-defined network for most multi-service stacks — more flexible "
            "and easier to reason about."
        ),
    },
    {
        "module": "07-pods",
        "type": "lab",
        "title": "Lab 07: Pod with Debug Sidecar",
        "bullets": [
            "podman pod create --name webpod -p 8080:80",
            "podman run -d --pod webpod --name nginx nginx:stable",
            "podman run -it --rm --pod webpod alpine sh",
            "  Inside sidecar: wget -qO- http://127.0.0.1:80/ | head",
            "podman pod rm -f webpod",
        ],
        "notes": (
            "Key moment: inside the sidecar container, http://127.0.0.1:80/ resolves "
            "to nginx — even though nginx is a different container. They share localhost "
            "because they share the network namespace. "
            "This is the sidecar pattern: attach a debug container to a running pod "
            "without exposing new ports, without modifying the main container. "
            "Practical use: attach a busybox or alpine sidecar to a pod to run netstat "
            "or dump environment variables when debugging without restarting the main service."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 08 — BUILDING IMAGES
    # ──────────────────────────────────────────────────────────────
    {
        "module": "08-building-images",
        "type": "section",
        "title": "Module 08",
        "subtitle": "Building Images (Containerfiles)   (2-3 hours)",
        "notes": (
            "Module 08 is the largest technical module. The four pillars: layer caching, "
            "non-root runtime, multi-stage builds, and build context hygiene. Students "
            "who master these four pillars can build images that are production-ready "
            "on the first attempt. Slow builds and bloated images are almost always "
            "caused by violating one of these four principles."
        ),
    },
    {
        "module": "08-building-images",
        "type": "content",
        "title": "Images, Layers, and Caching",
        "bullets": [
            "Each Containerfile instruction creates an immutable layer",
            "Cache is invalidated from the first changed instruction downward",
            "Slow-changing steps first: OS packages, dependency install",
            "Fast-changing steps last: application source code",
            "COPY . .  early = cache miss on every source change",
        ],
        "notes": (
            "Analogy: building a layer cake. You cannot change a lower layer without "
            "rebuilding everything above it. The cache optimisation rule: put stable "
            "steps at the bottom (base image, system packages, dependency installs), "
            "and volatile steps at the top (your app source). "
            "Bad example: FROM python:3.13, COPY . ., RUN pip install. Every time any "
            "source file changes, pip reruns. "
            "Good example: COPY requirements.txt first, RUN pip install, then COPY . . "
            "Now pip only reruns when requirements.txt changes."
        ),
    },
    {
        "module": "08-building-images",
        "type": "content",
        "title": "Essential Containerfile Instructions",
        "bullets": [
            "FROM     — base image (pin version; digest for prod)",
            "WORKDIR  — set working directory (avoids brittle cd chains)",
            "COPY     — copy files (prefer over ADD; use --chown=)",
            "RUN      — install/build steps (chain with && to reduce layers)",
            "USER     — run as non-root (must be after all root-requiring steps)",
            "CMD / ENTRYPOINT  — exec form preferred (correct signal handling)",
        ],
        "notes": (
            "COPY vs ADD: ADD has extra magic (tar extraction, URL fetching). "
            "Unless you need that specific magic, use COPY — it is explicit and predictable. "
            "Exec form for CMD: ['nginx', '-g', 'daemon off;'] vs shell form. "
            "Exec form makes the process PID 1, which means it receives SIGTERM directly "
            "when the container is stopped. Shell form wraps it in /bin/sh -c which "
            "means SIGTERM goes to the shell, not your process — causing graceful-shutdown bugs. "
            "USER placement: set USER after all root-requiring steps (apt-get, adduser, etc.)."
        ),
    },
    {
        "module": "08-building-images",
        "type": "content",
        "title": "Non-Root Runtime (Least Privilege in Images)",
        "bullets": [
            "RUN addgroup -S app && adduser -S -G app app",
            "COPY --chown=app:app . /app",
            "USER app",
            "Give write access only to: /tmp, app state dir, log dir",
            "Test: podman run --rm localhost/myapp:1 id   (must NOT be uid=0)",
        ],
        "notes": (
            "This is the image-level complement to rootless Podman (the host-level protection). "
            "Rootless Podman protects the host from container escapes. Non-root inside "
            "the container protects against: escape bugs that require in-container root, "
            "accidental writes to system paths, and overly permissive defaults. "
            "The 'podman run id' test is a quick smoke test for every image. If it returns "
            "uid=0(root), the image needs fixing before production. "
            "COPY --chown is cleaner than a separate RUN chown because it avoids creating "
            "an extra layer with duplicated files."
        ),
    },
    {
        "module": "08-building-images",
        "type": "content",
        "title": "Multi-Stage Builds",
        "bullets": [
            "Build stage: has compiler/toolchain, produces artifact",
            "Runtime stage: minimal image + artifact only",
            "FROM ... AS build  /  COPY --from=build /app/binary /app/",
            "podman build --target build   (stop at build stage for debugging)",
            "Result: runtime image has no compiler, headers, or build cache",
        ],
        "notes": (
            "Show the size comparison concretely: podman images after building both "
            "a naive image (with all build tools) and a multi-stage image. "
            "A Go binary in a scratch image is about 10 MB. The same binary with a "
            "full golang:1.23 base is about 800 MB. "
            "The --target flag is underused. If a multi-stage build fails late, stop at "
            "the build stage and run podman run -it localhost/myapp:build sh to inspect "
            "the filesystem interactively. This is far faster than print-debugging RUN statements."
        ),
    },
    {
        "module": "08-building-images",
        "type": "content",
        "title": "Build Context Hygiene",
        "bullets": [
            ".containerignore — prevents accidental COPY of .env, keys, node_modules",
            "Never: COPY . .   (may include secrets, build artifacts, caches)",
            "Prefer explicit: COPY src/ /app/src/   COPY package.json /app/",
            "Secrets in ARG or ENV = secret in image history = leak",
            "Inspect large layers: podman image history localhost/myapp:1",
        ],
        "notes": (
            "The .containerignore omission is the single most common image security bug "
            "in codebases that evolved from 'it works on my laptop'. Someone adds a "
            "COPY . . line for convenience, the .env file is in the same directory, "
            "and the production image ships with the database password baked in. "
            "ARG secrets: even though ARG values are not in the final image environment, "
            "they are visible in podman image history because they influence RUN steps. "
            "The image history command shows every layer and its size — use it to find "
            "unexpectedly large layers."
        ),
    },
    {
        "module": "08-building-images",
        "type": "lab",
        "title": "Lab 08: Build a Non-Root Service Image",
        "bullets": [
            "FROM python:3.13-alpine",
            "RUN addgroup -S app && adduser -S -G app app",
            "COPY --chown=app:app server.py /app/server.py",
            "USER app  /  EXPOSE 8080  /  CMD [\"python\", \"/app/server.py\"]",
            "Test: podman run --rm localhost/svc-lab:1 id   (must NOT be uid=0)",
        ],
        "notes": (
            "This lab ties together layers, non-root, and a working service. "
            "The 'id' test first ensures students cannot accidentally skip the USER step. "
            "Common failure: touch /app/ok: permission denied. This means COPY --chown "
            "was not used correctly, or the WORKDIR path is owned by root. "
            "If time allows, have students do the hello-bun example: examples/build/hello-bun. "
            "It shows a TypeScript app built in one stage and run in a minimal stage, "
            "with a healthcheck using a dedicated healthcheck.ts file."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 09 — MULTI-SERVICE WORKFLOWS
    # ──────────────────────────────────────────────────────────────
    {
        "module": "09-multiservice-workflows",
        "type": "section",
        "title": "Module 09",
        "subtitle": "Multi-Service Workflows   (60-90 min)",
        "notes": (
            "Module 09 bridges everything learned so far into a coherent stack. "
            "The key skill is writing a repeatable 'stack up / stack down' script. "
            "The provided examples/stack/stack.sh is a reference implementation — "
            "study it with students before running it."
        ),
    },
    {
        "module": "09-multiservice-workflows",
        "type": "content",
        "title": "Choosing a Multi-Service Pattern",
        "bullets": [
            "User-defined network + named containers  ->  best default for small stacks",
            "Pod (shared localhost)  ->  when sidecars need 127.0.0.1",
            "podman play kube  ->  when you want Kubernetes YAML locally",
            "Quadlet + systemd  ->  production, reboot-safe (Module 11)",
            "Compose tools  ->  convenient wrapper; learn primitives first",
        ],
        "notes": (
            "Decision tree: "
            "1. Need boot persistence? -> Quadlet (Module 11). "
            "2. Need shared localhost? -> Pod. "
            "3. Have Kubernetes YAML? -> play kube. "
            "4. Everything else: user-defined network. "
            "Compose tools (podman-compose, docker compose) are valid but they obscure "
            "what primitives are created. Students who learn the primitives first "
            "can debug any compose-generated setup because they understand what "
            "network create, volume create, and run commands are being issued."
        ),
    },
    {
        "module": "09-multiservice-workflows",
        "type": "lab",
        "title": "Lab 09: stack.sh Reference",
        "bullets": [
            "bash examples/stack/stack.sh up",
            "bash examples/stack/stack.sh status",
            "bash examples/stack/stack.sh down",
            "Study: idempotent creates, secret prompting, stable names",
            "DB has no published port — app reaches it via network DNS only",
        ],
        "notes": (
            "Before running, walk through the structure: "
            "1. Creates network and volume if they do not exist (idempotent). "
            "2. Creates the Podman secret for the DB password if not present, "
            "   prompting with read -s. "
            "3. Starts containers with stable names so the script is safe to re-run. "
            "4. The down command stops containers but leaves the volume to avoid data loss. "
            "Idempotency is the key production habit: a deploy script should be safe "
            "to run multiple times without side effects."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 10 — PODMAN PLAY KUBE
    # ──────────────────────────────────────────────────────────────
    {
        "module": "10-play-kube",
        "type": "section",
        "title": "Module 10",
        "subtitle": "podman play kube   (45-75 min)",
        "notes": (
            "Module 10 is for teams that already use or will use Kubernetes YAML. "
            "podman play kube runs a subset of Kubernetes Pod definitions locally. "
            "The security note about base64 is important: many teams store Kubernetes "
            "Secrets as YAML files without understanding that base64 is encoding, "
            "not encryption."
        ),
    },
    {
        "module": "10-play-kube",
        "type": "content",
        "title": "Running Kubernetes YAML Locally",
        "bullets": [
            "podman play kube examples/kube/webpod.yaml",
            "podman kube down examples/kube/webpod.yaml   # clean teardown",
            "Quadlet .kube unit: run YAML-defined pod under systemd",
            "Limitation: Pods only — no Deployments, Services, Ingress",
            "Secret YAML: base64 is encoding NOT encryption — never commit",
        ],
        "notes": (
            "The base64 point deserves extra emphasis. Show: "
            "echo -n supersecret | base64 produces a string any human can decode. "
            "Kubernetes Secret YAML is NOT encrypted by default. Committing Kubernetes "
            "Secret YAML to a public repo is the same as committing plaintext passwords. "
            "For secrets with play kube: provision them as Podman secrets out-of-band "
            "and reference them in the pod spec rather than embedding base64 values. "
            "The .kube Quadlet unit type is useful for teams that generate pod YAML "
            "in CI and want to run it under systemd for boot persistence."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 11 — QUADLET + SYSTEMD
    # ──────────────────────────────────────────────────────────────
    {
        "module": "11-quadlet",
        "type": "section",
        "title": "Module 11",
        "subtitle": "Production Baseline — systemd + Quadlet   (2-3 hours)",
        "notes": (
            "Module 11 is the production turning point. Everything before was development "
            "patterns; Quadlet is how services run in production on Linux. Quadlet converts "
            "simple declarative unit files into full systemd service units. The benefit: "
            "restart policies, boot ordering, journald logging, and boot persistence — all "
            "for free, using the same tooling that manages every other service on the host."
        ),
    },
    {
        "module": "11-quadlet",
        "type": "content",
        "title": "Why Quadlet?",
        "bullets": [
            "Linux-native: systemd manages restarts, logs, dependencies, boot start",
            "Quadlet file -> systemd generates the service unit automatically",
            "Files live at: ~/.config/containers/systemd/*.{container,network,volume,pod}",
            "Boot persistence: sudo loginctl enable-linger $USER",
            "journalctl --user -u myapp.service -n 100   (all logs in one place)",
        ],
        "notes": (
            "Key differentiator vs 'podman run in a script': systemd handles restart "
            "on failure, ordered startup (dependencies), graceful shutdown, and log collection. "
            "A cron-or-bash approach misses all of these. "
            "Linger: without loginctl enable-linger, user services stop when you log out. "
            "On a server you want services to run regardless of whether anyone is logged in. "
            "After enabling linger, user services start on boot with no active login session. "
            "The Quadlet generator runs at daemon-reload time. If Podman cannot parse your "
            "unit file, the generated service will not appear. Debug with: "
            "/usr/lib/systemd/system-generators/podman-system-generator --user --dryrun"
        ),
    },
    {
        "module": "11-quadlet",
        "type": "content",
        "title": "Quadlet Unit File Structure",
        "bullets": [
            "[Unit]      Description=My App",
            "[Container] Image=docker.io/library/nginx:stable",
            "[Container] PublishPort=127.0.0.1:8081:80",
            "[Container] Network=appnet.network  /  Volume=appdata.volume:/data",
            "[Service]   Restart=always",
            "[Install]   WantedBy=default.target",
        ],
        "notes": (
            "Walk through a real unit file from examples/quadlet/hello-nginx.container. "
            "[Container] section translates directly to podman run flags: "
            "Image -> --image, PublishPort -> -p, Network -> --network, Volume -> -v. "
            "The Network= and Volume= values reference other Quadlet units by filename stem. "
            "systemd will start the network and volume units before the container unit "
            "when you include them in After= and Requires=. "
            "[Install] WantedBy=default.target means the service starts on boot after "
            "linger is enabled. Without this line the service will not autostart."
        ),
    },
    {
        "module": "11-quadlet",
        "type": "lab",
        "title": "Lab 11: First Quadlet Service",
        "bullets": [
            "cp examples/quadlet/hello-nginx.container ~/.config/containers/systemd/",
            "systemctl --user daemon-reload",
            "systemctl --user start hello-nginx.service",
            "curl http://127.0.0.1:8081/   ->  nginx welcome page",
            "journalctl --user -u hello-nginx.service -n 20 --no-pager",
        ],
        "notes": (
            "Most common failure: forgetting daemon-reload after copying the file. "
            "Quadlet files are only processed at daemon-reload time — skip it and "
            "the service will not exist. "
            "Have students check: systemctl --user status hello-nginx.service. "
            "If it shows 'not found', daemon-reload was not run. "
            "If it shows 'failed', check journalctl for the Podman error. "
            "After success, show the clean-up: stop service, remove the .container file, "
            "daemon-reload again. This teaches that Quadlet is not a database — "
            "the file IS the configuration."
        ),
    },
    {
        "module": "11-quadlet",
        "type": "content",
        "title": "Secrets in Quadlet (Module 11a)",
        "bullets": [
            "In [Container]: Secret=db_password",
            "Container reads from /run/secrets/db_password at runtime",
            "Never put secret values in Environment= lines",
            "Rotation: update Secret= to new versioned name, daemon-reload, restart",
            "Verify: journalctl logs must not contain secret values",
        ],
        "notes": (
            "Rotation procedure: "
            "1. Create new secret: printf '%s' 'newval' | podman secret create db_password_v2 - "
            "2. Edit the .container file: change Secret=db_password_v1 to Secret=db_password_v2 "
            "3. systemctl --user daemon-reload && systemctl --user restart myapp.service "
            "4. Verify the service is healthy "
            "5. podman secret rm db_password_v1 "
            "The journald log verification step: journalctl --user -u myapp.service | grep -i password "
            "should return nothing. If it returns something, the app is logging secrets — "
            "fix the app before production."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 12 — SECURITY
    # ──────────────────────────────────────────────────────────────
    {
        "module": "12-security",
        "type": "section",
        "title": "Module 12",
        "subtitle": "Security Deep Dive   (60-120 min)",
        "notes": (
            "Module 12 formalises the security practices scattered throughout the course "
            "into a coherent hardening checklist. The key mental model: defence in depth. "
            "No single control is sufficient. Rootless + non-root + dropped capabilities "
            "+ read-only FS + SELinux + digest pinning = an auditable security posture."
        ),
    },
    {
        "module": "12-security",
        "type": "content",
        "title": "Baseline Hardening Checklist",
        "bullets": [
            "Run rootless (host protection against breakout)",
            "Run as non-root inside container (in-container least privilege)",
            "Drop capabilities: --cap-drop=ALL, add back only what is needed",
            "Read-only root FS: --read-only + --tmpfs for writable scratch",
            "--security-opt no-new-privileges",
            "Limit resources: --memory 256m --pids-limit 200",
        ],
        "notes": (
            "Walk through each control and ask what does this protect against: "
            "Rootless -> host breakout. Non-root-in-container -> in-container privilege "
            "escalation. Dropped capabilities -> kernel exploit needing a specific cap. "
            "Read-only FS -> malware writing persistence files. no-new-privileges -> "
            "setuid binaries inside the container cannot gain privileges. "
            "Resource limits -> denial of service from runaway processes. "
            "Collectively these make a container posture that is verifiable and auditable. "
            "Avoid --privileged as a debug shortcut — it grants all capabilities."
        ),
    },
    {
        "module": "12-security",
        "type": "lab",
        "title": "Lab 12: Read-Only + Dropped Caps",
        "bullets": [
            "podman run --rm --cap-drop=ALL alpine id",
            "podman run --rm --read-only --tmpfs /var/cache/nginx --tmpfs /var/run \\",
            "         --cap-drop=ALL --security-opt no-new-privileges nginx:stable",
            "If it fails: read error -> identify write path -> add targeted tmpfs",
            "Goal: nginx runs successfully with all restrictions applied",
        ],
        "notes": (
            "This lab deliberately fails first so students learn to read errors as a map "
            "of required permissions. nginx needs to write to /var/cache/nginx (temp files) "
            "and /var/run (PID file). Each time it fails, add the minimum required tmpfs "
            "and retry. Goal: understand why each restriction fails and add back only the "
            "minimum required exception. "
            "Image trust: pin by digest, use minimal base images (alpine variants), "
            "track upstream CVEs with tools like trivy or grype. "
            "Supply chain: prefer official images; avoid curl-piped-to-bash installer scripts."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 13 — TROUBLESHOOTING
    # ──────────────────────────────────────────────────────────────
    {
        "module": "13-troubleshooting",
        "type": "section",
        "title": "Module 13",
        "subtitle": "Troubleshooting and Ops   (60-120 min)",
        "notes": (
            "Module 13 is about turning 'it does not work' into a short, systematic "
            "process. The debug loop (state -> logs -> inspect -> reproduce) applies to "
            "100% of container failures. Students who memorise the loop save hours "
            "of random Googling. The failure drills make this visceral."
        ),
    },
    {
        "module": "13-troubleshooting",
        "type": "content",
        "title": "The Debug Loop",
        "bullets": [
            "1.  podman ps -a              state, exit codes",
            "2.  podman logs <name>        app output / crash reason",
            "3.  podman inspect <name>     ports, mounts, env, command",
            "4.  podman run --rm -it <image> sh    reproduce interactively",
            "Container exits too fast? -> override CMD to 'sleep 3600' then exec in",
        ],
        "notes": (
            "The loop is always the same, regardless of the failure. "
            "Step 1: is the container actually running or did it exit? "
            "Exit code 1 = application error. Exit code 137 = OOM killed. Exit code 139 = segfault. "
            "Step 2: for a Quadlet service, also check journalctl. Difference: "
            "podman logs shows container stdout/stderr; journalctl shows systemd "
            "lifecycle events AND container output. "
            "Step 4: if the container exits too fast, run the same image with "
            "--entrypoint sh or override CMD with 'sleep 3600' to get a shell "
            "in the same environment."
        ),
    },
    {
        "module": "13-troubleshooting",
        "type": "content",
        "title": "Ops Tools",
        "bullets": [
            "podman events          lifecycle events (start, stop, pull, network...)",
            "podman stats           live CPU / memory / I/O per container",
            "podman top <name>      processes inside the container",
            "podman system df       disk usage by type",
            "journalctl --user -u <svc>   systemd service logs",
        ],
        "notes": (
            "podman events is underused. It answers: what did Podman do in the last "
            "5 minutes? Invaluable when a container mysteriously stopped. "
            "Filter: podman events --filter type=container --since 1h. "
            "podman stats is the quick health check: if a container is consuming "
            "100% CPU continuously, something is wrong. If memory grows without bound "
            "there is a leak. "
            "For Quadlet services: both podman logs and journalctl are useful. "
            "journalctl shows the systemd perspective (failed to start, restart attempts). "
            "podman logs shows the application perspective."
        ),
    },
    {
        "module": "13-troubleshooting",
        "type": "lab",
        "title": "Lab 13: Failure Drills",
        "bullets": [
            "1.  Port conflict: two services on 8080 -> fix by changing host port",
            "2.  Permission denied: mount root-owned dir -> fix with unshare or :Z",
            "3.  Bad tag: deploy :latest that changes -> fix by pinning digest",
            "4.  DNS failure: containers on default network -> fix: user-defined network",
            "Run each: observe error, diagnose using debug loop, fix, verify",
        ],
        "notes": (
            "These drills should be done by students, not just demonstrated. "
            "Tell them: I will cause these failures on purpose. Your job is to diagnose "
            "and fix them using only the debug loop. "
            "Drill 1: 'address already in use' in podman logs. Fix: change host port. "
            "Drill 2: 'permission denied' writing to bind mount. Fix: unshare chown or add :Z. "
            "Drill 3: upstream changes tag -> service breaks on next restart. "
            "Fix: record digest, pin it. "
            "Drill 4: getent hosts fails. Check podman network inspect shows no dns_enabled. "
            "Fix: create user-defined network."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 14 — AUTO-UPDATES
    # ──────────────────────────────────────────────────────────────
    {
        "module": "14-autoupdate",
        "type": "section",
        "title": "Module 14",
        "subtitle": "Maintenance and Auto-Updates   (45-75 min)",
        "notes": (
            "Module 14 is about making an informed policy decision around auto-updates. "
            "Auto-update is not free: it introduces unplanned restarts and can "
            "silently change behaviour. The course position: digest pinning for production, "
            "auto-update only with monitoring and a documented rollback plan."
        ),
    },
    {
        "module": "14-autoupdate",
        "type": "content",
        "title": "Auto-Update: Policy, Not Magic",
        "bullets": [
            "podman auto-update: checks registry for new images, restarts units",
            "Works with Quadlet units that have AutoUpdate=registry",
            "Tags vs Digests: auto-update needs tags (digests are immutable)",
            "If you use auto-update: add healthchecks, alert on restart loops",
            "Rollback plan is mandatory before enabling auto-update",
        ],
        "notes": (
            "The tension: tags are convenient for auto-update but unpredictable. "
            "Digests are predictable but require manual upgrades. "
            "Recommendation: "
            "For non-critical services: auto-update with a stable tag is acceptable "
            "if you monitor and have a rollback plan. "
            "For production stateful services (databases, payment systems): digest pinning. "
            "Upgrade via deliberate change: pull new digest, update unit, restart. "
            "The minimum rollback plan: know the previous working image reference, "
            "have a procedure to update the unit to that reference, and have monitoring "
            "to detect failure within minutes of a restart."
        ),
    },
    {
        "module": "14-autoupdate",
        "type": "lab",
        "title": "Lab 14: Enable and Observe Auto-Update",
        "bullets": [
            "cp examples/quadlet/autoupdate-nginx.container ~/.config/containers/systemd/",
            "systemctl --user daemon-reload && start autoupdate-nginx.service",
            "podman auto-update   (manual trigger)",
            "systemctl --user status autoupdate-nginx.service",
            "journalctl --user -u autoupdate-nginx.service -n 50 --no-pager",
        ],
        "notes": (
            "The autoupdate-nginx.container example has AutoUpdate=registry set. "
            "Run podman auto-update manually and observe: if the image is already current, "
            "nothing restarts. If there is a newer image for the tag, it is pulled and "
            "the service restarts. "
            "Show the systemd timer approach: systemctl --user list-unit-files | grep auto-update "
            "may show a podman-auto-update timer that runs on a schedule. "
            "Key question for students: what happens if auto-update pulls a broken image? "
            "Answer: the service fails to start, systemd detects the failure, and raises "
            "an alert — IF you have monitoring. Without monitoring, it silently breaks."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 80 — CAPSTONE
    # ──────────────────────────────────────────────────────────────
    {
        "module": "80-capstone",
        "type": "section",
        "title": "Module 80",
        "subtitle": "Capstone Project   (3-6 hours)",
        "notes": (
            "The capstone is the course's final exam in practical form. Students deploy "
            "a real MariaDB + Adminer stack with full Quadlet management, secrets, "
            "backup/restore, and digest-pinned upgrades. The success criteria are "
            "measurable and match real production requirements."
        ),
    },
    {
        "module": "80-capstone",
        "type": "content",
        "title": "Capstone: What You Will Build",
        "bullets": [
            "MariaDB (private, no published port) + Adminer (UI on port 8082)",
            "Private network (capnet) — DB cannot reach internet (--internal)",
            "Named volumes for data and backups",
            "Podman secrets for the DB root password",
            "Quadlet units: reboot-safe, starts on boot via linger",
        ],
        "notes": (
            "This is not a toy: MariaDB with Quadlet plus secrets plus volumes is a "
            "realistic pattern for running a production database on a single host. "
            "The Adminer web UI gives a visual way to verify DB state. "
            "Architecture: capnet (--internal) -> only cap-mariadb and cap-adminer attached "
            "-> DB cannot reach internet, admin UI reaches DB via DNS name 'db' "
            "-> only Adminer publishes a port (8082) to the host "
            "-> passwords live in Podman secrets referenced by name in .container units."
        ),
    },
    {
        "module": "80-capstone",
        "type": "content",
        "title": "Capstone: Backup, Restore, Upgrade",
        "bullets": [
            "Backup: mysqldump via throwaway container -> cap-backups volume",
            "Restore: feed .sql into mysql -h db via throwaway container, verify data",
            "Upgrade: record digest -> pull new -> update Image= -> restart",
            "Rollback: restore previous digest -> daemon-reload -> restart -> verify",
            "Password rotation: create v2 -> ALTER USER -> update unit -> verify -> rm v1",
        ],
        "notes": (
            "The backup and restore procedure is designed to be testable: create a table, "
            "take a backup, drop the table, restore from backup, verify the table is back. "
            "Never call a backup procedure verified until you have successfully restored "
            "from it and confirmed data integrity. "
            "Password rotation requires two steps: create the new secret AND update the "
            "DB password with ALTER USER. The order matters: change the DB password first, "
            "then update the secret reference in the Quadlet unit, then restart. "
            "Rollback for password rotation is complex — keep the old password and the old "
            "secret until verification is complete."
        ),
    },
    {
        "module": "80-capstone",
        "type": "lab",
        "title": "Capstone Lab Steps",
        "bullets": [
            "1.  Create secret, install units, enable linger, daemon-reload, start",
            "2.  Verify: Adminer at :8082, DB has NO published ports",
            "3.  Insert test data (CREATE TABLE cap.t1, INSERT 1)",
            "4.  Backup -> DROP database -> Restore -> verify data is back",
            "5.  Upgrade by digest -> verify -> rollback to previous digest -> verify",
        ],
        "notes": (
            "Students who complete all five steps have demonstrated the complete "
            "production skillset this course teaches. "
            "Step 2: podman port cap-mariadb should return nothing. If it returns "
            "anything, the .container unit has a PublishPort= that must be removed. "
            "Step 4: the restore test is the most important. Force the issue: tell "
            "students to DROP DATABASE cap before restoring so they know the restore "
            "is actually working, not just reading a cached result. "
            "Step 5: use real digests from podman images --digests. Record them in "
            "a text file before upgrading so rollback is a copy-paste operation."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # MODULE 90 — EXTERNAL SECRETS
    # ──────────────────────────────────────────────────────────────
    {
        "module": "90-external-secrets-survey",
        "type": "section",
        "title": "Module 90 (Optional)",
        "subtitle": "External Secrets Survey   (45-90 min)",
        "notes": (
            "Module 90 is optional but valuable for teams that need to scale beyond "
            "a single host or have compliance requirements. The goal is not to implement "
            "any specific system — it is to build the mental model to choose the right "
            "one. Students who understand the decision framework can evaluate any "
            "secrets manager they encounter."
        ),
    },
    {
        "module": "90-external-secrets-survey",
        "type": "content",
        "title": "Choosing a Secrets System",
        "bullets": [
            "Key questions: how many hosts? rotation frequency? audit requirements?",
            "Option 1 — systemd Credentials: host-native, great for single host",
            "Option 2 — SOPS: encrypted files in git, GitOps-friendly",
            "Option 3 — Vault-class: central policy + auth + audit, multi-host",
            "Migration: external manager writes a file -> app reads the file (unchanged)",
        ],
        "notes": (
            "Decision framework: "
            "Single host, minimal infra -> systemd credentials. The credentials are "
            "encrypted at rest on the host and materialised as files at service start. "
            "Zero extra infrastructure. "
            "Small team, GitOps workflow -> SOPS. Secrets live encrypted in git alongside "
            "infrastructure code. Change history is in git. Audit = git log. "
            "Larger org, compliance requirements, multi-host -> Vault-class (HashiCorp Vault, "
            "AWS Secrets Manager). Dynamic credentials, fine-grained policies, "
            "full audit logs, automated rotation. "
            "Regardless of which system you choose, the delivery pattern stays the same: "
            "the external system writes a file, the container reads the file. "
            "This means migrating from Podman secrets does not require changing the application."
        ),
    },

    # ──────────────────────────────────────────────────────────────
    # CLOSING
    # ──────────────────────────────────────────────────────────────
    {
        "module": "closing",
        "type": "section",
        "title": "Course Complete",
        "subtitle": "You are now a production-ready Podman operator",
        "notes": (
            "Congratulations — students have covered every skill needed to run "
            "rootless Podman services in production. Remind them of the five habits "
            "that separate good operators from beginners: "
            "1. Rootless by default. "
            "2. Secrets as files, never environment variables. "
            "3. Volumes for state, .containerignore for builds. "
            "4. Digest-pinned images for anything that matters. "
            "5. Quadlet + systemd for anything that must survive a reboot. "
            "Point them to the cheatsheets/ directory for quick reference, and "
            "ASSESSMENTS.md for the two practical exams."
        ),
    },
    {
        "module": "closing",
        "type": "content",
        "title": "Five Habits of a Podman Operator",
        "bullets": [
            "1.  Rootless by default — explain every exception",
            "2.  Secrets as files — never environment variables",
            "3.  Volumes for state — writable layer is not persistence",
            "4.  Digest-pinned images — reproducibility + audit trail",
            "5.  Quadlet + systemd — reboot-safe production baseline",
        ],
        "notes": (
            "These five habits are a concise summary of the entire course. "
            "If a student can defend every deviation from these five habits, "
            "they are ready for production. "
            "Quick reference: cheatsheets/ directory contains CLI, rootless, Quadlet, "
            "troubleshooting, and security cheatsheets. "
            "Next steps: read the capstone assessment rubric (ASSESSMENTS.md Exam B), "
            "complete the capstone project, then run the Module 90 survey if you need "
            "to scale beyond a single host."
        ),
    },
]


# ---------------------------------------------------------------------------
# ODP builder
# ---------------------------------------------------------------------------

def build_presentation(output_path: str, slides: list | None = None) -> None:
    if slides is None:
        slides = SLIDES
    doc = OpenDocumentPresentation()

    # ── Page layout ──────────────────────────────────────────────
    pl = PageLayout(name="widescreen")
    doc.automaticstyles.addElement(pl)
    plp = PageLayoutProperties(
        margin="0cm",
        pagewidth=SLIDE_W,
        pageheight=SLIDE_H,
        printorientation="landscape",
    )
    pl.addElement(plp)

    # ── Master page ───────────────────────────────────────────────
    master = MasterPage(name="Dark", pagelayoutname=pl)
    doc.masterstyles.addElement(master)

    # ── Helper: create a Style object and register it ─────────────
    _style_counter = [0]

    def make_style(family: str, **props) -> Style:
        _style_counter[0] += 1
        s = Style(name=f"s{_style_counter[0]}", family=family)
        if family == "text":
            s.addElement(TextProperties(**props))
        elif family == "graphic":
            s.addElement(GraphicProperties(**props))
        elif family == "drawing-page":
            s.addElement(DrawingPageProperties(**props))
        doc.automaticstyles.addElement(s)
        return s

    # ── Pre-build all required styles ────────────────────────────
    S_TITLE_TEXT    = make_style("text", fontsize="34pt", fontweight="bold",   color=WHITE)
    S_SUBTITLE_TEXT = make_style("text", fontsize="18pt",                       color=TEXT_DIM)
    S_HEADING_TEXT  = make_style("text", fontsize="26pt", fontweight="bold",   color=ACCENT)
    S_BULLET_TEXT   = make_style("text", fontsize="15pt",                       color=TEXT_PRIMARY)
    S_CODE_TEXT     = make_style("text", fontsize="13pt",                       color=ACCENT,
                                 fontfamily="Liberation Mono")
    S_NOTES_TEXT    = make_style("text", fontsize="12pt",                       color="#111111")
    S_COPYRIGHT_TEXT = make_style("text", fontsize="14pt",                      color=TEXT_DIM)

    S_BG_DARK    = make_style("drawing-page", fill="solid", fillcolor=BG_DARK,    backgroundsize="border")
    S_BG_SECTION = make_style("drawing-page", fill="solid", fillcolor=BG_SECTION, backgroundsize="border")
    S_BG_LAB     = make_style("drawing-page", fill="solid", fillcolor=BG_LAB,     backgroundsize="border")

    S_BOX = make_style("graphic", stroke="none", fill="none")

    # ── Slide builder ─────────────────────────────────────────────
    def add_slide(data: dict) -> None:
        stype = data.get("type", "content")

        if stype == "section":
            bg_style = S_BG_SECTION
        elif stype == "lab":
            bg_style = S_BG_LAB
        else:
            bg_style = S_BG_DARK

        page = Page(stylename=bg_style, masterpagename=master)
        doc.presentation.addElement(page)

        # ── Title frame ─────────────────────────────────────────
        if stype in ("title", "section"):
            t_top, t_h = "3.2cm", "4.0cm"
        else:
            t_top, t_h = "0.8cm", "2.0cm"

        title_frame = Frame(
            stylename=S_BOX,
            width="23.4cm", height=t_h,
            x="1.0cm", y=t_top,
        )
        title_frame.setAttrNS(PRESENTATIONNS, "class", "title")
        title_tb = TextBox()
        title_frame.addElement(title_tb)

        t_style = S_TITLE_TEXT if stype in ("title", "section") else S_HEADING_TEXT
        tp = P()
        tp.addElement(Span(stylename=t_style, text=data.get("title", "")))
        title_tb.addElement(tp)
        page.addElement(title_frame)

        # ── Subtitle (title / section slides) ───────────────────
        if stype in ("title", "section") and data.get("subtitle"):
            sub_y = f"{float(t_top.replace('cm','')) + float(t_h.replace('cm','')) + 0.2:.2f}cm"
            sub_frame = Frame(
                stylename=S_BOX,
                width="23.4cm", height="1.6cm",
                x="1.0cm", y=sub_y,
            )
            sub_frame.setAttrNS(PRESENTATIONNS, "class", "subtitle")
            sub_tb = TextBox()
            sub_frame.addElement(sub_tb)
            sp = P()
            sp.addElement(Span(stylename=S_SUBTITLE_TEXT, text=data["subtitle"]))
            sub_tb.addElement(sp)
            page.addElement(sub_frame)

        # ── Content frame (bullets) ──────────────────────────────
        if stype not in ("title", "section"):
            content_frame = Frame(
                stylename=S_BOX,
                width="23.4cm", height="10.0cm",
                x="1.0cm", y="3.5cm",
            )
            content_frame.setAttrNS(PRESENTATIONNS, "class", "body")
            content_tb = TextBox()
            content_frame.addElement(content_tb)

            for bullet in data.get("bullets", []):
                bp = P()
                is_code = any(bullet.lstrip().startswith(tok) for tok in (
                    "podman ", "systemctl ", "journalctl ", "sudo ", "bash ",
                    "cp ", "mkdir ", "cat ", "printf ", "grep ", "curl ",
                    "chmod ", "read ", "uname ", "getenforce", "ip ",
                    "[", "Image=", "FROM ", "RUN ", "COPY ", "USER ", "CMD ",
                    "ENV ", "--", "-p ", "-v ", "-e ", "-d ",
                ))
                bp.addElement(Span(
                    stylename=S_CODE_TEXT if is_code else S_BULLET_TEXT,
                    text=bullet,
                ))
                content_tb.addElement(bp)

            page.addElement(content_frame)

        # ── Presenter notes ──────────────────────────────────────
        notes_text = data.get("notes", "")
        if notes_text:
            notes_el = Notes()

            # Slide thumbnail placeholder — required by LibreOffice Impress
            # to make the Notes panel visible at all.
            thumb_frame = Frame(
                stylename=S_BOX,
                width="17.0cm", height="12.57cm",
                x="2.06cm", y="1.14cm",
            )
            thumb_frame.setAttrNS(PRESENTATIONNS, "class", "page")
            notes_el.addElement(thumb_frame)

            # Notes text frame — positioned below the thumbnail
            notes_frame = Frame(
                stylename=S_BOX,
                width="17.0cm", height="11.0cm",
                x="2.06cm", y="14.36cm",
            )
            notes_frame.setAttrNS(PRESENTATIONNS, "class", "notes")
            notes_tb = TextBox()
            notes_frame.addElement(notes_tb)

            for para in textwrap.fill(notes_text, width=100).split("\n"):
                np = P()
                np.addElement(Span(stylename=S_NOTES_TEXT, text=para))
                notes_tb.addElement(np)

            notes_el.addElement(notes_frame)
            page.addElement(notes_el)

        # ── Footer: copyright line on every slide ─────────────────
        footer_frame = Frame(
            stylename=S_BOX,
            width="23.4cm", height="0.6cm",
            x="1.0cm", y="13.55cm",
        )
        footer_tb = TextBox()
        footer_frame.addElement(footer_tb)
        fp = P()
        fp.addElement(Span(
            stylename=S_COPYRIGHT_TEXT,
            text="\u00a9 2026 Jaco Steyn \u2014 Licensed under CC BY-SA 4.0 \u2014 Attribution Required",
        ))
        footer_tb.addElement(fp)
        page.addElement(footer_frame)

    # ── Build deck ────────────────────────────────────────────────
    for slide in slides:
        add_slide(slide)

    # ── Save ──────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(f"Saved {output_path}  ({len(slides)} slides)")


if __name__ == "__main__":
    import sys
    from collections import OrderedDict

    out_dir = sys.argv[1] if len(sys.argv) > 1 else "slides"
    os.makedirs(out_dir, exist_ok=True)

    # ── Per-module files ──────────────────────────────────────────
    # Preserve insertion order so files come out numbered correctly
    modules: "OrderedDict[str, list]" = OrderedDict()
    for slide in SLIDES:
        key = slide.get("module", "misc")
        modules.setdefault(key, []).append(slide)

    for module_key, module_slides in modules.items():
        out_path = os.path.join(out_dir, f"{module_key}.odp")
        build_presentation(out_path, module_slides)

    # ── Full combined deck ────────────────────────────────────────
    combined_path = os.path.join(out_dir, "podman-course.odp")
    build_presentation(combined_path, SLIDES)
    print(f"\nDone. {len(modules)} module files + 1 combined deck in '{out_dir}/'")
