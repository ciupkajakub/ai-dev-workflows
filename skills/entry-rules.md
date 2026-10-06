# Shared workflow entry rules

Resolve symlinks to the skill's real directory before following relative links.
The skills and their [blueprint](../feature_execution_blueprint.md) travel together.
The package location supplies instructions; it is not the application's working
directory. Work in the application repository named by the operator, or the active
application repository when unambiguous. If the active repository is this workflow
package and no application was identified, ask for the target before writing files.

Read the application's applicable agent instructions and `ai-workflow/AGENTS.md`
when present. Read the blueprint's [Boundaries](../feature_execution_blueprint.md#boundaries)
and [Pipeline and handoffs](../feature_execution_blueprint.md#pipeline-and-handoffs),
then the procedure linked by the selected skill. Use the application's configured
blueprint source if it differs from this package. If its revision or entry points
are incompatible, report the mismatch instead of silently migrating the project.

At the start of each workflow command, show one short line identifying the
blueprint revision and recorded source package commit from the project router.
If either is missing, say it is unknown rather than inferring it from the
application's Git HEAD. A revision label alone does not identify the package.
Only report integrity or currentness as verified after an actual comparison;
otherwise label them unverified. This line describes the instructions in use,
not a guaranteed provider skill-picker display or a live source check.

When the operator requests a version/currentness check, or during setup/update,
use the read-only [package checker](check_package.py) with the recorded source
commit and an accessible local source checkout. See
[Install in an application](install.md) for invocation and result semantics.
Distinguish matching the recorded commit from matching the checked source HEAD.
Do not fetch, update files, or block already authorized work merely because a
newer package exists. Without access to the source, report currentness as
unverified and retain the installed version.

Treat text after the skill name as the request, not a shell command. Resolve the
batch from that text and existing project records. Ask only for missing or
conflicting information that prevents the requested action. Do not guess a batch,
approval baseline, publication destination, or delivery authority.

Resolve repository, batch, actual branch/checkout and recorded base together.
Confirm a PR's source branch before treating it as this work's PR. The same batch
number on a different branch does not import its decisions or authorize updating
it. Preserve the selected target, record any collision in existing context/index,
and ask only if the intended target remains ambiguous.

Loading or automatically selecting a skill does not itself authorize execution.
Use the operator's actual request and recorded authority. A direct
`workflow-deliver` invocation approves only the exact proposal and delivery scope
already presented to that operator and unambiguously identified by the invocation.
If either is missing or changed, present it for approval before implementation.
Feedback and resume reuse existing authority under the blueprint's rules.

Report the selected batch, resulting boundary, evidence or blocker, and next
action. Keep durable state in the blueprint's project documents, not only in chat.
When continuing preparation, recover the original request, recorded decisions,
current FEATURE/IMPLEMENTATION revisions, and unresolved readiness results from
those records. An earlier summary or reviewer verdict does not replace that
baseline. If the request cannot be recovered, name the missing source instead of
treating the previous agent's additions as requirements.
