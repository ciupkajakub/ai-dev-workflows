---
name: workflow-setup
description: Set up the blueprint workflow and its native skill entry points in an application repository when the user requests workflow setup.
---

# Set up the workflow

Resolve this skill directory's symlinks before opening relative references.
Read the [shared entry rules](../entry-rules.md), then follow
[Set up a project](../../feature_execution_blueprint.md#set-up-a-project).

Use the active application repository or the project path supplied by the user.
Inspect existing workflow files and provider instructions before creating the
missing base files. Preserve existing policies and project commands.

For an initial installation, make these skills available to the requested
providers using [Install in an application](../install.md).
Use the active provider when none is specified; do not configure unused providers
or change global settings. Link the installed blueprint's exact source and revision
from the project router. Existing installations are not permission to upgrade or
migrate unrelated workflow artifacts.

Verify the installed paths and native instruction entry point. Confirm discovery
in a fresh session when the environment permits it; otherwise report that check
as pending rather than claiming setup is complete. Do not launch a paid model run
solely to validate installation without authorization.

Stop after setup. Do not prepare a feature, implement application code, or publish
changes unless the user's request separately includes those actions.
