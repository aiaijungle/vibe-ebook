/* No requests, external actions, credentials, or customer data in this supplement. */
(function () {
  'use strict';
  function init() {
    document.querySelectorAll('[data-aib-copy]').forEach(function (button) {
      button.addEventListener('click', async function () {
        var code = document.getElementById(button.getAttribute('data-aib-copy'));
        if (!code) return;
        var status = button.parentElement.querySelector('[role="status"]');
        try {
          if (!navigator.clipboard) throw new Error('clipboard unavailable');
          await navigator.clipboard.writeText(code.textContent);
          if (status) status.textContent = '템플릿을 복사했습니다.';
        } catch (_) {
          if (status) status.textContent = '복사가 제한된 환경입니다. 옆의 텍스트 저장 버튼을 이용하세요.';
        }
      });
    });
    document.querySelectorAll('[data-aib-download]').forEach(function (button) {
      button.addEventListener('click', function () {
        var code = document.getElementById(button.getAttribute('data-aib-download'));
        if (!code) return;
        var url = URL.createObjectURL(new Blob([code.textContent], { type: 'text/plain;charset=utf-8' }));
        var a = document.createElement('a');
        a.href = url; a.download = 'AI_Bible_' + code.id + '.txt';
        document.body.appendChild(a); a.click(); a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      });
    });
    document.querySelectorAll('[data-aib-check]').forEach(function (input) {
      var key = 'aib-20261025:' + location.pathname + ':' + input.getAttribute('data-aib-check');
      try { input.checked = localStorage.getItem(key) === '1'; } catch (_) {}
      input.addEventListener('change', function () {
        try { localStorage.setItem(key, input.checked ? '1' : '0'); } catch (_) {}
      });
    });
    document.querySelectorAll('#sidebar a[href="#aib-update-20261025"]').forEach(function (link) {
      link.addEventListener('click', function () {
        if (typeof window.closeMobileToc === 'function') window.closeMobileToc();
        if (typeof window.closeToc === 'function') window.closeToc();
        var sidebar = document.getElementById('sidebar');
        if (sidebar) sidebar.classList.remove('mobile-open');
      });
    });
    var labs = {
      normal: {title:'검토 준비 완료',facts:'고객 C-001 · 스튜디오 S-01 · 잔여 2회 · 겹치는 예약 없음',status:'ready_for_review',reason:'입력과 사실 확인을 통과했습니다. 아직 예약하지 않았습니다. 담당자가 내용과 최신 상태를 확인한 뒤 실행을 승인해야 합니다.'},
      overlap: {title:'예약 제안 차단',facts:'같은 자원 S-01에 14:30~15:30 확정 예약이 있습니다.',status:'blocked',reason:'요청한 14:00~15:00과 시간이 겹칩니다. 이름이 다른 상품도 같은 자원 ID라면 함께 확인합니다. 가능한 다른 시간을 조회해 제안하세요.'},
      unknown: {title:'추가 정보 필요',facts:'회차권 잔여 횟수가 원본에서 확인되지 않았습니다.',status:'needs_information',reason:'모르는 값을 0회 또는 2회로 만들지 않습니다. 회차권 관리 원본을 조회하고 확인 시각을 기록한 뒤 다시 검토합니다.'},
      stale: {title:'최신 정보 다시 조회',facts:'샘플 기준 시각 10:05 · 정보 유효 시각 09:55',status:'needs_information',reason:'이 실습에서 정한 유효 시각을 지났습니다. 온톨로지가 정리되어 있어도 정보가 저절로 갱신되지는 않습니다. 원본의 예약 현황과 회차권을 다시 읽어야 합니다.'},
      empty: {title:'예약 제안 차단',facts:'원본에 확인된 잔여 횟수가 0회입니다.',status:'blocked',reason:'정보 누락과 잔여 0회는 다릅니다. 추가 결제를 자동으로 시키지 말고, 이용 가능한 상품이나 담당자 확인을 안내합니다.'}
    };
    document.querySelectorAll('[data-aib-lab]').forEach(function (lab) {
      function render(key) {
        var item = labs[key]; if (!item) return;
        lab.querySelector('[data-lab-title]').textContent = item.title;
        lab.querySelector('[data-lab-facts]').textContent = item.facts;
        lab.querySelector('[data-lab-status]').textContent = item.status;
        lab.querySelector('[data-lab-reason]').textContent = item.reason;
        lab.querySelectorAll('[data-lab-case]').forEach(function (b) {
          b.setAttribute('aria-pressed', String(b.getAttribute('data-lab-case') === key));
        });
      }
      lab.querySelectorAll('[data-lab-case]').forEach(function (button) {
        button.addEventListener('click', function () { render(button.getAttribute('data-lab-case')); });
      });
      render('normal');
    });
    var overlay = document.getElementById('un-ov');
    var panel = document.getElementById('un-panel');
    var opener = document.getElementById('un-btn');
    var closer = document.getElementById('un-close');
    if (opener) {
      opener.classList.add('aib-ready');
      function positionUpdateButton() {
        var bar = document.getElementById('janda-bottom-bar');
        var height = bar && getComputedStyle(bar).display !== 'none' ? bar.getBoundingClientRect().height + 8 : 0;
        opener.style.setProperty('--aib-bottom-offset', height + 'px');
      }
      positionUpdateButton();
      window.addEventListener('resize', positionUpdateButton);
      new MutationObserver(positionUpdateButton).observe(document.body, {childList:true});
      var bar = document.getElementById('janda-bottom-bar');
      if (bar && window.ResizeObserver) new ResizeObserver(positionUpdateButton).observe(bar);
    }
    if (overlay && panel && opener && closer) {
      var heading = panel.querySelector('h2');
      if (heading) { heading.id = heading.id || 'aib-update-dialog-title'; panel.setAttribute('aria-labelledby', heading.id); }
      panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true');
      opener.setAttribute('aria-haspopup', 'dialog'); opener.setAttribute('aria-controls', 'un-ov');
      var oldOverflow = ''; var wasOpen = false;
      function sync() {
        var open = overlay.classList.contains('open');
        overlay.setAttribute('aria-hidden', String(!open)); opener.setAttribute('aria-expanded', String(open));
        if (open && !wasOpen) { oldOverflow = document.body.style.overflow; document.body.style.overflow = 'hidden'; closer.focus(); }
        if (!open && wasOpen) { document.body.style.overflow = oldOverflow; opener.focus(); }
        wasOpen = open;
      }
      new MutationObserver(sync).observe(overlay, {attributes:true, attributeFilter:['class']}); sync();
      panel.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') { overlay.classList.remove('open'); return; }
        if (event.key !== 'Tab') return;
        var items = Array.prototype.filter.call(panel.querySelectorAll('a[href],button,input,select,textarea,[tabindex="0"]'), function (n) { return !n.disabled && n.getClientRects().length; });
        if (!items.length) return;
        var first = items[0], last = items[items.length-1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      });
      panel.querySelectorAll('[data-aib-read-update]').forEach(function (a) {
        a.addEventListener('click', function () { overlay.classList.remove('open'); });
      });
    }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

/* Load the approved volume 5 UI assets on that page only. */
(function () {
  if (!/(^|\/)practical-bible\.html$/.test(location.pathname)) return;
  if (document.getElementById('volume5-mobile-assets')) return;
  var style = document.createElement('link');
  style.id = 'volume5-mobile-assets';
  style.rel = 'stylesheet';
  style.href = 'assets/practical-mobile-20261026.css';
  document.head.appendChild(style);
  var script = document.createElement('script');
  script.src = 'assets/practical-mobile-20261026.js';
  document.body.appendChild(script);
})();
