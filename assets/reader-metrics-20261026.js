/* Existing visit badges count repeat requests; no live audience is measured here. */
(function () {
  'use strict';
  var badge = document.getElementById('visit-badge');
  var fallback = document.getElementById('visit-num');
  var host = fallback ? fallback.parentElement : badge ? badge.parentElement : null;
  if (!host) host = document.querySelector('.header') || document.querySelector('h1');
  if (!host || document.getElementById('reader-metrics-status')) return;

  if (badge) {
    badge.alt = '전권 공통 방문 카운터 · 중복 방문 포함';
    badge.title = '재방문·새로고침·검수 요청 등이 포함될 수 있습니다. 고유 독자 수가 아닙니다.';
  }
  if (fallback) fallback.textContent = '집계 확인 불가';

  var note = document.createElement('span');
  note.id = 'reader-metrics-status';
  note.textContent = '실시간 열람 수 미집계';
  note.title = '현재 접속자 수를 측정하는 기능이 연결되지 않았습니다. 숫자를 추정해 표시하지 않습니다.';
  note.style.cssText = 'display:inline-block;max-width:100%;padding:3px 8px;margin:4px 0 4px 6px;border:1px solid currentColor;border-radius:6px;font-size:11px;line-height:1.6;white-space:normal;overflow-wrap:anywhere;vertical-align:middle;';
  if (host.tagName === 'H1') host.insertAdjacentElement('afterend', note);
  else host.appendChild(note);
})();
