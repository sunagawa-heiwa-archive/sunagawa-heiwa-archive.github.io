#!/usr/bin/env python3
"""Add the citation UI block (Copy archive URL / Copy citation) to every archived
article page, and load assets/citation.js in each article head.

Run from the repository root:  python3 scripts/inject-citation-ui.py
The script is idempotent: pages that already carry .cite-block are left untouched.

Citation text follows the archive's suggested form:
    Article title. Original publication date. 砂川平和ひろば公開記事アーカイブ. Archive URL. Original URL.
"""
import glob
import html
import re

ARTICLE_GLOB = 'articles/*.html'
CITATION_JS = '<script src="../assets/citation.js" defer></script>'

CITE_BLOCK_TMPL = (
    '<div class="cite-block" aria-label="Citation / 引用情報">\n'
    '<p class="cite-text">{cite_text}</p>\n'
    '<div class="cite-actions">\n'
    '<button type="button" class="cite-btn" data-copy-url="{archive_url}" '
    'data-copied-label="Copied / コピーしました" data-failed-label="Copy failed / コピー失敗">'
    'Copy archive URL / URLをコピー</button>\n'
    '<button type="button" class="cite-btn" data-copy-cite="{cite_text}" '
    'data-copied-label="Copied / コピーしました" data-failed-label="Copy failed / コピー失敗">'
    'Copy citation / 引用をコピー</button>\n'
    '</div>\n</div>'
)

BASE_URL = 'https://sunagawa-heiwa-archive.github.io/'


def main():
    updated = 0
    skipped = 0
    errors = []
    for fn in sorted(glob.glob(ARTICLE_GLOB)):
        with open(fn, encoding='utf-8') as fh:
            s = fh.read()

        if 'cite-block' in s:
            skipped += 1
            continue

        # --- extract metadata from the existing page ---
        h1 = re.search(r'<article><h1>(.*?)</h1>', s, re.S)
        if not h1:
            errors.append((fn, 'no h1'))
            continue
        title = html.unescape(re.sub(r'<[^>]+>', '', h1.group(1))).strip()

        src = re.search(r'<div class="source">(.*?)</div>', s, re.S)
        if not src:
            errors.append((fn, 'no .source'))
            continue
        inner = src.group(1)
        t = re.search(r'<time[^>]*>(.*?)</time>', inner)
        a = re.search(r'<a href="([^"]+)"[^>]*>', inner)
        if not t or not a:
            errors.append((fn, 'source missing time/a'))
            continue
        pub_date = html.unescape(t.group(1)).strip()
        orig_url = a.group(1)

        slug = fn.replace('articles/', '').replace('.html', '')
        archive_url = f'{BASE_URL}articles/{slug}.html'

        cite_text = f'{title}. {pub_date}. 砂川平和ひろば公開記事アーカイブ. {archive_url}. Original: {orig_url}'

        # --- insert cite block right after .source, before .body ---
        block = CITE_BLOCK_TMPL.format(
            cite_text=html.escape(cite_text, quote=True),
            archive_url=html.escape(archive_url, quote=True),
        )
        s = s.replace(src.group(0), src.group(0) + '\n' + block, 1)

        # --- load citation.js before </head> ---
        if CITATION_JS not in s:
            if s.count('</head>') != 1:
                errors.append((fn, 'unexpected head count'))
                continue
            s = s.replace('</head>', CITATION_JS + '</head>', 1)

        with open(fn, 'w', encoding='utf-8') as fh:
            fh.write(s)
        updated += 1

    print(f'updated={updated} skipped={skipped} errors={len(errors)}')
    for e in errors:
        print('  ERROR', e)


if __name__ == '__main__':
    main()
