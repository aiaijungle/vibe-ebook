# AI Bible: fictional ontology lab

This local exercise connects a shared business vocabulary to ordinary application checks. It is read-only and uses fictional customers, resources and reservations. It is not an OWL reasoner, an authorization service or a production booking system.

## Run

Use Python 3.10 or later; no third-party packages or API keys are needed.

```sh
cd examples/agent-ontology
python ontology_lab.py
python -m unittest -v test_ontology_lab.py
```

`sample_data.json` contains the request, authoritative training snapshot and fixed clock. All timestamps include a timezone. The fixture uses Asia/Seoul (+09:00); keep that offset when reproducing the exercise. The fixed clock makes the exercise independent of the actual calendar date.

## Read the output

| Status | Meaning |
| --- | --- |
| `ready_for_review` | The sample checks passed; a human can review the proposal. |
| `needs_information` | Required, fresh or complete information is missing. |
| `blocked` | A confirmed condition prevents the proposed use. |
| `duplicate` | Inspect the existing result instead of repeating the request. |

`executed` is always `false`. The shared fixture's detailed `reason` messages remain in Korean; use the English status meanings above. The English browser exercise in Volume 5 presents the five main scenarios in English.

## Understand the boundaries

Definitions describe customer, resource and reservation. Individual facts state which ID has a balance or occupies a resource. Python code validates time, balance, complete coverage, freshness, overlap and duplicate keys. Two products that use one resource still conflict when their time intervals overlap. Adjacent intervals are allowed in this sample; real setup-time policies may differ.

The evaluator has no authenticated user. Cross-store access must be rejected by a real authorized service; local data checks cannot establish permission. A production write also needs a fresh recheck, transaction/concurrency control, durable idempotency and an authoritative result ID. Review or approval does not replace these checks.

See the English practice chapters in AI Bible Volumes 2, 4 and 5. The lab does not send email, create reservations, deduct sessions, process payments or call a model.
