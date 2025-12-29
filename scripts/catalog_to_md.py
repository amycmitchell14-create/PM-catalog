#!/usr/bin/env python
"""
Simple helper: read catalog/catalog.yml and output a Markdown summary.
"""

from __future__ import annotations
import argparse
import pathlib
import sys
import yaml


def render_item_md(item):
    title = item.get("title", "Untitled")
    link = item.get("link", "")
    description = item.get("description", "")
    access = item.get("access", "")
    file_path = item.get("file") or item.get("filename") or None

    # URL-encode spaces for GitHub Pages links
    safe_file = file_path.replace(" ", "%20") if file_path else None

    lines = []

    # H4 item title
    lock = " 🔒" if access == "paid" else ""
    lines.append(f"#### 📄 [{title}]({link}){lock}")

    # Description
    if description:
        lines.append(f"*{description}*")
        lines.append("")

    # Metadata bullets
    meta = []
    if item.get("type"):
        meta.append(f"- **Type:** {item['type']}")
    if item.get("version"):
        meta.append(f"- **Version:** {item['version']}")
    if item.get("status"):
        meta.append(f"- **Status:** {item['status']}")
    if item.get("access"):
        meta.append(f"- **Access:** {item['access']}")

    lines.extend(meta)

    # Tags
    tags = item.get("tags")
    if isinstance(tags, (list, tuple)) and tags:
        tag_list = ", ".join(tags)
        lines.append(f"- **Tags:** {tag_list}")

    # File reference
    if safe_file:
        filename = item.get("filename") or safe_file.split("/")[-1]
        lines.append(f"- **File:** [{filename}]({safe_file})")
    elif access == "paid":
        lines.append("- **File:** *paid subscribers only*")

    # Divider
    lines.append("\n---\n")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="catalog_to_md",
        description="Render catalog/catalog.yml to Markdown"
    )
    parser.add_argument("-c", "--catalog", default="catalog.yml")
    parser.add_argument("-o", "--output")
    args = parser.parse_args(argv)

    catalog_path = pathlib.Path(args.catalog)
    if not catalog_path.exists():
        print(f"Error: catalog file not found at {catalog_path}", file=sys.stderr)
        return 2

    with catalog_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    # Header
    out_lines = [f"# {data.get('name', 'Catalog')}"]
    if data.get("description"):
        out_lines.append("")
        out_lines.append(data["description"])

    # Maintainer
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

    # ---------------------------
    # FAQ SECTION (always first)
    # ---------------------------
    faq_items = [i for i in items if i.get("type") == "info-type"]
    if faq_items:
        out_lines.append("\n## ❓ Frequently Asked Questions\n")
        for item in faq_items:
            out_lines.append(render_item_md(item))

    # ---------------------------
    # GROUPED CONTENT
    # ---------------------------
    access_groups = {
        "free": "🟢 Free Content",
        "paid": "🔒 Paid Content"
    }

    type_groups = {
        "slide-deck": "🎤 Slide Decks",
        "learning-path": "📖 Learning Paths",
        "quick-start": "📝 Quick Starts"
    }

    for access, access_label in access_groups.items():
        out_lines.append(f"\n## {access_label}\n")

        for t, t_label in type_groups.items():
            section_items = [
                i for i in items
                if i.get("access") == access
                and i.get("type") == t
            ]

            if section_items:
                out_lines.append(f"### {t_label}\n")
                for item in section_items:
                    out_lines.append(render_item_md(item))

    # Write output
    md = "\n".join(out_lines)

    index_path = pathlib.Path("index.md")
    index_path.write_text(md, encoding="utf-8")
    print(f"Wrote Markdown to {index_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())