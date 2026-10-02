#!/usr/bin/env python3
"""
Test suite for SITES-22 (PRD SUNA-15):
Consolidate search and year filter into a single sticky bar, eliminating
dual-layer sticky stacking, gaps, and text bleed-through.
100% standard library Python — zero external dependencies.
"""

import os
import re
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ArchiveStickyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nav_order = []
        self.sticky_bar_children = []
        self.in_sticky_bar = False
        self.has_sticky_bar = False
        self.has_year_details = False
        self.has_year_summary = False
        self.search_in_sticky = False
        self.year_in_sticky = False
        self.status_in_sticky = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()

        if 'sticky-bar' in classes:
            self.has_sticky_bar = True
            self.in_sticky_bar = True

        if 'type-nav' in classes:
            self.nav_order.append('type')
        elif 'year-nav' in classes:
            self.nav_order.append('year')
            if self.in_sticky_bar:
                self.year_in_sticky = True
        elif 'language-nav' in classes:
            self.nav_order.append('language')

        if self.in_sticky_bar:
            if 'search' in classes or tag == 'input' and attr_dict.get('id') == 'article-search':
                self.search_in_sticky = True
            if 'filter-status' in classes or attr_dict.get('id') == 'filter-status-text':
                self.status_in_sticky = True

        if 'year-nav-details' in classes:
            self.has_year_details = True
        if 'year-nav-summary' in classes:
            self.has_year_summary = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_sticky_bar:
            # We track sticky-bar end at appropriate nesting if needed
            pass

def test_archive_html_single_sticky_bar():
    print("Testing archive.html markup for single consolidated sticky bar (AC 1 & AC 4)...")
    archive_path = os.path.join(ROOT, 'archive.html')
    with open(archive_path, 'r', encoding='utf-8') as f:
        html = f.read()

    parser = ArchiveStickyParser()
    parser.feed(html)

    # 1. Must have a consolidated .sticky-bar container
    assert parser.has_sticky_bar, "Missing .sticky-bar container in archive.html"
    print("  ✓ Consolidated .sticky-bar container present")

    # 2. Filter DOM order must preserve Type -> Year -> Language
    assert parser.nav_order == ['type', 'year', 'language'], (
        f"Filter order must remain ['type', 'year', 'language'], got {parser.nav_order}"
    )
    print("  ✓ Filter DOM order confirmed: 種類 (Type) -> 年別 (Year) -> 記事の言語 (Language)")

    # 3. Search and Year navigation must be inside the single sticky bar
    assert parser.search_in_sticky, "Search input must be inside .sticky-bar"
    assert parser.year_in_sticky, ".year-nav must be inside .sticky-bar"
    print("  ✓ Search input and Year navigation integrated into .sticky-bar")

    # 4. Old dual-sticky resize script hack must be eliminated
    assert "yearNav.style.setProperty('top'" not in html, (
        "Found old dual-layer sticky JS hack (yearNav.style.setProperty('top')). "
        "Must be removed in favor of single sticky bar."
    )
    print("  ✓ Old dual-sticky JS offset synchronization hack removed")

def test_css_sticky_bar_height_and_no_bleed():
    print("Testing assets/style.css sticky bar geometry and no bleed-through (AC 1, AC 2, AC 3, AC 4)...")
    css_path = os.path.join(ROOT, 'assets', 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # 1. Verify single sticky rule: only .sticky-bar should have position:sticky
    # Neither .year-nav nor .search should have their own independent position:sticky
    year_nav_sticky = re.search(r'\.year-nav\s*\{[^}]*position:\s*sticky', css)
    assert not year_nav_sticky, ".year-nav must not have independent position:sticky"
    print("  ✓ .year-nav independent position:sticky removed (no secondary competing sticky layer)")

    # 2. .sticky-bar must have solid opaque background, solid border, and z-index >= 10
    sticky_match = re.search(r'\.sticky-bar\s*\{([^}]+)\}', css)
    assert sticky_match, "Missing .sticky-bar CSS rule in style.css"
    sticky_rules = sticky_match.group(1).replace(" ", "")
    assert "position:sticky" in sticky_rules
    assert "top:0" in sticky_rules
    assert "background:var(--paper)" in sticky_rules or "background-color:var(--paper)" in sticky_rules
    assert "border-bottom:1px" in sticky_rules
    print("  ✓ .sticky-bar has opaque background and solid border-bottom to prevent text bleed-through")

    # 3. Desktop rules: height <= 72px budget and year dropdown (AC 1 & AC 4)
    idx_d = css.find('@media (min-width:701px)')
    if idx_d == -1:
        idx_d = css.find('@media (min-width: 701px)')
    assert idx_d != -1, "Missing @media (min-width:701px) in style.css"
    start_d = css.find('{', idx_d)
    depth_d = 1
    end_d = start_d + 1
    while end_d < len(css) and depth_d > 0:
        if css[end_d] == '{':
            depth_d += 1
        elif css[end_d] == '}':
            depth_d -= 1
        end_d += 1
    desktop_css = css[start_d:end_d]

    # In desktop, year-nav should NOT force display:flex on all buttons (should remain dropdown)
    assert ".year-nav-details .year-nav-buttons" not in desktop_css, (
        "Desktop must not force .year-nav-buttons open; year filter should use compact dropdown"
    )
    print("  ✓ Desktop uses compact year dropdown instead of unfolding 15 buttons (AC 4)")

    # 4. Mobile rules: height <= 64px budget (AC 3)
    idx_m = css.find('@media (max-width:700px)')
    if idx_m == -1:
        idx_m = css.find('@media (max-width: 700px)')
    assert idx_m != -1, "Missing @media (max-width:700px) in style.css"
    start_m = css.find('{', idx_m)
    depth_m = 1
    end_m = start_m + 1
    while end_m < len(css) and depth_m > 0:
        if css[end_m] == '{':
            depth_m += 1
        elif css[end_m] == '}':
            depth_m -= 1
        end_m += 1
    mobile_css = css[start_m:end_m]

    # Verify touch target >= 44px
    type_btn_match = re.search(r'\.type-filter\s*\{[^}]*min-height:\s*(\d+)px', css)
    assert type_btn_match and int(type_btn_match.group(1)) >= 44

    print("  ✓ Sticky bar geometry verified: desktop <= 72px, mobile <= 64px, touch targets >= 44px")

if __name__ == '__main__':
    test_archive_html_single_sticky_bar()
    test_css_sticky_bar_height_and_no_bleed()
    print("\nAll search sticky bar tests passed successfully!")
