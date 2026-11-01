/* AI Bible interactive labs (2026-11-01).
   Each <section class="aib-lab" data-lab="spot|choice|builder|sort"> carries its data in
   <script type="application/json" class="lab-data">. Works offline, sends nothing, stores nothing. */
(function () {
  'use strict';

  function el(tag, attrs, text) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      if (k === 'class') n.className = attrs[k];
      else n.setAttribute(k, attrs[k]);
    });
    if (text != null) n.textContent = text;
    return n;
  }
  function feedback(host, kind, title, items) {
    host.textContent = '';
    host.className = 'lab-feedback ' + (kind || '');
    host.appendChild(el('strong', null, title));
    if (items && items.length) {
      var ul = el('ul');
      items.forEach(function (t) { ul.appendChild(el('li', null, t)); });
      host.appendChild(ul);
    }
    host.hidden = false;
  }
  function actions() { return el('div', { class: 'lab-actions' }); }
  function button(label, primary) {
    return el('button', { type: 'button', class: 'lab-btn' + (primary ? ' primary' : '') }, label);
  }

  /* 1. Spot the error: tap the sentences that do not match the source. */
  function spot(root, d) {
    var box = el('div', { class: 'lab-segs' });
    var segs = d.segments.map(function (s, i) {
      var b = el('button', { type: 'button', class: 'lab-seg', 'aria-pressed': 'false', 'data-i': String(i) }, s.text);
      b.addEventListener('click', function () {
        if (root.dataset.done) return;
        b.setAttribute('aria-pressed', b.getAttribute('aria-pressed') === 'true' ? 'false' : 'true');
      });
      box.appendChild(b); box.appendChild(document.createTextNode(' '));
      return b;
    });
    var fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite' }); fb.hidden = true;
    var act = actions(), check = button(d.checkLabel || '채점하기', true), reset = button('다시 하기');
    reset.hidden = true;
    check.addEventListener('click', function () {
      var hit = 0, total = 0, falsePick = 0, notes = [];
      d.segments.forEach(function (s, i) {
        var picked = segs[i].getAttribute('aria-pressed') === 'true';
        if (s.wrong) {
          total++;
          if (picked) { hit++; segs[i].classList.add('is-hit'); } else segs[i].classList.add('is-miss');
          notes.push((picked ? '찾음 · ' : '놓침 · ') + s.why);
        } else if (picked) {
          falsePick++; segs[i].classList.add('is-false');
          notes.push('원문과 맞는 문장 · ' + (s.why || '원문에 있는 내용입니다.'));
        }
      });
      root.dataset.done = '1';
      var perfect = hit === total && falsePick === 0;
      feedback(fb, perfect ? 'ok' : 'bad', hit + ' / ' + total + '개 찾음' + (falsePick ? ' · 잘못 고른 문장 ' + falsePick + '개' : '') + (perfect ? ' — 출고 가능한 검수입니다.' : ' — 놓친 부분을 확인하세요.'), notes.concat(d.takeaway ? ['정리 · ' + d.takeaway] : []));
      check.hidden = true; reset.hidden = false;
    });
    reset.addEventListener('click', function () {
      delete root.dataset.done;
      segs.forEach(function (b) { b.className = 'lab-seg'; b.setAttribute('aria-pressed', 'false'); });
      fb.hidden = true; check.hidden = false; reset.hidden = true;
    });
    act.appendChild(check); act.appendChild(reset);
    if (d.source) { var src = el('div', { class: 'lab-source' }); src.appendChild(el('b', null, '원문')); src.appendChild(document.createTextNode(d.source)); root.appendChild(src); }
    root.appendChild(el('p', { class: 'lab-q' }, d.question));
    root.appendChild(box); root.appendChild(act); root.appendChild(fb);
  }

  /* 2. Choice simulator: one situation at a time, immediate reasoning. */
  function choice(root, d) {
    var i = 0, score = 0;
    var prog = el('p', { class: 'lab-progress' }), bar = el('div', { class: 'lab-bar' }), fill = el('i');
    bar.appendChild(fill);
    var stage = el('div'), fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite' }); fb.hidden = true;
    var act = actions(), next = button('다음 상황', true); next.hidden = true; act.appendChild(next);
    function render() {
      stage.textContent = ''; fb.hidden = true; next.hidden = true;
      prog.textContent = '상황 ' + (i + 1) + ' / ' + d.steps.length + ' · 맞힌 판단 ' + score;
      fill.style.width = (i / d.steps.length * 100) + '%';
      var s = d.steps[i];
      if (s.context) stage.appendChild(el('div', { class: 'lab-source' }, s.context));
      stage.appendChild(el('p', { class: 'lab-q' }, s.q));
      var opts = el('div', { class: 'lab-options', role: 'group', 'aria-label': '선택지' });
      s.options.forEach(function (o) {
        var b = el('button', { type: 'button', class: 'lab-opt' }, o.label);
        b.addEventListener('click', function () {
          Array.prototype.forEach.call(opts.children, function (c) { c.disabled = true; });
          s.options.forEach(function (oo, k) { if (oo.best) opts.children[k].classList.add('is-ok'); });
          if (!o.best) b.classList.add('is-bad'); else score++;
          var best = s.options.filter(function (x) { return x.best; })[0];
          feedback(fb, o.best ? 'ok' : 'bad', o.best ? '좋은 판단입니다.' : '더 안전한 선택이 있습니다: ' + best.label, [o.why].concat(o.best ? [] : [best.why]));
          next.textContent = i + 1 < d.steps.length ? '다음 상황' : '결과 보기';
          next.hidden = false; next.focus();
        });
        opts.appendChild(b);
      });
      stage.appendChild(opts);
    }
    function finish() {
      if (d.steps.length > 1) stage.textContent = '';
      next.hidden = true; fill.style.width = '100%';
      prog.textContent = '완료';
      var r = d.results.filter(function (x) { return score >= x.min; })[0];
      feedback(fb, score === d.steps.length ? 'ok' : '', d.steps.length + '개 중 ' + score + '개 · ' + r.title, [r.text].concat(d.takeaway ? ['정리 · ' + d.takeaway] : []));
      var again = button('처음부터 다시');
      again.addEventListener('click', function () { i = 0; score = 0; again.remove(); render(); });
      act.appendChild(again);
    }
    next.addEventListener('click', function () { i++; if (i < d.steps.length) render(); else finish(); });
    root.appendChild(prog); root.appendChild(bar); root.appendChild(stage); root.appendChild(fb); root.appendChild(act);
    render();
  }

  /* 3. Builder: fill the fields, watch the instruction and its checklist update. */
  function builder(root, d) {
    var form = el('div'), inputs = {};
    d.fields.forEach(function (f) {
      var lab = el('label', { class: 'lab-field' });
      lab.appendChild(el('span', null, f.label));
      if (f.hint) lab.appendChild(el('small', null, f.hint));
      var ta = el('textarea', { rows: '2', placeholder: f.placeholder || '' });
      if (f.example) ta.dataset.example = f.example;
      lab.appendChild(ta); form.appendChild(lab); inputs[f.key] = ta;
      ta.addEventListener('input', update);
    });
    var meter = el('p', { class: 'lab-progress', 'aria-live': 'polite' }), bar = el('div', { class: 'lab-bar' }), fill = el('i');
    bar.appendChild(fill);
    var checks = el('ul', { class: 'lab-checks' }), out = el('pre', { class: 'lab-out', tabindex: '0', 'aria-label': '완성된 지시서' });
    var act = actions(), ex = button('예시로 채우기'), copy = button('지시서 복사', true), clear = button('비우기');
    var note = el('p', { class: 'lab-progress', role: 'status' });
    ex.addEventListener('click', function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = inputs[k].dataset.example || ''; }); update(); });
    clear.addEventListener('click', function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = ''; }); update(); });
    copy.addEventListener('click', function () {
      var text = out.textContent;
      function manual() {
        var r = document.createRange(); r.selectNodeContents(out);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        note.textContent = '자동 복사가 막혀 있습니다. 선택된 내용을 직접 복사하세요.';
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { note.textContent = '복사했습니다.'; }, manual);
      } else manual();
    });
    act.appendChild(ex); act.appendChild(copy); act.appendChild(clear);
    function val(k) { return (inputs[k].value || '').trim(); }
    function update() {
      var lines = [];
      d.fields.forEach(function (f) { lines.push('## ' + f.label + '\n' + (val(f.key) || '(비어 있음)')); });
      if (d.footer) lines.push(d.footer);
      out.textContent = lines.join('\n\n');
      checks.textContent = ''; var okN = 0;
      d.checks.forEach(function (c) {
        var v = val(c.key), ok = v.length >= (c.min || 1) && (!c.pattern || new RegExp(c.pattern).test(v));
        if (ok) okN++;
        checks.appendChild(el('li', null, (ok ? '✔ ' : '○ ') + (ok ? c.ok : c.todo)));
      });
      fill.style.width = (okN / d.checks.length * 100) + '%';
      meter.textContent = '지시서 완성도 ' + okN + ' / ' + d.checks.length + (okN === d.checks.length ? ' — AI에게 넘겨도 됩니다.' : '');
      note.textContent = '';
    }
    root.appendChild(form); root.appendChild(meter); root.appendChild(bar); root.appendChild(checks);
    root.appendChild(out); root.appendChild(act); root.appendChild(note);
    update();
  }

  /* 4. Sort: assign each item to a level, then compare with the reasoning. */
  function sort(root, d) {
    var legend = el('ul', { class: 'lab-legend' });
    d.levels.forEach(function (l) { legend.appendChild(el('li', null, l.label + ' — ' + l.desc)); });
    var rows = d.items.map(function (it, i) {
      var row = el('div', { class: 'lab-sort-row' });
      var id = 'lab-' + (root.id || 'sort') + '-' + i;
      row.appendChild(el('label', { for: id }, it.text));
      var sel = el('select', { id: id });
      sel.appendChild(el('option', { value: '' }, '단계 선택'));
      d.levels.forEach(function (l) { sel.appendChild(el('option', { value: l.id }, l.label)); });
      row.appendChild(sel);
      var why = el('p', { class: 'lab-sort-why' }); why.hidden = true; row.appendChild(why);
      return { row: row, sel: sel, why: why, it: it };
    });
    var fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite' }); fb.hidden = true;
    var act = actions(), check = button('정답과 비교', true);
    check.addEventListener('click', function () {
      var ok = 0, empty = 0;
      rows.forEach(function (r) {
        if (!r.sel.value) { empty++; return; }
        var good = r.sel.value === r.it.answer;
        if (good) ok++;
        var ans = d.levels.filter(function (l) { return l.id === r.it.answer; })[0];
        r.why.className = 'lab-sort-why lab-feedback ' + (good ? 'ok' : 'bad');
        r.why.textContent = (good ? '맞음 · ' : '권장: ' + ans.label + ' · ') + r.it.why;
        r.why.hidden = false;
      });
      if (empty) { feedback(fb, 'bad', '아직 고르지 않은 항목이 ' + empty + '개 있습니다.'); return; }
      feedback(fb, ok === rows.length ? 'ok' : '', rows.length + '개 중 ' + ok + '개가 권장 단계와 같습니다.', d.takeaway ? ['정리 · ' + d.takeaway] : []);
    });
    act.appendChild(check);
    root.appendChild(legend);
    if (d.question) root.appendChild(el('p', { class: 'lab-q' }, d.question));
    rows.forEach(function (r) { root.appendChild(r.row); });
    root.appendChild(act); root.appendChild(fb);
  }

  /* 5. Steps: a timed checklist with progress and a finish line. */
  function steps(root, d) {
    var prog = el('p', { class: 'lab-progress', 'aria-live': 'polite' }), bar = el('div', { class: 'lab-bar' }), fill = el('i');
    bar.appendChild(fill);
    var list = el('ol', { class: 'lab-steps' }), boxes = [];
    var fb = el('div', { class: 'lab-feedback ok', role: 'status' }); fb.hidden = true;
    d.steps.forEach(function (s, i) {
      var li = el('li'), lab = el('label');
      var cb = el('input', { type: 'checkbox' });
      lab.appendChild(cb);
      var body = el('span');
      body.appendChild(el('strong', null, (s.time ? '[' + s.time + '] ' : '') + s.title));
      if (s.detail) { body.appendChild(el('br')); body.appendChild(document.createTextNode(s.detail)); }
      lab.appendChild(body); li.appendChild(lab);
      if (s.code) li.appendChild(el('pre', { class: 'lab-out' }, s.code));
      list.appendChild(li); boxes.push(cb);
      cb.addEventListener('change', update);
    });
    var key = d.persist ? 'aib-steps-' + d.persist : null;
    if (key) {
      try {
        var saved = JSON.parse(window.localStorage.getItem(key) || '[]');
        saved.forEach(function (i) { if (boxes[i]) boxes[i].checked = true; });
      } catch (e) { /* storage unavailable: progress simply is not remembered */ }
    }
    function update() {
      if (key) {
        try {
          window.localStorage.setItem(key, JSON.stringify(boxes.map(function (b, i) { return b.checked ? i : -1; }).filter(function (i) { return i >= 0; })));
        } catch (e) { /* ignore */ }
      }
      var n = boxes.filter(function (b) { return b.checked; }).length;
      fill.style.width = (n / boxes.length * 100) + '%';
      prog.textContent = n + ' / ' + boxes.length + ' 단계 완료';
      if (n === boxes.length) feedback(fb, 'ok', d.done || '완료했습니다.', d.next ? ['다음 · ' + d.next] : []);
      else fb.hidden = true;
    }
    root.appendChild(prog); root.appendChild(bar); root.appendChild(list); root.appendChild(fb);
    update();
  }

  var TYPES = { spot: spot, choice: choice, builder: builder, sort: sort, steps: steps };
  function init() {
    Array.prototype.forEach.call(document.querySelectorAll('section.aib-lab[data-lab]'), function (sec) {
      if (sec.dataset.ready) return;
      var src = sec.querySelector('script.lab-data'), mount = sec.querySelector('.lab-mount');
      if (!src || !mount || !TYPES[sec.dataset.lab]) return;
      try { TYPES[sec.dataset.lab](mount, JSON.parse(src.textContent)); sec.dataset.ready = '1'; }
      catch (e) { mount.textContent = '실습을 불러오지 못했습니다. 페이지를 새로고침해 주세요.'; }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
