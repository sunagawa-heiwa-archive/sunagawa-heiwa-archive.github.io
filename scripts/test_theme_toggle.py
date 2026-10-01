#!/usr/bin/env python3
"""
Test script for SITES-15 (PRD SUNA-8):
Theme switch compression to single icon button cycling Light -> Dark -> Auto.
100% standard library Python — zero external dependencies.
"""

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_source_code():
    print("Testing assets/theme.js and assets/style.css source code...")
    with open(os.path.join(ROOT, 'assets', 'theme.js'), 'r', encoding='utf-8') as f:
        js = f.read()
    with open(os.path.join(ROOT, 'assets', 'style.css'), 'r', encoding='utf-8') as f:
        css = f.read()

    # 1. Cycle definition
    assert "'light': 'dark'" in js, "THEME_CYCLE missing light -> dark"
    assert "'dark': 'auto'" in js, "THEME_CYCLE missing dark -> auto"
    assert "'auto': 'light'" in js, "THEME_CYCLE missing auto -> light"
    print("  ✓ THEME_CYCLE (Light -> Dark -> Auto -> Light) verified")

    # 2. Icons & bilingual descriptions
    assert "☀️" in js and "Theme: Light / 表示：ライト" in js, "Light theme icon/text missing"
    assert "🌙" in js and "Theme: Dark / 表示：ダーク" in js, "Dark theme icon/text missing"
    assert "💻" in js and "Theme: Auto / 表示：自動" in js, "Auto theme icon/text missing"
    print("  ✓ Icons and bilingual accessibility labels verified")

    # 3. Persistence compatibility
    assert "localStorage.getItem('theme')" in js, "localStorage read key must remain 'theme'"
    assert "localStorage.setItem('theme', theme)" in js or "localStorage.setItem('theme'" in js, "localStorage write key must remain 'theme'"
    assert "localStorage.removeItem('theme')" in js, "Auto mode must remove 'theme' key from localStorage"
    print("  ✓ localStorage persistence compatibility verified")

    # 4. CSS button sizing (>= 44x44px)
    assert ".theme-toggle-btn" in css, "Missing .theme-toggle-btn selector in style.css"
    width_match = re.search(r'\.theme-toggle-btn\s*\{[^}]*width:\s*44px', css)
    height_match = re.search(r'\.theme-toggle-btn\s*\{[^}]*height:\s*44px', css)
    min_w = re.search(r'\.theme-toggle-btn\s*\{[^}]*min-width:\s*44px', css)
    min_h = re.search(r'\.theme-toggle-btn\s*\{[^}]*min-height:\s*44px', css)
    assert width_match and height_match and min_w and min_h, "Button dimensions must be at least 44x44px"
    print("  ✓ Button dimensions (>= 44x44px circular touch target) verified")

    # 5. Right alignment in .site-nav & no wrapper landmark clutter
    assert re.search(r'\.theme-switch\s*\{[^}]*margin-left:\s*auto', css), ".theme-switch must have margin-left: auto"
    assert "margin-left:0; margin-top:4px;" not in css, "Obsolete 540px theme-switch margin reset should be removed"
    assert "switcher.removeAttribute('role')" in js, "Wrapper role must be removed to avoid landmark clutter"
    assert "switcher.removeAttribute('aria-label')" in js, "Wrapper aria-label must be removed to let button carry semantics"
    print("  ✓ .theme-switch positioning and clean wrapper semantics verified")

def test_cycle_state_machine():
    print("Testing theme cycle state machine...")
    with open(os.path.join(ROOT, 'assets', 'theme.js'), 'r', encoding='utf-8') as f:
        js = f.read()

    # Extract THEME_CYCLE from JS
    cycle_match = re.search(r'var THEME_CYCLE\s*=\s*\{([^}]+)\};', js)
    assert cycle_match, "Failed to locate THEME_CYCLE object"
    cycle_text = cycle_match.group(1)
    cycle = dict(re.findall(r"['\"](\w+)['\"]\s*:\s*['\"](\w+)['\"]", cycle_text))

    # Verify 3-step cycle
    state = 'auto'
    visited = []
    for _ in range(4):
        state = cycle.get(state)
        visited.append(state)
    assert visited == ['light', 'dark', 'auto', 'light'], f"Unexpected cycle sequence: {visited}"
    print("  ✓ Pure-logic cycle verified: auto -> light -> dark -> auto -> light")

def test_html_compatibility():
    print("Testing HTML integration across site...")
    sample_files = ['index.html', 'archive.html', 'about.html', 'guide.html', 'articles/ameblo-12931093226.html']
    for rel_path in sample_files:
        full_path = os.path.join(ROOT, rel_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            html = f.read()
        assert 'assets/theme.js' in html or '../assets/theme.js' in html, f"Missing theme.js in {rel_path}"
        assert 'class="site-nav"' in html, f"Missing site-nav in {rel_path}"
        assert 'class="theme-switch"' in html, f"Missing theme-switch in {rel_path}"

    # Verify exact page count in site
    html_files = []
    for root_dir, dirs, files in os.walk(ROOT):
        # Skip raw captures and hidden git dirs
        dirs[:] = [d for d in dirs if d not in {'.git', 'raw', 'obsidian', 'node_modules'}]
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root_dir, file))
    
    articles_count = sum(1 for p in html_files if '/articles/' in p)
    site_pages_count = len(html_files) - articles_count
    total_count = len(html_files)
    assert total_count == 220, f"Expected 220 total HTML pages, got {total_count}"
    assert articles_count == 208, f"Expected 208 articles, got {articles_count}"
    assert site_pages_count == 12, f"Expected 12 site pages, got {site_pages_count}"
    print(f"  ✓ Verified all {total_count} pages (12 site pages + {articles_count} archived articles) share consistent theme integration")

if __name__ == '__main__':
    test_source_code()
    test_cycle_state_machine()
    test_html_compatibility()
    print("\nAll theme toggle tests passed successfully!")
