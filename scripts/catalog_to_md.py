#!/usr/bin/env python
"""
Simple helper: read catalog/catalog.yml and output a Markdown summary.
"""

from __future__ import annotations
import argparse
import pathlib
import sys
import yaml

from urllib.parse import quote

# GitHub Pages base URL (public-facing)
GITHUB_PAGES_BASE = "https://amycmitchell14-create.github.io/PM-catalog/"

# GitHub raw file base URL (direct file download)
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/amycmitchell14-create/PM-catalog/main/"

def render_item_md(item):
    title = item.get("title", "Untitled")
    raw_link = item.get("link")
    file_path = item.get("file") or item.get("filename")

    # Ignore placeholder file paths
    if file_path in ("not available", "paid subscribers only"):
        file_path = None

    # Determine if link is external
    is_external_link = bool(
        raw_link and (raw_link.startswith("http://") or raw_link.startswith("https://"))
    )

    # External links should NOT be encoded
    if is_external_link:
        safe_link = raw_link
    else:
        # Local link value (e.g., "content/foo.pdf") if present
        safe_link = quote(raw_link) if raw_link else None

    # Encode file path for GitHub URLs
    safe_file = quote(file_path) if file_path else None

    # --- TARGET LINK LOGIC FOR TITLE ---
    if item.get("access") == "paid":
        # Paid items ALWAYS use explicit external link
        target = safe_link or ""
    else:
        # Free items:
        if is_external_link and safe_link:
            # If user explicitly gave an external link, honor it
            target = safe_link
        else:
            # Otherwise, use GitHub Pages URL based on file path (preferred)
            if safe_file:
                target = GITHUB_PAGES_BASE + safe_file
            elif safe_link:
                # Fallback: if only a local link exists, treat it as a path on Pages
                target = GITHUB_PAGES_BASE + safe_link
            else:
                target = ""

    lines = []

    lock = " 🔒" if item.get("access") == "paid" else ""
    lines.append(f"#### 📄 [{title}]({target}){lock}")

    # Description
    description = item.get("description")
    if description:
        lines.append(f"*{description}*")
        lines.append("")

    # Metadata
    for key in ("type", "version", "status", "access"):
        if item.get(key):
            lines.append(f"- **{key.capitalize()}:** {item[key]}")

    # Tags
    tags = item.get("tags")
    if tags:
        lines.append(f"- **Tags:** {', '.join(tags)}")

    # File reference
    if safe_file:
        filename = item.get("filename") or file_path.split("/")[-1]
        public_file_url = GITHUB_RAW_BASE + safe_file
        lines.append(f"- **File:** [{filename}]({public_file_url})")
    else:
        if item.get("access") == "paid":
            lines.append("- **File:** *paid subscribers only*")

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