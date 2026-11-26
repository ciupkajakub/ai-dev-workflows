# First real deliveries under the 2026-11-25 rules

Date: 2026-11-26. Instructions installed in the application: the rules merged in PR
6, as quoted in the sessions. Source: five exported Claude Code sessions (Opus 5.5,
effort medium) from the Smashnego application on 2026-11-25 and 2026-11-26: NMI-227
(B130), B131, NMI-228 (B132), the session that started B131 and NMI-228, and an
interrupted first start of B131. The exports were read after the fact. The
application code, PRs and CI were not inspected independently, so results below are
what the transcripts and their tool output show.

## What happened

| Work | Path | Outcome in the transcript |
| --- | --- | --- |
| NMI-227 | plan, 3 plan reviews, approval, implementation, 2 implementation reviews, PR 226, approved delta with its own plan and code review | merged on the owner's request after green CI |
| B131 | plan, 3 plan reviews, approval, implementation, 2 implementation reviews, PR 227 | merged on the owner's request after green CI |
| NMI-228 | AppSignal plan v1–v3 with 3 reviews, owner questioned the tool, Sentry plan v4–v7 with 3 reviews | superseded by a separate session outside the workflow; a later small fix went out as PR 229 without workflow records or review |

The owner asked for no tests in all three. NMI-227 and B131 reached their PR in 33
and 26 minutes, owner approval included.

## Observed mechanisms

| Observation | Rule involved | Disposition |
| --- | --- | --- |
| Independent reviews found defects the author missed: two paths to a second payment in the B131 plan and two more in its code, reports sent to the wrong location, a check recorded as OK on HTTP 500, a setting that would stop the app from booting, and a quota that one stuck order would exhaust in days. | prepare.md and verify.md review | Rules worked as intended; no change. |
| B131 records claimed results that were not committed. The implementation reviewer found it before the PR. | verify.md evidence standard | Rules worked as intended; no change. |
| `run_check.py -- bin/rubocop \| tail -1 && git push` pushed despite an offense. | deliver.md, joining checks | Changed: the pipe is named next to `;`, and `--tail` replaces it. |
| RuboCop ran on changed application files; CI linted an evidence `.rb` file and failed. | verify.md, full commands | Changed: local checks cover the files CI selects, records and evidence included. |
| Three AppSignal plan reviews refined workarounds of the gem without asking whether another service avoided them. | prepare.md, choosing the approach | Changed: an existing mechanism that needs workarounds is compared with replacing it. |
| "Skip tests" was read as also skipping existing specs after an unanswered question; CI failed on three of them. | SKILL.md, exceptions | Changed: an unclear exception takes its narrowest reading. |
| The agent switched its recommendation twice within minutes when the owner questioned it. | none | Not a procedure gap; no rule added. |
| An agent offered the app's PR monitoring after delivery. | SKILL.md forbids recommending it | The host app's own instructions ask for that offer; not changed here. |

## Limits

Observations come from one application, one model and three tasks. No run without
the workflow is available for comparison, except the separate NMI-228 session that
was not exported; it is known only from another session's description of it. The
changes above have had no agent trial.
