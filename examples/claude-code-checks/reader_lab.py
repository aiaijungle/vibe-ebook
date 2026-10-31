"""Offline teaching fixtures. No network, subprocesses, reservations or sending."""
import json


RECORDS = [
    {"id": "R1", "authority": "meeting", "current": False, "topic": "cancel", "value": "1 hour"},
    {"id": "R2", "authority": "policy", "current": True, "topic": "cancel", "value": "24 hours"},
    {"id": "R3", "authority": "policy", "current": True, "topic": "capacity", "value": 4},
    {"id": "R4", "authority": "transaction", "current": True, "topic": "remaining", "value": 1},
    {"id": "R5", "authority": "preference", "current": True, "topic": "color", "value": "blue"},
    {"id": "R6", "authority": "meeting", "current": True, "topic": "promotion", "value": "draft"},
]


def select_context(records):
    """For this exercise only: scoped current policies + transaction evidence."""
    return [r["id"] for r in records if r["current"] and
            ((r["authority"] == "policy" and r["topic"] in {"cancel", "capacity"}) or
             (r["authority"] == "transaction" and r["topic"] == "remaining"))]


CASES = [
    {"id": "normal", "evidence": True, "approved": True, "duplicate": False, "tool_ok": True,
     "expected": {"status": "recorded", "writes": 1}},
    {"id": "missing_evidence", "evidence": False, "approved": True, "duplicate": False, "tool_ok": True,
     "expected": {"status": "needs_evidence", "writes": 0}},
    {"id": "approval_required", "evidence": True, "approved": False, "duplicate": False, "tool_ok": True,
     "expected": {"status": "awaiting_approval", "writes": 0}},
    {"id": "duplicate", "evidence": True, "approved": True, "duplicate": True, "tool_ok": True,
     "expected": {"status": "already_recorded", "writes": 0}},
    {"id": "tool_failure", "evidence": True, "approved": True, "duplicate": False, "tool_ok": False,
     "expected": {"status": "reconcile_required", "writes": 0}},
]


def simulate(case):
    """Fresh fake ledger per trial. A write is a local list append, never an API."""
    ledger = ["request-001"] if case["duplicate"] else []
    before = len(ledger)
    if not case["evidence"]:
        status = "needs_evidence"
    elif not case["approved"]:
        status = "awaiting_approval"
    elif "request-001" in ledger:
        status = "already_recorded"
    elif not case["tool_ok"]:
        status = "reconcile_required"
    else:
        ledger.append("request-001")
        status = "recorded"
    return {"status": status, "writes": len(ledger) - before}


def main():
    results = []
    for case in CASES:
        for trial in (1, 2):
            actual = simulate(case)
            results.append({"case": case["id"], "trial": trial, "actual": actual,
                            "passed": actual == case["expected"]})
    print(json.dumps({"selected_context": select_context(RECORDS), "results": results,
                      "external_actions": 0}, indent=2))
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
