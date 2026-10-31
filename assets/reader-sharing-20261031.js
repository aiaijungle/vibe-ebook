(function () {
  'use strict';
  var files = ['book1.html', 'index.html', 'agent-bible.html', 'claude-code-bible.html', 'practical-bible.html'];
  function publicUrl() {
    var file = location.pathname.split('/').pop() || 'index.html';
    if (files.indexOf(file) < 0) file = 'start-here.html';
    return 'https://aiaijungle.github.io/vibe-ebook/' + file;
  }
  function notify(message) {
    var status = document.getElementById('aib-sharing-status');
    if (!status) {
      status = document.createElement('div');
      status.id = 'aib-sharing-status';
      status.setAttribute('role', 'status');
      status.style.cssText = 'position:fixed;bottom:100px;left:50%;transform:translateX(-50%);max-width:calc(100vw - 32px);padding:12px 18px;border-radius:10px;background:#172033;color:#fff;z-index:2147483647;line-height:1.5;pointer-events:none';
      document.body.appendChild(status);
    }
    status.textContent = message;
    status.hidden = false;
    clearTimeout(status._timer);
    status._timer = setTimeout(function () { status.hidden = true; }, 4000);
  }
  async function copy(text) {
    text = String(text || publicUrl());
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        notify('복사했습니다. 원하는 곳에 붙여넣으세요.');
        return true;
      }
    } catch (_) { /* Offer a selectable alternative; do not report success. */ }
    window.prompt('자동 복사를 사용할 수 없습니다. 아래 내용을 직접 선택해 복사하세요.', text);
    return false;
  }
  async function share(data) {
    data = Object.assign({}, data || {}, { url: publicUrl() });
    if (navigator.share) {
      try { await navigator.share(data); return true; }
      catch (error) { if (error && error.name === 'AbortError') return false; }
    }
    return copy([data.title, data.text, data.url].filter(Boolean).join('\n'));
  }
  window.BibleSharing = { publicUrl: publicUrl, copy: copy, share: share, notify: notify };
})();
