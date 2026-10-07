# Install, update or inspect the package

This procedure installs instruction files and native discovery links in the
selected application. It does not implement a feature, migrate batches or supply
publication authority. A version-check request is read-only. Use the same package
in every tool; provider differences below concern discovery only.

## Install or update

1. Identify the source Git checkout, exact commit and target application. Inspect
   existing package/discovery locations and applicable project instructions.
   Do not install the package into its own source repository or overwrite another
   skill named `workflow`. Before replacing an existing copy, compare it with its
   recorded source commit using its existing checker when available. Preserve and
   reconcile local changes; a newer source does not authorize discarding them.
2. Copy `LICENSE` and the complete `skills/` directory from that exact commit into
   `ai-workflow/tooling/`. Use committed bytes, for example Git archive extraction,
   rather than labelling a dirty working copy as HEAD. Keep relative paths intact.
   During an update remove obsolete package-owned files only after reconciling
   local differences. Keep application rules and work records outside the package.
3. Expose the one canonical `skills/workflow` directory through the native paths
   for the tools the user uses. Each link is relative to its containing directory:

   | Tools | Application link | Target |
   | --- | --- | --- |
   | Codex / Cursor | `.agents/skills/workflow` | `../../ai-workflow/tooling/skills/workflow` |
   | Claude Code | `.claude/skills/workflow` | `../../ai-workflow/tooling/skills/workflow` |

   Both paths may point to the same canonical directory. Preserve matching links
   and report conflicts. If the filesystem cannot preserve them, report the
   installation limitation instead of creating divergent instruction copies.
4. In existing project instruction files record the source repository/full commit
   and optional local source path once, together with a pointer to the installed
   `skills/workflow/SKILL.md` when this workflow is requested. Other native entry
   files can point to that record. Preserve project commands and policies; create
   no additional workflow router, backlog or index. Do not force every unrelated
   task to load the workflow or change global model/tool settings.
5. Check links and relative references, then compare installed contents:

   ```sh
   python3 -B ai-workflow/tooling/skills/check_package.py \
     --source <source-checkout> --commit <recorded-source-commit>
   ```

   Exit 0 confirms content integrity, 1 reports differences and 2 means the check
   could not run. Compare with the checked local source HEAD separately: an intact
   older copy can have an update available. Without source access, report the
   comparison as unavailable. No fetch or update is part of a read-only check.
6. Confirm `workflow` discovery in a fresh session of each selected tool when
   available. Static link checks do not prove native discovery. Report unchecked
   tools as unverified; do not start delivery as a discovery test. Retain the
   package and links in application version control under the user's authorized
   commit/publication scope. Report the source commit, content comparison and
   discovery actually checked.

## Transition from the five-skill package

This is an incompatible instruction/document layout. An authorized package update
replaces the old blueprint and five skill directories with the new package.
Remove only discovery links that resolve to the replaced package's `workflow-setup`,
`workflow-prepare`, `workflow-deliver`, `workflow-feedback` and `workflow-resume`.
Reconcile package-owned references in existing instruction files while preserving
application-specific rules. Leave other links and all existing batches intact.

The old source commit remains the source for interpreting an unmigrated batch.
Package update alone does not rename its documents, revoke decisions or expand
approval. To continue old work with the new workflow, obtain an explicit request
to migrate that selected batch; do not migrate every batch during setup.

For that migration, preserve the old files through Git history or an unchanged
archive. Read its original request, FEATURE, IMPLEMENTATION, PROGRESS and relevant
index entry; compare them with the actual checkout and GitHub. Reconcile them
into the four [batch sections](workflow/SKILL.md#one-batch-record), preserving
requirements, identities, approvals, limitations and evidence links. Record the
old snapshot and retire only that batch's redundant current records after the
comparison. Legacy completion labels are claims to reconcile, not new approval.
Resolve material contradictions instead of guessing. Migration itself does not
start application delivery unless the user's instruction also authorizes it.
