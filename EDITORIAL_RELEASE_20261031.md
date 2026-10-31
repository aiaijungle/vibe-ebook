# AI Bible practical learning edition — 31 October 2026

Base: `550611aea526fbf89c66031d600444c42b76f641`. Local branch: `improve/bible-practical-global-20261031`.

## Reader outcomes

- Korean five-volume readers: public learning routes, prerequisites, concrete outputs, and substantive exercises inside the existing locked October companion sections.
- Suggested beginner sequence: 1 → 2 → 4 → 3 → 5. Operators can begin with Volume 5.
- `start-here.html`: complete free fact-check exercise with answer key, local-only worksheet, reader-result sharing template, and links to existing purchase information.
- English sales, learning guide and media kit: deliverables, prerequisites, language scope, access conditions and existing purchase routes.
- `en/first-workflow.html`: complete free English exercise with revision practice and checklist.
- English readers: practical entry links and selected factual corrections.

## Accuracy and preservation

Corrected selected unsupported research claims, absolute hallucination claims, SDK naming, Shorts guidance, zero-cost generalizations, per-message arithmetic and worker/headcount equivalence. Literal HTML inside Korean Volume 3 code samples now displays as code; injected site timer code was removed from the example. Historical model credits and incident records are retained. Current model guidance links to official documentation and separates historical provider snippets from the verified local lab.

Original purchase scripts in all five Korean readers were compared with HEAD and preserved. Astra verified preservation of English reader scripts and IDs and existing checkout links. This preservation is not an audit of the existing static paywall's security.

## Validation

- Existing standard-library ontology lab: 21 unittest tests PASS; sample returns `ready_for_review`, `executed=false`.
- Korean five readers and free entry page: 390px and 1280px browser checks, no body horizontal overflow; new exercise hidden before unlock; learning routes present; no `{title}` interpreted as a heading.
- Free Korean answer disclosure and worksheet input: PASS.
- Astra English review: four guide/sample pages and five reader pages at 390/1280px; navigation, answer disclosure, checkboxes and scoped layout PASS.
- Structured-data JSON and sitemap XML parse checks PASS. `git diff --check` PASS.
- Mobile free-practice screenshot visually reviewed.

Run the existing local lab from `examples/agent-ontology/` with `python -m unittest -v test_ontology_lab.py`.

The browser verification function is `scripts/verify_editorial_browser.js`. It assumes a static localhost server on port 8937 and is designed for Playwright CLI `run-code --filename`.

## Release limits

This is an editorial improvement with local browser verification, not a sales-performance result. No payment was made, no real customer was contacted, no review or conversion number was invented, and no live purchase-to-access flow was exercised. Existing checkout/payment policy and buyer credentials were not changed. No claim is made that all provider code, translations, third-party company statistics or device combinations have been revalidated.

Static client-side paywall weaknesses remain a separate release concern; preserving compatibility is not secure server-side authorization. The English edition still includes some Korean-origin examples/media as described in its edition guide. Japanese readers were not revised in this change.

The initial editorial audit was unpublished. The user subsequently explicitly requested completion and redeployment of volumes 1-5. This authorizes the reviewed edition's commit, push and existing GitHub Pages deployment; it does not change payment or refund terms. The public `release-20261031.json` identifies the exact edition and hashes of its reader pages, assets and exercise downloads.

## Official references checked

## Content-first and mobile follow-up

Each Korean volume now explains its learning context, central outcome and readiness for the next volume in a compact disclosure. Purchase copy emphasizes a concrete workflow and verification outcome; unsupported urgency and failure-rate claims were removed in the edited prompts. Free practice remains available before a purchase decision.

Mobile fixes: Volume 2's learning route was moved inside its fixed reader; its automatic completion observer was replaced with an explicit reflection button to avoid interrupting reading. Volume 3's floating gift button no longer blocks the mobile table of contents. Volume 4's table-of-contents control has a larger labeled touch target. Volume 2's update button clears the bottom navigation. Payment and entitlement endpoints were not changed; reader presentation and completion UI logic were changed in this follow-up.

`scripts/verify_mobile_reading.js` passed all 15 combinations of five Korean readers at 360, 390 and 430 pixels: no body horizontal overflow, working prerequisite disclosure, no unsolicited completion popup, locked new paid practice, and working open/close controls with at least 44px targets wherever a floating mobile table of contents exists. All 106 extracted inline JavaScript bodies passed syntax checking. Browser checks used desktop mobile viewport emulation with external HTTPS requests blocked; physical devices and live checkout were not tested.

These mobile observations describe the pre-publication pass. For this release the user chose manuscript/code review without a new browser run. Do not present the earlier viewport checks as visual verification of the final edition.

## Reference links

Detailed follow-up audit: `QUALITY_AUDIT_20261031.md`. The later audit intentionally changes reader UI scripts: synthetic social proof, global copy/selection guards, heuristic legal-warning overlays and repetitive watermarks were removed; scroll restoration and sharing were corrected. Earlier statements about script preservation describe the initial editorial pass, not these later reader UI changes. Existing payment/entitlement behavior and refund terms were retained. This still does not certify the client-side paywall as secure.

- https://platform.claude.com/docs/en/models/overview
- https://code.claude.com/docs/en/setup
- https://code.claude.com/docs/en/agent-sdk/overview
- https://developers.google.com/search/docs/appearance/ai-features
- https://support.google.com/youtube/answer/15424877
- https://mitsloan.mit.edu/ideas-made-to-matter/when-humans-and-ai-work-best-together-and-when-each-better-alone
