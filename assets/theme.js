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

  var THEME_CYCLE = {
    'light': 'dark',
    'dark': 'auto',
    'auto': 'light'
  };

  var THEME_CONFIG = {
    'light': { icon: '☀️', text: 'Theme: Light / 表示：ライト' },
    'dark': { icon: '🌙', text: 'Theme: Dark / 表示：ダーク' },
    'auto': { icon: '💻', text: 'Theme: Auto / 表示：自動' }
  };

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
    var toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    var cfg = THEME_CONFIG[currentTheme] || THEME_CONFIG.auto;
    for (var i = 0; i < toggleBtns.length; i++) {
      var toggleBtn = toggleBtns[i];
      toggleBtn.setAttribute('data-theme-val', currentTheme);
      toggleBtn.setAttribute('aria-label', cfg.text);
      toggleBtn.title = cfg.text;
      var iconEl = toggleBtn.querySelector('.theme-toggle-icon');
      if (iconEl) {
        iconEl.textContent = cfg.icon;
      } else {
        toggleBtn.innerHTML = '<span class="theme-toggle-icon" aria-hidden="true">' + cfg.icon + '</span>';
      }
    }

    var buttons = document.querySelectorAll('.theme-btn');
    for (var j = 0; j < buttons.length; j++) {
      var btn = buttons[j];
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

  function cycleTheme() {
    var current = getStoredTheme();
    var next = THEME_CYCLE[current] || 'light';
    setStoredTheme(next);
    applyTheme(next);
  }

  function mountThemeSwitch() {
    var switchers = document.querySelectorAll('.theme-switch');
    var currentTheme = getStoredTheme();
    var cfg = THEME_CONFIG[currentTheme] || THEME_CONFIG.auto;

    if (!switchers.length) {
      var nav = document.querySelector('.site-nav');
      if (nav) {
        var sw = document.createElement('div');
        sw.className = 'theme-switch';
        nav.appendChild(sw);
        switchers = [sw];
      }
    }

    for (var i = 0; i < switchers.length; i++) {
      var switcher = switchers[i];
      switcher.setAttribute('role', 'region');
      switcher.setAttribute('aria-label', 'Theme / テーマ切替');
      switcher.innerHTML =
        '<button type="button" class="theme-toggle-btn" data-theme-val="' + currentTheme + '" aria-label="' + cfg.text + '" title="' + cfg.text + '">' +
          '<span class="theme-toggle-icon" aria-hidden="true">' + cfg.icon + '</span>' +
        '</button>';
    }

    applyTheme(currentTheme);
  }

  // Handle button clicks via delegation
  document.addEventListener('click', function(e) {
    var toggleBtn = e.target.closest ? e.target.closest('.theme-toggle-btn') : null;
    if (toggleBtn) {
      cycleTheme();
      return;
    }

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
