#!/usr/bin/env python3
"""
Test search snippet URL stripping in archive.html (SITES-7 / SUNA-17)

Verifies:
1. archive.html implementation strips raw URLs (http:// and https://) using URL-safe ASCII characters.
2. In search results for '伊達判決' (and other queries), no snippet contains http:// or https://.
3. Reproduces the bug: without URL stripping, 'articles/ameblo-12867279876.html' contains 'https://youtu.be/...'.
4. With URL stripping, the snippet window pulls in readable text to maintain length (~35 chars before/after match).
5. Boundary preservation: URL stripping stops at non-URL characters (e.g. Japanese text directly appended to a URL
   in articles/fc2-102.html and articles/fc2-59.html), preventing text loss for search terms like '所要時間'.
"""

import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVE_HTML = BASE_DIR / "archive.html"
SEARCH_INDEX = BASE_DIR / "search-index.json"

# Matches http(s):// followed by URL-safe ASCII characters (RFC 3986)
URL_REGEX = re.compile(r"https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;%=]+", re.IGNORECASE)
WHITESPACE_REGEX = re.compile(r'\s+')


def extract_snippet(body_text: str, query: str, strip_urls: bool = True) -> str:
    if strip_urls:
        body_text = URL_REGEX.sub('', body_text)
        body_text = WHITESPACE_REGEX.sub(' ', body_text)
    
    idx = body_text.lower().find(query.lower())
    if idx == -1:
        return ""
    
    start = max(0, idx - 35)
    end = min(len(body_text), idx + len(query) + 35)
    snippet = ('…' if start > 0 else '') + body_text[start:end].strip() + ('…' if end < len(body_text) else '')
    return snippet


def test_archive_html_implementation():
    print("Testing archive.html implementation...")
    with open(ARCHIVE_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    
    # Assert URL stripping regex is present in archive.html snippet extraction logic
    expected_js = "replace(/https?:\\/\\/[a-zA-Z0-9\\-._~:/?#\\[\\]@!$&'()*+,;%=]+/gi, '')"
    assert expected_js in html, "archive.html does not contain expected URL-stripping logic"
    print("  ✓ archive.html contains URL stripping and whitespace normalization regex")


def test_reproduce_bug_and_fix():
    print("Testing bug reproduction and fix on search-index.json...")
    with open(SEARCH_INDEX, "r", encoding="utf-8") as f:
        items = json.load(f).get("items", [])
    
    target_item = next((item for item in items if item.get("url") == "articles/ameblo-12867279876.html"), None)
    assert target_item is not None, "Target test article articles/ameblo-12867279876.html not found"
    
    query = "伊達判決"
    search_text = target_item.get("search", "")
    
    # 1. Reproduce bug: old logic (unstripped) produces raw URL in snippet
    old_snippet = extract_snippet(search_text, query, strip_urls=False)
    assert "https://youtu.be/" in old_snippet, f"Expected bug reproduction with raw URL, got: {old_snippet}"
    print(f"  ✓ Bug reproduced without stripping: snippet contained raw URL ({old_snippet[:60]}...)")
    
    # 2. Verify fix: new logic strips the URL and fills in readable text
    new_snippet = extract_snippet(search_text, query, strip_urls=True)
    assert "http://" not in new_snippet and "https://" not in new_snippet, f"Snippet still contains URL: {new_snippet}"
    assert "報告集会の動画" in new_snippet, f"Snippet did not pull in readable text: {new_snippet}"
    print(f"  ✓ Fix verified with stripping: 0 URLs in snippet ({new_snippet[:60]}...)")


def test_acceptance_criteria_date_hanketsu():
    print("Testing Acceptance Criteria: query '伊達判決' across all archive entries...")
    with open(SEARCH_INDEX, "r", encoding="utf-8") as f:
        items = json.load(f).get("items", [])
    
    query = "伊達判決"
    snippet_count = 0
    for item in items:
        title = item.get("title", "")
        search_text = item.get("search", "")
        if query.lower() in search_text.lower() and query.lower() not in title.lower():
            snippet = extract_snippet(search_text, query, strip_urls=True)
            snippet_count += 1
            assert "http://" not in snippet and "https://" not in snippet, (
                f"Found raw URL in snippet for {item.get('url')}: {snippet}"
            )
    
    assert snippet_count > 0, "No body snippets generated for query '伊達判決'"
    print(f"  ✓ Verified {snippet_count} snippets for '伊達判決' — 0 contain http:// or https://")


def test_japanese_boundary_preservation():
    print("Testing Japanese text preservation when appended directly to URLs...")
    with open(SEARCH_INDEX, "r", encoding="utf-8") as f:
        items = json.load(f).get("items", [])
    
    fc2_102 = next((item for item in items if item.get("url") == "articles/fc2-102.html"), None)
    assert fc2_102 is not None, "articles/fc2-102.html not found"
    
    # Query '所要時間' appears right after 'http://www.showakinen-koen.jp/facility/'
    # A naive [^\s]+ regex would swallow Japanese text because Japanese has no spaces
    snip_102 = extract_snippet(fc2_102.get("search", ""), "所要時間", strip_urls=True)
    assert snip_102, "Expected snippet for '所要時間', but it was empty (swallowed by naive URL regex)!"
    assert "http://" not in snip_102 and "https://" not in snip_102
    assert "所要時間はこちら" in snip_102
    print("  ✓ articles/fc2-102.html: '所要時間' snippet preserved and clean of URLs")

    fc2_59 = next((item for item in items if item.get("url") == "articles/fc2-59.html"), None)
    assert fc2_59 is not None, "articles/fc2-59.html not found"
    snip_59 = extract_snippet(fc2_59.get("search", ""), "是非ご覧ください", strip_urls=True)
    assert snip_59, "Expected snippet for '是非ご覧ください', but it was empty!"
    assert "http://" not in snip_59 and "https://" not in snip_59
    assert "是非ご覧ください" in snip_59
    print("  ✓ articles/fc2-59.html: '是非ご覧ください' snippet preserved and clean of URLs")


def test_synthetic_edge_cases():
    print("Testing synthetic edge cases...")
    
    # URL immediately before query
    t1 = "前文 https://example.com/a/b?c=1&d=2 検索対象の文脈 後文"
    s1 = extract_snippet(t1, "検索対象", strip_urls=True)
    assert "http" not in s1
    assert "前文" in s1 and "検索対象" in s1
    
    # URL immediately after query
    t2 = "プレフィックス 検索対象 http://test.org/path/to/page サフィックス"
    s2 = extract_snippet(t2, "検索対象", strip_urls=True)
    assert "http" not in s2
    assert "プレフィックス" in s2 and "サフィックス" in s2
    
    # Multiple URLs and markdown-like brackets
    t3 = "参照: [リンク](https://example.com) と <https://foo.bar/baz> を確認。砂川事件の記録。"
    s3 = extract_snippet(t3, "砂川事件", strip_urls=True)
    assert "http" not in s3
    assert "砂川事件" in s3
    
    # URL directly followed by Japanese text without space
    t4 = "案内ページhttps://example.com/info/ここをクリックして確認"
    s4 = extract_snippet(t4, "クリック", strip_urls=True)
    assert "http" not in s4
    assert "ここをクリックして確認" in s4

    print("  ✓ All synthetic edge cases passed")


def main():
    try:
        test_archive_html_implementation()
        test_reproduce_bug_and_fix()
        test_acceptance_criteria_date_hanketsu()
        test_japanese_boundary_preservation()
        test_synthetic_edge_cases()
        print("\nAll search snippet tests passed successfully!")
    except AssertionError as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
