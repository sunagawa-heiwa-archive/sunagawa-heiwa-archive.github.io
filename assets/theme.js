(function() {
  'use strict';

  function getStoredTheme() {
    try {
      var t = localStorage.getItem('theme');
      return (t === 'light' || t === 'dark') ? t : 'auto';
    } catch (e) {
      return 'auto';
    }
  }

  function setStoredTheme(theme) {
    try {
      if (theme === 'light' || theme === 'dark') {
        localStorage.setItem('theme', theme);
      } else {
        localStorage.removeItem('theme');
      }
    } catch (e) {
      /* ignore */
    }
  }

  function updateThemeColorMeta(theme) {
    var metaThemeColors = document.querySelectorAll('meta[name="theme-color"]');
    if (!metaThemeColors.length) return;

    for (var i = 0; i < metaThemeColors.length; i++) {
      var meta = metaThemeColors[i];
      if (theme === 'auto') {
        var media = meta.getAttribute('media');
        if (media && media.indexOf('dark') !== -1) {
          meta.setAttribute('content', '#181b19');
        } else if (media && media.indexOf('light') !== -1) {
          meta.setAttribute('content', '#496f61');
        }
      } else {
        meta.setAttribute('content', theme === 'dark' ? '#181b19' : '#496f61');
      }
    }
  }

  function applyTheme(theme) {
    var root = document.documentElement;
    if (theme === 'light' || theme === 'dark') {
      root.setAttribute('data-theme', theme);
    } else {
      root.removeAttribute('data-theme');
    }

    updateThemeColorMeta(theme);
    updateSwitchUI(theme);
  }

  function updateSwitchUI(currentTheme) {
    var buttons = document.querySelectorAll('.theme-btn');
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      var val = btn.getAttribute('data-theme-val');
      var isCurrent = val === currentTheme;
      if (isCurrent) {
        btn.classList.add('active');
        btn.setAttribute('aria-pressed', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-pressed', 'false');
      }
    }
  }

  function mountThemeSwitch() {
    var nav = document.querySelector('.site-nav');
    if (!nav) return;

    var existing = nav.querySelector('.theme-switch');
    if (!existing) {
      var switcher = document.createElement('div');
      switcher.className = 'theme-switch';
      switcher.setAttribute('role', 'group');
      switcher.setAttribute('aria-label', 'Theme / テーマ切替');
      switcher.innerHTML =
        '<button type="button" class="theme-btn" data-theme-val="light" aria-pressed="false" title="Light / ライト"><span aria-hidden="true">☀️</span> <span>Light</span></button>' +
        '<button type="button" class="theme-btn" data-theme-val="dark" aria-pressed="false" title="Dark / ダーク"><span aria-hidden="true">🌙</span> <span>Dark</span></button>' +
        '<button type="button" class="theme-btn" data-theme-val="auto" aria-pressed="false" title="Auto / 自動"><span aria-hidden="true">💻</span> <span>Auto</span></button>';
      nav.appendChild(switcher);
    }

    applyTheme(getStoredTheme());
  }

  // Handle button clicks via delegation
  document.addEventListener('click', function(e) {
    var btn = e.target.closest ? e.target.closest('.theme-btn') : null;
    if (!btn) return;

    var val = btn.getAttribute('data-theme-val');
    if (!val) return;

    setStoredTheme(val);
    applyTheme(val);
  });

  // Listen for system theme changes when in 'auto' mode
  if (window.matchMedia) {
    var mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    var onSystemChange = function() {
      if (getStoredTheme() === 'auto') {
        applyTheme('auto');
      }
    };
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', onSystemChange);
    } else if (mediaQuery.addListener) {
      mediaQuery.addListener(onSystemChange);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountThemeSwitch);
  } else {
    mountThemeSwitch();
  }
})();
