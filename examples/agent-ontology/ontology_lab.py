"""AI Bible educational lab. Fictional data; read-only; no API, approval, or booking.

Run: python ontology_lab.py
This is an application-vocabulary/rule-check example, not an OWL reasoner,
an authorization service, or a production reservation system.
"""
from datetime import datetime
from pathlib import Path
import json


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be text')
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError('timezone required')
    return result


def evaluate(request, world, now):
    """Return a proposal decision. Never authorizes or performs a write."""
    def result(status, reason, evidence=None):
        return {'status': status, 'reason': reason,
                'evidence': evidence or [], 'executed': False}

    required = ('customer_id', 'resource_id', 'start', 'end', 'idempotency_key')
    if any(not isinstance(request.get(k), str) or not request[k].strip()
           for k in required):
        return result('needs_information', '고객·자원·시작·종료·중복방지 키를 확인하세요.')
    try:
        current, start, end = timestamp(now), timestamp(request['start']), timestamp(request['end'])
        verified = timestamp(world['verified_at'])
        expires = timestamp(world['valid_until'])
    except (ValueError, TypeError, KeyError):
        return result('needs_information', '날짜 형식과 시간대, 정보 확인 시각을 확인하세요.')
    if start >= end or start <= current:
        return result('blocked', '미래의 유효한 시작·종료 시간이어야 합니다.')
    if verified > current or current > expires or expires < verified:
        return result('needs_information', '현재 유효한 원본 스냅샷을 다시 조회하세요.')

    customer = world.get('customers', {}).get(request['customer_id'])
    resource = world.get('resources', {}).get(request['resource_id'])
    if customer is None or resource is None:
        return result('needs_information', '고객과 자원의 고유 ID를 원본에서 확인하세요.')
    balance = customer.get('remaining_sessions')
    if type(balance) is not int or balance < 0:
        return result('needs_information', '잔여 횟수가 누락되었거나 유효한 정수가 아닙니다.')
    if balance == 0:
        return result('blocked', '확인된 잔여 횟수가 0회입니다.', [request['customer_id']])

    coverage_ok = False
    try:
        for coverage in world.get('availability_coverage', []):
            if (coverage.get('resource_id') == request['resource_id']
                    and coverage.get('complete') is True
                    and timestamp(coverage['start']) <= start
                    and end <= timestamp(coverage['end'])):
                coverage_ok = True
    except (ValueError, TypeError, KeyError):
        return result('needs_information', '예약 조회 범위와 완전성 표시를 확인하세요.')
    if not coverage_ok:
        return result('needs_information', '이 자원·시간대의 전체 예약 조회가 필요합니다.')

    seen = world.get('processed_requests', {})
    if request['idempotency_key'] in seen:
        return result('duplicate', '이미 처리된 요청입니다. 기존 결과를 조회하세요.',
                      [seen[request['idempotency_key']]])
    try:
        for booking in world.get('reservations', []):
            if booking.get('resource_id') != request['resource_id']:
                continue
            if booking.get('status') == 'cancelled':
                continue
            if booking.get('status') not in ('confirmed', 'pending'):
                return result('needs_information', '알 수 없는 예약 상태를 확인하세요.')
            other_start, other_end = timestamp(booking['start']), timestamp(booking['end'])
            if other_start >= other_end:
                return result('needs_information', '원본 예약의 시간 범위를 확인하세요.')
            if start < other_end and other_start < end:
                return result('blocked', '같은 자원에 겹치는 예약이 있습니다.',
                              [booking.get('id', 'unknown-reservation')])
    except (ValueError, TypeError, KeyError):
        return result('needs_information', '원본 예약의 날짜 형식을 확인하세요.')
    return result('ready_for_review', '검토 준비 완료. 승인 및 실제 예약은 수행하지 않았습니다.',
                  [request['customer_id'], request['resource_id'], world.get('source', 'training-fixture')])


if __name__ == '__main__':
    fixture = json.loads(Path(__file__).with_name('sample_data.json').read_text(encoding='utf-8'))
    print(json.dumps(evaluate(fixture['request'], fixture['world'], fixture['now']),
                     ensure_ascii=False, indent=2))
