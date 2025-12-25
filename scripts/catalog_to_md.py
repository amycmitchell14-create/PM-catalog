#!/usr/bin/env python
"""
Simple helper: read catalog/catalog.yml and output a Markdown summary.

Usage examples:
  # print to stdout
  python scripts/catalog_to_md.py

  # write to a file
  python scripts/catalog_to_md.py -o output.md

Requires: pyyaml (pip install pyyaml)
"""
from __future__ import annotations

import argparse
import pathlib
import sys

try:
    import yaml
except Exception:  # pragma: no cover - helpful error if pyyaml isn't installed
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise

def render_item_md(item):
    title = item.get("title", "Untitled")
    link = item.get("link", "")
    lines = []

    # Auto-generate GitHub Pages link for free items if file is present
    if item.get("access") == "free":
        if item.get("file"):
            safe_path = str(item["file"]).replace(" ", "%20")
            base_url = "https://amycmitchell14-create.github.io/catalog-paid/"
            link = base_url + safe_path
        lines.append(f"- [{title}]({link})")
    elif item.get("access") == "paid":
        lines.append(f"- [{title}]({link}) 🔒")
    else:
        lines.append(f"- {title}")

    # Description
    if item.get("description"):
        lines.append(f"  *{item['description']}*")

    # Metadata
    meta = []
    if item.get("type"):
        meta.append(f"**Type:** {item['type']}")
    if item.get("version"):
        meta.append(f"**Version:** {item['version']}")
    if item.get("status"):
        meta.append(f"**Status:** {item['status']}")
    if item.get("access"):
        meta.append(f"**Access:** {item['access']}")

    if meta:
        lines.append("  " + ", ".join(meta))

    # Tags
    tags = item.get("tags")
    if isinstance(tags, (list, tuple)) and tags:
        tags_line = ", ".join(str(t) for t in tags)
        lines.append(f"  **Tags:** {tags_line}")

    # File reference
    if item.get("file"):
        filename = item.get("filename") or "Download"
        lines.append(f"  **File:** [{filename}]({item['file']})")

    return "\n".join(lines)

    # tags
    tags = item.get("tags")
    if isinstance(tags, (list, tuple)) and tags:
        lines.append("")
        tags_line = ", ".join(str(t) for t in tags)
        lines.append(f"**Tags:** {tags_line}")

    # file/path link as clickable Markdown
    paths = item.get("file") or item.get("path") or item.get("filename")
    filename = item.get("filename") or "Download"
    if paths:
      lines.append("")
      lines.append(f"**File:** [{filename}]({paths})")

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="catalog_to_md", description="Render catalog/catalog.yml to Markdown")
    parser.add_argument("-c", "--catalog", default="catalog.yml", help="Path to catalog.yml (default: catalog.yml)")
    parser.add_argument("-o", "--output", help="Write markdown to this file (stdout if omitted)")
    args = parser.parse_args(argv)

    catalog_path = pathlib.Path(args.catalog)
    if not catalog_path.exists():
        print(f"Error: catalog file not found at {catalog_path}", file=sys.stderr)
        return 2

    with catalog_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    out_lines = [f"# {data.get('name', 'Catalog')}"]
    if data.get("description"):
        out_lines.append("")
        out_lines.append(data["description"])

    maint = data.get("maintainer")
    if maint:
        out_lines.append("")
        mn = maint.get("name") or ""
        me = maint.get("email")
        if me:
            out_lines.append(f"**Maintainer:** {mn} <{me}>")
        else:
            out_lines.append(f"**Maintainer:** {mn}")

    items = data.get("items") or []
    if not items:
        out_lines.append("\n## Items\n\n*(no items found in catalog.yml)*")
    else:
        # Group by access and type
        access_groups = {"free": "🟢 Free Content", "paid": "🔒 Paid Content"}
        type_groups = {"slide-deck": "🎤 Slide Decks", "learning-path": "📖 Learning Paths", "quick-start": "📝 Quick Starts"}

        for access, access_label in access_groups.items():
            out_lines.append(f"\n## {access_label}\n")
            for t, t_label in type_groups.items():
                section_items = [i for i in items if i.get("access") == access and i.get("type") == t]
                if section_items:
                    out_lines.append(f"### {t_label}\n")
                    for item in section_items:
                        out_lines.append(render_item_md(item))

    md = "\n".join(out_lines)

    # Ensure public folder exists
    public_dir = pathlib.Path("public")
    public_dir.mkdir(exist_ok=True)

    # Always write index.md for GitHub Pages
    index_path = pathlib.Path("index.md")
    index_path.write_text(md, encoding="utf-8")
    print(f"Wrote Markdown to {index_path}")

    return 0

    # maintainer
    maint = data.get("maintainer")
    if maint:
        out_lines.append("")
        mn = maint.get("name") or ""
        me = maint.get("email")
        if me:
            out_lines.append(f"**Maintainer:** {mn} <{me}>")
        else:
            out_lines.append(f"**Maintainer:** {mn}")

    out_lines.append("")
    out_lines.append("## Items")
    out_lines.append("")

    items = data.get("items") or []
    if not items:
        out_lines.append("*(no items found in catalog.yml)*")

    for item in items:
        out_lines.append(render_item_md(item))

    md = "\n".join(out_lines)

    if args.output:
        p = pathlib.Path(args.output)
        p.write_text(md, encoding="utf-8")
        print(f"Wrote Markdown to {p}")
    else:
        print(md)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
