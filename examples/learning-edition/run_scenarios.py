"""Read-only fictional scenarios. No API calls, bookings or file mutations."""
from copy import deepcopy
from pathlib import Path
import json
from ontology_lab import evaluate

base = json.loads(Path(__file__).with_name('sample_data.json').read_text(encoding='utf-8'))
cases = []
for name, expected in [('missing','needs_information'), ('zero','blocked'), ('normal','ready_for_review'), ('overlap','blocked'), ('expired','needs_information')]:
    data = deepcopy(base)
    if name == 'missing':
        del data['world']['customers']['C-001']['remaining_sessions']
    elif name == 'zero':
        data['world']['customers']['C-001']['remaining_sessions'] = 0
    elif name == 'overlap':
        data['world']['reservations'][0]['start'] = data['request']['start']
        data['world']['reservations'][0]['end'] = data['request']['end']
    elif name == 'expired':
        data['now'] = '2026-11-02T10:16:00+09:00'
    result = evaluate(data['request'], data['world'], data['now'])
    passed = result['status'] == expected and result['executed'] is False
    cases.append(passed)
    print(json.dumps({'case':name, 'expected':expected, 'passed':passed, **result}, ensure_ascii=False))
if not all(cases):
    raise SystemExit(1)
print('5/5 scenarios matched; executed=false in every case')
