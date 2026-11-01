/* AI Bible interactive labs (2026-11-01).
   Each <section class="aib-lab" data-lab="spot|choice|builder|sort"> carries its data in
   <script type="application/json" class="lab-data">. Works offline, sends nothing, stores nothing. */
(function () {
  'use strict';
  var EN = /^en/i.test(document.documentElement.lang || '');
  var M = EN ? {
    check: 'Check my answers', again: 'Try again', found: 'Found · ', missed: 'Missed · ', okLine: 'Matches the source · ', inSource: 'This is in the source.',
    foundN: function (h, t) { return h + ' / ' + t + ' found'; }, wrongPick: function (n) { return ' · ' + n + ' correct sentence(s) flagged'; },
    perfect: ' — ready to publish.', review: ' — review what you missed.', sum: 'Takeaway · ', source: 'Source',
    next: 'Next situation', sit: function (i, n, s) { return 'Situation ' + i + ' / ' + n + ' · correct ' + s; }, opts: 'Options',
    good: 'Good call.', safer: 'A safer choice: ', results: 'See result', done: 'Done', of: function (n, s) { return s + ' of ' + n + ' · '; }, restart: 'Start over',
    outLabel: 'Finished instruction', example: 'Fill with example', copy: 'Copy instruction', clear: 'Clear',
    manual: 'Automatic copy is blocked. The text is selected, so copy it manually.', copied: 'Copied.', empty: '(empty)',
    meter: function (o, n) { return 'Instruction completeness ' + o + ' / ' + n; }, ready: ' — ready to hand to AI.',
    pick: 'Choose', compare: 'Compare with answer', right: 'Correct · ', rec: function (l) { return 'Recommended: ' + l + ' · '; },
    unpicked: function (n) { return n + ' item(s) still unanswered.'; }, match: function (n, o) { return o + ' of ' + n + ' match the recommended level.'; },
    stepsDone: function (n, t) { return n + ' / ' + t + ' steps done'; }, finished: 'Finished.', nextUp: 'Next · ', fail: 'The exercise could not load. Please refresh the page.'
  } : {
    check: '채점하기', again: '다시 하기', found: '찾음 · ', missed: '놓침 · ', okLine: '원문과 맞는 문장 · ', inSource: '원문에 있는 내용입니다.',
    foundN: function (h, t) { return h + ' / ' + t + '개 찾음'; }, wrongPick: function (n) { return ' · 잘못 고른 문장 ' + n + '개'; },
    perfect: ' — 출고 가능한 검수입니다.', review: ' — 놓친 부분을 확인하세요.', sum: '정리 · ', source: '원문',
    next: '다음 상황', sit: function (i, n, s) { return '상황 ' + i + ' / ' + n + ' · 맞힌 판단 ' + s; }, opts: '선택지',
    good: '좋은 판단입니다.', safer: '더 안전한 선택이 있습니다: ', results: '결과 보기', done: '완료', of: function (n, s) { return n + '개 중 ' + s + '개 · '; }, restart: '처음부터 다시',
    outLabel: '완성된 지시서', example: '예시로 채우기', copy: '지시서 복사', clear: '비우기',
    manual: '자동 복사가 막혀 있습니다. 선택된 내용을 직접 복사하세요.', copied: '복사했습니다.', empty: '(비어 있음)',
    meter: function (o, n) { return '지시서 완성도 ' + o + ' / ' + n; }, ready: ' — AI에게 넘겨도 됩니다.',
    pick: '단계 선택', compare: '정답과 비교', right: '맞음 · ', rec: function (l) { return '권장: ' + l + ' · '; },
    unpicked: function (n) { return '아직 고르지 않은 항목이 ' + n + '개 있습니다.'; }, match: function (n, o) { return n + '개 중 ' + o + '개가 권장 단계와 같습니다.'; },
    stepsDone: function (n, t) { return n + ' / ' + t + ' 단계 완료'; }, finished: '완료했습니다.', nextUp: '다음 · ', fail: '실습을 불러오지 못했습니다. 페이지를 새로고침해 주세요.'
  };

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
    var act = actions(), check = button(d.checkLabel || M.check, true), reset = button(M.again);
    reset.hidden = true;
    check.addEventListener('click', function () {
      var hit = 0, total = 0, falsePick = 0, notes = [];
      d.segments.forEach(function (s, i) {
        var picked = segs[i].getAttribute('aria-pressed') === 'true';
        if (s.wrong) {
          total++;
          if (picked) { hit++; segs[i].classList.add('is-hit'); } else segs[i].classList.add('is-miss');
          notes.push((picked ? M.found : M.missed) + s.why);
        } else if (picked) {
          falsePick++; segs[i].classList.add('is-false');
          notes.push(M.okLine + (s.why || M.inSource));
        }
      });
      root.dataset.done = '1';
      var perfect = hit === total && falsePick === 0;
      feedback(fb, perfect ? 'ok' : 'bad', M.foundN(hit, total) + (falsePick ? M.wrongPick(falsePick) : '') + (perfect ? M.perfect : M.review), notes.concat(d.takeaway ? [M.sum + d.takeaway] : []));
      check.hidden = true; reset.hidden = false;
    });
    reset.addEventListener('click', function () {
      delete root.dataset.done;
      segs.forEach(function (b) { b.className = 'lab-seg'; b.setAttribute('aria-pressed', 'false'); });
      fb.hidden = true; check.hidden = false; reset.hidden = true;
    });
    act.appendChild(check); act.appendChild(reset);
    if (d.source) { var src = el('div', { class: 'lab-source' }); src.appendChild(el('b', null, M.source)); src.appendChild(document.createTextNode(d.source)); root.appendChild(src); }
    root.appendChild(el('p', { class: 'lab-q' }, d.question));
    root.appendChild(box); root.appendChild(act); root.appendChild(fb);
  }

  /* 2. Choice simulator: one situation at a time, immediate reasoning. */
  function choice(root, d) {
    var i = 0, score = 0;
    var prog = el('p', { class: 'lab-progress' }), bar = el('div', { class: 'lab-bar' }), fill = el('i');
    bar.appendChild(fill);
    var stage = el('div'), fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite' }); fb.hidden = true;
    var act = actions(), next = button(M.next, true); next.hidden = true; act.appendChild(next);
    function render() {
      stage.textContent = ''; fb.hidden = true; next.hidden = true;
      prog.textContent = M.sit(i + 1, d.steps.length, score);
      fill.style.width = (i / d.steps.length * 100) + '%';
      var s = d.steps[i];
      if (s.context) stage.appendChild(el('div', { class: 'lab-source' }, s.context));
      stage.appendChild(el('p', { class: 'lab-q' }, s.q));
      var opts = el('div', { class: 'lab-options', role: 'group', 'aria-label': M.opts });
      s.options.forEach(function (o) {
        var b = el('button', { type: 'button', class: 'lab-opt' }, o.label);
        b.addEventListener('click', function () {
          Array.prototype.forEach.call(opts.children, function (c) { c.disabled = true; });
          s.options.forEach(function (oo, k) { if (oo.best) opts.children[k].classList.add('is-ok'); });
          if (!o.best) b.classList.add('is-bad'); else score++;
          var best = s.options.filter(function (x) { return x.best; })[0];
          feedback(fb, o.best ? 'ok' : 'bad', o.best ? M.good : M.safer + best.label, [o.why].concat(o.best ? [] : [best.why]));
          next.textContent = i + 1 < d.steps.length ? M.next : M.results;
          next.hidden = false; next.focus();
        });
        opts.appendChild(b);
      });
      stage.appendChild(opts);
    }
    function finish() {
      if (d.steps.length > 1) stage.textContent = '';
      next.hidden = true; fill.style.width = '100%';
      prog.textContent = M.done;
      var r = d.results.filter(function (x) { return score >= x.min; })[0];
      feedback(fb, score === d.steps.length ? 'ok' : '', M.of(d.steps.length, score) + r.title, [r.text].concat(d.takeaway ? [M.sum + d.takeaway] : []));
      var again = button(M.restart);
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
    var checks = el('ul', { class: 'lab-checks' }), out = el('pre', { class: 'lab-out', tabindex: '0', 'aria-label': M.outLabel });
    var act = actions(), ex = button(M.example), copy = button(M.copy, true), clear = button(M.clear);
    var note = el('p', { class: 'lab-progress', role: 'status' });
    ex.addEventListener('click', function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = inputs[k].dataset.example || ''; }); update(); });
    clear.addEventListener('click', function () { Object.keys(inputs).forEach(function (k) { inputs[k].value = ''; }); update(); });
    copy.addEventListener('click', function () {
      var text = out.textContent;
      function manual() {
        var r = document.createRange(); r.selectNodeContents(out);
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
        note.textContent = M.manual;
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(function () { note.textContent = M.copied; }, manual);
      } else manual();
    });
    act.appendChild(ex); act.appendChild(copy); act.appendChild(clear);
    function val(k) { return (inputs[k].value || '').trim(); }
    function update() {
      var lines = [];
      d.fields.forEach(function (f) { lines.push('## ' + f.label + '\n' + (val(f.key) || M.empty)); });
      if (d.footer) lines.push(d.footer);
      out.textContent = lines.join('\n\n');
      checks.textContent = ''; var okN = 0;
      d.checks.forEach(function (c) {
        var v = val(c.key), ok = v.length >= (c.min || 1) && (!c.pattern || new RegExp(c.pattern).test(v));
        if (ok) okN++;
        checks.appendChild(el('li', null, (ok ? '✔ ' : '○ ') + (ok ? c.ok : c.todo)));
      });
      fill.style.width = (okN / d.checks.length * 100) + '%';
      meter.textContent = M.meter(okN, d.checks.length) + (okN === d.checks.length ? M.ready : '');
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
      sel.appendChild(el('option', { value: '' }, M.pick));
      d.levels.forEach(function (l) { sel.appendChild(el('option', { value: l.id }, l.label)); });
      row.appendChild(sel);
      var why = el('p', { class: 'lab-sort-why' }); why.hidden = true; row.appendChild(why);
      return { row: row, sel: sel, why: why, it: it };
    });
    var fb = el('div', { class: 'lab-feedback', role: 'status', 'aria-live': 'polite' }); fb.hidden = true;
    var act = actions(), check = button(M.compare, true);
    check.addEventListener('click', function () {
      var ok = 0, empty = 0;
      rows.forEach(function (r) {
        if (!r.sel.value) { empty++; return; }
        var good = r.sel.value === r.it.answer;
        if (good) ok++;
        var ans = d.levels.filter(function (l) { return l.id === r.it.answer; })[0];
        r.why.className = 'lab-sort-why lab-feedback ' + (good ? 'ok' : 'bad');
        r.why.textContent = (good ? M.right : M.rec(ans.label)) + r.it.why;
        r.why.hidden = false;
      });
      if (empty) { feedback(fb, 'bad', M.unpicked(empty)); return; }
      feedback(fb, ok === rows.length ? 'ok' : '', M.match(rows.length, ok), d.takeaway ? [M.sum + d.takeaway] : []);
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
      prog.textContent = M.stepsDone(n, boxes.length);
      if (n === boxes.length) feedback(fb, 'ok', d.done || M.finished, d.next ? [M.nextUp + d.next] : []);
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
      catch (e) { mount.textContent = M.fail; }
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
