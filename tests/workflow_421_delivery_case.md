# Workflow 4.2.1: implementation evidence check

Date: 2026-10-04. Source baseline: `8b9e534`.
This is a bounded read-only check of delivery verification, not an application
repair or proof of a completed delivery loop.

## Real failure and candidate

The Cursor run using 4.2.0 approved B119 plan revision 3, implemented it and
recorded T001–T003 as done. Its browser demonstration covered pickup with a cart
item. [PR 145](https://github.com/ciupkajakub/smashnego-rails/pull/145) subsequently
received four implementation findings: obsolete delivery quotes could overwrite
current data, partial recovery cleared fee/address, replacement consent data was
lost, and a successful quote retained an obsolete error. The obsolete-quote issue
had also appeared on PR 144. Initial local evidence did not prevent the recurrence.

The 4.2.1 candidate changes delivery verification: compare actual proof with the
planned scenario before task completion; exercise affected implementations through
their callers; preserve existing safeguards; and use one scoped implementation
review for shared contracts, asynchronous state or cross-component recovery.
Design review remains bounded and optional for a specific unresolved design risk.

## Independent method

One fresh native agent received the candidate deliver skill and routed blueprint,
the original request from [the retained fixture](fixtures/b119-request.txt) up to
but excluding its `Testy` section, and read-only access to B119's code/documents.
It was asked whether the recorded completion was supported and what should happen
next. It did not receive the remote comments, expected findings, prior conversation
or historical trial reports. Network, edits, suites, servers and publication were
excluded; small read-only method reproductions were permitted.

The fixed application HEAD was `3d16f27d67302029e52c1e0ead03721934a8b228`, base
`46bd9a1e`. The agent used one pass and ten tool calls. Its output is retained in
this Codex conversation as `delivery_evidence_check`. Application FEATURE matched
the approved snapshot; IMPLEMENTATION differed only in task statuses.

## Observed outcome

The agent rejected the recorded completion and independently identified:

- The four implementation mechanisms reported by remote review.
- Unassigned delivery check/dialog callbacks, confirmed by actual-class method
  reproduction with zero validation/dialog calls.
- Missing recovery for the separate expired delivery-offer error.
- Browser proof that covered pickup with a cart item, without the promised empty
  cart, delivery or checkout-loss scenarios. Filling a slot before page load did
  not demonstrate refreshing data that became stale after loading.
- Declared V002/V003 files without the promised delivery replacement assertions.

It recommended keeping the batch active, reopening T001 for missing proof and
T002/T003 for code defects and missing proof, and updating owning repair tasks and
checks before code changes. It did not claim that unrun suites passed or failed,
and distinguished method reproductions from browser evidence.

## Checks and limits

Markdown/link/discovery validation, six package-comparison tests, frontmatter
validation with Ruby YAML and whitespace checks passed. The skill-creator Python
validator could not start because PyYAML is unavailable; no dependency was installed.

This supports defect discovery and rejection of unsupported completion on one
known failing implementation. It does not prove successful repair, a fresh full
implementation, CI waiting, Cursor compliance, lower total cost or reliable
prevention across runs. There was no second review trial, application modification,
workflow installation or PR update. Remote review remains part of delivery.
