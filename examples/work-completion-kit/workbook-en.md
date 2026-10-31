# Finish one work task with a reviewable evidence package

This is an English companion workbook for the five-volume Korean edition. It does not claim that all five books have been translated or adapted to your market. Local business rules, source authority and permissions must be supplied by your organization.

The suggested route is Volume 1 → 2 → 4 → 3 → 5. Choose one recurring task: a checked customer-information draft, a request intake review, or an internal report draft. The deliverable is a package another person can inspect. Its final readiness label is `ready_for_review`, meaning **document-package review readiness**. It does not mean that a reservation, payment, message or deployment has occurred. The Volume 2 program also uses this label for an individual preflight decision; these are different assessment objects.

You need an editable document, authorized source material and a time record. You can complete the workbook without an AI account. The supplied Python labs use fictional data. Connecting your own application is separate work. The local workbench helps organize and export records; it does not authenticate an approver, test your application or perform business actions.

Read [the completed fictional example](completed-example.md) for structure and agree on [the acceptance rubric](acceptance-rubric.md) before starting. Copy the blank fields below. Unknown information stays unknown, with an owner and a follow-up date.

## Start with fifteen minutes today

Fifteen minutes is a suggested work interval, not a completion or results promise. Write only five lines: **one task, its owner, the intended source, one output, and the next unanswered question**. Save a draft, including unknowns. Verify the source before using factual claims in business work.

A Volume 1 reader can export just a brief and content record. Do not invent code commands, approvers or operating metrics to fill later sections. Complete those sections progressively when they are relevant. The workbench permits draft saving and export. Completing a small first exercise is different from preparing the full five-volume handoff. The full capstone is an optional advanced route.

## 0. Select a task that can be reviewed

Do not bundle a first draft, payment collection, customer delivery and business reporting into one first project. If your eventual goal includes external actions, limit this exercise to the proposal and evidence needed before those actions.

| Question | Required evidence | If missing |
|---|---|---|
| What goes in and what comes out? | One input format and one finished example | Ask the task owner for a completed case |
| Which source controls the answer? | Source ID, version, owner and validity | Resolve authority before generating claims |
| Who judges whether it is usable? | Reviewer and acceptance criteria | Name a reviewer or explicitly record self-review |

```text
project_id:
task_name: [a verb and one deliverable]
owner:
reviewer:
approver: [actual-use authority; unassigned if outside this scope]
scope_in:
scope_out:
output_artifact:
completion_unit: [one accepted information package, not one API call]
start_date / review_date:
```

For real work, use only the minimum required input. Remove identifying customer details and secrets before submitting material to an external AI service, or use an approved internal environment. Do not copy the fictional example's dates or validity assumptions into live work.

## 1. Source record and checked content — Volume 1

Record source authority and applicability before drafting. A recent download is not necessarily a current policy. Preserve the old version when a source changes.

| source_id | version | owner | checked_at | valid_until or recheck condition | applicability | approval evidence |
|---|---|---|---|---|---|---|
| | | | | | | |

If validity is unknown, record “hold until source owner confirms.” Do not invent an expiry date. Separate stable event information from rapidly changing availability.

| Fact | Source value and location | Draft value | Unresolved question |
|---|---|---|---|
| Date and time | | | |
| Amount, unit and conditions | | | |
| Audience and location | | | |
| Next action | | | |

Use this prompt, or follow the same procedure manually:

```text
Use only the approved facts from [source_id/version].
Create [deliverable] for [audience and intended next action].
Format: [title/body/FAQ].
Put missing information in a separate questions list.
Do not invent links, availability, discounts or outcome promises.
Return the draft, source IDs and statements requiring review.
```

| Sentence ID | Before | After | Reason and source | Reviewer outcome |
|---|---|---|---|---|
| | | | | keep / revise / hold |

Submit the source, draft, revision and fact-check table together. If you make two channel versions, compare dates, amounts, audience and next action. Different tone is acceptable; conflicting commitments are not. An unsupported claim blocks publication even when the wording sounds convincing.

