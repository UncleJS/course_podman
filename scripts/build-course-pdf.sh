#!/usr/bin/env bash
set -euo pipefail

# Build a single course PDF using Podman containers only:
# no host pandoc/LaTeX, no host python, no bind mounts (named-volume staging).
# Output: dist/course_podman.md + dist/course_podman.pdf

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT_DIR="$ROOT_DIR/dist"
VOLUME="course-build-pdf"
PYTHON_IMAGE="docker.io/library/python:3-alpine"
PANDOC_IMAGE="docker.io/pandoc/latex:latest"

mkdir -p "$OUT_DIR"

cleanup() {
  podman rm -f course-pdf-stage course-pdf-extract >/dev/null 2>&1 || true
  podman volume rm -f "$VOLUME" >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

# Stage the repo into a named volume (no bind mounts).
podman volume create "$VOLUME" >/dev/null
podman create --name course-pdf-stage -v "$VOLUME":/work "$PYTHON_IMAGE" true >/dev/null
podman cp "$ROOT_DIR/." course-pdf-stage:/work/
podman rm course-pdf-stage >/dev/null

# Assemble dist/course_podman.md inside a container (no host python).
podman run --rm -i -v "$VOLUME":/work -e ROOT_DIR=/work "$PYTHON_IMAGE" python3 - <<'PY'
from __future__ import annotations

import datetime as dt
import os
import re
import sys
from pathlib import Path

root = Path(os.environ["ROOT_DIR"]).resolve()
out_md = root / "dist" / "course_podman.md"
out_md.parent.mkdir(parents=True, exist_ok=True)

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8")

def extract_module_paths(modules_md: str) -> list[str]:
    # Lines look like: - `modules/00-setup.md`
    paths: list[str] = []
    for line in modules_md.splitlines():
        m = re.search(r"`(modules/[^`]+\.md)`", line)
        if m:
            paths.append(m.group(1))
    return paths

def section(title: str) -> str:
    return f"# {title}\n\n"

# Pandoc auto-ids are not GitHub slugs: an em dash becomes a different
# identifier, a heading that starts with a digit is not a valid LaTeX label,
# and repeated titles (Learning Goals, Checkpoint) all point at the first copy.
# Stamp an explicit id on each heading of one source file and rewrite that
# file's ](#slug) links to it. Sources are unchanged.
FENCE = re.compile(r"^```[^\n]*\n.*?^```[ \t]*$", re.M | re.S)
# [ \t] only: \s would swallow the newline and glue {#id} onto the next fence.
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*$", re.M)
LINK = re.compile(r"\]\(#([^)\s]+)\)")
HTML_TOC = re.compile(r'^<a id="table-of-contents"></a>\n?', re.M)
EXPLICIT_ID = re.compile(r"\{#([A-Za-z][A-Za-z0-9_-]*)\}\s*$")


def prefix_for(rel: str) -> str:
    path = Path(rel)
    if rel.startswith("modules/"):
        token = path.stem.split("-", 1)[0]
        return "m" + token
    if rel.startswith("cheatsheets/"):
        return "cs-" + path.stem
    names = {
        "README.md": "readme",
        "COURSE_OUTLINE.md": "outline",
        "MODULES.md": "modules",
        "ASSESSMENTS.md": "assess",
        "GLOSSARY.md": "glossary",
        "FAQ.md": "faq",
    }
    return names.get(rel, "x-" + path.stem)


def slug_variants(title: str) -> set[str]:
    title = EXPLICIT_ID.sub("", title).strip().replace("`", "").lower()
    # Drop punctuation. An em dash disappears and the spaces beside it stay,
    # so "Linger — Boot" becomes linger--boot. A second pass turns the dash
    # into a space and then collapses, which is the other slug the TOCs use.
    deleted = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    spaced = title.replace("—", " ").replace("–", " ").replace("−", " ")
    spaced = re.sub(r"[^\w\s-]", "", spaced, flags=re.UNICODE).strip()
    out: set[str] = set()
    for raw in (deleted, spaced):
        if not raw:
            continue
        each = raw.replace(" ", "-")
        collapsed = re.sub(r"\s+", "-", raw)
        out.add(each)
        out.add(collapsed)
        out.add(re.sub(r"-{2,}", "-", each))
        out.add(re.sub(r"-{2,}", "-", collapsed))
    out.discard("")
    return out


def primary_slug(title: str) -> str:
    title = EXPLICIT_ID.sub("", title).strip().replace("`", "").lower()
    deleted = re.sub(r"[^\w\s-]", "", title, flags=re.UNICODE).strip()
    slug = deleted.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9_-]", "", slug)
    return slug or "section"


