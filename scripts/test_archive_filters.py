#!/usr/bin/env python3
"""
Test suite for SITES-21 (PRD SUNA-14):
Filter section reordering (Type -> Year -> Language) and Language group collapse.
100% standard library Python — zero external dependencies.
"""

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class ArchiveFilterParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nav_order = []
        self.in_type_nav = False
        self.in_year_nav = False
        self.in_language_nav = False
        self.type_filters = []
        self.year_filters = []
        self.language_filters = []
        self.has_year_details = False
        self.has_language_details = False
        self.has_year_summary = False
        self.has_language_summary = False
        self.language_current_id = False
        self.year_current_id = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        tag_id = attr_dict.get('id', '')

        if 'type-nav' in classes:
            self.nav_order.append('type')
            self.in_type_nav = True
        elif 'year-nav' in classes:
            self.nav_order.append('year')
            self.in_year_nav = True
        elif 'language-nav' in classes:
            self.nav_order.append('language')
            self.in_language_nav = True

        if 'year-nav-details' in classes:
            self.has_year_details = True
        if 'language-nav-details' in classes:
            self.has_language_details = True
        if 'year-nav-summary' in classes:
            self.has_year_summary = True
        if 'language-nav-summary' in classes:
            self.has_language_summary = True

        if tag_id == 'year-nav-current':
            self.year_current_id = True
        if tag_id == 'language-nav-current':
            self.language_current_id = True

        if 'data-type-filter' in attr_dict:
            self.type_filters.append(attr_dict['data-type-filter'])
        if 'data-year-filter' in attr_dict:
            self.year_filters.append(attr_dict['data-year-filter'])
        if 'data-language-filter' in attr_dict:
            self.language_filters.append(attr_dict['data-language-filter'])

    def handle_endtag(self, tag):
        if tag in ('div', 'nav'):
            self.in_type_nav = False
            self.in_year_nav = False
            self.in_language_nav = False

def test_archive_html_structure():
    print("Testing archive.html DOM structure and filter order (AC 1 & AC 3)...")
    archive_path = os.path.join(ROOT, 'archive.html')
    with open(archive_path, 'r', encoding='utf-8') as f:
        html = f.read()

    parser = ArchiveFilterParser()
    parser.feed(html)

    # AC 1: DOM order must be Type -> Year -> Language
    assert parser.nav_order == ['type', 'year', 'language'], (
        f"Filter order must be ['type', 'year', 'language'], got {parser.nav_order}"
    )
    print("  ✓ Filter DOM order confirmed: 種類 (Type) -> 年別 (Year) -> 記事の言語 (Language)")

    # AC 3: Language details & summary structure
    assert parser.has_language_details, "Missing .language-nav-details in archive.html"
    assert parser.has_language_summary, "Missing .language-nav-summary in archive.html"
    assert parser.language_current_id, "Missing #language-nav-current in archive.html"

    # Verify all 5 language filters are present
    expected_languages = ['all', 'ja', 'en', 'ja-en', 'zh']
    assert parser.language_filters == expected_languages, (
        f"Expected language filters {expected_languages}, got {parser.language_filters}"
    )
    print("  ✓ Language details/summary dropdown with all 5 filters (all, ja, en, ja-en, zh) verified")

    # Verify year details & summary retained
    assert parser.has_year_details and parser.has_year_summary and parser.year_current_id
    print("  ✓ Year details/summary dropdown preserved")

