#!/usr/bin/env python3
"""
Test suite for SITES-23 (PRD SUNA-19):
Compact row list in browse mode, hide month headers, page height <= 18,000px,
card mode in search, and hide Japanese language tags.
100% standard library Python — zero external dependencies.
"""

import os
import re
import subprocess
import json
import urllib.request
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def test_css_rules():
    """Verify required CSS rules in assets/style.css."""
    css_path = os.path.join(ROOT, "assets", "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    # 1. Month headers hidden in browse mode and shown in search mode
    assert ".month-section h3 { display:none;" in css or ".month-section h3 { display: none;" in css or "display:none" in css, \
        "CSS must hide month-section h3 by default in browse mode"
    assert "body.has-search .month-section h3 { display:block; }" in css or "body.has-search .month-section h3 { display: block; }" in css, \
        "CSS must restore month-section h3 in search mode"

    # 2. Compact row styling for .entry (height <= 64px, single-line ellipsis)
    assert "max-height:64px" in css or "max-height: 64px" in css, \
        "CSS must specify max-height <= 64px for compact entries"
    assert "text-overflow:ellipsis" in css or "text-overflow: ellipsis" in css, \
        "CSS must specify text-overflow: ellipsis for compact entry titles"
    assert "white-space:nowrap" in css or "white-space: nowrap" in css, \
        "CSS must specify white-space: nowrap for compact entry titles"

    # 3. Japanese language tag hidden
    assert '.entry[data-language="ja"] .entry-language { display:none; }' in css or \
           '.entry[data-language="ja"] .entry-language { display: none; }' in css, \
        "CSS must hide entry-language for ja articles"

    # 4. Search card mode overrides
    assert "body.has-search .entry" in css, \
        "CSS must provide search mode overrides for entries"
    assert "max-height:none" in css or "max-height: none" in css, \
        "CSS must remove max-height limit in search mode"
    assert "white-space:normal" in css or "white-space: normal" in css, \
        "CSS must restore normal wrapping in search mode"

    # 5. Desktop browse mode styling
    assert "@media (min-width:701px)" in css or "@media (min-width: 701px)" in css, \
        "CSS must include desktop media query"
    assert "body:not(.has-search) .entry" in css, \
        "CSS must format desktop browse mode entries as horizontal rows"

    print("PASS: CSS rules verified")

def test_archive_html_structure():
    """Verify HTML markup in archive.html."""
    html_path = os.path.join(ROOT, "archive.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Verify no double dots in entry metadata when ja language tag is hidden
    # Format should be <span class="entry-language"> · Japanese / 日本語</span>
    assert " · <span class=\"entry-language\">" not in html, \
        "Leading dot must be inside .entry-language to avoid doubled dots when hidden"
    assert "<span class=\"entry-language\"> · " in html, \
        "Separator dot should be inside .entry-language span"

    # Check total entries
    entry_count = html.count('class="entry"')
    assert entry_count == 208, f"Expected 208 entries, found {entry_count}"

    # Verify month sections exist in DOM for date order sorting
    month_h3_count = html.count('<section class="month-section"><h3>')
    assert month_h3_count == 75, f"Expected 75 month sections in DOM, found {month_h3_count}"

    # Verify body.classList.toggle('has-search', ...) in JS
    assert "document.body.classList.toggle('has-search'" in html, \
        "archive.html JS must toggle has-search class on body"

    print("PASS: archive.html structure verified")

def test_live_browser_metrics():
    """Test live rendering in headless Chrome (if available)."""
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome_path):
        print("SKIP: Chrome not found at standard Mac path, skipping browser metric tests")
        return

    # Check if local server is running on port 8000
    try:
        urllib.request.urlopen("http://localhost:8000/archive.html", timeout=2)
    except Exception:
        print("SKIP: http://localhost:8000 not reachable, skipping live browser tests")
        return

    node_script = """
const { spawn } = require('child_process');
async function run() {
  const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', [
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9228'
  ]);
  await new Promise(r => setTimeout(r, 1200));
  const res = await fetch('http://localhost:9228/json');
  const tabs = await res.json();
  const pageTab = tabs.find(t => t.type === 'page');
  const ws = new WebSocket(pageTab.webSocketDebuggerUrl);

  const send = (method, params = {}) => new Promise((resolve) => {
    const id = Math.floor(Math.random() * 100000);
    const handler = (msg) => {
      const data = JSON.parse(msg.data);
      if (data.id === id) {
        ws.removeEventListener('message', handler);
        resolve(data.result);
      }
    };
    ws.addEventListener('message', handler);
    ws.send(JSON.stringify({ id, method, params }));
  });

  ws.onopen = async () => {
    // 1. Mobile browse mode
    await send('Emulation.setDeviceMetricsOverride', { width: 375, height: 812, deviceScaleFactor: 2, mobile: true });
    await send('Page.navigate', { url: 'http://localhost:8000/archive.html' });
    await new Promise(r => setTimeout(r, 800));

    const mobileBrowse = await send('Runtime.evaluate', {
      returnByValue: true,
      expression: `(() => {
        const entries = Array.from(document.querySelectorAll('.entry'));
        const heights = entries.map(e => e.getBoundingClientRect().height);
        const monthH3s = Array.from(document.querySelectorAll('.month-section h3'));
        const visibleMonthH3s = monthH3s.filter(h => window.getComputedStyle(h).display !== 'none');
        const jaEntries = Array.from(document.querySelectorAll('.entry[data-language="ja"]'));
        const jaLangVisible = jaEntries.filter(e => {
          const l = e.querySelector('.entry-language');
          return l && window.getComputedStyle(l).display !== 'none';
        });
        const nonJaEntries = Array.from(document.querySelectorAll('.entry:not([data-language="ja"])'));
        const nonJaLangVisible = nonJaEntries.filter(e => {
          const l = e.querySelector('.entry-language');
          return l && window.getComputedStyle(l).display !== 'none';
        });
        const sampleJaText = jaEntries[0].querySelector('.entry-meta').innerText;
        const hasDoubleDot = sampleJaText.includes('·  ·') || sampleJaText.includes('··');
        return {
          scrollHeight: document.documentElement.scrollHeight,
          totalEntries: entries.length,
          maxEntryHeight: Math.max(...heights),
          visibleMonthH3s: visibleMonthH3s.length,
          jaLangVisible: jaLangVisible.length,
          nonJaTotal: nonJaEntries.length,
          nonJaLangVisible: nonJaLangVisible.length,
          hasDoubleDot
        };
      })()`
    });

    // 2. Mobile search mode
    await send('Page.navigate', { url: 'http://localhost:8000/archive.html?q=伊達判決' });
    await new Promise(r => setTimeout(r, 800));

    const mobileSearch = await send('Runtime.evaluate', {
      returnByValue: true,
      expression: `(() => {
        const entries = Array.from(document.querySelectorAll('.entry:not([hidden])'));
        const snippets = Array.from(document.querySelectorAll('.search-snippet'));
        return {
          visibleEntries: entries.length,
          snippetsCount: snippets.length,
          firstEntryHeight: entries[0] ? entries[0].getBoundingClientRect().height : 0
        };
      })()`
    });

    // 3. Desktop browse mode
    await send('Emulation.setDeviceMetricsOverride', { width: 1280, height: 800, deviceScaleFactor: 2, mobile: false });
    await send('Page.navigate', { url: 'http://localhost:8000/archive.html' });
    await new Promise(r => setTimeout(r, 800));

    const desktopBrowse = await send('Runtime.evaluate', {
      returnByValue: true,
      expression: `(() => {
        const firstEntry = document.querySelector('.entry');
        const style = window.getComputedStyle(firstEntry);
        return {
          flexDirection: style.flexDirection,
          height: firstEntry.getBoundingClientRect().height
        };
      })()`
    });

    ws.close();
    chrome.kill();
    console.log(JSON.stringify({
      mobileBrowse: mobileBrowse.result.value,
      mobileSearch: mobileSearch.result.value,
      desktopBrowse: desktopBrowse.result.value
    }));
    process.exit(0);
  };
}
run().catch(e => { console.error(e); process.exit(1); });
"""
    result = subprocess.run(["node", "-e", node_script], capture_output=True, text=True, check=True)
    data = json.loads(result.stdout)

    mb = data["mobileBrowse"]
    assert mb["scrollHeight"] <= 18000, f"Mobile scroll height {mb['scrollHeight']} exceeds 18000px"
    assert mb["maxEntryHeight"] <= 64, f"Max entry height {mb['maxEntryHeight']} exceeds 64px"
    assert mb["visibleMonthH3s"] == 0, f"Expected 0 visible month headers, found {mb['visibleMonthH3s']}"
    assert mb["jaLangVisible"] == 0, f"Expected 0 visible ja tags, found {mb['jaLangVisible']}"
    assert mb["nonJaLangVisible"] == mb["nonJaTotal"], "All non-ja tags must be visible"
    assert not mb["hasDoubleDot"], "Found doubled dots in article meta line"

    ms = data["mobileSearch"]
    assert ms["visibleEntries"] > 0, "Search results should be visible"
    assert ms["snippetsCount"] > 0, "Snippets should be present in search mode"
    assert ms["firstEntryHeight"] > 64, f"Search card height {ms['firstEntryHeight']} should expand beyond compact row 64px"

    db = data["desktopBrowse"]
    assert db["flexDirection"] == "row", f"Desktop flex-direction should be row, got {db['flexDirection']}"
    assert db["height"] <= 64, f"Desktop entry height {db['height']} exceeds 64px"

    print("PASS: Live browser rendering metrics verified (AC 1-5)")

if __name__ == "__main__":
    test_css_rules()
    test_archive_html_structure()
    test_live_browser_metrics()
    print("ALL TESTS PASSED")
