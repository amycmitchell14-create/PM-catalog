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


def render_item_md(item: dict) -> str:
    lines = []
    title = item.get("title") or item.get("filename") or item.get("id")
    lines.append(f"### {title}")

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
        lines.append(" | ".join(meta))

    if item.get("description"):
        lines.append("")
        lines.append(item["description"])

    # tags
    tags = item.get("tags")
    if isinstance(tags, (list, tuple)) and tags:
        lines.append("")
        tags_line = ", ".join(str(t) for t in tags)
        lines.append(f"**Tags:** {tags_line}")

    # file/path link
    paths = item.get("file") or item.get("path") or item.get("filename")
    if paths:
        lines.append("")
        lines.append(f"**File:** `{paths}`")

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="catalog_to_md", description="Render catalog/catalog.yml to Markdown")
    parser.add_argument("-c", "--catalog", default="catalog.yml", help="Path to catalog.yml (default: catalog.yml)")
    parser.add_argument("-o", "--output", help="Write markdown to this file (stdout if omitted)")
    args = parser.parse_args(argv)

    catalog_path = pathlib.Path(__file__).parents[1] / args.catalog
    if not catalog_path.exists():
        print(f"Error: catalog file not found at {catalog_path}", file=sys.stderr)
        return 2

    with catalog_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)

    out_lines = []
    out_lines.append(f"# {data.get('name', 'Catalog')}")
    if data.get("description"):
        out_lines.append("")
        out_lines.append(data["description"])

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
