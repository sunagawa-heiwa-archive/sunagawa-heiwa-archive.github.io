#!/usr/bin/env python3
"""
Inject citation copy button into all 208 article HTML pages in <div class="source">.
Format: 《Title. 砂川平和ひろば公開記事アーカイブ (YYYY-MM-DD). URL》
"""

import re
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLES_DIR = BASE_DIR / "articles"
BASE_URL = "https://sunagawa-heiwa-archive.github.io/"

def main():
    article_files = sorted(ARTICLES_DIR.glob("*.html"))
    print(f"Found {len(article_files)} articles to process...")

    updated = 0
    skipped = 0

    for fpath in article_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        if 'data-format="capsule-cite"' in content:
            skipped += 1
            continue

        h1_m = re.search(r'<article><h1>(.*?)</h1>', content, re.DOTALL)
        if not h1_m:
            continue
        title = html.unescape(re.sub(r'<[^>]+>', '', h1_m.group(1))).strip()

        time_m = re.search(r'<time datetime="([^"]+)"', content)
        iso_date = time_m.group(1)[:10] if time_m else ""

        slug = fpath.stem
        archive_url = f"{BASE_URL}articles/{slug}.html"

        cite_text = f"《{title}. 砂川平和ひろば公開記事アーカイブ ({iso_date}). {archive_url}》"

        btn_html = (
            f' · <button type="button" class="cite-btn capsule-cite" data-format="capsule-cite" '
            f'data-copy-cite="{html.escape(cite_text, quote=True)}" '
            f'aria-label="Copy citation / 引用形式をコピー">📋 引用形式をコピー</button>'
        )

        src_m = re.search(r'(<div class="source">.*?)(</div>)', content, re.DOTALL)
        if src_m:
            content = content[:src_m.start(2)] + btn_html + content[src_m.start(2):]

        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

        updated += 1

    print(f"Finished: {updated} updated, {skipped} skipped.")

if __name__ == "__main__":
    main()
