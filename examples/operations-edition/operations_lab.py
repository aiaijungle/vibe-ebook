"""Offline teaching lab: compare releases and cost per usable result. No API calls."""
import csv
import hashlib
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def money(value):
    try:
        amount = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError("Invalid amount") from error
    if not amount.is_finite() or amount < 0:
        raise ValueError("Amounts must be finite and nonnegative")
    return amount


def release_gate(cases, results, baseline="A", candidate="B"):
    """Exact fixture checks, not an LLM judge or production safety guarantee."""
    case_map = {row["case_id"]: row for row in cases}
    if not cases or len(case_map) != len(cases):
        raise ValueError("Cases must have unique IDs and cannot be empty")
    indexed = {}
    for row in results:
        key = (row["variant"], row["case_id"])
        if row["case_id"] not in case_map or key in indexed:
            raise ValueError("Unknown or duplicate result")
        indexed[key] = row
    scores = {}
    for variant in [baseline, candidate]:
        passed, missing, critical = [], [], []
        for case_id, case in case_map.items():
            actual = indexed.get((variant, case_id))
            if actual is None:
                missing.append(case_id)
                continue
            correct = (actual["status"] == case["expected_status"] and
                       actual["quoted_price_krw"] == case["expected_price_krw"])
            if correct:
                passed.append(case_id)
            elif case["critical"] == "yes":
                critical.append(case_id)
        scores[variant] = {"passed": len(passed), "total": len(cases),
                           "missing": missing, "critical_failures": critical}
    before, after = scores[baseline], scores[candidate]
    reasons = []
    if before["missing"] or after["missing"]:
        reasons.append("incomplete_comparison")
    if after["critical_failures"]:
        reasons.append("candidate_critical_failure")
    if after["passed"] < before["passed"]:
        reasons.append("candidate_lower_pass_count")
    return {"decision": "hold" if reasons else "eligible_for_human_review",
            "reasons": reasons, "variants": scores, "executed": False}


def accepted_result_cost(records, hourly_rate_krw):
    rate = money(hourly_rate_krw)
    totals = {}
    accepted = {}
    seen = set()
    for row in records:
        unique = (row["variant"], row["result_id"])
        if unique in seen:
            raise ValueError("One final result row per variant/result_id is required")
        seen.add(unique)
        if row["accepted"] not in ("yes", "no"):
            raise ValueError("accepted must be yes or no")
        variant = row["variant"]
        total = totals.setdefault(variant, {"api_krw": Decimal(0),
            "review_minutes": Decimal(0), "other_krw": Decimal(0)})
        total["api_krw"] += money(row["api_krw"])
        total["review_minutes"] += money(row["review_minutes"])
        total["other_krw"] += money(row["other_krw"])
        accepted[variant] = accepted.get(variant, 0) + (row["accepted"] == "yes")
    output = {}
    for variant, total in totals.items():
        labor = total["review_minutes"] * rate / Decimal(60)
        full = total["api_krw"] + total["other_krw"] + labor
        count = accepted[variant]
        output[variant] = {**{key: str(value) for key, value in total.items()},
            "review_cost_krw": str(labor), "total_krw": str(full),
            "accepted_results": count,
            "per_accepted_krw": str((full / count).quantize(Decimal("0.01"))) if count else None}
    return output


def instant(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Timestamp needs a timezone")
    return value


def reconcile(local, snapshot, refreshed_at):
    """Compare only the covered prefix; a stale report is never a live budget."""
    cutoff = instant(refreshed_at)
    def index(items):
        result = {}
        for row in items:
            if row["request_id"] in result:
                raise ValueError("Duplicate request ID")
            result[row["request_id"]] = row
            money(row["cost_krw"])
        return result
    local_map, provider = index(local), index(snapshot)
    covered = {key: row for key, row in local_map.items() if instant(row["at"]) <= cutoff}
    unreflected = sorted(set(local_map) - set(covered))
    missing = sorted(set(covered) - set(provider))
    extra = sorted(set(provider) - set(covered))
    mismatched = sorted(key for key in covered.keys() & provider.keys()
                        if money(covered[key]["cost_krw"]) != money(provider[key]["cost_krw"]))
    return {"covered_requests": len(covered), "unreflected_requests": unreflected,
            "missing_in_report": missing, "extra_in_report": extra,
            "amount_mismatch": mismatched, "usable_as_live_budget": False,
            "note": "Synthetic per-request CSV; real provider reports may be aggregated and revised."}


def approval_fingerprint(version, tool_version, arguments):
    payload = {"version": version, "tool_version": tool_version, "arguments": arguments}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def approval_still_matches(approved, current):
    """Illustrates binding only; not authentication, authorization or durable execution."""
    return approved == current


def main():
    folder = Path(__file__).with_name("fixtures")
    print(json.dumps({
        "release_gate": release_gate(rows(folder / "eval_cases.csv"), rows(folder / "eval_results.csv")),
        "accepted_result_cost": accepted_result_cost(rows(folder / "costs.csv"), "12000"),
        "reconciliation": reconcile(rows(folder / "local_usage.csv"), rows(folder / "report_snapshot.csv"),
                                    "2026-11-03T09:00:00+09:00"),
        "external_calls": 0, "executed": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
