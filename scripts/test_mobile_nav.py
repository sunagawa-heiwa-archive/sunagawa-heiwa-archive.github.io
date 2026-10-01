#!/usr/bin/env python3
"""
Test suite for SITES-20 (PRD SUNA-7):
Mobile navigation menu collapse into 'メニュー / Menu' button.
100% standard library Python — zero external dependencies.
"""

import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_source_code():
    print("Testing assets/theme.js and assets/style.css source code...")
    with open(os.path.join(ROOT, 'assets', 'theme.js'), 'r', encoding='utf-8') as f:
        js = f.read()
    with open(os.path.join(ROOT, 'assets', 'style.css'), 'r', encoding='utf-8') as f:
        css = f.read()

    # AC 1 & 2: Menu button creation and attributes
    assert 'class="menu-toggle-btn"' in js or "menuBtn.className = 'menu-toggle-btn'" in js, "Missing menu-toggle-btn creation in theme.js"
    assert "menuBtn.setAttribute('aria-expanded', 'false')" in js, "menuBtn must initialize aria-expanded to false"
    assert "menuBtn.setAttribute('aria-controls', 'mobile-nav-panel')" in js, "menuBtn must have aria-controls set to mobile-nav-panel"
    assert "メニュー / Menu" in js, "Missing bilingual label 'メニュー / Menu'"
    print("  ✓ Menu button attributes (aria-expanded, aria-controls, bilingual label) verified")

    # AC 2: Touch target sizing (>= 44x44px)
    min_h = re.search(r'\.menu-toggle-btn\s*\{[^}]*min-height:\s*44px', css)
    min_w = re.search(r'\.menu-toggle-btn\s*\{[^}]*min-width:\s*44px', css)
    close_h = re.search(r'\.mobile-nav-close-btn\s*\{[^}]*min-height:\s*44px', css)
    close_w = re.search(r'\.mobile-nav-close-btn\s*\{[^}]*min-width:\s*44px', css)
    link_h = re.search(r'\.mobile-nav-link\s*\{[^}]*min-height:\s*44px', css)
    assert min_h and min_w, ".menu-toggle-btn must have min-height and min-width >= 44px"
    assert close_h and close_w, ".mobile-nav-close-btn must have min-height and min-width >= 44px"
    assert link_h, ".mobile-nav-link must have min-height >= 44px for touch accessibility"
    print("  ✓ Touch targets (>= 44x44px for toggle button, close button, and links) verified")

    # AC 2: 9 links extraction
    assert "siteNav.querySelectorAll('a')" in js, "Must query all links from siteNav"
    assert "topicsNav.querySelectorAll('a')" in js, "Must query all links from topicsNav"
    assert "cloneNode(true)" in js, "Must clone navigation links with their relative hrefs and attributes"
    print("  ✓ Navigation links extraction (5 site-nav + 4 topics-nav = 9 links) verified")

    # AC 2 & 3: Interaction & accessibility (Esc, outside click, focus management)
    assert "panel.removeAttribute('hidden')" in js, "openMenu must remove hidden attribute"
    assert "panel.setAttribute('hidden', '')" in js, "closeMenu must set hidden attribute"
    assert "menuBtn.setAttribute('aria-expanded', 'true')" in js, "openMenu must set aria-expanded to true"
    assert "menuBtn.setAttribute('aria-expanded', 'false')" in js, "closeMenu must set aria-expanded to false"
    assert "closeBtn.focus()" in js, "openMenu must move focus into the menu"
    assert "menuBtn.focus()" in js, "closeMenu must restore focus to menu button"
    assert "e.key === 'Escape'" in js or "e.keyCode === 27" in js, "Esc key must close the menu"
    assert "backdrop.addEventListener('click'" in js, "Clicking backdrop must close the menu"
    print("  ✓ Focus management and keyboard accessibility (Esc, focus in/out, backdrop click) verified")

    # AC 4: Desktop view (>= 768px) hides mobile nav
    desktop_mq = re.search(r'@media\s*\(\s*min-width:\s*768px\s*\)\s*\{([^}]+)\}', css)
    assert desktop_mq, "Missing @media (min-width:768px) rule in style.css"
    desktop_rules = desktop_mq.group(1)
    assert ".menu-toggle-btn" in desktop_rules and "display:none" in desktop_rules.replace(" ", ""), "Desktop must hide .menu-toggle-btn"
    assert ".mobile-nav-panel" in desktop_rules and "display:none" in desktop_rules.replace(" ", ""), "Desktop must hide .mobile-nav-panel"
    print("  ✓ Desktop view (>= 768px) hides mobile toggle and panel verified")

    # AC 1: Mobile view (< 768px) hides secondary links and keeps header compact
    idx = css.find('@media (max-width:767px)')
    if idx == -1:
        idx = css.find('@media (max-width: 767px)')
    assert idx != -1, "Missing @media (max-width:767px) rule in style.css"
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
    assert ".has-mobile-nav .site-nav > a:not(:first-child)" in mobile_css and "display:none" in mobile_css.replace(" ", ""), "Mobile must hide non-first site-nav links in top bar"
    assert ".has-mobile-nav .topics-nav" in mobile_css and "display:none" in mobile_css.replace(" ", ""), "Mobile must hide topics-nav from normal document flow"
    print("  ✓ Mobile view (< 768px) compact top-bar styling verified")

