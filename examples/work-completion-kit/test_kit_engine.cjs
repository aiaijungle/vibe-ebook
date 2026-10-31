/* Offline acceptance tests. No browser, network, subprocess or actual user data. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {validateProject, calculateCosts, generateArtifacts} = require('./kit-engine.js');
const example = JSON.parse(fs.readFileSync(path.join(__dirname, 'project-example.json'), 'utf8'));
const template = JSON.parse(fs.readFileSync(path.join(__dirname, 'project-template.json'), 'utf8'));
const AS_OF = '2026-11-02T10:05:00+09:00';
const costComparison = [
  {method:'A',unique_accepted:18,api_cost:400,tool_cost:0,prep_minutes:0,work_minutes:0,review_minutes:30,rework_minutes:0,hourly_value:12000},
  {method:'B',unique_accepted:18,api_cost:250,tool_cost:0,prep_minutes:0,work_minutes:0,review_minutes:50,rework_minutes:0,hourly_value:12000}
];
const clone = value => structuredClone(value);
let passed = 0;
function test(name, run) {
  try { run(); passed++; process.stdout.write('PASS ' + name + '\n'); }
  catch (error) { process.stderr.write('FAIL ' + name + '\n'); throw error; }
}
function blocked(mutator) {
  const project = clone(example);
  mutator(project);
  const result = validateProject(project, AS_OF);
  assert.equal(result.status, 'draft');
  assert.ok(result.blocking_items.length > 0);
}
function approximately(actual, expected) {
  assert.equal(typeof actual, 'number');
  assert.ok(Math.abs(actual - expected) < 1e-8, `${actual} != ${expected}`);
}

test('filled fictional illustration is review-ready only at its declared simulated time', () => {
  const result = validateProject(example, AS_OF);
  assert.equal(result.status, 'ready_for_review');
  assert.deepEqual(result.blocking_items, []);
  assert.equal(example.fictional, true);
  assert.ok(example.cases.every(item => /실제|수기|fixture-v1|가상/.test(item.evidence)));
});
test('blank template never becomes completed work', () => {
  const result = validateProject(template, AS_OF);
  assert.equal(result.status, 'draft');
  assert.ok(result.blocking_items.length > 0);
});
test('missing owner blocks review readiness', () => blocked(p => { p.owner = ''; }));
test('unrun observation is not counted as a passing case', () => blocked(p => { p.cases[0].actual_status = ''; }));
test('missing evidence blocks even when expected and actual labels match', () => blocked(p => { p.cases[0].evidence = ''; }));
test('nested empty evidence is not proof', () => blocked(p => { p.cases[0].evidence = {file: '', output: null}; }));
test('a mismatching observed result blocks completion', () => blocked(p => { p.cases[2].actual_status = 'ready_for_review'; }));
test('duplicate case IDs cannot inflate the set of checks', () => blocked(p => { p.cases[1].case_id = p.cases[0].case_id; }));
test('null input can correctly lead to needs_information while zero leads to blocked', () => {
  assert.equal(example.cases.find(c => c.case_id === 'MISSING').input.remaining_sessions, null);
  assert.equal(example.cases.find(c => c.case_id === 'ZERO').input.remaining_sessions, 0);
  assert.equal(validateProject(example, AS_OF).status, 'ready_for_review');
});
test('expired source blocks under an explicit simulated clock', () => blocked(p => { p.source.valid_until = '2026-11-02T10:04:59+09:00'; }));
test('a source checked in the future is not already verified', () => blocked(p => { p.source.checked_at = '2026-11-02T10:06:00+09:00'; }));
test('a changed clock makes the simulated source expire', () => {
  assert.equal(validateProject(example, '2026-11-03T10:05:00+09:00').status, 'draft');
});
test('assessment clock must have an explicit timezone and valid calendar date', () => {
  for (const clock of ['2026-11-02T10:05:00', '2026-02-31T10:05:00+09:00']) {
    assert.equal(validateProject(example, clock).status, 'draft');
  }
});
test('source timestamps reject nonexistent calendar days instead of normalizing them', () => {
  blocked(p => { p.source.checked_at = '2026-02-31T10:00:00+09:00'; });
});
test('manual illustration has evidence and no fabricated command outcomes', () => {
  const change = example.changes[0];
  assert.equal(change.verification_mode, 'manual');
  assert.ok(change.manual_evidence && change.not_applicable_reason);
  assert.deepEqual(change.commands, []);
  assert.deepEqual(change.exit_codes, []);
  assert.equal(validateProject(example, AS_OF).status, 'ready_for_review');
});
test('manual verification without evidence or applicability reason blocks', () => {
  blocked(p => { p.changes[0].manual_evidence = ''; });
  blocked(p => { p.changes[0].not_applicable_reason = ''; });
});
test('manual mode cannot launder a made-up successful command outcome', () => {
  blocked(p => { p.changes[0].commands = ['FAKE_CHECK']; p.changes[0].exit_codes = [0]; });
});
test('a command verification record can be reviewed when complete', () => {
  const project = clone(example);
  Object.assign(project.changes[0], {verification_mode:'command', manual_evidence:'',
    not_applicable_reason:'', commands:['python -m unittest -v'], exit_codes:[0]});
  assert.equal(validateProject(project, AS_OF).status, 'ready_for_review');
});
test('nonzero command outcome blocks despite a confident signoff', () => blocked(p => {
  Object.assign(p.changes[0], {verification_mode:'command',commands:['python -m unittest -v'],exit_codes:[1]});
}));
test('missing or mismatched command outcomes are not successful checks', () => {
  blocked(p => { Object.assign(p.changes[0], {verification_mode:'command',commands:[],exit_codes:[]}); });
  blocked(p => { Object.assign(p.changes[0], {verification_mode:'command',commands:['check-one','check-two'],exit_codes:[0]}); });
});
test('unknown verification mode blocks rather than skipping verification', () => {
  blocked(p => { p.changes[0].verification_mode = 'automatic-success'; });
});
test('explicitly unrun check blocks', () => blocked(p => { p.changes[0].unrun = ['manual privacy review']; }));
test('omitted unrun list is unknown rather than all-done', () => blocked(p => { delete p.changes[0].unrun; }));
test('expired, rejected or unknown approval state blocks the proposal', () => {
  blocked(p => { p.approval.expires_at = '2026-11-02T10:00:00+09:00'; });
  blocked(p => { p.approval.decision = 'rejected'; });
  blocked(p => { p.approval.decision = 'probably-approved'; });
});
test('a complete pending or not-yet-requested proposal can be reviewed without fabricated approval', () => {
  for (const decision of ['pending', 'not_requested']) {
    const project = clone(example);
    project.approval.decision = decision;
    const validation = validateProject(project, AS_OF);
    assert.equal(validation.status, 'ready_for_review');
    assert.ok(validation.warnings.some(warning => /실행|execution/i.test(warning)));
    const output = generateArtifacts(project, AS_OF);
    assert.equal(output.validation.status, 'ready_for_review');
    for (const file of output.files) {
      assert.match(file.content, /actual_execution["']?\s*:\s*false/);
    }
  }
});
test('a signoff with unresolved blockers stays draft', () => blocked(p => { p.signoff.blocking_items = ['confirm source owner']; }));
test('review time reverses API-only ranking with independent arithmetic', () => {
  const result = calculateCosts(costComparison);
  assert.equal(result.length, 2);
  const [a, b] = result;
  assert.equal(a.total_cost, 6400);
  assert.equal(b.total_cost, 10250);
  approximately(a.cost_per_accepted, 6400 / 18);
  approximately(b.cost_per_accepted, 10250 / 18);
  assert.ok(a.total_cost < b.total_cost);
});
test('preparation, direct work and rework are real costs too', () => {
  const run = clone(costComparison[0]);
  run.prep_minutes = 10;
  run.work_minutes = 15;
  run.rework_minutes = 5;
  const [cost] = calculateCosts([run]);
  assert.equal(cost.total_cost, 12400);
  approximately(cost.cost_per_accepted, 12400 / 18);
});
test('completed example matches the workbook fictional manual and assisted batch', () => {
  const [manual, assisted] = calculateCosts(example.baseline_runs);
  assert.equal(manual.total_cost, 14000);
  assert.equal(manual.cost_per_accepted, 3500);
  assert.equal(assisted.total_cost, 11200);
  assert.equal(assisted.cost_per_accepted, 2800);
});
test('zero accepted outputs have no per-result estimate', () => {
  const run = clone(costComparison[0]);
  run.unique_accepted = 0;
  const [cost] = calculateCosts([run]);
  assert.equal(cost.total_cost, 6400);
  assert.equal(cost.cost_per_accepted, null);
});
test('explicit zero cost is valid but unknown cost is not zero', () => {
  const run = {method:'zero illustration', unique_accepted:1, api_cost:0, tool_cost:0,
    prep_minutes:0, work_minutes:0, review_minutes:0, rework_minutes:0, hourly_value:0};
  assert.equal(calculateCosts([run])[0].total_cost, 0);
  assert.throws(() => calculateCosts([{...run, api_cost:null}]));
});
test('negative, infinite and fractional accepted counts are rejected', () => {
  for (const bad of [-1, Infinity, NaN]) {
    assert.throws(() => calculateCosts([{...costComparison[0], api_cost:bad}]));
  }
  assert.throws(() => calculateCosts([{...costComparison[0], unique_accepted:1.5}]));
});
test('methods must have distinct nonempty names', () => {
  assert.throws(() => calculateCosts([{...costComparison[0], method:''}]));
  assert.throws(() => calculateCosts([costComparison[0], costComparison[0]]));
});
test('five documents contain usable review forms before the JSON appendix', () => {
  const {files} = generateArtifacts(example, AS_OF);
  const main = files.map(file => file.content.split(/^`{3,}json$/m)[0]);
  assert.match(main[0], /도자기 수업 문의/);
  assert.match(main[0], /가상 운영 담당자 A/);
  assert.match(main[1], /NORMAL/);
  assert.match(main[1], /예상 상태/);
  assert.match(main[2], /교육용 수기 대조 예시/);
  assert.match(main[2], /코드·셸 실행이 없는 문서 실습/);
  assert.match(main[3], /원본 서비스의 권위 있는 상태/);
  assert.match(main[4], /수동 방식/);
  assert.match(main[4], /보조 방식/);
});
test('artifact paths are fixed and user fields cannot inject executable HTML or fenced sections', () => {
  const hostile = clone(example);
  hostile.task_name = '../../stolen.md\n# FORCE_APPROVED\n<script>alert(1)</script>\n```html\n<img src=x onerror=alert(1)>\n```';
  hostile.approval.target = '<script>sendEverything()</script>';
  const output = generateArtifacts(hostile, AS_OF);
  assert.ok(output.validation);
  assert.equal(output.files.length, 5);
  assert.deepEqual(output.files.map(file => file.name), [
    '01-task-brief.md', '02-evidence-and-evals.md', '03-change-and-approval.md',
    '04-operations.md', '05-cost-and-iteration.md']);
  const text = output.files.map(file => file.content).join('\n');
  // HTML is safe as literal text inside a fenced code block, not as raw Markdown HTML.
  for (const file of output.files) {
    let fence = null;
    const outside = [];
    for (const line of file.content.split('\n')) {
      const marker = line.match(/^(`{3,})(.*)$/);
      if (!fence && marker) { fence = marker[1]; continue; }
      if (fence && marker && marker[1].length >= fence.length && !marker[2].trim()) { fence = null; continue; }
      if (!fence) outside.push(line);
    }
    assert.equal(fence, null, 'All exported code fences must close');
    const rendered = outside.join('\n');
    assert.ok(!/<script|<img\b/i.test(rendered));
    assert.ok(!/^# FORCE_APPROVED/m.test(rendered));
    assert.ok(!/^```html/m.test(rendered));
  }
  assert.ok(!/executed\s*:\s*true/i.test(text));
});
test('draft artifacts remain drafts and never forge a successful check', () => {
  const unfinished = clone(example);
  unfinished.cases[0].actual_status = '';
  const output = generateArtifacts(unfinished, AS_OF);
  assert.equal(output.validation.status, 'draft');
  assert.ok(output.validation.blocking_items.length > 0);
});
test('generation does not silently modify the imported project', () => {
  const snapshot = JSON.stringify(example);
  generateArtifacts(example, AS_OF);
  assert.equal(JSON.stringify(example), snapshot);
});
process.stdout.write(JSON.stringify({passed, network:false, browser:false, actual_execution:false}) + '\n');
