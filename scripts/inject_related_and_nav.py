#!/usr/bin/env python3
"""
Generate and inject Related Articles and Back-to-List (with filter preservation)
into all 208 article HTML pages.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = BASE_DIR / "manifest.json"
ARTICLES_DIR = BASE_DIR / "articles"

def clean_summary(text, title):
    if not text:
        return ""
    # Remove "Title — " or "Title - "
    t_pattern = re.escape(title) + r'\s*[—–\-]\s*'
    cleaned = re.sub(r'^' + t_pattern, '', text).strip()
    return cleaned[:140] + ("…" if len(cleaned) > 140 else "")

def main():
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    items = manifest["items"]
    by_type = defaultdict(list)
    by_year = defaultdict(list)
    items_by_id = {}
    descriptions = {}

    print("Loading articles metadata and summaries...")
    for item in items:
        by_type[item.get("type", "record")].append(item)
        by_year[item["date"][:4]].append(item)
        items_by_id[item["id"]] = item

        # Read description from existing article HTML
        html_path = BASE_DIR / item["local_url"]
        if html_path.exists():
            with open(html_path, "r", encoding="utf-8") as hf:
                content = hf.read()
                m = re.search(r'<meta name="description" content="([^"]+)"', content)
                if m:
                    desc = m.group(1)
                    descriptions[item["id"]] = clean_summary(desc, item["title"])
                else:
                    descriptions[item["id"]] = ""

    print(f"Total articles to process: {len(items)}")

    # Process each article
    for item in items:
        html_path = BASE_DIR / item["local_url"]
        if not html_path.exists():
            continue

        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        # Calculate candidates
        t = item.get("type", "record")
        y = item["date"][:4]

        same_type = [it for it in by_type[t] if it["id"] != item["id"]]
        same_year = [it for it in by_year[y] if it["id"] != item["id"] and it not in same_type]

        candidates = same_type[:5]
        if len(candidates) < 3:
            candidates += same_year[:(5 - len(candidates))]

        # Build Related Articles HTML
        rel_items_html = []
        for c in candidates:
            c_file = Path(c["local_url"]).name
            c_title = c["title"]
            c_date_label = c["date"][:10].replace("-", ".")
            c_type_label = c.get("type_label", "記録")
            c_summary = descriptions.get(c["id"], "")

            summary_html = f'<p class="related-summary">{c_summary}</p>' if c_summary else ''
            rel_items_html.append(
                f'<li class="related-item">'
                f'<a class="related-link" href="{c_file}">'
                f'<span class="related-title">{c_title}</span>'
                f'<span class="related-meta"><time datetime="{c["date"]}">{c_date_label}</time> · <span class="related-tag">[{c_type_label}]</span></span>'
                f'</a>'
                f'{summary_html}'
                f'</li>'
            )

        related_section = (
            f'\n<section class="related-articles" aria-labelledby="related-heading">\n'
            f'<h2 id="related-heading">関連記事 / Related articles</h2>\n'
            f'<ul class="related-list">\n'
            + "\n".join(rel_items_html)
            + f'\n</ul>\n</section>\n'
        )

        # Back link HTML with inline session storage check
        back_link_html = (
            '<div class="back-nav"><a href="../" class="back-to-list" id="backToListLink">← アーカイブ一覧 / Back to archive</a></div>\n'
            '<script>(function(){var s=sessionStorage.getItem("archive_last_search");var a=document.getElementById("backToListLink");if(s&&a)a.href="../"+s;})();</script>'
        )

        # Check if already injected
        # 1) Back link: inject inside <header> right after <nav class="site-nav">...</nav>
        if 'id="backToListLink"' not in html_content:
            site_nav_end = html_content.find('</nav>')
            if site_nav_end != -1:
                insert_pos = site_nav_end + len('</nav>')
                html_content = html_content[:insert_pos] + "\n" + back_link_html + html_content[insert_pos:]

        # 2) Related section: inject right before <nav class="article-nav"
        if 'class="related-articles"' in html_content:
            # Replace existing related-articles section
            html_content = re.sub(r'<section class="related-articles".*?</section>\n?', related_section, html_content, flags=re.DOTALL)
        else:
            nav_pos = html_content.find('<nav class="article-nav"')
            if nav_pos != -1:
                html_content = html_content[:nav_pos] + related_section + html_content[nav_pos:]
            else:
                footer_pos = html_content.find('<footer>')
                if footer_pos != -1:
                    html_content = html_content[:footer_pos] + related_section + html_content[footer_pos:]

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    print("All 208 articles updated with related articles and back-to-list links successfully!")

if __name__ == "__main__":
    main()
