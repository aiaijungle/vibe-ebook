const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const crypto = require('node:crypto');
const source = fs.readFileSync('assets/reader-stats-20261026.js', 'utf8');
const baseline = {total_visits:24314,active_readers:0,active_by_book:{},updated_at:'2026-10-26T17:30:00Z'};
const settle = () => new Promise(resolve => setImmediate(resolve));
function setup(options = {}) {
  const values = {};
  for (const name of ['data-aib-total','data-aib-readers','data-aib-book-readers','data-aib-status']) values['['+name+']'] = {textContent:''};
  const root = {attrs:{},classList:{add(){}},setAttribute(k,v){this.attrs[k]=v;},querySelectorAll(selector){return selector.split(',').map(s => values[s]).filter(Boolean);}};
  const events = {}, calls = [], saved = new Map();
  const legacyParent = {tagName:'DIV',textContent:'누적 방문자 20,000+ 지금 37명 읽는 중',removed:false,querySelector(){return null;},remove(){this.removed=true;}};
  const legacy = options.legacy ? {parentElement:legacyParent,remove(){this.removed=true;}} : null;
  const document = {
    documentElement:{classList:{add(){}}},
    visibilityState:options.hidden ? 'hidden' : 'visible',focused:true,
    hasFocus(){return this.focused;},
    getElementById(id){return id === 'live-readers' ? legacy : null;},
    querySelector(selector){return selector === '[data-aib-presence]' ? root : null;},
    querySelectorAll(selector){return selector === '[data-aib-presence]' ? [root] : [];},
    addEventListener(name,fn){events[name]=fn;}
  };
  const window = {addEventListener(name,fn){events[name]=fn;},setInterval(fn,ms){assert.equal(ms,20000);events.interval=fn;}};
  const sandbox = {
    window,document,location:{pathname:'/vibe-ebook/'+(options.page || 'book1.html')},
    navigator:{doNotTrack:options.optOut ? '1' : '0'},crypto,Date,Intl,AbortSignal,
    localStorage:{getItem(k){return saved.get(k);},setItem(k,v){saved.set(k,v);}},
    fetch:async (url,opts) => {
      calls.push(opts);
      if (options.fetch) return options.fetch(url,opts);
      if (options.fail) throw Error('offline');
      return {ok:true,json:async () => baseline};
    }
  };
  vm.runInNewContext(source, sandbox);
  return {values,root,events,calls,saved,document,legacyParent};
}
test('zero remains zero, counters use server values and simulated badge is removed', async () => {
  const s = setup({legacy:true});await settle();
  assert.equal(s.values['[data-aib-total]'].textContent,'24,314');
  assert.equal(s.values['[data-aib-readers]'].textContent,'0');
  assert.equal(s.root.attrs['data-aib-state'],'live');
  assert.equal(s.legacyParent.removed,true);
  assert.equal(JSON.parse(s.calls[0].body).reading,true);
});
test('hidden page sends no heartbeat or visit', async () => {
  const s=setup({hidden:true});await settle();assert.equal(s.calls.length,0);
});
test('privacy opt-out reads aggregates without saving an identifier', async () => {
  const s=setup({optOut:true});await settle();
  assert.equal(s.calls.length,1);assert.equal(s.calls[0].method,'GET');assert.equal(s.saved.size,0);
});
test('network failure displays unavailable instead of a fabricated number', async () => {
  const s=setup({fail:true});await settle();
  assert.equal(s.root.attrs['data-aib-state'],'offline');
  assert.equal(s.values['[data-aib-readers]'].textContent,'—');
});
test('sales page records a visit but is not counted as reading a book', async () => {
  const s=setup({page:'sales.html'});await settle();
  assert.equal(JSON.parse(s.calls[0].body).bookId,'catalog');
  assert.equal(JSON.parse(s.calls[0].body).reading,false);
});
test('blur retires the reading tab', async () => {
  const s=setup();await settle();s.document.focused=false;s.events.blur();await settle();
  assert.equal(JSON.parse(s.calls[1].body).action,'leave');
  assert.equal(s.calls[1].keepalive,true);
});
test('a heartbeat finishing after blur is also retired', async () => {
  let release;
  const s=setup({fetch:async (_,opts) => {
    if(JSON.parse(opts.body).action==='heartbeat')await new Promise(resolve => {release=resolve;});
    return {ok:true,json:async()=>baseline};
  }});
  s.document.focused=false;s.events.blur();release();await settle();await settle();
  assert.equal(s.calls.length,2);assert.equal(JSON.parse(s.calls[1].body).action,'leave');
});
