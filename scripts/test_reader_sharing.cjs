// Security and failure-path checks; no browser, network or real clipboard use.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../assets/reader-sharing-20261031.js'), 'utf8');
function setup(navigator = {}, pathname = '/vibe-ebook/index.html') {
  const notices = [], prompts = [];
  const context = {navigator, location: {pathname, href: 'https://example.test'+pathname+'?unlock=PRIVATE&email=PRIVATE#PRIVATE'},
    document: {getElementById: () => null, createElement: () => ({style: {}, setAttribute() {}}), body: {appendChild: element => notices.push(element)}},
    setTimeout: () => 1, clearTimeout() {}, window: {prompt: (...args) => prompts.push(args)}};
  vm.runInNewContext(source, context);
  return {api: context.window.BibleSharing, notices, prompts};
}
(async () => {
  let tests = 0;
  for (const file of ['book1.html', 'index.html', 'agent-bible.html', 'claude-code-bible.html', 'practical-bible.html']) {
    const {api} = setup({}, '/vibe-ebook/'+file);
    assert.equal(api.publicUrl(), 'https://aiaijungle.github.io/vibe-ebook/'+file);
    assert(!/[?#]|PRIVATE/.test(api.publicUrl())); tests++;
  }
  let ctx = setup({}, '/unexpected.html');
  assert.equal(ctx.api.publicUrl(), 'https://aiaijungle.github.io/vibe-ebook/start-here.html'); tests++;
  let copied = '';
  ctx = setup({clipboard: {writeText: async value => {copied = value;}}});
  assert.equal(await ctx.api.copy('sample'), true); assert.equal(copied, 'sample'); assert.equal(ctx.notices.length, 1); tests++;
  ctx = setup({clipboard: {writeText: async () => {throw Error('denied');}}});
  assert.equal(await ctx.api.copy('sample'), false); assert.equal(ctx.notices.length, 0); assert.equal(ctx.prompts[0][1], 'sample'); tests++;
  ctx = setup();
  assert.equal(await ctx.api.copy('sample'), false); assert.equal(ctx.prompts.length, 1); tests++;
  ctx = setup({share: async () => {const error = Error('cancel'); error.name = 'AbortError'; throw error;}});
  assert.equal(await ctx.api.share({title: 'Sample'}), false); assert.equal(ctx.prompts.length, 0); assert.equal(ctx.notices.length, 0); tests++;
  let payload;
  ctx = setup({share: async value => {payload = value;}});
  assert.equal(await ctx.api.share({url: 'https://example.test/?unlock=PRIVATE', title: 'Sample'}), true);
  assert.equal(payload.url, 'https://aiaijungle.github.io/vibe-ebook/index.html'); tests++;
  ctx = setup({share: async () => {throw Error('unavailable');}, clipboard: {writeText: async value => {copied = value;}}});
  assert.equal(await ctx.api.share({title: 'Sample'}), true); assert(!copied.includes('PRIVATE')); tests++;
  console.log(JSON.stringify({passed: tests, network: false, realClipboard: false}));
})().catch(error => {console.error(error.message); process.exitCode = 1;});
