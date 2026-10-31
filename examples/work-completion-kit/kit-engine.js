(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.AIWorkCompletionKit = factory();
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  function text(v) { return typeof v === 'string' && v.trim().length > 0; }
  function object(v) { return v !== null && typeof v === 'object' && !Array.isArray(v); }
  function proof(v) {
    if (text(v)) return true;
    if (Array.isArray(v)) return v.length > 0 && v.every(proof);
    if (object(v)) return Object.keys(v).length > 0 && Object.values(v).every(proof);
    return typeof v === 'number' && Number.isFinite(v);
  }
  function identifier(v) { return typeof v === 'string' && /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(v); }
  function dateValue(v, dateOnly) {
    if (typeof v !== 'string') return NaN;
    var pattern = dateOnly ? /^\d{4}-\d{2}-\d{2}$/ : /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,3})?(?:Z|[+-]\d{2}:\d{2})$/;
    if (!pattern.test(v)) return NaN;
    var calendar = new Date(v.slice(0, 10) + 'T00:00:00Z');
    if (!Number.isFinite(calendar.getTime()) || calendar.toISOString().slice(0, 10) !== v.slice(0, 10)) return NaN;
    if (!dateOnly) {
      if (+v.slice(11, 13) > 23 || +v.slice(14, 16) > 59 || +v.slice(17, 19) > 59) return NaN;
      var offset = v.match(/[+-](\d{2}):(\d{2})$/);
      if (offset && (+offset[1] > 14 || +offset[2] > 59 || (+offset[1] === 14 && +offset[2] !== 0))) return NaN;
    }
    return Date.parse(dateOnly ? v + 'T00:00:00Z' : v);
  }
  function calculateCosts(runs) {
    if (!Array.isArray(runs)) throw new Error('baseline_runs는 배열이어야 합니다.');
    var methods = new Set();
    return runs.map(function (run, index) {
      if (!object(run) || !text(run.method)) throw new Error('비용 기록 ' + (index + 1) + ': 방법 이름이 필요합니다.');
      if (methods.has(run.method.trim())) throw new Error('비용 방법·측정 회차 이름을 서로 다르게 기록하세요.');
      methods.add(run.method.trim());
      ['unique_accepted', 'api_cost', 'tool_cost', 'prep_minutes', 'work_minutes', 'review_minutes', 'rework_minutes', 'hourly_value'].forEach(function (key) {
        if (typeof run[key] !== 'number' || !Number.isFinite(run[key]) || run[key] < 0) throw new Error('비용 기록 ' + (index + 1) + ': ' + key + '는 0 이상 유한 숫자여야 합니다.');
      });
      if (!Number.isSafeInteger(run.unique_accepted)) throw new Error('unique_accepted는 0 이상 안전한 정수여야 합니다.');
      var total = run.api_cost + run.tool_cost + (run.prep_minutes + run.work_minutes + run.review_minutes + run.rework_minutes) / 60 * run.hourly_value;
      if (!Number.isFinite(total)) throw new Error('비용 합계가 계산 범위를 넘었습니다.');
      return {method: run.method, unique_accepted: run.unique_accepted, total_cost: total, cost_per_accepted: run.unique_accepted === 0 ? null : total / run.unique_accepted};
    });
  }
  function validateProject(project, asOfISO) {
    var blocking = [], warnings = ['입력한 기록의 형식·누락·일치를 검사합니다. 근거의 진위, 실제 실행, 외부 승인이나 도구 권한을 검증하지 않습니다.'];
    function requireValue(ok, message) { if (!ok) blocking.push(message); }
    var now = dateValue(asOfISO, false);
    requireValue(Number.isFinite(now), '검토 기준 시각은 시간대가 포함된 ISO 시각이어야 합니다.');
    if (!object(project)) return {status: 'draft', blocking_items: blocking.concat(['프로젝트는 JSON 객체여야 합니다.']), warnings: warnings};
    var p = project;
    requireValue(identifier(p.project_id), 'project_id는 영문·숫자로 시작하는 1~64자 영문·숫자·밑줄·하이픈 식별자여야 합니다.');
    ['task_name', 'owner', 'reviewer', 'approver', 'output_artifact'].forEach(function (key) { requireValue(text(p[key]), key + '가 필요합니다.'); });
    ['scope_in', 'scope_out', 'input_fields'].forEach(function (key) { requireValue(Array.isArray(p[key]) && p[key].length > 0 && p[key].every(proof), key + '에 비어 있지 않은 목록을 기록하세요.'); });
    requireValue(proof(p.status_policy), '상태별 판정 기준(status_policy)이 필요합니다.');
    var s = object(p.source) ? p.source : {};
    requireValue(identifier(s.id), '근거 source.id 형식이 올바르지 않습니다.');
    requireValue(text(s.version) && text(s.owner), '근거 버전과 정본 책임자가 필요합니다.');
    var checked = dateValue(s.checked_at, false), valid = dateValue(s.valid_until, false);
    requireValue(Number.isFinite(checked) && Number.isFinite(valid), '근거 확인·만료 시각을 시간대가 있는 ISO 시각으로 기록하세요.');
    if (Number.isFinite(now) && Number.isFinite(checked)) requireValue(checked <= now, '근거 확인 시각이 검토 기준 시각보다 미래입니다.');
    if (Number.isFinite(valid) && Number.isFinite(checked)) requireValue(valid > checked, '근거 만료 시각은 확인 시각보다 늦어야 합니다.');
    if (Number.isFinite(now) && Number.isFinite(valid)) requireValue(valid > now, '근거가 만료되었습니다. 정본을 다시 확인하세요.');
    var allowed = object(p.status_policy) && Array.isArray(p.status_policy.allowed_statuses) ? p.status_policy.allowed_statuses : null;
    var cases = Array.isArray(p.cases) ? p.cases : [], caseIDs = new Set();
    requireValue(cases.length >= 5, '정상·정보누락·차단·중복·권한밖 등 최소 5개 평가 사례가 필요합니다.');
    cases.forEach(function (c, i) {
      if (!object(c)) { blocking.push('평가 사례 ' + (i + 1) + '는 객체여야 합니다.'); return; }
      var label = '평가 ' + (text(c.case_id) ? c.case_id : String(i + 1));
      requireValue(identifier(c.case_id) && !caseIDs.has(c.case_id), label + ': 고유한 case_id가 필요합니다.'); caseIDs.add(c.case_id);
      requireValue(object(c.input) && Object.keys(c.input).length > 0, label + ': 시험 입력 객체가 필요합니다(의도적 null 필드 허용).');
      requireValue(text(c.expected_status), label + ': 예상 상태가 필요합니다.');
      requireValue(text(c.actual_status), label + ': 실제 상태가 없습니다. 미실행을 통과로 표시하지 마세요.');
      if (text(c.expected_status) && text(c.actual_status)) requireValue(c.expected_status === c.actual_status, label + ': 예상·실제 상태가 다릅니다.');
      if (allowed) requireValue(allowed.indexOf(c.expected_status) >= 0 && (!text(c.actual_status) || allowed.indexOf(c.actual_status) >= 0), label + ': 정책에 없는 상태입니다.');
      requireValue(proof(c.evidence) && proof(c.result), label + ': 실행 근거와 실제 결과 기록이 필요합니다.');
    });
    requireValue(Array.isArray(p.baseline_runs) && p.baseline_runs.length >= 2, '같은 범위를 비교할 비용 기록을 최소 2개 남기세요.');
    try { calculateCosts(p.baseline_runs).forEach(function (r) { if (r.unique_accepted === 0) warnings.push(r.method + ': 승인된 고유 결과가 0개이므로 건당 비용은 계산하지 않습니다.'); }); }
    catch (error) { blocking.push(error.message); }
    var changes = Array.isArray(p.changes) ? p.changes : [], changeIDs = new Set();
    requireValue(changes.length > 0, '변경·검사 기록이 필요합니다.');
    changes.forEach(function (c, i) {
      if (!object(c)) { blocking.push('변경 기록 ' + (i + 1) + '는 객체여야 합니다.'); return; }
      var label = '변경 ' + (text(c.change_id) ? c.change_id : String(i + 1));
      requireValue(identifier(c.change_id) && !changeIDs.has(c.change_id), label + ': 고유 change_id가 필요합니다.'); changeIDs.add(c.change_id);
      requireValue(text(c.reason) && text(c.rollback_version), label + ': 변경 이유·복구 버전이 필요합니다.');
      requireValue(Array.isArray(c.files) && c.files.length > 0 && c.files.every(text), label + ': 확인한 파일·산출물 목록이 필요합니다.');
      requireValue(c.verification_mode === 'manual' || c.verification_mode === 'command', label + ': 검증 방식을 manual 또는 command로 구분하세요.');
      if (c.verification_mode === 'manual') {
        requireValue(proof(c.manual_evidence) && text(c.not_applicable_reason), label + ': 수기 대조 근거와 명령 검사가 해당하지 않는 이유가 필요합니다.');
        requireValue(Array.isArray(c.commands) && c.commands.length === 0 && Array.isArray(c.exit_codes) && c.exit_codes.length === 0, label + ': 수기 대조에 가짜 명령·종료코드를 넣지 마세요. 명령·종료코드는 빈 목록이어야 합니다.');
      } else if (c.verification_mode === 'command') {
        requireValue(Array.isArray(c.commands) && c.commands.length > 0 && c.commands.every(text), label + ': 실제 검사 명령이 필요합니다.');
        requireValue(Array.isArray(c.exit_codes) && Array.isArray(c.commands) && c.exit_codes.length === c.commands.length && c.exit_codes.every(function (x) { return Number.isInteger(x) && x === 0; }), label + ': 각 검사 명령의 종료코드 0을 기록하세요. 실패 검사는 해결 전 차단됩니다.');
      }
      requireValue(Array.isArray(c.unrun) && c.unrun.length === 0, label + ': 미실행 검사가 있거나 미실행 목록이 누락되었습니다.');
    });
    var a = object(p.approval) ? p.approval : {};
    requireValue(identifier(a.proposal_id) && text(a.version) && text(a.target) && object(a.args), '승인 제안 ID·버전·대상·인자 객체가 필요합니다.');
    requireValue(['approved', 'pending', 'not_requested'].indexOf(a.decision) >= 0, '승인 상태는 approved·pending·not_requested로 기록하세요. 반려된 제안은 수정 후 다시 검토해야 합니다.');
    if (a.decision === 'pending' || a.decision === 'not_requested') warnings.push('사람의 승인이 아직 없습니다. 검토 자료는 만들 수 있지만 실제 실행은 불가합니다.');
    if (a.decision === 'approved') warnings.push('approved는 입력한 승인 기록입니다. 승인자 신원·권한·실제 승인 여부를 이 도구가 확인하지 않습니다.');
    var expires = dateValue(a.expires_at, false);
    requireValue(Number.isFinite(expires) && Number.isFinite(now) && expires > now, '승인 제안의 유효 시한이 지났거나 시각이 올바르지 않습니다.');
    var ops = object(p.operations) ? p.operations : {};
    requireValue(text(ops.stop_condition) && text(ops.stop_owner), '운영 중단 조건과 중단 책임자가 필요합니다.');
    requireValue(Array.isArray(ops.pending_requests) && ops.pending_requests.length === 0, '미확인 요청을 조정한 뒤 검토하세요. pending_requests는 빈 목록이어야 합니다.');
    requireValue(ops.reconcile_before_retry === true || text(ops.reconcile_before_retry), '재시도 전 실제 상태 확인 원칙을 명시해야 합니다.');
    requireValue(Array.isArray(ops.resume_checks) && ops.resume_checks.length > 0 && ops.resume_checks.every(proof), '재개 전 확인 목록이 필요합니다.');
    requireValue(Array.isArray(p.iteration) && p.iteration.length > 0, '한 번 이상의 개선 기록이 필요합니다.');
    if (Array.isArray(p.iteration)) p.iteration.forEach(function (entry, i) {
      requireValue(object(entry) && (text(entry.day) || (Number.isInteger(entry.day) && entry.day > 0)) && text(entry.action) && proof(entry.evidence) && text(entry.next_decision), '개선 기록 ' + (i + 1) + ': 시점·행동·근거·다음 결정이 필요합니다.');
    });
    var sign = object(p.signoff) ? p.signoff : {};
    requireValue(sign.decision === 'ready_for_review' && text(sign.owner), '최종 검토 요청 판단과 책임자가 필요합니다.');
    requireValue(Array.isArray(sign.blocking_items) && sign.blocking_items.length === 0, '최종 차단 항목이 남았거나 목록이 누락되었습니다.');
    var onlyDate = /^\d{4}-\d{2}-\d{2}$/.test(sign.date || '');
    var signed = dateValue(sign.date, onlyDate);
    requireValue(Number.isFinite(signed) && Number.isFinite(now) && (onlyDate ? sign.date <= asOfISO.slice(0, 10) : signed <= now), '최종 판단 날짜가 없거나 미래입니다.');
    if (p.fictional === true) warnings.push('가상 사례입니다. 기준 시각에 맞춘 모의 검사이며 실제 업무 완료·승인·현재 유효성을 증명하지 않습니다.');
    return {status: blocking.length ? 'draft' : 'ready_for_review', blocking_items: blocking, warnings: warnings};
  }
  function generateArtifacts(project, asOfISO) {
    var validation = validateProject(project, asOfISO), p = object(project) ? project : {};
    function block(value) {
      var json = JSON.stringify(value === undefined ? null : value, null, 2).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
      var ticks = (json.match(/`+/g) || []).reduce(function (n, s) { return Math.max(n, s.length); }, 2) + 1;
      var fence = '`'.repeat(ticks);
      return fence + 'json\n' + json + '\n' + fence + '\n';
    }
    var preamble = (p.fictional === true ? '> 교육용 가상 기록입니다. 실제 실행·권한·성과를 증명하지 않습니다.\n\n' : '') + '> 입력 기록을 정리한 검토 초안입니다. 실제 실행·근거 진위·외부 승인·도구 권한을 검증하지 않습니다.\n\n' + block({assessment_at: asOfISO, fictional: p.fictional === true, status: validation.status, actual_execution: false, blocking_items: validation.blocking_items, warnings: validation.warnings});
    function safe(value) {
      if (value === undefined || value === null || value === '') return '미기록';
      var raw = typeof value === 'string' ? value : JSON.stringify(value);
      return raw.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/([\\`*_{}\[\]()#+.!|~\-])/g, '\\$1').replace(/[\r\n]+/g, ' / ');
    }
    function list(values, empty) { return Array.isArray(values) && values.length ? values.map(function (v) { return '- ' + safe(v); }).join('\n') + '\n' : '- ' + (empty || '미기록') + '\n'; }
    function table(headers, rows) { return '| ' + headers.join(' | ') + ' |\n|' + headers.map(function () { return '---'; }).join('|') + '|\n' + (rows.length ? rows : [headers.map(function () { return '미기록'; })]).map(function (row) { return '| ' + row.map(safe).join(' | ') + ' |'; }).join('\n') + '\n'; }
    var source = object(p.source) ? p.source : {}, approval = object(p.approval) ? p.approval : {}, ops = object(p.operations) ? p.operations : {}, sign = object(p.signoff) ? p.signoff : {};
    var cases = Array.isArray(p.cases) ? p.cases.filter(object) : [], changes = Array.isArray(p.changes) ? p.changes.filter(object) : [], iteration = Array.isArray(p.iteration) ? p.iteration.filter(object) : [], costs = [], costError = '';
    try { costs = calculateCosts(p.baseline_runs); } catch (e) { costError = e.message; }
    var summary = '## 검토자에게 먼저 전달할 판단\n\n' + (validation.status === 'ready_for_review' ? '기록 형식상 검토 준비입니다. 아래 근거를 사람이 확인한 뒤 승인 여부를 판단하세요.' : '아직 초안입니다. 아래 차단 항목을 해결하기 전 실행·완료로 보고하지 마세요.') + '\n\n' + '**검토 기준 시각:** ' + safe(asOfISO) + '\n\n**실제 외부 실행:** 없음. 생성된 문서는 도구 권한이나 실제 승인을 부여하지 않습니다.\n\n' + '### 먼저 해결할 항목\n\n' + list(validation.blocking_items, '형식상 차단 항목 없음. 근거의 진위와 승인 권한은 별도 확인.') + '\n';
    var brief = '## 이번 업무의 약속\n\n**업무:** ' + safe(p.task_name) + '\n\n**프로젝트:** ' + safe(p.project_id) + '\n\n' + table(['작업 책임자', '검토 담당자', '승인 담당자'], [[p.owner, p.reviewer, p.approver]]) + '\n### 포함할 일\n\n' + list(p.scope_in) + '\n### 하지 않을 일\n\n' + list(p.scope_out) + '\n### 받아야 할 입력\n\n' + list(p.input_fields) + '\n### 남길 결과물\n\n' + safe(p.output_artifact) + '\n\n### 인수인계 전 확인\n\n- [ ] 포함·제외 범위를 담당자와 합의했다.\n- [ ] 원본 버전과 유효 시한을 확인했다.\n- [ ] 실제로 수행한 검사와 미실행 검사를 구분했다.\n';
    var evaluations = '## 사용할 원본\n\n' + table(['식별자', '버전', '책임자', '확인 시각', '유효 시한'], [[source.id, source.version, source.owner, source.checked_at, source.valid_until]]) + '\n### 상태 판정 규칙\n\n' + list(object(p.status_policy) ? p.status_policy.rules : p.status_policy) + '\n## 예상과 실제를 대조한 사례\n\n' + table(['사례', '예상 상태', '실제 상태', '비교'], cases.map(function (c) { return [c.case_id, c.expected_status, c.actual_status, !text(c.actual_status) ? '미실행/미기록' : c.actual_status === c.expected_status ? '기록상 일치 · 실행 증명 별도' : '불일치']; })) + '\n' + cases.map(function (c) { return '### 사례 ' + safe(c.case_id) + '\n\n**시험 입력:** ' + safe(c.input) + '\n\n**확인 근거:** ' + safe(c.evidence) + '\n\n**실제 결과와 다음 행동:** ' + safe(c.result) + '\n'; }).join('\n') + '\n- [ ] 결과가 맞다는 문구 대신 근거 기록·실제 산출물을 열어 대조했다.\n- [ ] null과0, 검토 준비와 실제 실행을 구분했다.\n';
    var changeDoc = '## 바꾼 이유와 확인 범위\n\n' + (changes.length ? changes.map(function (c) { return '### 변경 ' + safe(c.change_id) + '\n\n**이유:** ' + safe(c.reason) + '\n\n**복구 버전·방법:** ' + safe(c.rollback_version) + '\n\n**파일·산출물:**\n\n' + list(c.files) + '\n**검증 방식:** ' + safe(c.verification_mode) + '\n\n**수기 대조 근거:** ' + safe(c.manual_evidence) + '\n\n**명령 검사가 해당하지 않는 이유:** ' + safe(c.not_applicable_reason) + '\n\n' + (c.verification_mode === 'manual' ? '수기 검토에는 명령 종료코드를 생성하지 않습니다.\n' : table(['실제 검사 명령', '종료코드 기록'], (Array.isArray(c.commands) ? c.commands : []).map(function (cmd, i) { return [cmd, Array.isArray(c.exit_codes) ? c.exit_codes[i] : null]; }))) + '\n**미실행 검사:**\n\n' + list(c.unrun, '없음으로 입력됨 · 기록의 진위는 별도 확인') + '\n'; }).join('\n') : '변경 기록이 없습니다.\n') + '\n## 사람에게 요청하는 승인 범위\n\n' + table(['제안 ID', '버전', '대상', '제안 유효 시한', '입력한 승인 상태'], [[approval.proposal_id, approval.version, approval.target, approval.expires_at, approval.decision]]) + '\n**정확한 인자:** ' + safe(approval.args) + '\n\n승인 대기여도 검토 자료를 준비할 수 있습니다. approved라는 입력값만으로 승인자 신원·실행 권한을 확인할 수 없습니다. 반려된 제안은 수정 후 새로 검토하세요.\n\n- [ ] 검토자가 변경 전후와 미실행 검사를 확인했다.\n- [ ] 승인 대상 버전·인자·시한이 현재 제안과 같다.\n- [ ] 실제 실행 권한은 원본 서비스의 절차로 별도 확인했다.\n';
    var operations = '## 멈출 때 먼저 볼 운영 카드\n\n' + '**중단 조건:** ' + safe(ops.stop_condition) + '\n\n**중단 책임자:** ' + safe(ops.stop_owner) + '\n\n### 아직 결과가 불명확한 요청\n\n' + list(ops.pending_requests, '없음으로 입력됨 · 실제 원본 상태와 대조 필요') + '\n### 같은 일을 다시 시키기 전\n\n' + safe(ops.reconcile_before_retry) + '\n\n### 재개 전 확인 목록\n\n' + list(ops.resume_checks) + '\n### 사고가 났을 때의 순서\n\n1. 해당 업무를 멈추고 책임자에게 현재 증상을 전달한다.\n2. 이미 처리된 요청인지 원본의 실제 상태와 식별자를 확인한다.\n3. 변경 버전과 승인 대상이 일치하는지 확인한다.\n4. 복구·재검수 후 담당자가 재개 여부를 판단한다.\n\n이 순서는 검토용 초안입니다. 페이지가 실제 업무를 멈추거나 재개하지 않습니다.\n';
    var costsDoc = '## 결과 한 건의 전체 비용\n\n총비용 = API + 도구 + (준비 + 직접 작업 + 검수 + 재작업 시간) ÷60 × 시간당 가치\n\n금액 단위·비교 범위·측정 기간을 통일하고 시간 구간을 중복 계산하지 마세요. 시간당 가치는 전제이며 현금 지출과 다릅니다.\n\n' + (costError ? '계산 불가: ' + safe(costError) + '\n' : table(['방법·측정 회차', '승인된 고유 결과', '총비용', '건당 비용'], costs.map(function (c) { return [c.method, c.unique_accepted, c.total_cost.toFixed(2), c.cost_per_accepted === null ? '계산 불가 ·0개' : c.cost_per_accepted.toFixed(2)]; }))) + '\nAPI가 저렴해져도 검수·재작업이 늘면 전체 비용은 증가할 수 있습니다. 이 표만으로 ROI·생산성·시간 절감이 입증되지는 않습니다.\n\n## 개선하며 남긴 결정\n\n' + table(['시점', '바꾼 것', '확인 근거', '다음 결정'], iteration.map(function (it) { return [it.day, it.action, it.evidence, it.next_decision]; })) + '\n## 최종 검토 요청\n\n' + table(['작성자 판단', '책임자', '기록 날짜'], [[sign.decision, sign.owner, sign.date]]) + '\n### 작성자가 남긴 차단 항목\n\n' + list(sign.blocking_items, '없음으로 입력됨 · 위 형식 검사 결과와 함께 확인') + '\n- [ ] 승인된 고유 결과만 분모에 넣었다.\n- [ ] 실제 측정과 가상 예시·추정 전제를 구분했다.\n- [ ] 다음 결정은 유지·수정·중단 중 무엇인지 담당자가 확인했다.\n';
    var specs = [
      ['01-task-brief.md', '1권 · 업무 지시서', brief, {project_id:p.project_id, task_name:p.task_name, owner:p.owner, reviewer:p.reviewer, approver:p.approver, scope_in:p.scope_in, scope_out:p.scope_out, input_fields:p.input_fields, output_artifact:p.output_artifact}],
      ['02-evidence-and-evals.md', '2권 · 근거와 평가 사례', evaluations, {source:p.source, status_policy:p.status_policy, cases:p.cases}],
      ['03-change-and-approval.md', '4권 · 변경 검사와 승인 기록', changeDoc, {changes:p.changes, approval:p.approval}],
      ['04-operations.md', '3권 · 중단·조정·재개', operations, {operations:p.operations}],
      ['05-cost-and-iteration.md', '5권 · 비용·개선·최종 검토', costsDoc, {baseline_runs:p.baseline_runs, calculated_costs:costs, iteration:p.iteration, signoff:p.signoff}]
    ];
    return {validation: validation, files: specs.map(function (s) { return {name:s[0], content:'# ' + s[1] + '\n\n' + (p.fictional === true ? '> 교육용 가상 기록입니다. 실제 실행·권한·성과를 증명하지 않습니다.\n\n' : '> 입력 기록을 정리한 검토 초안입니다. 실제 실행·근거 진위·승인을 검증하지 않습니다.\n\n') + summary + s[2] + '\n## 원본 기록 부록\n\n' + preamble + '\n' + block(s[3])}; })};
  }
  return {validateProject:validateProject, calculateCosts:calculateCosts, generateArtifacts:generateArtifacts};
}));
