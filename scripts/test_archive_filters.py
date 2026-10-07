#!/usr/bin/env python3
"""
Test suite for SITES-21 (PRD SUNA-14):
Filter section reordering (Type -> Year -> Language) and Language group collapse.
100% standard library Python — zero external dependencies.
"""

import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import threading
import time
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
        self.has_type_details = False
        self.has_year_details = False
        self.has_language_details = False
        self.has_type_summary = False
        self.has_year_summary = False
        self.has_language_summary = False
        self.type_current_id = False
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

        if 'type-nav-details' in classes:
            self.has_type_details = True
        if 'year-nav-details' in classes:
            self.has_year_details = True
        if 'language-nav-details' in classes:
            self.has_language_details = True
        if 'type-nav-summary' in classes:
            self.has_type_summary = True
        if 'year-nav-summary' in classes:
            self.has_year_summary = True
        if 'language-nav-summary' in classes:
            self.has_language_summary = True

        if tag_id == 'type-nav-current':
            self.type_current_id = True
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
    print("Testing archive.html DOM structure and filter order (AC 1 & AC 4)...")
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

    # AC 1: Type details & summary structure (SITES-38)
    assert parser.has_type_details, "Missing .type-nav-details in archive.html"
    assert parser.has_type_summary, "Missing .type-nav-summary in archive.html"
    assert parser.type_current_id, "Missing #type-nav-current in archive.html"
    expected_types = ['all', 'guide', 'lawsuit', 'gathering', 'links', 'newsletter', 'notice', 'community', 'record']
    assert parser.type_filters == expected_types, f"Expected 9 type filters {expected_types}, got {parser.type_filters}"
    print("  ✓ Type details/summary dropdown with all 9 filters verified")

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
    assert ".type-nav-details .type-nav-buttons" in desktop_rules
    assert "display:flex!important" in desktop_rules.replace(" ", "")
    print("  ✓ Desktop view (>= 701px) unfolds language and type chips verified")

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

    # Type nav mobile styling: natural flex-wrap wrapping (prevents text clipping on small viewports)
    assert "flex-wrap:wrap" in mobile_css.replace(" ", "")

    # Touch target constraints: summaries must be >= 44px min-height
    assert "min-height:44px" in mobile_css.replace(" ", "")
    assert ".language-nav-summary" in mobile_css
    assert ".type-nav-summary" in mobile_css
    assert ".year-nav-summary" in mobile_css

    # Dynamic Height Budget derivation directly from parsed CSS rules:
    # 1. Parse .type-filter min-height
    type_btn_match = re.search(r'\.type-filter\s*\{[^}]*min-height:\s*(\d+)px', css)
    assert type_btn_match, "Could not parse .type-filter min-height from style.css"
    type_btn_h = int(type_btn_match.group(1))

    # 2. Parse mobile summary min-height
    summary_min_h_match = re.search(r'(?:\.year-nav-summary|\.language-nav-summary|\.type-nav-summary)[^{]*\{[^}]*min-height:\s*(\d+)px', mobile_css)
    assert summary_min_h_match, "Could not parse summary min-height from mobile CSS"
    summary_min_h = int(summary_min_h_match.group(1))

    # 3. Parse mobile .language-nav vertical padding
    lang_pad_match = re.search(r'\.language-nav\s*\{[^}]*padding:\s*(\d+)px\s+\d+(?:px)?\s+(\d+)px', mobile_css)
    assert lang_pad_match, "Could not parse mobile .language-nav padding from style.css"
    lang_nav_pad_v = int(lang_pad_match.group(1)) + int(lang_pad_match.group(2))

    # Compute derived geometry directly from parsed rules:
    derived_lang_h = summary_min_h + lang_nav_pad_v

    assert type_btn_h >= 44, f"Type chip height {type_btn_h}px below 44px touch target"
    assert summary_min_h >= 44, f"Summary height {summary_min_h}px below 44px touch target"
    assert derived_lang_h <= 60, f"Language summary height {derived_lang_h}px exceeds 60px target"
    print(f"  ✓ Mobile geometry derived from CSS rules: Type touch target ({type_btn_h}px), Language collapsed ({derived_lang_h}px)")

