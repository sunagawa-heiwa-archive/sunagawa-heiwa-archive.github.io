// Citation / 引用 copy buttons for archived article pages.
// Reads data-copy-url / data-copy-cite on .cite-btn elements; works over https (secure context)
// with a textarea fallback for other environments.
(() => {
  const copyText = (text) => {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text).then(() => true, () => false);
    }
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.position = 'fixed';
    ta.style.top = '0';
    ta.style.left = '0';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    return Promise.resolve(ok);
  };

  document.querySelectorAll('.cite-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const text = btn.dataset.copyCite || btn.dataset.copyUrl || '';
      if (!text) return;
      copyText(text).then((ok) => {
        const old = btn.textContent;
        btn.textContent = ok ? (btn.dataset.copiedLabel || 'Copied / コピーしました') : (btn.dataset.failedLabel || 'Copy failed / コピー失敗');
        btn.classList.add('copied', ok ? 'is-ok' : 'is-error');
        setTimeout(() => {
          btn.textContent = old;
          btn.classList.remove('copied', 'is-ok', 'is-error');
        }, 1800);
      });
    });
  });
})();
