import copy
import unittest
from pathlib import Path
from operations_lab import (accepted_result_cost, approval_fingerprint,
    approval_still_matches, money, reconcile, release_gate, rows)

FIXTURES = Path(__file__).with_name("fixtures")


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.cases = rows(FIXTURES / "eval_cases.csv")
        self.results = rows(FIXTURES / "eval_results.csv")

    def test_higher_average_with_critical_failure_is_held(self):
        report = release_gate(self.cases, self.results)
        self.assertEqual(report["variants"]["A"]["passed"], 9)
        self.assertEqual(report["variants"]["B"]["passed"], 11)
        self.assertEqual(report["decision"], "hold")
        self.assertEqual(report["variants"]["B"]["critical_failures"], ["Q05"])

    def test_fixed_candidate_is_only_review_eligible_not_auto_released(self):
        for row in self.results:
            if row["variant"] == "B" and row["case_id"] == "Q05":
                row.update(status="blocked", quoted_price_krw="")
        report = release_gate(self.cases, self.results)
        self.assertEqual(report["decision"], "eligible_for_human_review")
        self.assertFalse(report["executed"])

    def test_unrun_case_prevents_complete_comparison(self):
        report = release_gate(self.cases, self.results[:-1])
        self.assertIn("incomplete_comparison", report["reasons"])
        self.assertEqual(report["variants"]["B"]["missing"], ["Q12"])

    def test_duplicate_results_are_not_counted_twice(self):
        with self.assertRaises(ValueError):
            release_gate(self.cases, self.results + [self.results[0]])

    def test_unknown_case_is_not_silently_accepted(self):
        self.results[0]["case_id"] = "UNKNOWN"
        with self.assertRaises(ValueError):
            release_gate(self.cases, self.results)

    def test_no_cases_is_not_perfect_score(self):
        with self.assertRaises(ValueError):
            release_gate([], [])

    def test_review_time_reverses_api_only_cost_ranking(self):
        cost = accepted_result_cost(rows(FIXTURES / "costs.csv"), "12000")
        self.assertEqual(cost["A"]["total_krw"], "6400.0")
        self.assertEqual(cost["B"]["total_krw"], "10250.0")
        self.assertEqual(cost["A"]["accepted_results"], 18)
        self.assertEqual(cost["A"]["per_accepted_krw"], "355.56")
        self.assertEqual(cost["B"]["per_accepted_krw"], "569.44")

    def test_zero_accepted_is_not_free_per_result(self):
        data = [{"variant": "A", "result_id": "R1", "accepted": "no",
                 "api_krw": "100", "review_minutes": "3", "other_krw": "0"}]
        self.assertIsNone(accepted_result_cost(data, "12000")["A"]["per_accepted_krw"])

    def test_repeated_result_cannot_inflate_denominator(self):
        data = rows(FIXTURES / "costs.csv")
        with self.assertRaises(ValueError):
            accepted_result_cost(data + [data[0]], "12000")

    def test_invalid_cost_is_rejected(self):
        for value in ["-1", "NaN", "Infinity", "abc"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                money(value)

    def test_report_lag_is_not_missing_local_work_or_available_budget(self):
        result = reconcile(rows(FIXTURES / "local_usage.csv"),
            rows(FIXTURES / "report_snapshot.csv"), "2026-11-03T09:00:00+09:00")
        self.assertEqual(result["unreflected_requests"], ["REQ-03"])
        self.assertEqual(result["missing_in_report"], [])
        self.assertFalse(result["usable_as_live_budget"])

    def test_amount_disagreement_surfaces_instead_of_overwriting_ledger(self):
        snapshot = rows(FIXTURES / "report_snapshot.csv")
        snapshot[0]["cost_krw"] = "999"
        result = reconcile(rows(FIXTURES / "local_usage.csv"), snapshot,
                           "2026-11-03T09:00:00+09:00")
        self.assertEqual(result["amount_mismatch"], ["REQ-01"])

    def test_unqualified_local_time_is_rejected(self):
        with self.assertRaises(ValueError):
            reconcile([], [], "2026-11-03T09:00:00")

    def test_changed_action_arguments_do_not_reuse_prior_binding(self):
        args = {"class_id": "CLASS-01", "resource_id": "S-01", "quoted_price": 35000}
        approved = approval_fingerprint("A", "review-v1", args)
        unchanged = approval_fingerprint("A", "review-v1", dict(reversed(list(args.items()))))
        self.assertTrue(approval_still_matches(approved, unchanged))
        changed = copy.deepcopy(args)
        changed["resource_id"] = "S-02"
        self.assertFalse(approval_still_matches(approved, approval_fingerprint("A", "review-v1", changed)))
        self.assertFalse(approval_still_matches(approved, approval_fingerprint("B", "review-v1", args)))
        self.assertFalse(approval_still_matches(approved, approval_fingerprint("A", "review-v2", args)))


if __name__ == "__main__":
    unittest.main()