## 2. Requirements and state cases — Volume 2

Define required inputs and what happens when they are missing. Zero is a known value; missing is not zero. Specify date, time zone and units where relevant.

| input_field | type and unit | required? | missing-data action | source |
|---|---|---|---|---|
| | | | | |

The supplied Volume 2 lab uses `needs_information`, `blocked` and `ready_for_review`; every case has `executed=false`. If your application uses other states, provide a mapping instead of silently replacing names.

| case_id | Input and reference time | expected_status | User wording and next action | actual_status | evidence | result |
|---|---|---|---|---|---|---|
| T01 normal | | | | not run | | |
| T02 missing required data | | | | not run | | |
| T03 known disqualifying condition | | | | not run | | |
| T04 conflict or duplicate | | | | not run | | |
| T05 expired information | | | | not run | | |

You may start with a paper walkthrough. Label evidence as **manual comparison**, **supplied fictional-code run**, or **your application integration test**. A correct paper answer is not proof of application behavior.

Use this triage sequence:

1. Missing or conflicting evidence → hold for information; ask the source owner; review the same case again.
2. Confirmed unmet condition → block and explain the condition or an alternative; do not bypass it.
3. Conditions met but approval missing → submit a fixed proposal; do not execute.
4. Request sent but outcome unknown → query the existing request ID; do not assume failure and submit a fresh request.
5. Actual output differs from the expected result → preserve input, version and evidence; move to the change record.

Completion evidence is five cases with reasons and next actions. If no application exists, mark application tests as not run. The package can be ready for document review while the application remains unimplemented.

## 3. Minimal change and reproducible evidence — Volume 4

If there is no defect, record “no change” and retain evidence of current behavior. Use a fictional copy for deliberate failure practice.

```text
change_id:
reason:
current_version / rollback_version:
reproduction_input_and_time:
expected_result / actual_result:
scope / rules_to_preserve:
files: [changed file and reason; none if unchanged]
verification_mode: manual / command
manual_evidence: [source comparison, before/after record and location]
not_applicable_reason: [why command checks do not apply to this scope]
commands: [exact location and command; empty list for manual review]
exit_codes: [observed values; empty list for manual review, never invent a zero]
evidence_location:
unrun: [test and reason]
```

Reproduce the failure before editing, then check both the failed case and normal cases. Changing an expected answer requires a justified change of business policy, not a desire for green tests. Manually repairing an output CSV can test an evaluator's response; it does not repair an AI system or application.

The Volume 3/4 checker tests the fictional ledger's `needs_evidence`, `awaiting_approval` and related states. It does not test the Volume 2 remaining-session rules. Match the checker to the work being changed. Exit code 0 proves only that the command succeeded. It is not proof of deployment or a customer journey.

For content-only work, use source comparisons and before/after revisions. Mark command and exit-code fields as not applicable with that explanation. A post-execution check does not automatically reverse an action already performed.

## 4. Roles and approval plan — Volume 3

Separate drafting, review, approval and execution. One person can hold multiple roles, but each decision still needs a distinct record.

| Role | Receives | Produces | Must not assume |
|---|---|---|---|
| Author | Approved sources | Draft and proposal | A draft is an executed action |
| Reviewer | Sources, output and evidence | Revision request or approval request | Missing evidence can be guessed |
| Approver | Fixed proposal version | Scoped decision | An old approval covers changed arguments |
| Execution owner | Valid approval and permissions | Result ID and verification | An unknown outcome is a failed action |

```text
proposal_id:
version: [proposal and tool versions]
target:
args: [reviewed amounts, times, content and recipients]
expires_at: [validity condition; unknown means no execution]
evidence / unresolved_questions:
approver / decision_time:
decision: pending / not_requested / approved / rejected
A pending proposal can be ready for document review. Approved requires an actual scoped decision.
expires_at describes proposal validity; it is not proof of authorization.
external_actions_in_this_workbook: none
```

