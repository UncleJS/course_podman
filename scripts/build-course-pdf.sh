#!/usr/bin/env bash
set -euo pipefail

# Build a single course PDF using a Podman container (no host pandoc install).
# Output: dist/course_podman.pdf

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
OUT_DIR="$ROOT_DIR/dist"
OUT_MD="$OUT_DIR/course_podman.md"
OUT_PDF="$OUT_DIR/course_podman.pdf"

OUT_MD_IN_CONTAINER="dist/course_podman.md"
OUT_PDF_IN_CONTAINER="dist/course_podman.pdf"

mkdir -p "$OUT_DIR"

ROOT_DIR="$ROOT_DIR" python3 - <<'PY'
from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path

root = Path(os.environ["ROOT_DIR"]).resolve()
out_md = root / "dist" / "course_podman.md"

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

out_md.write_text("".join(parts), encoding="utf-8")
print(str(out_md))
PY

# Build inside a container so the host does not need pandoc/LaTeX.
podman run --rm \
  -v "$ROOT_DIR:/data:Z" \
  -w /data \
  docker.io/pandoc/latex:latest \
    "$OUT_MD_IN_CONTAINER" \
    -o "$OUT_PDF_IN_CONTAINER" \
    --from markdown \
    --toc \
    --toc-depth=2 \
    --number-sections \
    -V geometry:margin=1in

printf '%s\n' "Wrote: $OUT_PDF"
