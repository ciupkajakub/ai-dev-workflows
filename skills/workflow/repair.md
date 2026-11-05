# Handle a finding or unexpected result

Read this file again each time a review report, requested feedback or unexpected
check result arrives, before changing code or tests. An earlier reading does not
count. After publication, the [entry contract](SKILL.md) still requires approval.

## When a result is unexpected

Stop and find its cause before editing. This includes your own new test failing,
output of an unexpected shape, a hang, or a run that executed nothing.

- Do not make a check pass by loosening parsing, assertions or filters unless you
  can show the earlier expectation was wrong. Record why.
- A test proving something is absent also asserts the request succeeded or failed
  as required. Skipped, empty or zero-test runs are not passes.
- A failed or missing diagnostic tool tells you nothing about the system it checks.
  Confirm the environment has changed before repeating a failed run.

## Keep one entry per finding

In IMPLEMENTATION, record each finding or unexpected result:

| Field | Content |
| --- | --- |
| Source | Report or check, and its [class](verify.md#findings-and-completion). |
| Before | Command, exit code and observation, or a conclusive code trace. |
| Cause | Confirmed cause, or `hypothesis`. |
| Change | What changed and its commit. Read project rules for that area first. |
| After | The regression check fails without the repair and passes with it, or why that is impossible and what else separates right from wrong. |
| Replaced behavior | Old and new output compared on data real callers reach, or `n/a` with the reason. Passing tests and similar code are not this comparison. |
| Dependents | Consumers and paths checked. |
| Status | `open`, `closed`, `rejected`, or `decided`. |

`closed` needs Before, Cause and After from observation. A `hypothesis` stays `open`.
`rejected` needs evidence. `decided` names who decided and the technical reason.
Reopen a `rejected` or `decided` entry only on new evidence, not because a new
review repeats it.
