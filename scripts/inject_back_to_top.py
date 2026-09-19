#!/usr/bin/env python3
"""
Add id="top" to <body> and inject Back-to-Top button before <footer> in all article pages.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLES_DIR = BASE_DIR / "articles"

BTN_HTML = '''<div class="article-footer-nav">
<a class="back-to-top-link" href="#top">↑ ページの先頭へ / Back to top</a>
</div>\n'''

def main():
    article_files = sorted(ARTICLES_DIR.glob("*.html"))
    print(f"Processing {len(article_files)} articles...")

    updated = 0
    skipped = 0

    for fpath in article_files:
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        if 'class="back-to-top-link"' in content:
            skipped += 1
            continue

        # 1. Ensure <body id="top">
        if '<body id="top">' not in content:
            content = content.replace("<body>", '<body id="top">', 1)

        # 2. Inject button right before <footer>
        footer_idx = content.find("<footer>")
        if footer_idx != -1:
            content = content[:footer_idx] + BTN_HTML + content[footer_idx:]
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            updated += 1
        else:
            print(f"Warning: No <footer> in {fpath.name}")

    print(f"Finished: {updated} updated, {skipped} skipped.")

if __name__ == "__main__":
    main()
