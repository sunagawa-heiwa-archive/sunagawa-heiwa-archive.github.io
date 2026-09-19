#!/usr/bin/env python3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE = BASE_DIR / "index.html"

container_html = '''<section class="on-this-day" id="onThisDay" style="display:none;" aria-label="On This Day / 往年の今日">
<div class="on-this-day-header">
<span class="on-this-day-badge" id="otdBadge">往年の今日 / On This Day</span>
<span class="on-this-day-date" id="otdDate"></span>
</div>
<ul class="on-this-day-list" id="otdList"></ul>
</section>'''

js_logic = '''
    // On This Day (今日は何の日)
    (() => {
      const otdSec = document.getElementById('onThisDay');
      const otdList = document.getElementById('otdList');
      const otdDate = document.getElementById('otdDate');
      const otdBadge = document.getElementById('otdBadge');
      if (!otdSec || !otdList || !entries.length) return;

      const now = new Date();
      const pad = n => String(n).padStart(2, '0');
      const curMonth = now.getMonth() + 1;
      const curDay = now.getDate();
      const curMd = `${pad(curMonth)}-${pad(curDay)}`;

      const allItems = entries.map(el => {
        const timeEl = el.querySelector('time');
        const dt = timeEl ? timeEl.getAttribute('datetime') : '';
        const titleEl = el.querySelector('a');
        const typeEl = el.querySelector('.entry-type') || el.querySelector('.type-tag');
        return {
          el,
          dt,
          year: dt ? dt.slice(0, 4) : '',
          md: dt ? dt.slice(5, 10) : '',
          month: dt ? parseInt(dt.slice(5, 7), 10) : 0,
          day: dt ? parseInt(dt.slice(8, 10), 10) : 0,
          title: titleEl ? titleEl.textContent.trim() : '',
          href: titleEl ? titleEl.getAttribute('href') : '',
          type: typeEl ? typeEl.textContent.trim() : ''
        };
      }).filter(it => it.dt);

      // 1. Exact match
      let matches = allItems.filter(it => it.md === curMd);
      let isExact = true;

      // 2. Fallback: +-3 days
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
        otdBadge.textContent = '往年の今日 / On This Day';
        otdDate.textContent = `${curMonth}月${curDay}日`;
      } else {
        otdBadge.textContent = 'この時期の記録 / In This Season';
        otdDate.textContent = `${curMonth}月${curDay}日 前後`;
      }

      otdList.innerHTML = matches.map(m => `
        <li class="on-this-day-item">
          <span class="on-this-day-year">${m.year}年</span>
          <a href="${m.href}">${m.title}</a>
          ${m.type ? `<span class="on-this-day-tag">${m.type}</span>` : ''}
        </li>
      `).join('');

      otdSec.style.display = 'block';
    })();
'''

with open(INDEX_FILE, "r", encoding="utf-8") as f:
    text = f.read()

search_idx = text.find('<div class="search">')
if 'id="onThisDay"' not in text and search_idx != -1:
    text = text[:search_idx] + container_html + '\n' + text[search_idx:]

last_script_end = text.rfind('})();')
if 'On This Day (今日は何の日)' not in text and last_script_end != -1:
    text = text[:last_script_end] + js_logic + text[last_script_end:]

with open(INDEX_FILE, "w", encoding="utf-8") as f:
    f.write(text)

print("On This Day module injected into index.html successfully!")
