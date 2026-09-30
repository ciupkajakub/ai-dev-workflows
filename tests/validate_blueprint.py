#!/usr/bin/env python3
"""Check the repository's Markdown structure and local links without running agents."""

from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]


def markdown_structure(path):
    anchors = set()
    occurrences = {}
    prose = []
    errors = []
    fence = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, tail = marker.groups()
            if fence is None:
                fence = (run[0], len(run), number)
            elif run[0] == fence[0] and len(run) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence:
            continue
        prose.append((number, line))
        heading = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            slug = re.sub(r"[^\w\- ]", "", heading[1].lower()).replace(" ", "-")
            count = occurrences.get(slug, 0)
            occurrences[slug] = count + 1
            anchors.add(f"{slug}-{count}" if count else slug)
    if fence:
        errors.append(f"{path.relative_to(ROOT)}:{fence[2]}: unclosed code fence")
    return anchors, prose, errors


def main():
    documents = sorted(ROOT.glob("*.md"))
    structures = {path: markdown_structure(path) for path in documents}
    errors = [error for _, _, found in structures.values() for error in found]
    for name in ("README.md", "feature_execution_blueprint.md"):
        if not (ROOT / name).is_file():
            errors.append(f"missing document: {name}")
    links_checked = 0
    for path, (_, prose, _) in structures.items():
        for number, line in prose:
            for raw in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", line):
                link = urlsplit(raw.strip("<>"))
                if link.scheme or link.netloc:
                    continue
                target = (path.parent / unquote(link.path)).resolve() if link.path else path
                links_checked += 1
                location = f"{path.relative_to(ROOT)}:{number}"
                if not target.is_relative_to(ROOT):
                    errors.append(f"{location}: local link escapes repository: {raw}")
                elif not target.is_file():
                    errors.append(f"{location}: missing local link target: {raw}")
                elif link.fragment and target.suffix == ".md":
                    target_structure = structures.get(target)
                    if target_structure is None:
                        target_structure = markdown_structure(target)
                    if unquote(link.fragment) not in target_structure[0]:
                        errors.append(f"{location}: missing heading anchor: {raw}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Checked {len(documents)} Markdown files and {links_checked} local links.")
    print("Structure is valid. Agent behavior and project delivery were not evaluated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
