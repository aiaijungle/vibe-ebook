/* AI 바이블 모바일 UX 보정 (2026-11-04): 학습 안내 카드를 책 제목 뒤로, 제목 아래 읽기/구매 버튼, 지난 출간 띠 숨김, 겹치는 업데이트 버튼 올리기, 끝에 무료 6권 안내. */
(function () {
  'use strict';
  var vol = document.body && document.body.getAttribute('data-aib-volume') || '';
  function run() {
    var h1 = document.querySelector('h1');
    var route = document.getElementById('aib-learning-route');
    // 1) 첫 화면에 책 제목이 먼저 보이게: 학습 안내 카드를 제목 블록 뒤로
    if (h1 && route && (route.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_FOLLOWING)) {
      var next = h1.nextElementSibling;
      var anchor = next && next.classList.contains('aib-update-notice') ? next : h1;
      anchor.insertAdjacentElement('afterend', route);
      var first = document.getElementById('may-countdown');
      if (first && (first.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_FOLLOWING)) anchor.insertAdjacentElement('afterend', first);
      var cta = document.createElement('div');
      cta.className = 'aib-hero-cta';
      cta.innerHTML = '<a class="aib-cta-read" href="#aib-learning-route">📖 무료로 읽기 시작</a>' +
        '<a class="aib-cta-buy" href="sales.html?utm_source=aibible&amp;utm_medium=hero&amp;utm_content=vol' + vol + '">구매 안내 →</a>';
      h1.insertAdjacentElement('afterend', cta);
      // 공유·선물 상자가 뒤늦게 제목 바로 뒤에 끼어들면 버튼이 밀리므로 로드 후 다시 제목 바로 아래로
      var pin = function () { if (h1.nextElementSibling !== cta) h1.insertAdjacentElement('afterend', cta); };
      window.addEventListener('load', function () { pin(); setTimeout(pin, 800); });
    }
    // 2) 5월 출간 알림 띠·"5권 출간" 문구는 지난 이벤트 → 숨김
    Array.prototype.forEach.call(document.querySelectorAll('body > div, body > a'), function (el) {
      var t = el.textContent || '';
      if (/5권 출간 · jbooking\.kr 결제/.test(t) || (/5권 「AI에게 일시키는/.test(t) && t.length < 400)) el.style.display = 'none';
    });
    // 2-1) "6/1 출간 — 가격" 띠(지난 출간·옛 가격 표기) 숨김
    Array.prototype.forEach.call(document.querySelectorAll('body div'), function (el) {
      if (el.children.length < 6 && /^\s*6\/1 출간 — 가격/.test(el.textContent || '')) el.style.display = 'none';
    });
    // 2-2) 휴대폰: 실시간 업데이트 띠 숨김, 시리즈 메뉴는 가로로 밀어 보는 한 줄
    var mobile = Math.min(window.innerWidth || 9999, document.documentElement.clientWidth || 9999) <= 480;
    if (mobile && h1) {
      // 제목 앞 소개 상자(훅·"바이블" 뜻·서문 팁)를 제목 아래 안내 뒤로 → 첫 화면에 제목
      var tail = document.getElementById('aib-learning-route') || h1;
      Array.prototype.slice.call(document.querySelectorAll('body div')).filter(function (el) {
        if (!(el.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_FOLLOWING) || el.contains(h1)) return false;
        return /^(📖 "바이블"은 정답이라|💡 \[본격적인 시작에 앞서|🌱 AI로 맡길 업무|🤖 봇과 에이전트|⚡ Claude Code, 이름)/.test((el.textContent || '').trim());
      }).filter(function (el, i, arr) { return !arr.some(function (o) { return o !== el && o.contains(el); }); })
        .forEach(function (el) { tail.insertAdjacentElement('afterend', el); tail = el; });
      Array.prototype.forEach.call(document.querySelectorAll('body div, body nav'), function (el) {
        if (!(el.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_FOLLOWING) || el.closest('#sidebar')) return;
        var t = (el.textContent || '').trim();
        if (/^🔄 이 책은 실시간으로 업데이트/.test(t) && el.children.length < 4) el.style.display = 'none';
        else if (/^(?:📚 ?)?AI 바이블 시리즈/.test(t) && el.querySelectorAll('a[href$="bible.html"]').length >= 3) {
          el.classList.add('aib-series-row');
        }
      });
    }
    // 3) 하단 고정 바가 있으면 업데이트 버튼을 그 위로
    var un = document.getElementById('un-btn');
    var bar = document.getElementById('mob-nav-bar') || document.getElementById('janda-bottom-bar');
    if (un && bar && getComputedStyle(bar).display !== 'none') {
      var h = bar.getBoundingClientRect().height;
      if (h > 0) un.style.bottom = (h + 12) + 'px';
    }
    if (un && Math.min(window.innerWidth || 9999, document.documentElement.clientWidth || 9999) <= 480) un.classList.add('aib-un-compact');
    // 4) 책 끝에 무료 6권 안내 (없을 때만)
    if (!document.querySelector('a[href*="parenting"]')) {
      var a = document.createElement('a');
      a.className = 'aib-next6';
      a.href = 'parenting/?utm_source=aibible&utm_medium=crosslink&utm_content=vol' + vol;
      a.innerHTML = '<strong>📗 무료 6권 《원질》</strong>AI 시대에 아이를 키우는 부모를 위한 책입니다. 결제 없이 바로 읽을 수 있어요. 무료로 읽기 →';
      var foot = document.querySelector('footer');
      if (foot) foot.insertAdjacentElement('beforebegin', a); else document.body.appendChild(a);
    }
  }
  // defer 실행 시점엔 본문 인라인 스크립트(공유·선물 상자)의 DOMContentLoaded가 아직 남아 있음 → 그 뒤에 실행
  var ran = false, once = function () { if (!ran) { ran = true; run(); } };
  if (document.readyState === 'complete') once();
  else { document.addEventListener('DOMContentLoaded', once); window.addEventListener('load', once); }
})();