def anchorize(text: str, prefix: str) -> str:
    pieces: list[tuple[str, str]] = []
    pos = 0
    for m in FENCE.finditer(text):
        pieces.append(("text", text[pos:m.start()]))
        pieces.append(("fence", m.group(0)))
        pos = m.end()
    pieces.append(("text", text[pos:]))
    pieces = [
        ("text", HTML_TOC.sub("", chunk)) if kind == "text" else (kind, chunk)
        for kind, chunk in pieces
    ]

    found: list[tuple[int, re.Match[str]]] = []
    for i, (kind, chunk) in enumerate(pieces):
        if kind != "text":
            continue
        for m in HEADING.finditer(chunk):
            found.append((i, m))

    used: set[str] = set()
    frag_map: dict[str, str] = {}
    assigned: list[tuple[int, re.Match[str], str | None]] = []
    for i, m in found:
        title = m.group(2)
        existing = EXPLICIT_ID.search(title)
        if existing:
            eid = existing.group(1)
            assigned.append((i, m, None))
        else:
            eid = f"{prefix}-{primary_slug(title)}"
            if not eid[:1].isalpha():
                eid = "s" + eid
            base = eid
            n = 2
            while eid in used:
                eid = f"{base}-{n}"
                n += 1
            assigned.append((i, m, eid))
        used.add(eid)
        for variant in slug_variants(title):
            frag_map.setdefault(variant, eid)

    by_piece: dict[int, list[tuple[re.Match[str], str | None]]] = {}
    for i, m, eid in assigned:
        by_piece.setdefault(i, []).append((m, eid))

    rebuilt: list[str] = []
    unmapped: set[str] = set()
    for i, (kind, chunk) in enumerate(pieces):
        if kind != "text":
            rebuilt.append(chunk)
            continue
        for m, eid in reversed(by_piece.get(i, [])):
            if eid is None:
                continue
            chunk = chunk[: m.end()] + " {#" + eid + "}" + chunk[m.end() :]

        def repl(match: re.Match[str], mapping: dict[str, str] = frag_map) -> str:
            frag = match.group(1)
            eid = mapping.get(frag)
            if eid is None:
                unmapped.add(frag)
                return match.group(0)
            return "](#" + eid + ")"

        rebuilt.append(LINK.sub(repl, chunk))
    if unmapped:
        print(f"unmapped #{prefix}: " + ", ".join(sorted(unmapped)), file=sys.stderr)
    return "".join(rebuilt)


def add(text: str, prefix: str) -> None:
    parts.append(anchorize(text, prefix))


today = dt.date.today().isoformat()

parts: list[str] = []
parts.append("---\n")
parts.append('title: "Podman Zero-to-Expert Course"\n')
parts.append(f'date: "{today}"\n')
parts.append("---\n\n")

# Front matter
front = ["README.md", "COURSE_OUTLINE.md", "MODULES.md"]
add(section("Front Matter"), "book")
for i, fp in enumerate(front):
    add(f"## {fp}\n\n", "book")
    add(read_text(root / fp), prefix_for(fp))
    parts.append("\n")
    if i != len(front) - 1:
        parts.append("\\newpage\n\n")

# Modules (each starts on a new page)
modules_list = extract_module_paths(read_text(root / "MODULES.md"))
parts.append("\\newpage\n\n")
add(section("Modules"), "book")
for fp in modules_list:
    parts.append("\\newpage\n\n")
    add(read_text(root / fp), prefix_for(fp))
    parts.append("\n")

# Cheatsheets
parts.append("\\newpage\n\n")
add(section("Cheatsheets"), "book")
for p in sorted((root / "cheatsheets").glob("*.md")):
    rel = str(p.relative_to(root))
    parts.append("\\newpage\n\n")
    add(f"## {p.name}\n\n", "book")
    add(read_text(p), prefix_for(rel))
    parts.append("\n")

# Assessments / Glossary / FAQ
appendix = ["ASSESSMENTS.md", "GLOSSARY.md", "FAQ.md"]
parts.append("\\newpage\n\n")
add(section("Appendix"), "book")
for fp in appendix:
    parts.append("\\newpage\n\n")
    add(f"## {fp}\n\n", "book")
    add(read_text(root / fp), prefix_for(fp))
    parts.append("\n")

# Transliterate symbols pdflatex cannot typeset (sources keep the Unicode;
# only this combined build output is downgraded to ASCII equivalents).
LATEX_SAFE = {
    "↑": "^",      # ↑ (Go to TOC links)
    "→": "->",     # →
    "←": "<-",     # ←
    "≥": ">=",     # ≥
    "≤": "<=",     # ≤
    "✅": "[OK]",   # ✅
    "❌": "[X]",    # ❌
    "⚠": "(!)",    # ⚠
    "️": "",       # variation selector (emoji presentation)
}
text = "".join(parts)
for char, repl in LATEX_SAFE.items():
    text = text.replace(char, repl)

out_md.write_text(text, encoding="utf-8")
print(str(out_md))
PY

# Render the PDF inside the pandoc/latex container (volume, not bind mount).
podman run --rm \
  -v "$VOLUME":/work \
  -w /work \
  "$PANDOC_IMAGE" \
    dist/course_podman.md \
    -o dist/course_podman.pdf \
    --from markdown \
    --toc \
    --toc-depth=2 \
    --number-sections \
    -V geometry:margin=1in

# Extract the artifacts back out of the volume.
podman create --name course-pdf-extract -v "$VOLUME":/work "$PYTHON_IMAGE" true >/dev/null
podman cp course-pdf-extract:/work/dist/course_podman.md "$OUT_DIR/"
podman cp course-pdf-extract:/work/dist/course_podman.pdf "$OUT_DIR/"

printf '%s\n' "Wrote: $OUT_DIR/course_podman.md" "Wrote: $OUT_DIR/course_podman.pdf"
