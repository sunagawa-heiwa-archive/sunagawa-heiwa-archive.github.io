#!/usr/bin/env python3
"""Check that every internal link and image in the site's HTML files resolves.

Usage: python3 scripts/check_links.py [site_root]
Exit code 0 = all internal references resolve, 1 = broken references found.
External links (http/https/mailto/etc.) are not checked.
"""
import os
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
SKIP_DIRS = {".git", "raw", "obsidian", "node_modules"}
ATTR_RE = re.compile(r'''(?:href|src)\s*=\s*["']([^"'#?]+)[^"']*["']''', re.IGNORECASE)
EXTERNAL = ("http://", "https://", "//", "mailto:", "tel:", "data:", "javascript:")


def resolve(page_path, ref):
    ref = unquote(ref.strip())
    if ref.startswith("/"):
        target = os.path.join(ROOT, ref.lstrip("/"))
    else:
        target = os.path.join(os.path.dirname(page_path), ref)
    target = os.path.normpath(target)
    if os.path.isdir(target):
        target = os.path.join(target, "index.html")
    return target


def main():
    broken = []
    pages = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if not name.endswith(".html") or " 2." in name:
                continue
            page = os.path.join(dirpath, name)
            pages += 1
            with open(page, encoding="utf-8", errors="replace") as fh:
                html = fh.read()
            for ref in ATTR_RE.findall(html):
                if not ref.strip() or ref.lower().startswith(EXTERNAL) or urlparse(ref).scheme:
                    continue
                if not os.path.exists(resolve(page, ref)):
                    broken.append((os.path.relpath(page, ROOT), ref))
    for page, ref in broken:
        print(f"BROKEN  {page}  ->  {ref}")
    print(f"Checked {pages} pages: {len(broken)} broken internal reference(s).")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
