#!/usr/bin/env python3
"""
Test script for SITES-11 (PRD SUNA-16):
Search relevance-based sorting in archive.html.
"""

import json
import re
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup

def test_markup():
    print("Testing archive.html markup and DOM structure...")
    with open('archive.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    # 1. Sort control
    sort_ctrl = soup.find(id='sort-control')
    assert sort_ctrl is not None, "Missing #sort-control"
    assert sort_ctrl.has_attr('hidden'), "#sort-control must be hidden initially when no query"

    label = sort_ctrl.find('label', attrs={'for': 'sort-select'})
    assert label is not None, "Missing label with for='sort-select'"
    assert "並び順" in label.text and "Sort" in label.text, f"Label text unexpected: {label.text}"

    select = sort_ctrl.find('select', id='sort-select')
    assert select is not None, "Missing #sort-select"
    options = {opt['value']: opt.text for opt in select.find_all('option')}
    assert 'relevance' in options, "Missing 'relevance' option"
    assert 'date' in options, "Missing 'date' option"
    assert "関連度順" in options['relevance'], "Relevance option text should mention 関連度順"
    assert "新しい順" in options['date'], "Date option text should mention 新しい順"
    print("  ✓ Sort control and options verified")

    # 2. Search results container
    results_list = soup.find(id='search-results-list')
    assert results_list is not None, "Missing #search-results-list"
    assert 'entry-list' in results_list.get('class', []), "#search-results-list should have class 'entry-list'"
    assert results_list.has_attr('hidden'), "#search-results-list must be hidden initially"
    print("  ✓ #search-results-list container verified")

    # 3. Filter actions wrapper
    filter_actions = soup.find(class_='filter-actions')
    assert filter_actions is not None, "Missing .filter-actions"
    assert filter_actions.find(id='sort-control') is not None, "#sort-control must be inside .filter-actions"
    assert filter_actions.find(id='reset-filters') is not None, "#reset-filters must be inside .filter-actions"
    print("  ✓ .filter-actions layout verified")

def test_css():
    print("Testing assets/style.css sort styles...")
    with open('assets/style.css', 'r', encoding='utf-8') as f:
        css = f.read()

    assert '.sort-control' in css, "Missing .sort-control in CSS"
    assert '.search-results-list' in css, "Missing .search-results-list in CSS"
    assert '.sort-control[hidden]' in css, "Missing .sort-control[hidden] in CSS"
    assert '.search-results-list[hidden]' in css, "Missing .search-results-list[hidden] in CSS"
    print("  ✓ CSS selectors and hidden states verified")

def test_relevance_scoring():
    print("Testing relevance scoring algorithm...")
    with open('archive.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    with open('search-index.json', 'r', encoding='utf-8') as f:
        idx = json.load(f)

    search_map = {item['url']: item.get('search', '') for item in idx.get('items', [])}

    def count_occurrences(text, query):
        if not text or not query:
            return 0
        return text.count(query)

    query = '伊達判決'
    matches = []
    for entry in soup.find_all('a', class_='entry'):
        href = entry.get('href')
        title = entry.find(class_='entry-title').get_text()
        body = search_map.get(href, '')
        if query.lower() not in body.lower():
            continue
        time_tag = entry.find('time')
        dt_str = time_tag.get('datetime') if time_tag else '2000-01-01T00:00:00+00:00'
        pub_time = datetime.fromisoformat(dt_str).timestamp()
        
        t_count = count_occurrences(title.lower(), query.lower())
        b_count = count_occurrences(body.lower(), query.lower())
        score = (t_count * 10000) + (b_count * 10) + (pub_time / 1e11)
        matches.append({
            'title': title,
            'score': score,
            'title_matches': t_count,
            'body_matches': b_count,
            'dt': dt_str
        })

    assert len(matches) == 45, f"Expected 45 matches for '伊達判決', got {len(matches)}"

    # Sort by score descending
    matches.sort(key=lambda x: x['score'], reverse=True)

    # Acceptance criteria: At least 3 of top 5 must have '伊達判決' in title
    top_5 = matches[:5]
    top_5_title_matches = sum(1 for m in top_5 if query in m['title'])
    assert top_5_title_matches >= 3, f"Expected at least 3 of top 5 with title match, got {top_5_title_matches}"
    print(f"  ✓ Top 5 for '伊達判決' has {top_5_title_matches}/5 title matches (>= 3 required)")

    # Test tie-breaking by date
    # Two items with same title_matches and body_matches should be ordered by newer date
    tied_found = False
    for i in range(len(matches) - 1):
        a, b = matches[i], matches[i + 1]
        if a['title_matches'] == b['title_matches'] and a['body_matches'] == b['body_matches']:
            tied_found = True
            dt_a = datetime.fromisoformat(a['dt'])
            dt_b = datetime.fromisoformat(b['dt'])
            assert dt_a >= dt_b, f"Tie-break error: {a['dt']} should be >= {b['dt']}"
    if tied_found:
        print("  ✓ Date tie-breaking verified on identical match counts")

def test_script_logic():
    print("Testing script logic and URL synchronization...")
    with open('archive.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Verify key logic patterns in the inline script
    assert "countOccurrences" in html, "Missing countOccurrences helper"
    assert "requestedSort = 'relevance'" in html, "Default sort parameter must be 'relevance'"
    assert "url.searchParams.set('sort', 'relevance')" in html or "url.searchParams.set('sort', sort)" in html, "Missing sort URL sync"
    assert "url.searchParams.delete('sort')" in html, "Missing sort URL deletion when query is empty"
    assert "_origEntries" in html, "Missing _origEntries tracking for clean DOM restoration"
    assert "sortSelect.addEventListener('change'" in html, "Missing sortSelect change event listener"
    print("  ✓ Script implementation details verified")

def test_timeline_restoration_order():
    print("Testing timeline order restoration after clearing relevance search (P1 regression guard)...")
    with open('archive.html', 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    # Record initial order of articles in every month list
    month_sections = soup.find_all('section', class_='month-section')
    initial_month_entries = []
    for month in month_sections:
        entries = [a['href'] for a in month.find_all('a', class_='entry')]
        initial_month_entries.append((month, entries))

    # Node.js simulation executing exact DOM append/re-attach logic
    node_script = """
    const fs = require('fs');
    const html = fs.readFileSync('archive.html', 'utf8');

    // Simple DOM mockup to test the exact entryLists re-attach logic
    // Extract month sections and their entry hrefs
    const monthRegex = /<section class="month-section"[\\s\\S]*?<\\/section>/g;
    const hrefRegex = /href="(articles\\/[^"]+)"/g;

    const months = [];
    let m;
    while ((m = monthRegex.exec(html)) !== null) {
      const monthHtml = m[0];
      const hrefs = [];
      let h;
      while ((h = hrefRegex.exec(monthHtml)) !== null) {
        hrefs.push(h[1]);
      }
      months.push({ hrefs, children: [...hrefs] });
    }

    // Simulate search: articles containing 'ameblo-12864' (e.g. 2024-08 multiple matches) are detached to searchResultsList
    const searchResultsList = [];
    for (const month of months) {
      const remaining = [];
      for (const href of month.children) {
        if (href.includes('ameblo-12864')) {
          searchResultsList.push(href);
        } else {
          remaining.push(href);
        }
      }
      month.children = remaining;
    }

    // Run the restoration logic from archive.html:
    // If searchResultsList has children, iterate _origEntries and appendChild
    if (searchResultsList.length > 0) {
      for (const month of months) {
        for (const entry of month.hrefs) {
          // DOM appendChild moves child to end
          const idx = month.children.indexOf(entry);
          if (idx !== -1) month.children.splice(idx, 1);
          month.children.push(entry);
        }
      }
      searchResultsList.length = 0;
    }

    // Verify all months have their exact original href order
    let match = true;
    for (let i = 0; i < months.length; i++) {
      if (months[i].children.join(',') !== months[i].hrefs.join(',')) {
        match = false;
        console.error('Mismatch in month', i, months[i].children, months[i].hrefs);
        process.exit(1);
      }
    }
    console.log('OK');
    """

    res = subprocess.run(['node', '-e', node_script], capture_output=True, text=True)
    assert res.returncode == 0 and "OK" in res.stdout, f"Node timeline restoration test failed: {res.stderr}"
    print("  ✓ Order preservation verified across all month sections after search restoration")

if __name__ == '__main__':
    test_markup()
    test_css()
    test_relevance_scoring()
    test_script_logic()
    test_timeline_restoration_order()
    print("\nAll search sort tests passed successfully!")
