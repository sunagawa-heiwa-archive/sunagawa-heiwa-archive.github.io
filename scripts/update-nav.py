#!/usr/bin/env python3
"""Insert the Topics navigation into every page and bump the stylesheet
cache-buster version.

Audit-driven change (2.1): the topic pages (砂川事件とは / 伊達判決とは /
砂川闘争年表 / Research guide) were only reachable from the homepage hub,
never from the site navigation.  This adds a second, compact navigation row
labelled "Topics / テーマ" directly after the existing site nav on every page,
including the 208 article pages, with the correct relative prefix.

Idempotent: pages that already contain the Topics nav are left untouched, and
the version bump only rewrites the exact previous version string.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'articles').glob('*.html'))


def topics_nav(prefix):
    return (
        '<nav class="topics-nav" aria-label="Topics / テーマ">\n'
        f'<a href="{prefix}sunagawa-incident.html">砂川事件とは / Sunagawa Incident</a>\n'
        f'<a href="{prefix}date-judgment.html">伊達判決とは / Date Judgment</a>\n'
        f'<a href="{prefix}sunagawa-history.html">砂川闘争年表 / Struggle Chronology</a>\n'
        f'<a href="{prefix}research-guide.html" class="en-badge">Research guide / 英語入門</a>\n'
        '</nav>'
    )


count_nav = 0
count_ver = 0
missing_nav = []
for p in PAGES:
    s = p.read_text(encoding='utf-8')
    orig = s
    if 'class="topics-nav"' not in s:
        start = s.find('<nav class="site-nav"')
        if start == -1:
            missing_nav.append(str(p))
            continue
        end = s.find('</nav>', start)
        if end == -1:
            missing_nav.append(str(p))
            continue
        prefix = '../' if p.parent.name == 'articles' else ''
        s = s[:end + 6] + '\n' + topics_nav(prefix) + s[end + 6:]
        count_nav += 1
    # Version-aware bump: match whatever ?v= is currently in the stylesheet link
    # (404.html carried v=20260909-4, not v=20260911-3) and pin to the target.
    new_s = re.sub(r'(assets/style\.css\?v=)[0-9]{8}-[0-9]+', r'\g<1>20260911-4', s)
    if new_s != s:
        s = new_s
        count_ver += 1
    if s != orig:
        p.write_text(s, encoding='utf-8')

print(f'pages scanned: {len(PAGES)}')
print(f'topics-nav inserted: {count_nav}')
print(f'version bumped: {count_ver}')
if missing_nav:
    print('missing site-nav:', *missing_nav, sep='\n  ')
