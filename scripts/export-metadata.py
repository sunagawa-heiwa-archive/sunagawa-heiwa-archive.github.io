#!/usr/bin/env python3
"""Export machine-readable metadata for the 208 archive articles.

Parses the homepage's entry list (the canonical source for title, date,
language, type, year and platform) and writes:
  - articles-metadata.csv  (UTF-8, one row per article)
  - articles-metadata.json (array of the same records)

Researchers can use this to reference or re-analyse the corpus without
scraping the pages, which is a natural extension of the About page's
「由来を辿れる」 promise.
"""
import csv
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://sunagawa-heiwa-archive.github.io'

idx = (ROOT / 'index.html').read_text(encoding='utf-8')
entries = re.findall(
    r'<a class="entry" data-language="([^"]+)" data-year="([^"]+)" data-type="([^"]+)" '
    r'href="articles/([^"]+\.html)"><span class="entry-title">(.*?)</span>'
    r'<span class="entry-meta"><time datetime="([^"]+)"', idx)

records = []
for lang, year, typ, file, title, dt in entries:
    title = re.sub(r'<[^>]+>', '', title)
    platform = 'Ameblo' if file.startswith('ameblo-') else 'FC2'
    if platform == 'Ameblo':
        art_id = file[len('ameblo-'):-len('.html')]
        original = f'https://ameblo.jp/2021fukuoka-ameba/entry-{art_id}.html'
    else:
        art_id = file[len('fc2-'):-len('.html')]
        original = f'https://sunagawaheiwa.blog.fc2.com/blog-entry-{art_id}.html'
    records.append({
        'title': title,
        'publication_date': dt,
        'year': year,
        'language': lang,
        'type': typ,
        'platform': platform,
        'local_url': f'{SITE}/articles/{file}',
        'original_url': original,
    })

# Keep the same order as the page (reverse-chronological); stable sort guard.
if len(records) != 208:
    raise SystemExit(f'expected 208 entries, got {len(records)}')

out_csv = ROOT / 'articles-metadata.csv'
out_json = ROOT / 'articles-metadata.json'
fields = ['title', 'publication_date', 'year', 'language', 'type',
          'platform', 'local_url', 'original_url']
with out_csv.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(records)
with out_json.open('w', encoding='utf-8') as f:
    json.dump({'generated': '2026-09-15', 'count': len(records),
               'items': records}, f, ensure_ascii=False, indent=1)

print(f'wrote {out_csv.name} ({len(records)} rows), {out_json.name}')
