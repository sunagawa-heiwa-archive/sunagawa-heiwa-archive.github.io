#!/usr/bin/env python3
"""
Test suite for SITES-39:
Normalize excessive whitespace in directory titles in archive.html.
Verifies:
1. All 208 article titles in archive.html have no consecutive whitespace (half-width or full-width ideographic).
2. Specifically checks 2023-09-14 ameblo-12820410904 title whitespace collapse.
3. Punctuation, Japanese/English characters, dates, and order preserved.
4. Zero changes to articles/ or raw/ directory, byte-identical to origin/main (AC 5).
5. Search matching and keyword highlighting work with normalized title.
6. Live headless Chrome viewport checks at 320px, 375px, and desktop for zero horizontal overflow,
   browse mode compact ellipsis (SITES-23), and search mode natural title wrapping (AC 3 & AC 4).
"""

import http.server
import json
import os
import re
import shutil
import socket
import subprocess
import threading
from html.parser import HTMLParser

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TitleParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles = []
        self.entries = []
        self.in_entry_title = False
        self.current_entry = {}
        self.current_title_parts = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag == "a" and "entry" in attr_dict.get("class", "").split():
            self.current_entry = {
                "href": attr_dict.get("href", ""),
                "year": attr_dict.get("data-year", ""),
                "type": attr_dict.get("data-type", ""),
            }
        elif tag == "span" and "entry-title" in attr_dict.get("class", "").split():
            self.in_entry_title = True
            self.current_title_parts = []

    def handle_endtag(self, tag):
        if tag == "span" and self.in_entry_title:
            self.in_entry_title = False
            title_text = "".join(self.current_title_parts)
            self.titles.append(title_text)
            if self.current_entry:
                self.current_entry["title"] = title_text
                self.entries.append(self.current_entry)
                self.current_entry = {}

    def handle_data(self, data):
        if self.in_entry_title:
            self.current_title_parts.append(data)


def test_no_excessive_whitespace_in_titles():
    """AC 1 & AC 2: All titles in archive.html have 0 consecutive spaces / full-width spaces."""
    archive_path = os.path.join(ROOT, "archive.html")
    with open(archive_path, "r", encoding="utf-8") as f:
        html = f.read()

    parser = TitleParser()
    parser.feed(html)

    assert len(parser.titles) == 208, f"Expected 208 article titles, found {len(parser.titles)}"

    excessive = []
    for entry in parser.entries:
        t = entry["title"]
        if re.search(r"[\s\u3000]{2,}", t):
            excessive.append((entry["href"], repr(t)))

    assert not excessive, (
        f"Found {len(excessive)} titles with consecutive whitespace in archive.html:\n"
        + "\n".join(f"  {href}: {title}" for href, title in excessive)
    )
    print("  ✓ All 208 article titles have whitespace collapsed (0 consecutive spaces)")


def test_target_article_title_normalization():
    """Verify specific articles mentioned in user story & acceptance criteria."""
    archive_path = os.path.join(ROOT, "archive.html")
    with open(archive_path, "r", encoding="utf-8") as f:
        html = f.read()

    parser = TitleParser()
    parser.feed(html)
    entry_map = {e["href"]: e["title"] for e in parser.entries}

    target_href = "articles/ameblo-12820410904.html"
    assert target_href in entry_map, f"Target article {target_href} not found in archive.html"
    expected_title = "砂川平和ひろば主催 10.14集会 「多摩の水汚染を考える」 チラシ完成"
    actual_title = entry_map[target_href]
    assert actual_title == expected_title, (
        f"Expected title:\n  {expected_title}\nGot:\n  {actual_title}"
    )
    print("  ✓ Target article 2023-09-14 title accurately normalized")


def test_articles_and_raw_untouched():
    """AC 5: Ensure articles/ and raw/ files are completely unmodified and byte-identical to origin/main."""
    # 1. Assert git diff against origin/main for articles/ and raw/ is clean
    res = subprocess.run(["git", "diff", "--quiet", "origin/main", "--", "articles", "raw"], cwd=ROOT)
    assert res.returncode == 0, "articles/ or raw/ directory has differences versus origin/main!"

    # 2. Specifically assert target article retains original 8 consecutive ideographic spaces
    target_article = os.path.join(ROOT, "articles", "ameblo-12820410904.html")
    assert os.path.isfile(target_article), "Target article file missing"
    with open(target_article, "r", encoding="utf-8") as f:
        content = f.read()
    assert "\u3000\u3000\u3000\u3000\u3000\u3000\u3000\u3000" in content, (
        "Original 8 full-width spaces must be preserved byte-identical in archived article page"
    )
    print("  ✓ articles/ and raw/ confirmed 100% byte-identical to origin/main with raw spaces preserved")


