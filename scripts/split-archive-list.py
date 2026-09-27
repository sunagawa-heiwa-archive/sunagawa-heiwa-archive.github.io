#!/usr/bin/env python3
"""Split the 47-screen homepage into a short portal (index.html) and a
dedicated list/search page (archive.html).

Audit item P1-6 (2026-09-27): the homepage carried the six topic cards, the
stats strip, the filter UI and all 208 article entries in one document, so on a
375px viewport the search box only appeared after roughly three screens of
scrolling and the page ran to ~38,500px.  This moves the browsable list to
archive.html and leaves index.html as a short front door.

Every existing deep link keeps working:
  - index.html forwards to archive.html whenever the URL carries a search or
    filter parameter, or the #article-search anchor.
  - The schema.org SearchAction target moves to archive.html?q=.
Article pages' "back to the archive" links now point straight at archive.html.

Idempotent: refuses to run once archive.html exists.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / 'index.html'
ARCHIVE = ROOT / 'archive.html'

NEW_TITLE = '全記事一覧と検索 / All articles | Sunagawa Heiwa Hiroba'
NEW_DESC = ('砂川平和ひろば公開記事アーカイブの全208記事を、年・言語・種別・キーワードで検索・閲覧できる一覧ページです。'
            '砂川闘争、砂川事件、伊達判決、国賠訴訟、現地活動に関する公開記録を収録しています。')

text = INDEX.read_text(encoding='utf-8')

if ARCHIVE.exists():
    raise SystemExit('archive.html already exists; refusing to re-run.')


def at(marker, start=0):
    pos = text.find(marker, start)
    if pos == -1:
        raise SystemExit(f'marker not found: {marker!r}')
    return pos


def end_of(marker, start=0):
    pos = at(marker, start)
    return pos + len(marker)


# ---------------------------------------------------------------- slices
head_end = at('<body id="top">')
HEAD = text[:head_end]

hero_pos_start = at('<p class="hero-position">')
hero_intro_start = at('<p class="hero-intro">')
en_note_start = at('<div class="en-note" lang="en">')
en_note_end = end_of('</div>', en_note_start)
topic_hub_start = at('<section class="topic-hub"')
topic_hub_end = end_of('</section>', topic_hub_start)
topic_extra_start = at('<p class="topic-extra">')
topic_extra_end = end_of('</p>', topic_extra_start)
stats_start = at('<div class="stats"')
year_gap_start = at('<p class="year-gap note">')
search_start = at('<div class="search">')
official_start = at('<section class="official-links"')
official_end = end_of('</section>', official_start)
footer_start = at('<footer>')
footer_end = end_of('</footer>', footer_start)
backtotop_start = at('<a class="back-to-top"')
backtotop_end = end_of('</a>', backtotop_start)
script_start = at('<script>\n  (() =>')
script_end = end_of('</script>', script_start)

hero_position = text[hero_pos_start:hero_intro_start]
hero_intro = text[hero_intro_start:en_note_start]
en_note = text[en_note_start:en_note_end]
topic_hub = text[topic_hub_start:topic_hub_end]
topic_extra = text[topic_extra_start:topic_extra_end]
stats = text[stats_start:year_gap_start]
year_gap = text[year_gap_start:search_start]
list_block = text[search_start:official_start]
official = text[official_start:official_end]
footer = text[footer_start:footer_end]
backtotop = text[backtotop_start:backtotop_end]
script = text[script_start:script_end]

BODY_START = text[head_end:hero_pos_start]          # body open + navs + header + <main>

# ---------------------------------------------------------------- head for archive.html
archive_head = HEAD
archive_head = re.sub(r'<title>.*?</title>', f'<title>{NEW_TITLE}</title>', archive_head, count=1)
archive_head = re.sub(r'<meta name="description" content="[^"]*">',
                      f'<meta name="description" content="{NEW_DESC}">', archive_head, count=1)
archive_head = archive_head.replace(
    '<link rel="canonical" href="https://sunagawa-heiwa-archive.github.io/">',
    '<link rel="canonical" href="https://sunagawa-heiwa-archive.github.io/archive.html">')
archive_head = archive_head.replace(
    '<meta property="og:url" content="https://sunagawa-heiwa-archive.github.io/">',
    '<meta property="og:url" content="https://sunagawa-heiwa-archive.github.io/archive.html">')
archive_head = re.sub(r'<meta property="og:title" content="[^"]*">',
                      f'<meta property="og:title" content="{NEW_TITLE}">', archive_head, count=1)
archive_head = re.sub(r'<meta property="og:description" content="[^"]*">',
                      f'<meta property="og:description" content="{NEW_DESC}">', archive_head, count=1)
archive_head = re.sub(r'<meta name="twitter:title" content="[^"]*">',
                      f'<meta name="twitter:title" content="{NEW_TITLE}">', archive_head, count=1)
archive_head = re.sub(r'<meta name="twitter:description" content="[^"]*">',
                      f'<meta name="twitter:description" content="{NEW_DESC}">', archive_head, count=1)
# site verification belongs on the front door only
archive_head = re.sub(r'<meta name="google-site-verification" content="[^"]*">', '', archive_head, count=1)
# WebSite + SearchAction stays on index.html; the list page gets a CollectionPage
archive_head = re.sub(
    r'<script type="application/ld\+json">\{"@context":"https://schema.org","@type":"WebSite".*?</script>',
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"CollectionPage",'
    f'"name":"{NEW_TITLE}","description":"{NEW_DESC}","inLanguage":"ja",'
    '"url":"https://sunagawa-heiwa-archive.github.io/archive.html",'
    '"isPartOf":{"@type":"WebSite","name":"Sunagawa Heiwa Hiroba Public Article Archive",'
    '"url":"https://sunagawa-heiwa-archive.github.io/"}}</script>',
    archive_head, count=1, flags=re.S)

# ---------------------------------------------------------------- body markup
home_plain = '<a href="./">Home / トップ</a>'
home_current = '<a href="./" aria-current="page">Home / トップ</a>'
articles_current = '<a href="archive.html" aria-current="page">Articles / 記事一覧</a>'

archive_body_start = BODY_START.replace(
    '<a href="./" aria-current="page">Archive / アーカイブ</a>',
    home_plain + '\n' + articles_current)
archive_body_start = archive_body_start.replace(
    '<a class="skip-link" href="#article-search">検索へ</a>',
    '<a class="skip-link" href="#article-search">Skip to the list / 記事一覧へ</a>')
archive_body_start = archive_body_start.replace(
    '<h1>砂川平和ひろば</h1>\n<div class="lede">公開記事アーカイブ</div>',
    '<h1>公開記事アーカイブ</h1>\n<div class="lede">208件の収録記事を年・言語・種別・全文検索で探す</div>')

archive_html = (
    archive_head
    + archive_body_start
    + stats + year_gap + list_block
    + '</main>\n'
    + footer + backtotop + script
    + '</div></body></html>'
)

# ---------------------------------------------------------------- new index.html
index_head = HEAD
index_head = index_head.replace(
    '"target":"https://sunagawa-heiwa-archive.github.io/?q={search_term_string}"',
    '"target":"https://sunagawa-heiwa-archive.github.io/archive.html?q={search_term_string}"')
# Keep old /-with-query and /#article-search links working by handing them to the
# list page before anything renders.
forward = ('<script>(function(){var s=location.search,h=location.hash;'
           'if(s||h==="#article-search")location.replace("archive.html"+s+h);})();</script>')
index_head = index_head.replace('</head>', forward + '</head>')

cta = ('<p class="hero-cta"><a href="archive.html">'
       '全208件の記事を検索・閲覧する / Browse &amp; search all 208 articles →</a></p>')

index_body_start = BODY_START
index_body_start = index_body_start.replace(
    '<a href="./" aria-current="page">Archive / アーカイブ</a>',
    home_current + '\n<a href="archive.html">Articles / 記事一覧</a>')
index_body_start = index_body_start.replace(
    '<a class="skip-link" href="#article-search">検索へ</a>',
    '<a class="skip-link" href="#main">Skip to content / 本文へ</a>')
index_body_start = index_body_start.replace('<main>', '<main id="main">', 1)
# drop the mobile-only jump-to-search pill; the CTA replaces it
hero_position = re.sub(r'<p class="hero-search-jump">.*?</p>\n', '', hero_position, count=1, flags=re.S)

index_html = (
    index_head
    + index_body_start
    + hero_position + cta + hero_intro + en_note + topic_hub + topic_extra + stats + official
    + '</main>\n'
    + footer
    + '</div></body></html>'
)

ARCHIVE.write_text(archive_html, encoding='utf-8')
INDEX.write_text(index_html, encoding='utf-8')
print('wrote archive.html and a new index.html')
