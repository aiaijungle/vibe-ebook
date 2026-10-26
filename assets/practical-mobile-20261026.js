/* Volume 5 reading UI. No payment, unlock, analytics, or external requests. */
(function () {
  'use strict';
  function init() {
    var root = document.documentElement;
    if (root.dataset.volume5MobileReady || !document.querySelector('.cover-hero')) return;
    var header = document.querySelector('.top-bar');
    if (!header) return;
    root.dataset.volume5MobileReady = 'true';
    // Adapt existing visible controls without touching the original book HTML.
    if (!header.querySelector('.top-bar-identity')) {
      var identity = document.createElement('div');
      identity.className = 'top-bar-identity';
      var controls = document.createElement('div');
      controls.className = 'top-bar-actions';
      ['.menu-toggle', '.top-bar-title', '.top-bar-chapter'].forEach(function (selector) {
        var node = header.querySelector(selector);
        if (node) identity.appendChild(node);
      });
      Array.from(header.children).forEach(function (node) { controls.appendChild(node); });
      header.appendChild(identity);
      header.appendChild(controls);
    }
    var progress = document.getElementById('top-progress');
    var promo = progress && progress.previousElementSibling;
    if (promo && !promo.classList.contains('book-promo')) {
      var price = promo.querySelector('strong');
      var purchase = promo.querySelector('a');
      var master = promo.textContent.match(/5권 마스터 [\d,]+원/);
      if (price && purchase && master) {
        var prices = document.createElement('span');
        prices.className = 'book-promo-prices';
        price.textContent = '🚀 ' + price.textContent.trim();
        prices.appendChild(price);
        var masterPrice = document.createElement('span');
        masterPrice.textContent = master[0];
        prices.appendChild(masterPrice);
        promo.replaceChildren(prices, purchase);
        promo.classList.add('book-promo');
      }
    }
    var series = header.nextElementSibling;
    if (series && series.querySelector('a[href*="book1.html"]')) {
      series.classList.add('series-nav');
      series.setAttribute('role', 'navigation');
      series.setAttribute('aria-label', 'AI바이블 시리즈');
      var seriesSpans = Array.from(series.children).filter(function (node) { return node.tagName === 'SPAN'; });
      if (seriesSpans[0]) seriesSpans[0].classList.add('series-label');
      if (seriesSpans[1]) {
        seriesSpans[1].classList.add('series-current');
        seriesSpans[1].setAttribute('aria-current', 'page');
      }
    }
    var sidebar = document.getElementById('sidebar');
    var toggle = document.querySelector('.menu-toggle');
    if (toggle) {
      toggle.setAttribute('aria-controls', 'sidebar');
      // The original outside-click listener otherwise mistakes the icon for an outside click.
      toggle.addEventListener('click', function (event) { event.stopPropagation(); });
    }
    var actions = document.querySelector('.top-bar-actions');
    var updates = document.getElementById('un-btn');
    var mobile = window.matchMedia('(max-width: 768px)');
    var originalParent = updates && updates.parentNode;
    var originalNext = updates && updates.nextSibling;
    var backdrop = document.createElement('button');
    backdrop.className = 'mobile-toc-backdrop';
    backdrop.type = 'button';
    backdrop.tabIndex = -1;
    backdrop.setAttribute('aria-label', '목차 닫기');
    document.body.appendChild(backdrop);
    var close = document.createElement('button');
    close.className = 'mobile-toc-close';
    close.type = 'button';
    close.textContent = '×';
    close.setAttribute('aria-label', '목차 닫기');
    if (sidebar) sidebar.querySelector('.sidebar-logo').appendChild(close);

    function closeToc(restoreFocus) {
      if (sidebar) sidebar.classList.remove('mobile-open');
      if (restoreFocus && toggle) toggle.focus();
    }
    function syncToc() {
      var open = mobile.matches && sidebar && sidebar.classList.contains('mobile-open');
      backdrop.classList.toggle('is-open', !!open);
      if (sidebar) sidebar.inert = mobile.matches && !open;
      if (toggle) {
        toggle.setAttribute('aria-expanded', String(!!open));
        toggle.setAttribute('aria-label', open ? '목차 닫기' : '목차 열기');
      }
    }
    close.addEventListener('click', function () { closeToc(true); });
    backdrop.addEventListener('click', function () { closeToc(true); });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && sidebar && sidebar.classList.contains('mobile-open')) closeToc(true);
    });
    if (sidebar) {
      new MutationObserver(syncToc).observe(sidebar, {attributes: true, attributeFilter: ['class']});
      sidebar.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function () { closeToc(false); });
      });
    }
    function syncLayout() {
      if (updates && actions) {
        if (mobile.matches && updates.parentNode !== actions) actions.insertBefore(updates, actions.firstChild);
        if (!mobile.matches && updates.parentNode === actions) originalParent.insertBefore(updates, originalNext);
      }
      var bar = document.getElementById('janda-bottom-bar');
      var noticeLink = bar && bar.querySelector('a');
      if (noticeLink && noticeLink.textContent === '이어서 읽기 →') {
        noticeLink.textContent = '구매 안내 →';
        noticeLink.setAttribute('rel', 'noopener');
      }
      var height = bar && getComputedStyle(bar).display !== 'none' ? bar.getBoundingClientRect().height : 0;
      root.style.setProperty('--book-purchase-height', height + 'px');
      if (header) root.style.setProperty('--book-header-height', header.getBoundingClientRect().height + 'px');
      if (bar && bar.querySelector('button')) bar.querySelector('button').setAttribute('aria-label', '구매 안내 닫기');
      syncToc();
    }
    mobile.addEventListener('change', function () { closeToc(false); syncLayout(); });
    window.addEventListener('resize', syncLayout);
    new MutationObserver(syncLayout).observe(document.body, {childList: true});
    if (window.ResizeObserver) {
      var observer = new ResizeObserver(syncLayout);
      if (header) observer.observe(header);
      var bar = document.getElementById('janda-bottom-bar');
      if (bar) observer.observe(bar);
    }
    syncLayout();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
