#!/usr/bin/env python
"""
Validate a minimal schema for catalog.yml.

Exit with non-zero status when required fields are missing or wrong type.

Rules (kept intentionally simple):
  - top-level `name` and `items` required
  - `items` must be a sequence
  - each item must include these keys: id, title (or filename), (file or path), type, version, description, tags (list), access, status

Usage: python scripts/validate_catalog.py -c catalog.yml
"""
from __future__ import annotations

import argparse
import sys
import pathlib
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    raise


def error(msg: str) -> None:
    print("ERROR:", msg, file=sys.stderr)


def validate_item(idx: int, item: dict[str, Any]) -> bool:
    ok = True
    prefix = f"items[{idx}]"

    # id
    if not item.get("id"):
        error(f"{prefix}: missing 'id'")
        ok = False

    # title or filename
    if not (item.get("title") or item.get("filename")):
        error(f"{prefix}: missing 'title' or 'filename'")
        ok = False

    # file or path
    if not (item.get("file") or item.get("path") or item.get("filename")):
        error(f"{prefix}: missing 'file' or 'path' or 'filename'")
        ok = False

    # type
    if not item.get("type"):
        error(f"{prefix}: missing 'type'")
        ok = False

    # version
    if not item.get("version"):
        error(f"{prefix}: missing 'version'")
        ok = False

    # description
    if not item.get("description"):
        error(f"{prefix}: missing 'description'")
        ok = False

    # tags must be list if present
    tags = item.get("tags")
    if tags is None:
        error(f"{prefix}: missing 'tags' (should be a list)")
        ok = False
    elif not isinstance(tags, (list, tuple)):
        error(f"{prefix}: 'tags' should be a list/sequence")
        ok = False

    # access and status
    if not item.get("access"):
        error(f"{prefix}: missing 'access'")
        ok = False
    if not item.get("status"):
        error(f"{prefix}: missing 'status'")
        ok = False

    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a catalog.yml file against a small schema")
    parser.add_argument("-c", "--catalog", default="catalog.yml", help="Path to catalog.yml")
    args = parser.parse_args(argv)

    p = pathlib.Path(__file__).parents[1] / args.catalog
    if not p.exists():
        error(f"catalog file not found at {p}")
        return 2

    try:
        doc = yaml.safe_load(p.read_text(encoding="utf-8"))
    except Exception as e:
        error(f"failed to parse YAML: {e}")
        return 3

    ok = True

    if not doc:
        error("catalog is empty or invalid YAML")
        return 4

    if not doc.get("name"):
        error("top-level 'name' is required")
        ok = False

    items = doc.get("items")
    if items is None:
        error("top-level 'items' is required and must be a sequence")
        return 5
    if not isinstance(items, (list, tuple)):
        error("top-level 'items' must be a sequence/list")
        return 6

    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            error(f"items[{idx}] should be a mapping/object")
            ok = False
            continue
        if not validate_item(idx, item):
            ok = False

    if not ok:
        error("Catalog schema validation failed")
        return 1

    print("catalog.yml schema validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
