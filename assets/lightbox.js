(() => {
  const isImageHref = (href) => {
    if (!href) return false;
    const cleanPath = href.split(/[?#]/)[0];
    return /\.(jpe?g|png|gif|webp|svg)$/i.test(cleanPath);
  };

  // Select images, excluding OGP card icons and images wrapped in non-image navigation links
  const rawImages = [...document.querySelectorAll('.body img, .prose img')];
  const images = rawImages.filter((img) => {
    if (img.classList.contains('ogpCard_icon') || img.closest('.ogpCard_iconWrap')) {
      return false;
    }
    const link = img.closest('a');
    if (link && !isImageHref(link.getAttribute('href') || '')) {
      return false;
    }
    return true;
  });

  if (!images.length) return;

  // Build lightbox modal DOM
  const overlay = document.createElement('div');
  overlay.className = 'lightbox-dialog';
  overlay.setAttribute('role', 'dialog');
  overlay.setAttribute('aria-modal', 'true');
  overlay.setAttribute('aria-label', 'Image viewer / 画像ビューアー');
  overlay.hidden = true;

  overlay.innerHTML = `
    <div class="lightbox-backdrop"></div>
    <div class="lightbox-controls">
      <div class="lightbox-counter" aria-live="polite"></div>
      <button type="button" class="lightbox-btn lightbox-close" aria-label="Close / 閉じる">✕ Close / 閉じる</button>
    </div>
    <button type="button" class="lightbox-btn lightbox-prev" aria-label="Previous image / 前の画像">‹</button>
    <button type="button" class="lightbox-btn lightbox-next" aria-label="Next image / 次の画像">›</button>
    <div class="lightbox-content">
      <img class="lightbox-image" src="" alt="" />
      <div class="lightbox-caption"></div>
    </div>
  `;

  document.body.appendChild(overlay);

  const backdrop = overlay.querySelector('.lightbox-backdrop');
  const imgEl = overlay.querySelector('.lightbox-image');
  const captionEl = overlay.querySelector('.lightbox-caption');
  const counterEl = overlay.querySelector('.lightbox-counter');
  const closeBtn = overlay.querySelector('.lightbox-close');
  const prevBtn = overlay.querySelector('.lightbox-prev');
  const nextBtn = overlay.querySelector('.lightbox-next');

  let currentIndex = 0;
  let closeTimer = null;

  const items = images.map((img) => {
    const link = img.closest('a');
    const fullSrc = (link && isImageHref(link.getAttribute('href') || ''))
      ? (link.href || link.getAttribute('href'))
      : (img.currentSrc || img.src || img.getAttribute('src'));
    const alt = img.getAttribute('alt') || '';
    return { fullSrc, alt, trigger: img, link: link || null };
  });

  const getFocusable = () => [closeBtn, prevBtn, nextBtn].filter((btn) => !btn.hidden);

  const show = (index) => {
    if (index < 0) index = items.length - 1;
    if (index >= items.length) index = 0;
    currentIndex = index;

    const item = items[currentIndex];
    imgEl.src = item.fullSrc;
    imgEl.alt = item.alt;

    // Display clean caption if alt text exists
    captionEl.textContent = item.alt;
    captionEl.hidden = !item.alt.trim();

    if (items.length > 1) {
      counterEl.textContent = `${currentIndex + 1} / ${items.length}`;
      counterEl.hidden = false;
      prevBtn.hidden = false;
      nextBtn.hidden = false;
    } else {
      counterEl.textContent = '';
      counterEl.hidden = true;
      prevBtn.hidden = true;
      nextBtn.hidden = true;
    }
  };

  const open = (index) => {
    if (closeTimer) {
      clearTimeout(closeTimer);
      closeTimer = null;
    }
    show(index);
    overlay.hidden = false;
    void overlay.offsetWidth; // Force layout reflow
    overlay.classList.add('is-open');
    document.body.classList.add('lightbox-active');
    closeBtn.focus();
    document.addEventListener('keydown', onKeyDown);
  };

  const close = () => {
    overlay.classList.remove('is-open');
    document.body.classList.remove('lightbox-active');
    document.removeEventListener('keydown', onKeyDown);

    closeTimer = setTimeout(() => {
      overlay.hidden = true;
      imgEl.src = '';
      const currentItem = items[currentIndex];
      const returnTarget = currentItem ? (currentItem.link || currentItem.trigger) : null;
      if (returnTarget) {
        returnTarget.focus();
      }
    }, 180);
  };

  const onKeyDown = (e) => {
    if (e.key === 'Escape') {
      e.preventDefault();
      close();
    } else if (e.key === 'ArrowLeft') {
      if (items.length > 1) {
        e.preventDefault();
        show(currentIndex - 1);
      }
    } else if (e.key === 'ArrowRight') {
      if (items.length > 1) {
        e.preventDefault();
        show(currentIndex + 1);
      }
    } else if (e.key === 'Tab') {
      const focusable = getFocusable();
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      }
    }
  };

  closeBtn.addEventListener('click', close);
  backdrop.addEventListener('click', close);
  imgEl.addEventListener('click', close);
  prevBtn.addEventListener('click', () => show(currentIndex - 1));
  nextBtn.addEventListener('click', () => show(currentIndex + 1));

  // Connect images and links
  items.forEach((item, idx) => {
    const { link, trigger } = item;
    if (link) {
      link.classList.add('lightbox-trigger');
      link.setAttribute('aria-haspopup', 'dialog');
      link.addEventListener('click', (e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        open(idx);
      });
      link.addEventListener('keydown', (e) => {
        if (e.key === ' ') {
          e.preventDefault();
          open(idx);
        }
      });
    } else {
      trigger.classList.add('lightbox-trigger');
      trigger.setAttribute('tabindex', '0');
      trigger.setAttribute('role', 'button');
      trigger.setAttribute('aria-haspopup', 'dialog');
      trigger.setAttribute('aria-label', `View image: ${item.alt || 'Archival image'}`);
      trigger.addEventListener('click', () => open(idx));
      trigger.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          open(idx);
        }
      });
    }
  });
})();
