#!/usr/bin/env python3
"""Point every page at the new list page (archive.html) after the P1-6 split.

Companion to scripts/split-archive-list.py.  Three kinds of links move:

  * the site navigation gains a distinct "Articles / 記事一覧" entry, and the
    old first entry is renamed to "Home / トップ" (it still links to "/", which
    is now the portal rather than the list);
  * article pages' "back to the archive" / "back to search" links go straight to
    archive.html, including the sessionStorage-restored filter state;
  * editorial pages' "/?q=..." deep links become "archive.html?q=..." so a
    shared search link opens the list page directly.

404.html keeps "/" as the site top and only its search link moves.

Idempotent: skips pages that already carry the new navigation entry.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'articles').glob('*.html'))
SKIP = {'index.html', 'archive.html'}

NAV_ITEM = 'Articles / 記事一覧'
changed = {'nav': 0, 'back': 0, 'deep': 0}
skipped = []

for p in PAGES:
    if p.name in SKIP:
        continue
    s = orig = p.read_text(encoding='utf-8')
    is_article = p.parent.name == 'articles'

    # ---- 1. site navigation -------------------------------------------------
    if NAV_ITEM not in s:
        if is_article:
            old = '<a href="../">Archive / アーカイブ</a>'
            new = '<a href="../">Home / トップ</a>\n<a href="../archive.html">Articles / 記事一覧</a>'
        elif p.name == '404.html':
            old = '<a href="/">Archive / アーカイブ</a>'
            new = '<a href="/">Home / トップ</a>\n<a href="/archive.html">Articles / 記事一覧</a>'
        else:
            old = '<a href="./">Archive / アーカイブ</a>'
            new = '<a href="./">Home / トップ</a>\n<a href="archive.html">Articles / 記事一覧</a>'
        if old in s:
            s = s.replace(old, new, 1)
            changed['nav'] += 1
        else:
            skipped.append(f'{p.name}: nav anchor not found')

    # ---- 2. article pages: back to the list, not the portal ------------------
    if is_article:
        before = s
        s = s.replace('<div class="back-nav"><a href="../" class="back-to-list"',
                      '<div class="back-nav"><a href="../archive.html" class="back-to-list"', 1)
        s = s.replace('a.href="../"+s', 'a.href="../archive.html"+s', 1)
        s = s.replace('href="../#article-search"', 'href="../archive.html#article-search"', 1)
        if s != before:
            changed['back'] += 1

    # ---- 3. editorial deep links into the list ------------------------------
    if not is_article:
        before = s
        s = s.replace('href="./?q=', 'href="archive.html?q=')
        if p.name == '404.html':
            s = s.replace('href="/#article-search"', 'href="/archive.html#article-search"', 1)
        if p.name == 'reading-paths.html':
            s = s.replace('<a href="./">アーカイブ一覧</a>', '<a href="archive.html">アーカイブ一覧</a>', 1)
        if s != before:
            changed['deep'] += 1

    if s != orig:
        p.write_text(s, encoding='utf-8')

# ---- sitemap: list page added, front door and changelog bumped -------------
sm = ROOT / 'sitemap.xml'
t = sm.read_text(encoding='utf-8')
if 'archive.html' not in t:
    t = t.replace(
        '<url><loc>https://sunagawa-heiwa-archive.github.io/</loc><lastmod>2026-09-11</lastmod></url>',
        '<url><loc>https://sunagawa-heiwa-archive.github.io/</loc><lastmod>2026-09-27</lastmod></url>\n'
        '  <url><loc>https://sunagawa-heiwa-archive.github.io/archive.html</loc><lastmod>2026-09-27</lastmod></url>', 1)
    sm.write_text(t, encoding='utf-8')
    print('sitemap: archive.html added, front door lastmod bumped')
else:
    print('sitemap: already contains archive.html')

print(f"pages scanned: {len(PAGES)}")
print(f"nav updated:   {changed['nav']}")
print(f"back links:    {changed['back']}")
print(f"deep links:    {changed['deep']}")
if skipped:
    print('NOT updated:')
    for item in skipped:
        print(f'  {item}')
