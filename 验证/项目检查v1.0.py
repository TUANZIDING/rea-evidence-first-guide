#!/usr/bin/env python3
"""项目检查 v1.0：检查Markdown/HTML中的本地链接、图片与锚点，以及SVG可解析。
Project check v1.0: local links, images, anchors and SVG well-formedness. 不联网 / offline.
"""
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r'(?:\]\(([^)\s]+)\)|(?:href|src)="([^"]+)")')
errors = []


def anchors(text: str) -> set:
    return set(re.findall(r'<a id="([^"]+)"', text))


for md in ROOT.rglob("*.md"):
    if ".git" in md.parts:
        continue
    text = md.read_text(encoding="utf-8")
    for m in LINK.finditer(text):
        target = m.group(1) or m.group(2)
        if re.match(r"^(https?:|mailto:)", target):
            continue
        path, _, frag = target.partition("#")
        dest = (md.parent / unquote(path)).resolve() if path else md
        if not dest.exists():
            errors.append(f"{md.relative_to(ROOT)}: missing {target}")
            continue
        if frag and dest.suffix == ".md" and frag not in anchors(dest.read_text(encoding="utf-8")):
            errors.append(f"{md.relative_to(ROOT)}: missing anchor #{frag} in {path or md.name}")

for svg in ROOT.rglob("*.svg"):
    try:
        ET.parse(svg)
    except ET.ParseError as exc:
        errors.append(f"{svg.relative_to(ROOT)}: {exc}")

for name in ["README.md", "LICENSE", "文档/英文说明v1.0.md", "文档/十步工作流v1.0.md"]:
    if not (ROOT / name).exists():
        errors.append(f"missing required file {name}")

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("项目检查通过 / project check passed")