The fictional ledger uses `recorded`, `needs_evidence`, `awaiting_approval`, `already_recorded`, and `reconcile_required`. `recorded` means a local list entry, not a real booking. Unknown external outcomes require reconciliation. Preserve request and result IDs and verify the actual service's duplicate-prevention behavior before relying on it.

## 5. Cost and operational handoff — Volume 5

Compare the same task and acceptance standard. Keep baseline and assisted runs separate, and record learning effects if the second run benefits from familiarity. If you have no measured run, label values as estimates. Small samples are not evidence of average productivity or sales impact.

| method | requests | unique_accepted | api_cost | tool_cost | prep_minutes | work_minutes | review_minutes | rework_minutes | hourly_value |
|---|---|---|---|---|---|---|---|---|---|
| Existing method | | | | | | | | | |
| Assisted method | | | | | | | | | |

```text
total_minutes = prep + work + review + rework
comparison_cost = API cost + allocated tool cost + total_minutes / 60 × hourly value
cost_per_accepted_result = comparison_cost / unique accepted results
```

Include failed and abandoned attempts in the numerator. Do not count retries as additional successful results, or add retry costs again when the API amount already includes them. Zero accepted results means unit cost cannot be calculated. Track review backlog and oldest waiting time as well. Separate cash expenditure from the calculated value of human time.

| Handoff field | Your record |
|---|---|
| stop_condition | Evidence expiry, critical error, budget or review-capacity threshold |
| stop_owner | Primary and backup owner |
| stop_scope | Which work stops and which status queries remain available |
| last_good_result | ID, version, time and review state |
| pending_requests | Request IDs and known/unknown outcomes |
| reconcile_before_retry | Query method, owner and fallback if status cannot be confirmed |
| rollback_version | Document/code version and separate handling of external effects |
| resume_checks | Cause resolved, valid source, permissions, budget, duplicate check, trial review |

These are design records in an offline workbook. They do not enforce a live spending cap or prevent duplicate transactions. Rolling back code does not unsend a message or cancel a confirmed reservation.

## 6. Two-week working schedule

Assign actual dates to ten working days over two weeks; leave four weekend days unassigned. Set your own time allowance. If a step takes longer, revise the schedule and record what remains; do not omit checks to meet a date.

| Day | Work | Evidence and exit condition |
|---|---|---|
| 1 | Select one task and reviewer | Input, output and scope agreed |
| 2 | Establish sources | Authority and unresolved questions recorded |
| 3 | Run or document the baseline | Completion unit and criteria fixed |
| 4 | Produce assisted draft | Fact comparison and time record |
| 5 | Walk through five states | Expected/actual and evidence type identified |
| 6 | Fix one issue or record no change | Before/after evidence and preserved normal behavior |
| 7 | Prepare roles and approval | Fixed proposal, scope and no execution claim |
| 8 | Calculate cost and handoff | No missing or double-counted costs |
| 9 | Ask another person to review | Findings and revisions; label self-review honestly |
| 10 | Submit the manager summary | Ready for review or explicit hold reasons |

Choose one variable for the next iteration, such as a missing-input message or draft length. Keep sources and expected answers fixed. If policy changes, version the evaluation set too.

## 7. One-page manager submission

```text
project_id / task_name:
owner / reviewer / approver:
deliverable_location_and_version:
scope_in / scope_out:
source_ids_versions_checked_at_validity:
input_count / unique_accepted:
evidence_type: manual / supplied lab / own integration
key_change_and_before_after_evidence:
tests_passed / failed / not_run:
baseline_cost / assisted_cost / measured_or_assumed:
critical_failures_and_open_questions:
stop_condition / stop_owner / resume_checks:
pending_requests_and_reconciliation:
rollback_version_and_external_effect_handling:
signoff.decision: revise / hold / ready_for_review
signoff.blocking_items:
signoff.owner / date:
next_experiment / planned_date:
external_execution: not performed
```

Use the rubric to review the submission. A generator can detect missing fields and produce documents, but it cannot establish source truth, reviewer identity or operational safety. Resolve missing evidence before improving presentation.