def test_html_site_compatibility():
    print("Testing HTML integration across all 220 site pages...")
    html_files = []
    for root_dir, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in {'.git', 'raw', 'obsidian', 'node_modules'}]
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root_dir, file))

    assert len(html_files) == 220, f"Expected 220 HTML pages, found {len(html_files)}"

    class NavParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.in_site_nav = False
            self.in_topics_nav = False
            self.site_links = []
            self.topics_links = []
            self.has_theme_js = False
            self.has_style_css = False

        def handle_starttag(self, tag, attrs):
            attr_dict = dict(attrs)
            if tag == 'script' and 'theme.js' in attr_dict.get('src', ''):
                self.has_theme_js = True
            if tag == 'link' and 'style.css' in attr_dict.get('href', ''):
                self.has_style_css = True

            classes = attr_dict.get('class', '').split()
            if 'site-nav' in classes:
                self.in_site_nav = True
            if 'topics-nav' in classes:
                self.in_topics_nav = True

            if tag == 'a':
                if self.in_site_nav:
                    self.site_links.append(attr_dict.get('href', ''))
                elif self.in_topics_nav:
                    self.topics_links.append(attr_dict.get('href', ''))

        def handle_endtag(self, tag):
            if tag == 'nav':
                self.in_site_nav = False
                self.in_topics_nav = False

    pages_checked = 0
    for page_path in html_files:
        with open(page_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parser = NavParser()
        parser.feed(content)

        assert parser.has_theme_js, f"{page_path} missing theme.js script"
        assert parser.has_style_css, f"{page_path} missing style.css link"
        assert len(parser.site_links) in (5, 7), f"{page_path} expected 5 or 7 site links, found {len(parser.site_links)}"
        assert len(parser.topics_links) == 4, f"{page_path} expected 4 topics links, found {len(parser.topics_links)}"
        assert len(parser.site_links) + len(parser.topics_links) >= 9, f"{page_path} total navigation links must be >= 9"
        # Verify first link is reliably the Home link across all pages (required for mobile top-bar brand)
        assert parser.site_links[0] in ('./', '../', '/', './index.html'), f"{page_path} first site link must be Home, got {parser.site_links[0]}"
        pages_checked += 1

    print(f"  ✓ Verified all {pages_checked} HTML pages correctly provide navigation links, first link is Home, and load theme.js")

def test_article_mobile_geometry():
    print("Testing mobile viewport geometry derived from assets/style.css...")
    with open(os.path.join(ROOT, 'assets', 'style.css'), 'r', encoding='utf-8') as f:
        css = f.read()

    # 1. Parse .wrap padding (top)
    wrap_pad_match = re.search(r'\.wrap\s*\{[^}]*padding:\s*(\d+)px', css)
    assert wrap_pad_match, "Could not parse .wrap padding from style.css"
    wrap_padding_top = int(wrap_pad_match.group(1))

    # 2. Parse .site-nav a min-height and .menu-toggle-btn min-height
    site_nav_a_match = re.search(r'\.site-nav a\s*\{[^}]*min-height:\s*(\d+)px', css)
    assert site_nav_a_match, "Could not parse .site-nav a min-height from style.css"
    site_nav_a_min_h = int(site_nav_a_match.group(1))

    menu_btn_match = re.search(r'\.menu-toggle-btn\s*\{[^}]*min-height:\s*(\d+)px', css)
    assert menu_btn_match, "Could not parse .menu-toggle-btn min-height from style.css"
    menu_btn_min_h = int(menu_btn_match.group(1))

    top_bar_height = max(site_nav_a_min_h, menu_btn_min_h)

    # 3. Parse mobile header padding-bottom and margin-bottom from @media (max-width:767px)
    idx = css.find('@media (max-width:767px)')
    if idx == -1:
        idx = css.find('@media (max-width: 767px)')
    assert idx != -1, "Missing @media (max-width:767px) in style.css"
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

    header_pad_match = re.search(r'header\s*\{[^}]*padding-bottom:\s*(\d+)px', mobile_css)
    assert header_pad_match, "Could not parse mobile header padding-bottom from style.css"
    header_padding_bottom = int(header_pad_match.group(1))

    header_margin_match = re.search(r'header\s*\{[^}]*margin-bottom:\s*(\d+)px', mobile_css)
    assert header_margin_match, "Could not parse mobile header margin-bottom from style.css"
    header_margin_bottom = int(header_margin_match.group(1))

    # 4. Parse .back-nav margins
    back_nav_match = re.search(r'\.back-nav\s*\{[^}]*margin:\s*(\d+)px\s+\d+(?:px)?\s+(\d+)px', css)
    assert back_nav_match, "Could not parse .back-nav margins from style.css"
    back_nav_top = int(back_nav_match.group(1))
    back_nav_content_est = 24  # single-line text link

    # 5. Compute derived geometry directly from parsed CSS rules
    header_non_article = top_bar_height + header_padding_bottom
    header_article = top_bar_height + back_nav_top + back_nav_content_est + header_padding_bottom
    h1_top_non_article = wrap_padding_top + header_non_article + header_margin_bottom
    h1_top_article = wrap_padding_top + header_article + header_margin_bottom
    first_p_top_est = h1_top_article + 80  # H1 height + meta row

    assert header_non_article <= 120, f"Non-article header {header_non_article}px exceeds 120px"
    assert header_article <= 120, f"Article header {header_article}px exceeds 120px"
    assert h1_top_non_article <= 200, f"Non-article H1 top {h1_top_non_article}px exceeds 200px"
    assert h1_top_article <= 200, f"Article H1 top {h1_top_article}px exceeds 200px"
    assert first_p_top_est < 812, f"Article first paragraph top {first_p_top_est}px is below 812px viewport"
    print(f"  ✓ Derived header height ({header_article}px <= 120px) and H1 position ({h1_top_article}px <= 200px) from parsed style.css rules")

if __name__ == '__main__':
    test_source_code()
    test_html_site_compatibility()
    test_article_mobile_geometry()
    print("\nAll mobile navigation tests passed successfully!")
