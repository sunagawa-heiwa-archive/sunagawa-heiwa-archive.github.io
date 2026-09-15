#!/usr/bin/env python3
"""Audit round 2, article-page fixes (applied to all 208 article pages).

- D5: move the citation block (Copy archive URL / Copy citation) from
  before the article body to the end of the article (readers meet the
  prose first, the grey citation box last).
- D7: add a "Back to search / 検索に戻る" link to the article nav so
  readers can return to the full-text search instead of being stranded
  on a single page.
- Bump the stylesheet cache-buster to v=20260911-5 (version-aware, so it
  also covers any page that carried an older version string).

Idempotent: the citation block is only moved when it still precedes the
body; the back-to-search link is only inserted when absent.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARTICLES = sorted((ROOT / 'articles').glob('*.html'))
TARGET_VER = '20260911-5'


def extract_div(s, start):
    """Return s[start:end] covering the div opened at start (incl. '</div>')."""
    depth = 0
    pos = s.find('>', start) + 1
    while True:
        nxt_open = s.find('<div', pos)
        nxt_close = s.find('</div>', pos)
        if nxt_close == -1:
            raise ValueError('unbalanced div')
        if nxt_open != -1 and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + 4
        else:
            if depth == 0:
                return s[start:nxt_close + 6]
            depth -= 1
            pos = nxt_close + 6


moved = 0
added = 0
bumped = 0
problems = []
for p in ARTICLES:
    s = p.read_text(encoding='utf-8')
    orig = s

    # D5: move cite-block to end of article
    cite_start = s.find('<div class="cite-block"')
    body_start = s.find('<div class="body"')
    if cite_start == -1 or body_start == -1:
        problems.append(f'{p.name}: missing cite-block or body')
        continue
    if cite_start < body_start:
        block = extract_div(s, cite_start)
        s = s[:cite_start] + s[cite_start + len(block):]
        close = s.rfind('</article>')
        if close == -1:
            problems.append(f'{p.name}: no </article>')
            continue
        s = s[:close] + '\n' + block + s[close:]
        moved += 1

    # D7: back-to-search link
    if 'article-nav-back' not in s:
        i_nav = s.find('<nav class="article-nav"')
        if i_nav == -1:
            problems.append(f'{p.name}: no article-nav')
            continue
        tag_end = s.find('>', i_nav)
        back = ('\n<a class="article-nav-back" href="../#article-search">'
                '<span class="article-nav-label">Back to search / 検索に戻る</span>'
                '<span class="article-nav-title">Search the full archive / 全記事を検索</span></a>')
        s = s[:tag_end + 1] + back + s[tag_end + 1:]
        added += 1

    # CSS cache-buster bump (version-aware)
    new_s = re.sub(r'(assets/style\.css\?v=)[0-9]{8}-[0-9]+',
                   rf'\g<1>{TARGET_VER}', s)
    if new_s != s:
        s = new_s
        bumped += 1

    if s != orig:
        p.write_text(s, encoding='utf-8')

print(f'articles: {len(ARTICLES)}')
print(f'cite-block moved: {moved}')
print(f'back-to-search added: {added}')
print(f'version bumped: {bumped}')
if problems:
    print('problems:')
    for x in problems:
        print('  ', x)
