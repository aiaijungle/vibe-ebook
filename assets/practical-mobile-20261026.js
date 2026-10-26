/* Volume 5 reading UI. No payment, unlock, analytics, or external requests. */
(function () {
  'use strict';
  function init() {
    var root = document.documentElement;
    var sidebar = document.getElementById('sidebar');
    var toggle = document.querySelector('.menu-toggle');
    var header = document.querySelector('.top-bar');
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