def test_css_styling_and_height_budget():
    print("Testing assets/style.css mobile height budget and layout (AC 2 & AC 3)...")
    css_path = os.path.join(ROOT, 'assets', 'style.css')
    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    # Desktop rule: language-nav-buttons and year-nav-buttons must display flex
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
    desktop_rules = css[start_d:end_d]
    assert ".language-nav-details .language-nav-buttons" in desktop_rules
    assert ".year-nav-details .year-nav-buttons" in desktop_rules
    assert "display:flex!important" in desktop_rules.replace(" ", "")
    print("  ✓ Desktop view (>= 701px) unfolds both year and language chips verified")

    # Mobile rule: extract @media (max-width:700px) block
    idx = css.find('@media (max-width:700px)')
    if idx == -1:
        idx = css.find('@media (max-width: 700px)')
    assert idx != -1, "Missing @media (max-width:700px) in style.css"
    start_brace = css.find('{', idx)
    brace_depth = 1
    end_brace = start_brace + 1
    while end_brace < len(css) and brace_depth > 0:
        if css[end_brace] == '{':
            brace_depth += 1
        elif css[end_brace] == '}':
            brace_depth -= 1
        end_brace += 1
    mobile_css = css[start_brace:end_brace]

    # Type nav mobile styling: horizontal scroll / nowrap
    assert "overflow-x:auto" in mobile_css.replace(" ", "") or "overflow-x: scroll" in mobile_css
    assert "flex-wrap:nowrap" in mobile_css.replace(" ", "")
    assert ".type-filter{flex-shrink:0" in mobile_css.replace(" ", "")
    assert "scrollbar-width:thin" in mobile_css.replace(" ", "")
    assert ".type-nav::-webkit-scrollbar" in mobile_css

    # Touch target constraints: summaries must be >= 44px min-height
    assert "min-height:44px" in mobile_css.replace(" ", "")
    assert ".language-nav-summary" in mobile_css
    assert ".year-nav-summary" in mobile_css

    # Dynamic Height Budget derivation directly from parsed CSS rules (matches test_mobile_nav.py methodology):
    # 1. Parse .type-filter min-height
    type_btn_match = re.search(r'\.type-filter\s*\{[^}]*min-height:\s*(\d+)px', css)
    assert type_btn_match, "Could not parse .type-filter min-height from style.css"
    type_btn_h = int(type_btn_match.group(1))

    # 2. Parse mobile .type-nav vertical padding
    type_pad_match = re.search(r'\.type-nav\s*\{[^}]*padding:\s*(\d+)px\s+\d+(?:px)?\s+(\d+)px', mobile_css)
    assert type_pad_match, "Could not parse mobile .type-nav padding from style.css"
    type_nav_pad_v = int(type_pad_match.group(1)) + int(type_pad_match.group(2))

    # 3. Parse mobile summary min-height
    summary_min_h_match = re.search(r'(?:\.year-nav-summary|\.language-nav-summary)[^{]*\{[^}]*min-height:\s*(\d+)px', mobile_css)
    assert summary_min_h_match, "Could not parse summary min-height from mobile CSS"
    summary_min_h = int(summary_min_h_match.group(1))

    # 4. Parse mobile .year-nav vertical padding
    year_pad_match = re.search(r'\.year-nav\s*\{[^}]*padding:\s*(\d+)px\s+\d+(?:px)?\s+(\d+)px', mobile_css)
    assert year_pad_match, "Could not parse mobile .year-nav padding from style.css"
    year_nav_pad_v = int(year_pad_match.group(1)) + int(year_pad_match.group(2))

    # 5. Parse mobile .language-nav vertical padding
    lang_pad_match = re.search(r'\.language-nav\s*\{[^}]*padding:\s*(\d+)px\s+\d+(?:px)?\s+(\d+)px', mobile_css)
    assert lang_pad_match, "Could not parse mobile .language-nav padding from style.css"
    lang_nav_pad_v = int(lang_pad_match.group(1)) + int(lang_pad_match.group(2))

    # Compute derived geometry directly from parsed rules:
    derived_type_h = type_btn_h + type_nav_pad_v
    derived_year_h = summary_min_h + year_nav_pad_v
    derived_lang_h = summary_min_h + lang_nav_pad_v
    total_derived_height = derived_type_h + derived_year_h + derived_lang_h

    assert type_btn_h >= 44, f"Type chip height {type_btn_h}px below 44px touch target"
    assert summary_min_h >= 44, f"Summary height {summary_min_h}px below 44px touch target"
    assert total_derived_height <= 250, (
        f"Derived mobile filter height {total_derived_height}px exceeds AC 2 requirement of <= 250px"
    )
    print(f"  ✓ Mobile height budget dynamically derived from CSS rules: Type({derived_type_h}px) + Year({derived_year_h}px) + Language({derived_lang_h}px) = {total_derived_height}px <= 250px (down from ~477px)")

def test_javascript_behavior():
    print("Testing archive.html JavaScript filter logic and URL compatibility (AC 3 & AC 4)...")
    archive_path = os.path.join(ROOT, 'archive.html')
    with open(archive_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # AC 3: 0-count options disabled logic
    assert "button.disabled = langValue !== 'all' && langValue !== language && langCount === 0;" in html, (
        "archive.html must disable 0-count language options"
    )
    print("  ✓ 0-count disabled logic for language filter options verified")

    # AC 3: summary label update logic
    assert "languageCurrent.textContent" in html, "archive.html must update #language-nav-current textContent"
    assert "languagePanel.open = false" in html, "Selecting language on mobile must collapse the dropdown"
    print("  ✓ Language dropdown selection and summary text update verified")

    # AC 4: URL compatibility for type, year, language
    assert "url.searchParams.set('language', language)" in html
    assert "url.searchParams.delete('language')" in html
    assert "url.searchParams.set('year', year)" in html
    assert "url.searchParams.delete('year')" in html
    assert "url.searchParams.set('type', type)" in html
    assert "url.searchParams.delete('type')" in html
    assert "p.get('language') || 'all'" in html
    assert "p.get('year') || 'all'" in html
    assert "p.get('type') || 'all'" in html
    print("  ✓ URL parameter compatibility (type, year, language) verified on refresh and sharing")

if __name__ == '__main__':
    test_archive_html_structure()
    test_css_styling_and_height_budget()
    test_javascript_behavior()
    print("\nAll archive filter tests passed successfully!")
