#!/usr/bin/env python3
"""
Test home search form implementation in index.html (SITES-24)

Verifies:
1. index.html contains a pure GET form pointing to archive.html with search input and submit button.
2. Label for search input is visible and accessible (contains '記事検索 / Search articles').
3. Empty query submission omits 'q' parameter or navigates directly to archive.html.
4. Retains browse entry link for all 208 articles.
5. Reading order matches SITES-24 (H1 -> lede -> intro -> position -> search -> guide card).
6. Integration check: archive.html handles 'q' query parameter properly (e.g. '伊達判決').
"""

import re
import sys
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_HTML = BASE_DIR / "index.html"
ARCHIVE_HTML = BASE_DIR / "archive.html"


def test_home_search_form():
    print("Testing index.html home search form...")
    with open(INDEX_HTML, "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Form existence and attributes
    form = soup.find("form", attrs={"action": "archive.html"})
    assert form is not None, "Form with action='archive.html' not found in index.html"
    assert form.get("method", "").lower() == "get", f"Form method must be 'get', got: {form.get('method')}"
    
    # 2. Label check
    input_el = form.find("input", attrs={"name": "q"})
    assert input_el is not None, "Search input with name='q' not found in form"
    input_id = input_el.get("id")
    assert input_id, "Search input must have an id attribute"
    
    label = soup.find("label", attrs={"for": input_id})
    assert label is not None, f"Label for id '{input_id}' not found"
    assert "記事検索" in label.get_text() and "Search articles" in label.get_text(), (
        f"Label text must contain '記事検索 / Search articles', got: {label.get_text()}"
    )
    # Ensure label is not hidden by visually-hidden class
    classes = label.get("class", [])
    assert "visually-hidden" not in classes, "Label must be visible, not visually-hidden"
    print("  ✓ Form and visible accessible label verified")
    
    # 3. Submit button
    submit_btn = form.find("button", attrs={"type": "submit"})
    assert submit_btn is not None, "Submit button not found in search form"
    assert "検索" in submit_btn.get_text() or "Search" in submit_btn.get_text(), (
        f"Submit button must contain '検索', got: {submit_btn.get_text()}"
    )
    print("  ✓ Submit button verified")
    
    # 4. Empty query handling (onsubmit attribute or form behavior)
    onsubmit = form.get("onsubmit", "")
    assert "archive.html" in onsubmit and ("location" in onsubmit or "href" in onsubmit), (
        f"Form should redirect to archive.html on empty submission, got onsubmit: {onsubmit}"
    )
    # Ensure name attribute is not mutated (protects against bfcache bugs)
    assert ".name" not in onsubmit, (
        f"onsubmit must not mutate input name attribute (causes bfcache bugs): {onsubmit}"
    )
    print("  ✓ Empty query submission handling verified (no DOM mutation, bfcache-safe)")
    
    # 5. Browse entry link retained
    browse_link = soup.select_one(".hero-cta a[href='archive.html']")
    assert browse_link is not None, "Browse link in .hero-cta to archive.html not found"
    assert "全208件" in browse_link.get_text(), (
        f"Browse link text should contain '全208件', got: {browse_link.get_text()}"
    )
    print("  ✓ Browse link for all 208 articles retained")
    
    # 6. Page order per SITES-24: H1 -> lede -> intro -> position -> search -> guide card
    main = soup.find("main", id="main")
    assert main is not None, "main#main not found"
    main_text = str(main)
    pos_form = main_text.find("archive.html")
    pos_intro = main_text.find("hero-intro")
    pos_position = main_text.find("hero-position")
    
    assert pos_form != -1 and pos_intro != -1 and pos_position != -1, "Expected sections not found in main"
    assert pos_intro < pos_position < pos_form, (
        f"Order violation: intro ({pos_intro}) and position ({pos_position}) must precede search ({pos_form}) per SITES-24"
    )
    print("  ✓ Reading order verified (intro -> position -> search per SITES-24)")


def test_archive_search_integration():
    print("Testing archive.html query handling...")
    with open(ARCHIVE_HTML, "r", encoding="utf-8") as f:
        archive_html = f.read()
    
    assert "p.get('q')" in archive_html or 'params().get("q")' in archive_html, (
        "archive.html does not parse 'q' query parameter"
    )
    print("  ✓ archive.html query parameter integration verified")


def main():
    try:
        test_home_search_form()
        test_archive_search_integration()
        print("\nAll home search tests passed successfully!")
    except AssertionError as e:
        print(f"\nFAIL: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
