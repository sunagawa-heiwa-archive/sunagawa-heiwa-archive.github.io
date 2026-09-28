# Sunagawa Heiwa Hiroba Public Article Archive / 砂川平和ひろば公開記事アーカイブ

Public web archive preserving articles from **Sunagawa Heiwa Hiroba (砂川平和ひろば)**, served via GitHub Pages at [https://sunagawa-heiwa-archive.github.io/](https://sunagawa-heiwa-archive.github.io/).

## Archive Overview

This archive preserves 208 public articles originally published across two blogging platforms:
- **FC2**: `https://sunagawaheiwa.blog.fc2.com/` (90 articles, primarily 2011–2018)
- **Ameblo**: `https://ameblo.jp/2021fukuoka-ameba/` (118 articles, primarily 2020–2026)

Captured on **2026-09-05**.

### Language Breakdown
- **Japanese / 日本語**: 190
- **English / 英語**: 10
- **Japanese + English / 日本語 + 英語**: 5
- **Chinese / 中文（繁體・简体）**: 3

## Site Structure & Key Pages

- **`index.html`** — Archive portal with an introduction to the Sunagawa Struggle, topic navigation cards, and curated starting points.
- **`archive.html`** — Complete searchable article catalog with interactive language, publication year, and keyword filters.
- **`articles/`** — 208 individual static HTML article pages with metadata, accessible images, related posts, and adjacent article navigation.
- **`guide.html`** — Beginner's guide to the Sunagawa Struggle, key legal milestones, and walking routes for historic sites.
- **`case-timeline.html`** — Chronological timeline of the Sunagawa civil damages lawsuit (国賠訴訟の経過) through 2025.
- **`sunagawa-incident.html`** & **`date-judgment.html`** — Topic overviews for the Sunagawa Incident (砂川事件) and the landmark 1959 Date Judgment (伊達判決).
- **`sunagawa-history.html`** — Historical chronology of the Sunagawa Struggle.
- **`reading-paths.html`** — Curated reading paths tailored for educators, journalists, and researchers.
- **`research-guide.html`** — English-language research guide and navigation for international readers.
- **`about.html`** — Archive provenance, relationship to Sunagawa Heiwa Hiroba, citation guide, and policies.
- **`changelog.html`** — Maintenance record, corrections log, and takedown request procedures.

## Data & Machine-Readable Formats

- **`articles-metadata.csv`** & **`articles-metadata.json`** — Full machine-readable metadata for all 208 articles (title, date, platform, language, source URL).
- **`feed.xml`** — Atom syndication feed for the archive.
- **`sitemap.xml`** & **`robots.txt`** — Search engine indexing metadata.
- **`obsidian/`** — Markdown versions formatted for local Obsidian vaults.
- **`raw/`** — Untouched original HTML captures preserved for archival audit.

## Technical Design & Preservation Principles

- **Zero External Dependencies**: Pure static HTML/CSS/vanilla JS. No external scripts, web fonts, cookies, trackers, or analytics.
- **Self-Hosted Assets**: 405 images are downloaded and hosted locally in `images/` (~48 MB); 2 unavailable source URLs (404 during capture) are retained with local placeholders.
- **Theme Support**: Lightweight client-side light/dark/auto theme toggle respecting system preferences.
- **Strict Preservation**: Archived article text, dates, titles, and images are preserved byte-identical to original publications.

## Development & Verification

To run local checks before opening a pull request:

```bash
# Verify all internal links, anchors, and images resolve
python3 scripts/check_links.py

# Preview site locally
python3 -m http.server 8000
```

Refer to `AGENTS.md` for repo rules, branch workflows, and PR standards.

## Contact

- **Sunagawa Heiwa Hiroba (Original organization)**: `sunagawa.heiwa@gmail.com` | [Official YouTube Channel](https://www.youtube.com/@%E7%A0%82%E5%B7%9D%E5%B9%B3%E5%92%8C%E3%81%B2%E3%82%8D%E3%81%B0)
- **Archive Maintenance & Corrections / Takedown**: `zezelunar@gmail.com` (see `changelog.html` for takedown policy)
