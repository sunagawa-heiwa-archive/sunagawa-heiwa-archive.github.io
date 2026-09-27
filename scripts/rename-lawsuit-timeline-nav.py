#!/usr/bin/env python3
"""Rename the site-nav label for case-timeline.html on every page.

Audit item N10 (2026-09-27): the first-level navigation pointed readers at
"Case timeline / 国賠年表" while the second-level "Topics" navigation offered
"砂川闘争年表 / Struggle Chronology".  The two pages cover different things
(the civil damages lawsuit's progress vs. the 1609-1977 history of the
struggle), but the labels differed only by a prefix, so first-time readers
could not tell them apart from the navigation alone.

This keeps "年表" for the history page and names the lawsuit page after what it
actually is: 国賠訴訟の経過 / Lawsuit timeline.

Only the navigation anchor text changes; prose links that point at
case-timeline.html keep their own wording, which reads naturally in context.

Idempotent: pages that already carry the new label are left untouched, and the
script refuses to rewrite an occurrence whose surrounding markup is not the
navigation link.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob('*.html')) + sorted((ROOT / 'articles').glob('*.html'))

OLD = 'Case timeline / 国賠年表'
NEW = '国賠訴訟の経過 / Lawsuit timeline'

renamed = 0
already = 0
unexpected = []
for p in PAGES:
    s = p.read_text(encoding='utf-8')
    old_count = s.count(OLD)
    if not old_count:
        if NEW in s:
            already += 1
        continue
    # Every occurrence must sit inside the nav link to case-timeline.html.
    problems = []
    pos = 0
    while True:
        pos = s.find(OLD, pos)
        if pos == -1:
            break
        if 'case-timeline.html' not in s[max(0, pos - 60):pos]:
            problems.append(f'{p}: {s[max(0, pos - 60):pos]!r}')
        pos += len(OLD)
    if problems:
        unexpected.extend(problems)
        continue
    p.write_text(s.replace(OLD, NEW), encoding='utf-8')
    renamed += 1

print(f'pages scanned: {len(PAGES)}')
print(f'nav label renamed: {renamed}')
print(f'already renamed: {already}')
if unexpected:
    print('occurrences NOT in the nav link (left untouched):')
    for item in unexpected:
        print(f'  {item}')
