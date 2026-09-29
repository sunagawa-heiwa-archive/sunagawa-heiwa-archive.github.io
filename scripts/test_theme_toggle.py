#!/usr/bin/env python3
"""
Test script for SITES-15 (PRD SUNA-8):
Theme switch compression to single icon button cycling Light -> Dark -> Auto.
"""

import json
import re
import subprocess
from bs4 import BeautifulSoup

def test_source_code():
    print("Testing assets/theme.js and assets/style.css source code...")
    with open('assets/theme.js', 'r', encoding='utf-8') as f:
        js = f.read()
    with open('assets/style.css', 'r', encoding='utf-8') as f:
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

    # 5. Right alignment in .site-nav
    assert re.search(r'\.theme-switch\s*\{[^}]*margin-left:\s*auto', css), ".theme-switch must have margin-left: auto"
    assert "margin-left:0; margin-top:4px;" not in css, "Obsolete 540px theme-switch margin reset should be removed"
    print("  ✓ .theme-switch positioning and responsiveness verified")

def test_execution_simulation():
    print("Testing theme cycle execution in Node.js environment...")
    node_test = """
    const fs = require('fs');
    const vm = require('vm');

    // Mock DOM and localStorage
    const storage = {};
    const localStorage = {
      getItem: (k) => (k in storage ? storage[k] : null),
      setItem: (k, v) => { storage[k] = String(v); },
      removeItem: (k) => { delete storage[k]; }
    };

    const docAttrs = {};
    const documentElement = {
      setAttribute: (k, v) => { docAttrs[k] = v; },
      removeAttribute: (k) => { delete docAttrs[k]; },
      getAttribute: (k) => docAttrs[k] || null,
      hasAttribute: (k) => k in docAttrs
    };

    class MockElement {
      constructor(tagName, className = '') {
        this.tagName = tagName;
        this.className = className;
        this.attributes = {};
        this.children = [];
        this._innerHTML = '';
        this.textContent = '';
      }
      set innerHTML(html) {
        this._innerHTML = html;
        if (html.includes('theme-toggle-btn')) {
          const btn = new MockElement('button', 'theme-toggle-btn');
          const valMatch = html.match(/data-theme-val="([^"]+)"/);
          if (valMatch) btn.setAttribute('data-theme-val', valMatch[1]);
          const ariaMatch = html.match(/aria-label="([^"]+)"/);
          if (ariaMatch) btn.setAttribute('aria-label', ariaMatch[1]);
          const titleMatch = html.match(/title="([^"]+)"/);
          if (titleMatch) btn.title = titleMatch[1];
          this.children = [btn];
        }
      }
      get innerHTML() { return this._innerHTML; }
      setAttribute(k, v) { this.attributes[k] = v; }
      getAttribute(k) { return this.attributes[k] || null; }
      removeAttribute(k) { delete this.attributes[k]; }
      appendChild(child) { this.children.push(child); }
      querySelector(sel) {
        if (sel === '.theme-switch') return this.children.find(c => c.className === 'theme-switch') || null;
        if (sel === '.theme-toggle-btn') return this.children.find(c => c.className === 'theme-toggle-btn') || null;
        if (sel === '.theme-toggle-icon') return { textContent: '' };
        return null;
      }
      querySelectorAll(sel) {
        if (sel === '.theme-switch') return this.children.filter(c => c.className === 'theme-switch');
        if (sel === '.theme-toggle-btn') return this.children.filter(c => c.className === 'theme-toggle-btn');
        if (sel === '.theme-btn') return [];
        if (sel === 'meta[name="theme-color"]') return [];
        return [];
      }
    }

    const nav = new MockElement('nav', 'site-nav');
    const switcher = new MockElement('div', 'theme-switch');
    nav.appendChild(switcher);

    const listeners = {};
    const document = {
      documentElement,
      readyState: 'complete',
      addEventListener: (evt, fn) => { listeners[evt] = fn; },
      querySelector: (sel) => {
        if (sel === '.site-nav') return nav;
        if (sel === '.theme-toggle-btn') return switcher.querySelector('.theme-toggle-btn');
        return null;
      },
      querySelectorAll: (sel) => {
        if (sel === '.theme-switch') return [switcher];
        if (sel === '.theme-toggle-btn') {
          const btn = switcher.querySelector('.theme-toggle-btn');
          return btn ? [btn] : [];
        }
        if (sel === '.theme-btn') return [];
        if (sel === 'meta[name="theme-color"]') return [];
        return [];
      }
    };

    const window = {
      localStorage,
      matchMedia: () => ({ addEventListener: () => {}, addListener: () => {} })
    };

    const code = fs.readFileSync('assets/theme.js', 'utf8');
    vm.runInNewContext(code, { document, window, localStorage, console });

    // Verify initial mount
    const toggleBtn = switcher.children.find(c => c.className === 'theme-toggle-btn');
    if (!toggleBtn) throw new Error('Toggle button not mounted');
    if (toggleBtn.getAttribute('data-theme-val') !== 'auto') throw new Error('Initial theme should be auto');
    if (!toggleBtn.getAttribute('aria-label').includes('Auto')) throw new Error('Initial aria-label should mention Auto');

    // Simulate click 1: auto -> light
    listeners['click']({ target: { closest: (sel) => (sel === '.theme-toggle-btn' ? toggleBtn : null) } });
    if (localStorage.getItem('theme') !== 'light') throw new Error('Click 1: storage should be light');
    if (documentElement.getAttribute('data-theme') !== 'light') throw new Error('Click 1: data-theme should be light');
    if (toggleBtn.getAttribute('data-theme-val') !== 'light') throw new Error('Click 1: button val should be light');
    if (!toggleBtn.getAttribute('aria-label').includes('Light')) throw new Error('Click 1: aria-label should mention Light');

    // Simulate click 2: light -> dark
    listeners['click']({ target: { closest: (sel) => (sel === '.theme-toggle-btn' ? toggleBtn : null) } });
    if (localStorage.getItem('theme') !== 'dark') throw new Error('Click 2: storage should be dark');
    if (documentElement.getAttribute('data-theme') !== 'dark') throw new Error('Click 2: data-theme should be dark');
    if (toggleBtn.getAttribute('data-theme-val') !== 'dark') throw new Error('Click 2: button val should be dark');
    if (!toggleBtn.getAttribute('aria-label').includes('Dark')) throw new Error('Click 2: aria-label should mention Dark');

    // Simulate click 3: dark -> auto
    listeners['click']({ target: { closest: (sel) => (sel === '.theme-toggle-btn' ? toggleBtn : null) } });
    if (localStorage.getItem('theme') !== null) throw new Error('Click 3: storage should be removed for auto');
    if (documentElement.hasAttribute('data-theme')) throw new Error('Click 3: data-theme should be removed for auto');
    if (toggleBtn.getAttribute('data-theme-val') !== 'auto') throw new Error('Click 3: button val should be auto');
    if (!toggleBtn.getAttribute('aria-label').includes('Auto')) throw new Error('Click 3: aria-label should mention Auto');

    // Simulate click 4: auto -> light (cycle loops)
    listeners['click']({ target: { closest: (sel) => (sel === '.theme-toggle-btn' ? toggleBtn : null) } });
    if (localStorage.getItem('theme') !== 'light') throw new Error('Click 4: cycle should loop back to light');

    console.log('OK');
    """

    res = subprocess.run(['node', '-e', node_test], capture_output=True, text=True)
    assert res.returncode == 0 and "OK" in res.stdout, f"Node execution failed: {res.stderr}\n{res.stdout}"
    print("  ✓ Full theme cycle (auto -> light -> dark -> auto -> light) simulated & verified in Node.js")

def test_html_compatibility():
    print("Testing HTML integration across representative templates...")
    sample_files = ['index.html', 'archive.html', 'about.html', 'guide.html', 'articles/ameblo-12931093226.html']
    for path in sample_files:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        assert 'assets/theme.js' in html or '../assets/theme.js' in html, f"Missing theme.js in {path}"
        assert 'class="site-nav"' in html, f"Missing site-nav in {path}"
        assert 'class="theme-switch"' in html, f"Missing theme-switch in {path}"
    print(f"  ✓ Verified {len(sample_files)} representative HTML pages link theme.js and include .theme-switch")

if __name__ == '__main__':
    test_source_code()
    test_execution_simulation()
    test_html_compatibility()
    print("\nAll theme toggle tests passed successfully!")
