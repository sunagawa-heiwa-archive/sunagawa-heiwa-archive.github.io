#!/usr/bin/env python3
"""
Test suite for SITES-37:
Preserve search/filter state and scroll position on return.
Verifies:
1. Static script checks in archive.html (AC 1 & AC 4):
   - Initial load syncs sessionStorage.archive_last_search when arriving with query params.
   - Click listener on article entries records archive_last_article.
   - Position restoration logic scrolls target entry into view after render.
2. Static script checks in articles/*.html (AC 2 & AC 5):
   - #backToListLink exists and reads archive_last_search.
3. Live browser integration test (via headless Chrome):
   - Arriving at archive.html?q=伊達判決 sets sessionStorage.archive_last_search.
   - Clicking an article in search results navigates to the article page.
   - The article page's #backToListLink contains ?q=伊達判決.
   - Returning to archive.html restores 45 results and scrolls the clicked article into view.
   - Direct visitor with empty sessionStorage has backToListLink falling back to ../archive.html.
"""

import os
import re
import sys
import shutil
import socket
import threading
import subprocess
import json
import urllib.request
import http.server

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ARCHIVE_HTML = os.path.join(ROOT, "archive.html")


def test_static_archive_html():
    print("Testing static implementation in archive.html...")
    with open(ARCHIVE_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # AC 1: initial run must remember/sync archive_last_search
    # Concrete wiring check for initial run with remember=true and Promise chain
    assert re.search(
        r'run\s*\(\s*initialLanguage,\s*initialYear,\s*initialType,\s*initial\.q,\s*initialSort,\s*true,\s*true\s*\)\.then\(',
        html,
    ), "archive.html must invoke run(initialLanguage, initialYear, initialType, initial.q, initialSort, true, true).then(...)"
    assert "sessionStorage.setItem('archive_last_search'" in html, (
        "archive.html must sync query string to sessionStorage.archive_last_search"
    )

    # AC 4: entry click tracking and restoration concrete wiring
    assert "document.addEventListener('click', saveClickedEntry)" in html, (
        "archive.html must attach click listener for article entry tracking"
    )
    assert "document.addEventListener('auxclick', saveClickedEntry)" in html, (
        "archive.html must attach auxclick listener for article entry tracking"
    )
    assert "sessionStorage.setItem('archive_last_article', href)" in html, (
        "archive.html must record clicked article href into sessionStorage"
    )
    assert "sessionStorage.setItem('archive_last_scroll', String(window.scrollY))" in html, (
        "archive.html must record scroll position into sessionStorage"
    )
    assert "targetEntry.scrollIntoView({ block: 'center'" in html, (
        "archive.html must restore entry position using scrollIntoView({ block: 'center' })"
    )
    print("  ✓ Static archive.html concrete wiring checks passed")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def test_live_browser_flow():
    print("Testing live browser return state and scroll restoration...")
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

    port = find_free_port()
    debug_port = find_free_port()

    # Start local HTTP server
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
    await send('Emulation.setDeviceMetricsOverride', {{ width: 1200, height: 800, deviceScaleFactor: 1, mobile: false }});

    // 1. Visit archive with query
    await send('Page.navigate', {{ url: '{base_url}/archive.html?q=伊達判決' }});
    await new Promise(r => setTimeout(r, 800));

    // Check sessionStorage.archive_last_search
    const initStorageRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `sessionStorage.getItem('archive_last_search')`
    }});
    const initStorage = initStorageRaw.result ? initStorageRaw.result.value : null;

    // Get 5th entry href and simulate click on it (recording to sessionStorage)
    const clickResultRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const entries = Array.from(document.querySelectorAll('#search-results-list .entry:not([hidden])'));
        if (entries.length < 5) return {{ error: 'Less than 5 entries' }};
        const target = entries[4];
        const href = target.getAttribute('href');
        target.click();
        return {{ href, targetHref: target.href }};
      }})()`
    }});
    const clickResult = clickResultRaw.result ? clickResultRaw.result.value : {{}};

    // Explicitly navigate to the article page to ensure clean navigation
    await send('Page.navigate', {{ url: clickResult.targetHref }});
    await new Promise(r => setTimeout(r, 800));

    // Check article back link
    const articleBackLinkRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const link = document.getElementById('backToListLink');
        return link ? link.getAttribute('href') : null;
      }})()`
    }});
    const articleBackLink = articleBackLinkRaw.result ? articleBackLinkRaw.result.value : null;

    // Navigate back to the backToListLink destination
    const returnUrl = new URL(articleBackLink, clickResult.targetHref).href;
    await send('Page.navigate', {{ url: returnUrl }});
    await new Promise(r => setTimeout(r, 1000));

    // Verify state on return
    const returnStateRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const searchVal = document.getElementById('article-search').value;
        const visibleEntries = Array.from(document.querySelectorAll('#search-results-list .entry:not([hidden])'));
        const targetEntry = visibleEntries.find(e => e.getAttribute('href') === '${{clickResult.href}}');
        let rect = null;
        if (targetEntry) {{
          rect = targetEntry.getBoundingClientRect();
        }}
        return {{
          searchVal,
          count: visibleEntries.length,
          hasTarget: !!targetEntry,
          top: rect ? rect.top : null,
          bottom: rect ? rect.bottom : null,
          innerHeight: window.innerHeight,
          scrollY: window.scrollY
        }};
      }})()`
    }});
    const returnState = returnStateRaw.result ? returnStateRaw.result.value : {{}};

    // Direct visitor check: clear sessionStorage and navigate to article
    await send('Runtime.evaluate', {{ expression: `sessionStorage.clear()` }});
    await send('Page.navigate', {{ url: '{base_url}/articles/ameblo-12863375762.html' }});
    await new Promise(r => setTimeout(r, 600));
    const fallbackLinkRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const link = document.getElementById('backToListLink');
        return link ? link.getAttribute('href') : null;
      }})()`
    }});
    const fallbackLink = fallbackLinkRaw.result ? fallbackLinkRaw.result.value : null;

    // Mobile check at 375px width (AC 4 & UAT step 7)
    await send('Emulation.setDeviceMetricsOverride', {{ width: 375, height: 667, deviceScaleFactor: 2, mobile: true }});
    await send('Page.navigate', {{ url: '{base_url}/archive.html?q=伊達判決' }});
    await new Promise(r => setTimeout(r, 800));

    const mobileClickRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const entries = Array.from(document.querySelectorAll('#search-results-list .entry:not([hidden])'));
        const target = entries[6];
        target.click();
        return {{ href: target.getAttribute('href'), targetHref: target.href }};
      }})()`
    }});
    const mobileClick = mobileClickRaw.result ? mobileClickRaw.result.value : {{}};

    await send('Page.navigate', {{ url: mobileClick.targetHref }});
    await new Promise(r => setTimeout(r, 800));

    const mobileBackLinkRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const link = document.getElementById('backToListLink');
        return link ? link.getAttribute('href') : null;
      }})()`
    }});
    const mobileBackLink = mobileBackLinkRaw.result ? mobileBackLinkRaw.result.value : null;

    const mobileReturnUrl = new URL(mobileBackLink, mobileClick.targetHref).href;
    await send('Page.navigate', {{ url: mobileReturnUrl }});
    await new Promise(r => setTimeout(r, 1000));

    const mobileReturnStateRaw = await send('Runtime.evaluate', {{
      returnByValue: true,
      expression: `(() => {{
        const searchVal = document.getElementById('article-search').value;
        const visibleEntries = Array.from(document.querySelectorAll('#search-results-list .entry:not([hidden])'));
        const targetEntry = visibleEntries.find(e => e.getAttribute('href') === '${{mobileClick.href}}');
        let rect = null;
        if (targetEntry) {{
          rect = targetEntry.getBoundingClientRect();
        }}
        return {{
          searchVal,
          count: visibleEntries.length,
          hasTarget: !!targetEntry,
          top: rect ? rect.top : null,
          innerHeight: window.innerHeight,
          scrollY: window.scrollY
        }};
      }})()`
    }});
    const mobileReturnState = mobileReturnStateRaw.result ? mobileReturnStateRaw.result.value : {{}};

    console.log(JSON.stringify({{
      initStorage,
      clickResult,
      articleBackLink,
      returnState,
      fallbackLink,
      mobileBackLink,
      mobileReturnState
    }}));

    chrome.kill();
    process.exit(0);
  }};
}}
run().catch(e => {{ console.error(e); process.exit(1); }});
"""
    result = subprocess.run([node_bin, "-e", node_script], capture_output=True, text=True)
    server.shutdown()

    if result.returncode != 0:
        raise RuntimeError(f"Node execution failed: {result.stderr}")

    data = json.loads(result.stdout.strip())
    print(f"  Live test results: {data}")

    # Assertions
    unquoted_init = urllib.parse.unquote(data["initStorage"] or "")
    unquoted_back = urllib.parse.unquote(data["articleBackLink"] or "")

    assert "伊達判決" in unquoted_init, (
        f"sessionStorage.archive_last_search not set on arrival: {data['initStorage']}"
    )
    assert "伊達判決" in unquoted_back, (
        f"Article backToListLink did not contain query: {data['articleBackLink']}"
    )
    ret = data["returnState"]
    assert ret["searchVal"] == "伊達判決", f"Search input value lost on return: {ret['searchVal']}"
    assert ret["count"] == 45, f"Search results count unexpected: {ret['count']}"
    assert ret["hasTarget"], "Target entry was not found in returned list"
    assert ret["top"] is not None and -100 <= ret["top"] <= ret["innerHeight"], (
        f"Target entry is not in viewport: top={ret['top']}, innerHeight={ret['innerHeight']}"
    )
    assert data["fallbackLink"] == "../archive.html", (
        f"Direct visitor fallback link incorrect: {data['fallbackLink']}"
    )

    # Mobile assertions
    unquoted_mob_back = urllib.parse.unquote(data["mobileBackLink"] or "")
    assert "伊達判決" in unquoted_mob_back, (
        f"Mobile back link did not contain query: {data['mobileBackLink']}"
    )
    m_ret = data["mobileReturnState"]
    assert m_ret["searchVal"] == "伊達判決", f"Mobile search input lost: {m_ret['searchVal']}"
    assert m_ret["count"] == 45, f"Mobile results count unexpected: {m_ret['count']}"
    assert m_ret["hasTarget"], "Mobile target entry not found"
    assert m_ret["top"] is not None and -100 <= m_ret["top"] <= m_ret["innerHeight"], (
        f"Mobile target entry is not in viewport: top={m_ret['top']}, innerHeight={m_ret['innerHeight']}"
    )
    print("  ✓ Live browser return state & scroll restoration verified (desktop + 375px mobile)")


def main():
    try:
        test_static_archive_html()
        test_live_browser_flow()
        print("\nAll search return state tests passed successfully!")
    except AssertionError as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
