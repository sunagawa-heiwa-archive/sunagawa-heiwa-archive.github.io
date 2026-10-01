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
    var nav = document.querySelector('.site-nav');
    if (!nav) return;

    var switcher = nav.querySelector('.theme-switch');
    if (!switcher) {
      switcher = document.createElement('div');
      switcher.className = 'theme-switch';
      nav.appendChild(switcher);
    }

    // Drop wrapper role and aria-label so it doesn't create landmark clutter;
    // the button itself carries the accessible label.
    switcher.removeAttribute('role');
    switcher.removeAttribute('aria-label');

    var currentTheme = getStoredTheme();
    var cfg = THEME_CONFIG[currentTheme] || THEME_CONFIG.auto;
    switcher.innerHTML =
      '<button type="button" class="theme-toggle-btn" data-theme-val="' + currentTheme + '" aria-label="' + cfg.text + '" title="' + cfg.text + '">' +
        '<span class="theme-toggle-icon" aria-hidden="true">' + cfg.icon + '</span>' +
      '</button>';

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

  function mountMobileNav() {
    var siteNav = document.querySelector('.site-nav');
    var topicsNav = document.querySelector('.topics-nav');
    if (!siteNav || !topicsNav) return;

    if (siteNav.querySelector('.menu-toggle-btn')) return;

    document.documentElement.classList.add('has-mobile-nav');

    var menuBtn = document.createElement('button');
    menuBtn.type = 'button';
    menuBtn.className = 'menu-toggle-btn';
    menuBtn.setAttribute('aria-expanded', 'false');
    menuBtn.setAttribute('aria-controls', 'mobile-nav-panel');
    menuBtn.setAttribute('aria-label', 'メニュー / Menu');
    menuBtn.innerHTML =
      '<span class="menu-toggle-icon" aria-hidden="true">☰</span>' +
      '<span class="menu-toggle-label">メニュー / Menu</span>';

    var themeSwitch = siteNav.querySelector('.theme-switch');
    if (themeSwitch) {
      siteNav.insertBefore(menuBtn, themeSwitch);
    } else {
      siteNav.appendChild(menuBtn);
    }

    var panel = document.createElement('div');
    panel.id = 'mobile-nav-panel';
    panel.className = 'mobile-nav-panel';
    panel.setAttribute('hidden', '');

    var backdrop = document.createElement('div');
    backdrop.className = 'mobile-nav-backdrop';
    backdrop.setAttribute('tabindex', '-1');

    var dialog = document.createElement('div');
    dialog.className = 'mobile-nav-dialog';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-label', 'メニュー / Menu');

    var pHeader = document.createElement('div');
    pHeader.className = 'mobile-nav-header';
    pHeader.innerHTML =
      '<span class="mobile-nav-title">メニュー / Menu</span>' +
      '<button type="button" class="mobile-nav-close-btn" aria-label="閉じる / Close menu">✕</button>';

    var siteSec = document.createElement('nav');
    siteSec.className = 'mobile-nav-section';
    siteSec.setAttribute('aria-label', 'サイト / Site');
    var siteTitle = document.createElement('div');
    siteTitle.className = 'mobile-nav-section-title';
    siteTitle.textContent = 'Site / サイト';
    var siteLinksWrap = document.createElement('div');
    siteLinksWrap.className = 'mobile-nav-links';

    var siteLinks = siteNav.querySelectorAll('a');
    for (var i = 0; i < siteLinks.length; i++) {
      var sLink = siteLinks[i];
      var sClone = sLink.cloneNode(true);
      sClone.className = 'mobile-nav-link';
      siteLinksWrap.appendChild(sClone);
    }
    siteSec.appendChild(siteTitle);
    siteSec.appendChild(siteLinksWrap);

    var topicsSec = document.createElement('nav');
    topicsSec.className = 'mobile-nav-section';
    topicsSec.setAttribute('aria-label', 'テーマ / Topics');
    var topicsTitle = document.createElement('div');
    topicsTitle.className = 'mobile-nav-section-title';
    topicsTitle.textContent = 'Topics / テーマ';
    var topicsLinksWrap = document.createElement('div');
    topicsLinksWrap.className = 'mobile-nav-links';

    var topicsLinks = topicsNav.querySelectorAll('a');
    for (var j = 0; j < topicsLinks.length; j++) {
      var tLink = topicsLinks[j];
      var tClone = tLink.cloneNode(true);
      tClone.className = 'mobile-nav-link';
      topicsLinksWrap.appendChild(tClone);
    }
    topicsSec.appendChild(topicsTitle);
    topicsSec.appendChild(topicsLinksWrap);

    dialog.appendChild(pHeader);
    dialog.appendChild(siteSec);
    dialog.appendChild(topicsSec);

    panel.appendChild(backdrop);
    panel.appendChild(dialog);
    document.body.appendChild(panel);

    var closeBtn = pHeader.querySelector('.mobile-nav-close-btn');

    function openMenu() {
      panel.removeAttribute('hidden');
      menuBtn.setAttribute('aria-expanded', 'true');
      document.body.classList.add('mobile-nav-open');
      closeBtn.focus();
    }

    function closeMenu(restoreFocus) {
      if (panel.hasAttribute('hidden')) return;
      panel.setAttribute('hidden', '');
      menuBtn.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('mobile-nav-open');
      if (restoreFocus) {
        menuBtn.focus();
      }
    }

    function toggleMenu() {
      if (panel.hasAttribute('hidden')) {
        openMenu();
      } else {
        closeMenu(true);
      }
    }

    menuBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      toggleMenu();
    });

    closeBtn.addEventListener('click', function(e) {
      closeMenu(true);
    });

    backdrop.addEventListener('click', function(e) {
      closeMenu(true);
    });

    panel.addEventListener('click', function(e) {
      if (!dialog.contains(e.target)) {
        closeMenu(true);
      }
    });

    dialog.addEventListener('click', function(e) {
      var link = e.target.closest ? e.target.closest('.mobile-nav-link') : null;
      if (link) {
        closeMenu(false);
      }
    });

    document.addEventListener('keydown', function(e) {
      if (panel.hasAttribute('hidden')) return;

      if (e.key === 'Escape' || e.keyCode === 27) {
        e.preventDefault();
        closeMenu(true);
        return;
      }

      if (e.key === 'Tab' || e.keyCode === 9) {
        var focusable = dialog.querySelectorAll('button, a[href]');
        if (!focusable.length) return;
        var first = focusable[0];
        var last = focusable[focusable.length - 1];

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
    });

    var lastWidth = window.innerWidth;
    window.addEventListener('resize', function() {
      var currentWidth = window.innerWidth;
      if (currentWidth === lastWidth) return;
      lastWidth = currentWidth;
      if (currentWidth >= 768) {
        closeMenu(false);
      }
    });
  }

  function initNavAndTheme() {
    mountThemeSwitch();
    mountMobileNav();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavAndTheme);
  } else {
    initNavAndTheme();
  }
})();
