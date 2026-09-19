#!/usr/bin/env python3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.html"
CSS_FILE = BASE_DIR / "assets/style.css"

# 1. Update CSS
with open(CSS_FILE, "r", encoding="utf-8") as f:
    css = f.read()

# Replace or insert better on-this-day styles
new_otd_css = '''/* On This Day (今日は何の日) */
.on-this-day { margin: 24px 0 20px; padding: 18px 22px; background: white; border: 1px solid var(--line); border-left: 4px solid var(--accent); border-radius: 12px; }
.on-this-day-header { display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 6px; }
.on-this-day-badge { display: inline-flex; align-items: center; gap: 6px; background: var(--accent); color: white; font-size: 0.8rem; font-weight: 700; padding: 3px 10px; border-radius: 999px; letter-spacing: 0.02em; }
.on-this-day-date { font-size: 0.92rem; font-weight: 650; color: var(--muted); }
.on-this-day-desc { margin: 4px 0 12px; font-size: 0.85rem; color: var(--muted); line-height: 1.5; }
.on-this-day-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.on-this-day-item { display: flex; align-items: baseline; flex-wrap: wrap; gap: 8px 12px; padding: 6px 0; border-top: 1px dashed var(--line); }
.on-this-day-item:first-child { border-top: none; }
.on-this-day-year { background: var(--paper); color: var(--accent); border: 1px solid var(--line); border-radius: 4px; padding: 1px 7px; font-weight: 700; font-size: 0.82rem; flex-shrink: 0; }
.on-this-day-title { color: var(--ink); text-decoration: none; font-weight: 550; font-size: 0.95rem; line-height: 1.4; flex-grow: 1; }
.on-this-day-title:hover { color: var(--accent); text-decoration: underline; }
.on-this-day-tag { font-size: 0.78rem; color: var(--muted); border: 1px solid var(--line); border-radius: 999px; padding: 1px 7px; flex-shrink: 0; }
'''

if '/* On This Day (今日は何の日) */' in css:
    css = re.sub(r'/\* On This Day \(今日は何の日\) \*/.*?\.on-this-day-tag\s*\{[^}]+\}\n?', new_otd_css, css, flags=re.DOTALL)
else:
    css += '\n' + new_otd_css

with open(CSS_FILE, "w", encoding="utf-8") as f:
    f.write(css)

# 2. Update index.html
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# Replace container
old_container_pattern = r'<section class="on-this-day".*?</section>'
new_container = '''<section class="on-this-day" id="onThisDay" style="display:none;" aria-label="On This Day / 往年の今日・同時期の記録">
<div class="on-this-day-header">
<span class="on-this-day-badge" id="otdBadge">🗓️ 往年の今日 / On This Day</span>
<span class="on-this-day-date" id="otdDate"></span>
</div>
<p class="on-this-day-desc" id="otdDesc">過去のこの時期に公開された記事です。当時の集会や活動の記録を振り返ります。</p>
<ul class="on-this-day-list" id="otdList"></ul>
</section>'''

if re.search(old_container_pattern, text, flags=re.DOTALL):
    text = re.sub(old_container_pattern, new_container, text, flags=re.DOTALL)
else:
    search_idx = text.find('<div class="search">')
    if search_idx != -1:
        text = text[:search_idx] + new_container + '\n' + text[search_idx:]

# Replace JS logic
old_js_pattern = r'// On This Day \(今日は何の日\).*?otdSec\.style\.display = \'block\';\s*\}\)\(\);'

new_js = '''// On This Day (今日は何の日)
    (() => {
      const otdSec = document.getElementById('onThisDay');
      const otdList = document.getElementById('otdList');
      const otdDate = document.getElementById('otdDate');
      const otdBadge = document.getElementById('otdBadge');
      const otdDesc = document.getElementById('otdDesc');
      if (!otdSec || !otdList || !entries.length) return;

      const now = new Date();
      const pad = n => String(n).padStart(2, '0');
      const curMonth = now.getMonth() + 1;
      const curDay = now.getDate();
      const curMd = `${pad(curMonth)}-${pad(curDay)}`;

      const allItems = entries.map(el => {
        const timeEl = el.querySelector('time');
        const dt = timeEl ? timeEl.getAttribute('datetime') : '';
        const titleEl = el.querySelector('.entry-title');
        const typeEl = el.querySelector('.entry-type');
        return {
          el,
          dt,
          year: dt ? dt.slice(0, 4) : '',
          md: dt ? dt.slice(5, 10) : '',
          month: dt ? parseInt(dt.slice(5, 7), 10) : 0,
          day: dt ? parseInt(dt.slice(8, 10), 10) : 0,
          title: titleEl ? titleEl.textContent.trim() : el.textContent.trim(),
          href: el.getAttribute('href') || '',
          type: typeEl ? typeEl.textContent.trim() : ''
        };
      }).filter(it => it.dt && it.title);

      let matches = allItems.filter(it => it.md === curMd);
      let isExact = true;

      if (!matches.length) {
        matches = allItems.filter(it => it.month === curMonth && Math.abs(it.day - curDay) <= 3);
        isExact = false;
      }

      if (!matches.length) {
        otdSec.style.display = 'none';
        return;
      }

      matches.sort((a, b) => b.year.localeCompare(a.year));

      if (isExact) {
        otdBadge.textContent = '🗓️ 往年の今日 / On This Day';
        otdDate.textContent = `${curMonth}月${curDay}日`;
        otdDesc.textContent = `過去の${curMonth}月${curDay}日に公開された記事です。当時の集会や活動の記録を振り返ります。`;
      } else {
        otdBadge.textContent = '🗓️ この時期の記録 / In This Season';
        otdDate.textContent = `${curMonth}月中旬（${curMonth}月${Math.max(1, curDay-3)}日〜${curDay+3}日頃）`;
        otdDesc.textContent = `過去の${curMonth}月中旬に公開された記事です。当時の集会や活動の記録を振り返ります。`;
      }

      otdList.innerHTML = matches.map(m => `
        <li class="on-this-day-item">
          <span class="on-this-day-year">${m.year}年</span>
          <a class="on-this-day-title" href="${m.href}">${m.title}</a>
          ${m.type ? `<span class="on-this-day-tag">${m.type}</span>` : ''}
        </li>
      `).join('');

      otdSec.style.display = 'block';
    })();'''

if re.search(old_js_pattern, text, flags=re.DOTALL):
    text = re.sub(old_js_pattern, new_js, text, flags=re.DOTALL)
else:
    last_script_end = text.rfind('})();')
    if last_script_end != -1:
        text = text[:last_script_end] + '\n' + new_js + '\n' + text[last_script_end:]

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed on-this-day UI and extraction logic successfully!")
