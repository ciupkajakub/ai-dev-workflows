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

Treat text after the skill name as the request, not a shell command. Resolve the
batch from that text and existing project records. Ask only for missing or
conflicting information that prevents the requested action. Do not guess a batch,
approval baseline, publication destination, or delivery authority.

Loading or automatically selecting a skill does not itself authorize execution.
Use the operator's actual request and recorded authority. A direct
`workflow-deliver` invocation approves only the exact proposal and delivery scope
already presented to that operator and unambiguously identified by the invocation.
If either is missing or changed, present it for approval before implementation.
Feedback and resume reuse existing authority under the blueprint's rules.

Report the selected batch, resulting boundary, evidence or blocker, and next
action. Keep durable state in the blueprint's project documents, not only in chat.
