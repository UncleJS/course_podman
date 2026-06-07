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

today = dt.date.today().isoformat()

parts: list[str] = []
parts.append("---\n")
parts.append('title: "Podman Zero-to-Expert Course"\n')
parts.append(f'date: "{today}"\n')
parts.append("---\n\n")

# Front matter
front = ["README.md", "COURSE_OUTLINE.md", "MODULES.md"]
parts.append(section("Front Matter"))
for i, fp in enumerate(front):
    p = root / fp
    parts.append(f"## {fp}\n\n")
    parts.append(read_text(p))
    parts.append("\n")
    if i != len(front) - 1:
        parts.append("\\newpage\n\n")

# Modules (each starts on a new page)
modules_list = extract_module_paths(read_text(root / "MODULES.md"))
parts.append("\\newpage\n\n")
parts.append(section("Modules"))
for fp in modules_list:
    parts.append("\\newpage\n\n")
    parts.append(read_text(root / fp))
    parts.append("\n")

# Cheatsheets
parts.append("\\newpage\n\n")
parts.append(section("Cheatsheets"))
for p in sorted((root / "cheatsheets").glob("*.md")):
    parts.append("\\newpage\n\n")
    parts.append(f"## {p.name}\n\n")
    parts.append(read_text(p))
    parts.append("\n")

# Assessments / Glossary / FAQ
appendix = ["ASSESSMENTS.md", "GLOSSARY.md", "FAQ.md"]
parts.append("\\newpage\n\n")
parts.append(section("Appendix"))
for fp in appendix:
    parts.append("\\newpage\n\n")
    parts.append(f"## {fp}\n\n")
    parts.append(read_text(root / fp))
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
