#!/usr/bin/env python3
"""
Add Search Highlight & Context Snippet to index.html and style.css
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.html"
CSS_FILE = BASE_DIR / "assets/style.css"

# 1. Update style.css
with open(CSS_FILE, "r", encoding="utf-8") as f:
    css = f.read()

highlight_css = '''
/* Search Highlight & Snippet */
mark.search-highlight {
  background-color: #ffe066;
  color: #202522;
  font-weight: 600;
  padding: 0 3px;
  border-radius: 2px;
}
.search-snippet {
  margin: 6px 0 2px;
  font-size: 0.86rem;
  color: var(--muted);
  line-height: 1.5;
  display: block;
}
'''

if 'mark.search-highlight' not in css:
    idx = css.find('@media print')
    if idx != -1:
        css = css[:idx] + highlight_css + '\n' + css[idx:]
    else:
        css += '\n' + highlight_css

    with open(CSS_FILE, "w", encoding="utf-8") as f:
        f.write(css)
    print("style.css updated with search-highlight styles.")

# 2. Update index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    html = f.read()

# Locate applyFilters in index.html
old_entries_loop = '''      entries.forEach((entry) => { entry.hidden = !hasLanguage(entry) || !hasType(entry) || !hasSearch(entry) || (year !== 'all' && entry.dataset.year !== year); });'''

new_entries_loop = '''      const escapeRegExp = (s) => s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
      const escapeHtml = (s) => s.replace(/[&<>'"]/g, t => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[t]||t));

      entries.forEach((entry) => {
        const isHidden = !hasLanguage(entry) || !hasType(entry) || !hasSearch(entry) || (year !== 'all' && entry.dataset.year !== year);
        entry.hidden = isHidden;

        const titleEl = entry.querySelector('.entry-title');
        if (!titleEl) return;
        if (!titleEl.dataset.origText) titleEl.dataset.origText = titleEl.textContent;

        const existingSnippet = entry.querySelector('.search-snippet');

        if (!isHidden && query) {
          const orig = titleEl.dataset.origText;
          const safeQ = escapeRegExp(query);
          const regex = new RegExp(`(${safeQ})`, 'gi');
          
          // 1. Highlight in title if present
          if (regex.test(orig)) {
            titleEl.innerHTML = escapeHtml(orig).replace(new RegExp(`(${escapeRegExp(escapeHtml(query))})`, 'gi'), '<mark class="search-highlight">$1</mark>');
            if (existingSnippet) existingSnippet.remove();
          } else {
            // Title didn't match directly, restore title text
            titleEl.textContent = orig;
            // 2. Extract snippet from entry.dataset.search if query in body
            const bodyText = entry.dataset.search || '';
            const matchIdx = bodyText.toLowerCase().indexOf(query);
            if (matchIdx !== -1) {
              const start = Math.max(0, matchIdx - 35);
              const end = Math.min(bodyText.length, matchIdx + query.length + 35);
              let snippet = (start > 0 ? '…' : '') + bodyText.slice(start, end).trim() + (end < bodyText.length ? '…' : '');
              const safeSnippet = escapeHtml(snippet).replace(new RegExp(`(${escapeRegExp(escapeHtml(query))})`, 'gi'), '<mark class="search-highlight">$1</mark>');
              
              if (existingSnippet) {
                existingSnippet.innerHTML = safeSnippet;
              } else {
                const snipEl = document.createElement('span');
                snipEl.className = 'search-snippet';
                snipEl.innerHTML = safeSnippet;
                entry.appendChild(snipEl);
              }
            } else if (existingSnippet) {
              existingSnippet.remove();
            }
          }
        } else {
          // Restore plain title and remove snippets when query cleared or entry hidden
          titleEl.textContent = titleEl.dataset.origText;
          if (existingSnippet) existingSnippet.remove();
        }
      });'''

if old_entries_loop in html:
    html = html.replace(old_entries_loop, new_entries_loop)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("index.html updated with search highlight and snippet successfully!")
else:
    print("Old entries loop not found, checking if already modified.")