def test_javascript_behavior():
    print("Testing archive.html JavaScript filter logic and URL compatibility (AC 1, AC 3 & AC 4)...")
    archive_path = os.path.join(ROOT, 'archive.html')
    with open(archive_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # AC 1: Type summary label update and collapse logic
    assert "typeCurrent.textContent" in html, "archive.html must update #type-nav-current textContent"
    assert "typePanel.open = false" in html, "Selecting type on mobile must collapse the dropdown"
    assert "typePanel.open = isDesktop" in html, "syncFilterPanels must keep typePanel open on desktop"
    print("  ✓ Type dropdown selection and summary text update verified")

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

def test_live_viewport_above_the_fold():
    print("Testing live browser viewport height budget at 375px & 608px (AC 2 & AC 3)...")
    chrome_bin = (
        shutil.which("google-chrome")
        or shutil.which("chromium")
        or shutil.which("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    )
    if not chrome_bin and os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        chrome_bin = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    if not chrome_bin:
        raise RuntimeError("Google Chrome or Chromium is required for live browser tests. Chrome binary not found.")

    node_bin = shutil.which("node")
    if not node_bin:
        raise RuntimeError("Node.js is required for headless browser automation. node binary not found.")

    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=ROOT, **kwargs)

        def log_message(self, format, *args):
            pass

        def handle(self):
            try:
                super().handle()
            except (BrokenPipeError, ConnectionResetError):
                pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), SilentHandler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://127.0.0.1:{port}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        debug_port = s.getsockname()[1]

    node_script = f"""
const {{ spawn }} = require('child_process');
async function run() {{
  const chrome = spawn('{chrome_bin}', [
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port={debug_port}'
  ]);
  await new Promise(r => setTimeout(r, 1200));
  const res = await fetch('http://localhost:{debug_port}/json');
  const tabs = await res.json();
  const pageTab = tabs.find(t => t.type === 'page');
  const ws = new WebSocket(pageTab.webSocketDebuggerUrl);

  const send = (method, params = {{}}) => new Promise((resolve) => {{
    const id = Math.floor(Math.random() * 100000);
    const handler = (msg) => {{
      const data = JSON.parse(msg.data);
      if (data.id === id) {{
        ws.removeEventListener('message', handler);
        resolve(data.result);
      }}
    }};
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({{ id, method, params }}));
  }});

  ws.onopen = async () => {{
    const results = {{}};

    for (const width of [375, 608]) {{
      await send('Emulation.setDeviceMetricsOverride', {{ width, height: 812, deviceScaleFactor: 1, mobile: true }});
      await send('Page.navigate', {{ url: '{base_url}/archive.html?q=伊達判決' }});
      await new Promise(r => setTimeout(r, 1000));

      const evalRes = await send('Runtime.evaluate', {{
        returnByValue: true,
        expression: `(() => {{
          const firstEntry = document.querySelector('.search-results-list .entry');
          const searchBox = document.querySelector('#article-search');
          const statusText = document.querySelector('#filter-status-text');
          const rect = firstEntry ? firstEntry.getBoundingClientRect() : null;
          return {{
            width: window.innerWidth,
            firstEntryTop: rect ? Math.round(rect.top) : null,
            firstEntryFound: Boolean(firstEntry),
            searchVisible: Boolean(searchBox),
            status: statusText ? statusText.textContent : ''
          }};
        }})()`
      }});
      results[width] = evalRes.result.value;
    }}

    // Desktop 1024px
    await send('Emulation.setDeviceMetricsOverride', {{ width: 1024, height: 800, deviceScaleFactor: 1, mobile: false }});
    await send('Page.navigate', {{ url: '{base_url}/archive.html' }});
    await new Promise(r => setTimeout(r, 1000));

    const desktopEval = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const typeSummary = document.querySelector('.type-nav-summary');
        const typeButtons = document.querySelector('.type-nav-buttons');
        const buttons = [...document.querySelectorAll('.type-filter')];
        return {{
          typeSummaryDisplay: window.getComputedStyle(typeSummary).display,
          typeButtonsDisplay: window.getComputedStyle(typeButtons).display,
          typeButtonsCount: buttons.length,
          allButtonsVisible: buttons.every(b => b.getBoundingClientRect().height > 0)
        }};
      }})()`
    }});
    results['desktop'] = desktopEval.result.value;

    console.log(JSON.stringify(results));
    ws.close();
    chrome.kill();
    process.exit(0);
  }};
}}
run().catch(e => {{ console.error(e); process.exit(1); }});
"""
    try:
        proc = subprocess.run([node_bin, "-e", node_script], capture_output=True, text=True, check=True)
        results = json.loads(proc.stdout.strip().splitlines()[-1])
        for w in [375, 608]:
            val = results[str(w)]
            assert val['searchVisible'], f"Search box not visible at {w}px"
            assert "45" in val['status'], f"Active result count not 45 at {w}px: {val['status']}"
            assert val['firstEntryFound'], f"First article entry not found at {w}px"
            assert val['firstEntryTop'] is not None and val['firstEntryTop'] <= 450, (
                f"First entry top {val['firstEntryTop']}px exceeds 450px budget at {w}px"
            )
            print(f"  ✓ Viewport {w}px: first entry top = {val['firstEntryTop']}px (<= 450px), search & count visible")

        d_val = results['desktop']
        assert d_val['typeSummaryDisplay'] == 'none', "Type summary should be hidden on desktop"
        assert d_val['typeButtonsDisplay'] == 'flex', "Type buttons should be display: flex on desktop"
        assert d_val['typeButtonsCount'] == 9, f"Expected 9 type buttons, found {d_val['typeButtonsCount']}"
        assert d_val['allButtonsVisible'], "All 9 type buttons must be visible on desktop"
        print("  ✓ Desktop view (1024px): type buttons unfolded (display: flex) and all 9 buttons visible")
    finally:
        server.shutdown()

if __name__ == '__main__':
    test_archive_html_structure()
    test_css_styling_and_height_budget()
    test_javascript_behavior()
    test_live_viewport_above_the_fold()
    print("\nAll archive filter tests passed successfully!")