def test_live_viewport_and_search_highlight():
    """AC 3 & AC 4: Test live Chrome rendering at 320px, 375px, 1024px and search highlighting."""
    chrome_bin = (
        shutil.which("google-chrome")
        or shutil.which("chromium")
        or shutil.which("chrome")
        or (
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            if os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
            else None
        )
    )
    if not chrome_bin:
        raise RuntimeError("Google Chrome binary not found for live browser tests.")

    node_bin = shutil.which("node")
    if not node_bin:
        raise RuntimeError("Node.js binary not found for live browser tests.")

    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), SilentHandler)
    port = server.server_port
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

    // 1. Check responsive viewports for horizontal overflow and browse-mode compact ellipsis
    for (const width of [320, 375, 1024]) {{
      await send('Emulation.setDeviceMetricsOverride', {{ width, height: 800, deviceScaleFactor: 1, mobile: width < 700 }});
      await send('Page.navigate', {{ url: '{base_url}/archive.html' }});
      await new Promise(r => setTimeout(r, 1000));

      const evalRes = await send('Runtime.evaluate', {{
        returnByValue: true,
        expression: `(() => {{
          const targetEntry = document.querySelector('a.entry[href*="12820410904"]');
          const titleEl = targetEntry ? targetEntry.querySelector('.entry-title') : null;
          const titleStyle = titleEl ? window.getComputedStyle(titleEl) : null;
          return {{
            width: window.innerWidth,
            scrollWidth: document.documentElement.scrollWidth,
            hasHorizontalOverflow: document.documentElement.scrollWidth > window.innerWidth,
            browseWhiteSpace: titleStyle ? titleStyle.whiteSpace : '',
            browseTextOverflow: titleStyle ? titleStyle.textOverflow : '',
            browseTruncated: titleEl ? titleEl.scrollWidth > titleEl.clientWidth : false
          }};
        }})()`
      }});
      results[width] = evalRes.result.value;
    }}

    // 2. Check search mode: keyword highlight and natural title wrapping without truncation
    await send('Emulation.setDeviceMetricsOverride', {{ width: 375, height: 800, deviceScaleFactor: 1, mobile: true }});
    await send('Page.navigate', {{ url: '{base_url}/archive.html?q=多摩の水汚染' }});
    await new Promise(r => setTimeout(r, 1200));

    const searchEval = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const targetEntry = document.querySelector('a.entry[href*="12820410904"]');
        const titleEl = targetEntry ? targetEntry.querySelector('.entry-title') : null;
        const titleStyle = titleEl ? window.getComputedStyle(titleEl) : null;
        const mark = titleEl ? titleEl.querySelector('mark.search-highlight') : null;
        return {{
          entryFound: Boolean(targetEntry),
          titleText: titleEl ? titleEl.textContent : '',
          markFound: Boolean(mark),
          markText: mark ? mark.textContent : '',
          searchWhiteSpace: titleStyle ? titleStyle.whiteSpace : '',
          searchOverflow: titleStyle ? titleStyle.overflow : ''
        }};
      }})()`
    }});
    results['search'] = searchEval.result.value;

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

        for w in [320, 375, 1024]:
            val = results[str(w)]
            assert not val['hasHorizontalOverflow'], f"Horizontal overflow detected at {w}px: scrollWidth={val['scrollWidth']}"
            print(f"  ✓ Viewport {w}px: zero horizontal overflow (scrollWidth {val['scrollWidth']}px <= {w}px)")

        # Verify browse mode compact ellipsis behavior (as established by SITES-23)
        b375 = results['375']
        assert b375['browseWhiteSpace'] == 'nowrap', "Browse mode must use nowrap"
        assert b375['browseTextOverflow'] == 'ellipsis', "Browse mode must use ellipsis"
        assert b375['browseTruncated'], "Long title at 375px should truncate with ellipsis in browse mode"
        print("  ✓ Browse mode (375px): compact ellipsis truncation confirmed (SITES-23 format)")

        # Verify search mode wraps naturally without truncation
        s_val = results['search']
        assert s_val['entryFound'], "Search for '多摩の水汚染' did not find target entry ameblo-12820410904"
        assert s_val['markFound'], "Search keyword '多摩の水汚染' was not highlighted in title"
        assert s_val['markText'] == "多摩の水汚染", f"Unexpected highlight text: {s_val['markText']}"
        assert s_val['searchWhiteSpace'] == 'normal', "Search mode must allow natural title wrapping (white-space: normal)"
        assert s_val['searchOverflow'] == 'visible', "Search mode must display full title (overflow: visible)"
        print("  ✓ Search mode (375px): title wraps naturally without truncation and keyword is highlighted")
    finally:
        server.shutdown()


if __name__ == "__main__":
    print("Testing title whitespace normalization (SITES-39)...")
    test_no_excessive_whitespace_in_titles()
    test_target_article_title_normalization()
    test_articles_and_raw_untouched()
    test_live_viewport_and_search_highlight()
    print("\nAll title whitespace tests passed successfully!")
