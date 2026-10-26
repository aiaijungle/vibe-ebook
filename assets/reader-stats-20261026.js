(function () {
  'use strict';
  var books = {'book1.html':'book1','index.html':'book2','agent-bible.html':'book3','claude-code-bible.html':'book4','practical-bible.html':'book5','sales.html':'catalog','ai-bible.html':'overview'};
  var page = location.pathname.split('/').pop() || 'index.html';
  var book = books[page];
  if (!book || window.__aibReaderStatsLoaded) return;
  window.__aibReaderStatsLoaded = true;
  document.documentElement.classList.add('aib-actual-stats');
  var endpoint = 'https://hzobwciaqtbfaxxvcots.supabase.co/functions/v1/ai-bible-reader-stats';
  // Public anon JWT; the private RPC is callable only by the server function.
  var key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6b2J3Y2lhcXRiZmF4eHZjb3RzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg2NTMxMTYsImV4cCI6MjA5NDIyOTExNn0.9VatQ5UxJrAKEE9gOcknvVvd_9I0j9GgQWe_UvtcfCg';
  var isBook = /^book[1-5]$/.test(book);
  // Retire legacy badge rows and simulated readers, including the mobile fallback.
  ['live-readers','visit-num','visit-badge','visit-num-mobile'].forEach(function (id) {
    var node = document.getElementById(id);
    if (!node) return;
    var parent = node.parentElement;
    if (id === 'visit-num-mobile' ||
        (parent && parent.tagName === 'DIV' && parent.textContent.indexOf('누적 방문자') !== -1 && !parent.querySelector('h1,h2,h3,a,button'))) {
      if (parent) parent.remove();
    } else node.remove();
  });
  document.querySelectorAll('.un-meta').forEach(function (node) {
    if (node.textContent.indexOf('초판(2026.4~6)') !== -1)
      node.textContent = node.textContent.replace('초판(2026.4~6)', '초판(2026년 5월)');
  });
  if (book === 'book1') document.querySelectorAll('.book-sub').forEach(function (node) {
    node.textContent = node.textContent.replace('바이브코딩바이블 시리즈', 'AI 바이블 시리즈');
  });
  if (!document.querySelector('[data-aib-presence]')) {
    var heading = document.querySelector('h1');
    if (!heading) return;
    var root = document.createElement('div');
    root.setAttribute('data-aib-presence', '');
    root.setAttribute('data-paywall-keep', '');
    heading.insertAdjacentElement('afterend', root);
  }
  var roots = Array.prototype.slice.call(document.querySelectorAll('[data-aib-presence]'));
  var visitor = null, tab = null, posted = false, inFlight = false;
  var lastActivity = Date.now(), failures = 0, nextTry = 0, epoch = 0;
  var uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  var optedOut = navigator.doNotTrack === '1' || navigator.globalPrivacyControl === true;
  if (!optedOut) {
    try {
      visitor = localStorage.getItem('aib.reader.visitor.v1');
      if (!uuidPattern.test(visitor || '')) {
        visitor = crypto.randomUUID();
        localStorage.setItem('aib.reader.visitor.v1', visitor);
      }
    } catch (_) { visitor = crypto.randomUUID(); }
    tab = crypto.randomUUID();
  }
  roots.forEach(function (root) {
    root.classList.add('aib-live-stats');
    root.setAttribute('role', 'status');
    root.setAttribute('aria-label', 'AI 바이블 실시간 방문·읽기 집계');
    root.setAttribute('aria-live', 'off');
    root.setAttribute('data-aib-state', 'loading');
    root.innerHTML = '<span class="aib-stat-item"><span>누적 방문</span> <strong data-aib-total>—</strong>회</span>' +
      '<span class="aib-stat-item"><span class="aib-stat-dot" aria-hidden="true"></span><span>현재 읽는 중</span> <strong data-aib-readers>—</strong>명</span>' +
      (isBook ? '<span class="aib-stat-item">이 책 <strong data-aib-book-readers>—</strong>명</span>' : '') +
      '<small data-aib-status>집계 연결 중</small>';
    root.title = '누적 방문은 기존 방문 배지의 24,314회에 새 집계의 방문 횟수를 이어 붙인 값입니다. 새 집계는 같은 브라우저의 30분 이내 재방문을 1회로 셉니다. 현재 읽는 중은 최근 60초 안에 응답한 읽기 화면의 브라우저 수이며 여러 탭은 중복 제외합니다. 백그라운드·5분 이상 활동 없는 화면과 추적 차단 브라우저는 제외됩니다.';
  });
  function visible() { return document.visibilityState !== 'hidden'; }
  function eligible() {
    return visible() && (typeof document.hasFocus !== 'function' || document.hasFocus()) && Date.now() - lastActivity < 300000;
  }
  function each(selector, fn) {
    roots.forEach(function (root) { Array.prototype.forEach.call(root.querySelectorAll(selector), fn); });
  }
  function valid(n) { return Number.isSafeInteger(n) && n >= 0; }
  function unavailable() {
    roots.forEach(function (root) { root.setAttribute('data-aib-state', 'offline'); });
    each('[data-aib-total],[data-aib-readers],[data-aib-book-readers]', function (node) { node.textContent = '—'; });
    each('[data-aib-status]', function (node) { node.textContent = '연결 확인 중'; });
  }
  function render(data) {
    if (!data || !valid(data.total_visits) || !valid(data.active_readers) || !data.active_by_book || !Number.isFinite(Date.parse(data.updated_at))) throw Error('Invalid statistics');
    var local = data.active_by_book[book] === undefined ? 0 : data.active_by_book[book];
    if (!valid(local)) throw Error('Invalid book count');
    roots.forEach(function (root) { root.setAttribute('data-aib-state', 'live'); });
    each('[data-aib-total]', function (node) { node.textContent = data.total_visits.toLocaleString('ko-KR'); });
    each('[data-aib-readers]', function (node) { node.textContent = data.active_readers.toLocaleString('ko-KR'); });
    each('[data-aib-book-readers]', function (node) { node.textContent = local.toLocaleString('ko-KR'); });
    var stamp = new Intl.DateTimeFormat('ko-KR', {timeZone:'Asia/Seoul',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(new Date(data.updated_at));
    each('[data-aib-status]', function (node) { node.textContent = stamp + ' 기준 · 20초 갱신'; });
  }
  async function request(action, keepalive) {
    var options = {method:action ? 'POST' : 'GET',headers:{apikey:key,Authorization:'Bearer ' + key},cache:'no-store'};
    if (action) {
      options.headers['Content-Type'] = 'application/json';
      options.body = JSON.stringify({action:action,visitorId:visitor,tabId:tab,bookId:book,reading:action === 'heartbeat' && isBook && eligible()});
    }
    if (keepalive) options.keepalive = true;
    else options.signal = AbortSignal.timeout(8000);
    var response = await fetch(endpoint, options);
    if (!response.ok) throw Error('Statistics unavailable');
    return response.json();
  }
  function leave() {
    epoch += 1;
    if (!visitor || !posted) return;
    posted = false;
    request('leave', true).then(function (data) { if (visible()) render(data); }).catch(function () { if (visible()) unavailable(); });
  }
  async function refresh() {
    if (!visible() || inFlight || Date.now() < nextTry) return;
    inFlight = true;
    var currentEpoch = epoch;
    try {
      var ping = visitor && eligible();
      if (!ping && posted) { leave(); currentEpoch = epoch; }
      var data = await request(ping ? 'heartbeat' : null, false);
      if (ping) {
        posted = true;
        // A heartbeat that finished after blur must also be retired.
        if (currentEpoch !== epoch || !eligible()) { leave(); return; }
      }
      if (currentEpoch === epoch) render(data);
      failures = 0; nextTry = 0;
    } catch (_) {
      failures += 1;
      nextTry = Date.now() + Math.min(120000, 5000 * Math.pow(2, failures - 1));
      unavailable();
    } finally { inFlight = false; }
  }
  function activity() {
    var wasIdle = Date.now() - lastActivity >= 300000;
    lastActivity = Date.now();
    if (wasIdle) refresh();
  }
  ['pointerdown','keydown','scroll','touchstart'].forEach(function (name) { window.addEventListener(name, activity, {passive:true}); });
  document.addEventListener('visibilitychange', function () {
    if (visible()) { lastActivity = Date.now(); nextTry = 0; refresh(); } else leave();
  });
  window.addEventListener('focus', function () { lastActivity = Date.now(); nextTry = 0; refresh(); });
  window.addEventListener('blur', leave);
  window.addEventListener('pagehide', leave);
  window.addEventListener('online', function () { nextTry = 0; refresh(); });
  window.addEventListener('offline', unavailable);
  refresh();
  window.setInterval(refresh, 20000);
})();
