"""Behavior tests for the book's read-only training example."""
import copy
import json
from pathlib import Path
import unittest
from ontology_lab import evaluate


class ProposalTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(Path(__file__).with_name('sample_data.json').read_text(encoding='utf-8'))
        self.request, self.world, self.now = data['request'], data['world'], data['now']

    def decision(self):
        return evaluate(self.request, self.world, self.now)

    def test_valid_data_produces_review_only(self):
        before = copy.deepcopy(self.world)
        self.assertEqual(self.decision()['status'], 'ready_for_review')
        self.assertFalse(self.decision()['executed'])
        self.assertEqual(self.world, before)

    def test_model_cannot_approve_itself(self):
        self.request['approved'] = True
        self.assertEqual(self.decision()['status'], 'ready_for_review')
        self.assertFalse(self.decision()['executed'])

    def test_missing_balance_is_unknown_not_zero(self):
        del self.world['customers']['C-001']['remaining_sessions']
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_zero_balance_is_blocked(self):
        self.world['customers']['C-001']['remaining_sessions'] = 0
        self.assertEqual(self.decision()['status'], 'blocked')

    def test_boolean_is_not_a_session_balance(self):
        self.world['customers']['C-001']['remaining_sessions'] = True
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_unknown_customer_or_resource(self):
        for key in ('customer_id', 'resource_id'):
            with self.subTest(key=key):
                request = dict(self.request, **{key: 'unknown'})
                self.assertEqual(evaluate(request, self.world, self.now)['status'], 'needs_information')

    def test_required_fields(self):
        for key in ('customer_id', 'resource_id', 'start', 'end', 'idempotency_key'):
            with self.subTest(key=key):
                request = dict(self.request)
                del request[key]
                self.assertEqual(evaluate(request, self.world, self.now)['status'], 'needs_information')

    def test_stale_information(self):
        self.world['valid_until'] = '2026-11-02T10:04:00+09:00'
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_future_verification_time(self):
        self.world['verified_at'] = '2026-11-02T10:06:00+09:00'
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_incomplete_query_is_not_availability(self):
        self.world['reservations'] = []
        self.world['availability_coverage'][0]['complete'] = False
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_request_outside_query_range(self):
        self.request['start'] = '2026-11-04T14:00:00+09:00'
        self.request['end'] = '2026-11-04T15:00:00+09:00'
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_overlapping_booking(self):
        self.world['reservations'][0]['start'] = '2026-11-03T14:30:00+09:00'
        self.assertEqual(self.decision()['status'], 'blocked')

    def test_enclosing_booking(self):
        self.world['reservations'][0]['start'] = '2026-11-03T13:00:00+09:00'
        self.assertEqual(self.decision()['status'], 'blocked')

    def test_adjacent_booking_is_not_overlap(self):
        self.world['reservations'][0]['start'] = self.request['end']
        self.assertEqual(self.decision()['status'], 'ready_for_review')

    def test_different_resource_does_not_block(self):
        self.world['reservations'][0]['resource_id'] = 'S-02'
        self.world['reservations'][0]['start'] = '2026-11-03T14:30:00+09:00'
        self.assertEqual(self.decision()['status'], 'ready_for_review')

    def test_cancelled_booking_does_not_block(self):
        self.world['reservations'][0]['status'] = 'cancelled'
        self.world['reservations'][0]['start'] = '2026-11-03T14:30:00+09:00'
        self.assertEqual(self.decision()['status'], 'ready_for_review')

    def test_unknown_status_is_not_assumed_cancelled(self):
        self.world['reservations'][0]['status'] = 'unrecognized'
        self.assertEqual(self.decision()['status'], 'needs_information')

    def test_duplicate_request_returns_existing_reference(self):
        self.world['processed_requests'][self.request['idempotency_key']] = 'existing-result-001'
        self.assertEqual(self.decision()['status'], 'duplicate')
        self.assertEqual(self.decision()['evidence'], ['existing-result-001'])

    def test_naive_and_malformed_timestamps(self):
        for value in ('2026-11-03T14:00:00', 'tomorrow', None):
            with self.subTest(value=value):
                self.request['start'] = value
                self.assertEqual(self.decision()['status'], 'needs_information')

    def test_end_must_follow_start(self):
        self.request['end'] = self.request['start']
        self.assertEqual(self.decision()['status'], 'blocked')

    def test_booking_must_be_in_future(self):
        self.now = '2026-11-04T10:05:00+09:00'
        self.assertEqual(self.decision()['status'], 'blocked')


if __name__ == '__main__':
    unittest.main()
