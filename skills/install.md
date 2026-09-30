# Install in an application

Use this procedure for an authorized `workflow-setup` request in an application
repository. It installs instruction files and discovery links, not an agent runner.

1. Resolve the source package's real path and the target application repository.
   Inspect existing workflow and skill locations. Do not install this package into
   itself or overwrite another skill with the same name.
2. For a new installation, copy `feature_execution_blueprint.md`, `LICENSE`, and
   the complete `skills/` directory together into `ai-workflow/tooling/` in the
   application. Preserve this layout so relative references remain valid. Record
   the source package commit and blueprint revision in `ai-workflow/AGENTS.md`.
   If a package is already installed, reuse it; replacing it requires an authorized
   update and reconciliation with the project's configured blueprint.
3. Expose each of the five `workflow-*` skill directories using relative directory
   symlinks. Create only missing parent directories and links. Preserve existing
   links that already resolve to the intended skill; report a conflicting target.

   | Provider | Link location in the application | Relative link target |
   | --- | --- | --- |
   | Codex and Cursor | `.agents/skills/workflow-<action>` | `../../ai-workflow/tooling/skills/workflow-<action>` |
   | Claude Code | `.claude/skills/workflow-<action>` | `../../ai-workflow/tooling/skills/workflow-<action>` |

   Replace `<action>` with `setup`, `prepare`, `deliver`, `feedback`, and `resume`.
   Cursor also discovers `.claude/skills`, so a Claude-only installation already
   exposes the skills to Cursor. Do not add a separate `.cursor/skills` copy.
   When both discovery paths exist, they must resolve to the same canonical files.
   If the checkout cannot preserve directory symlinks, report that installation
   limitation rather than changing Git settings or creating divergent copies.
4. Follow [Set up a project](../feature_execution_blueprint.md#set-up-a-project)
   to connect the application's native instructions to `ai-workflow/AGENTS.md`.
   Use the root `AGENTS.md` for Codex/Cursor or `CLAUDE.md` for Claude Code,
   preserving existing instructions. The router points to the installed blueprint.
5. Check that every discovery link resolves and that the blueprint and shared
   skill references can be read from the canonical directories. Confirm the five
   names appear in a fresh provider session when possible. If not checked, report
   discovery as pending. Do not invoke delivery merely to test the menu entry.

Keep the installed package and discovery links in the application's version
control so teammates and remote checkouts use the same instructions. Commit or
publish them only under the applicable authorization. There is no automatic
update: changing this source repository does not change an installed snapshot.

For the initial bootstrap, an operator can point the application's agent at the
source `skills/workflow-setup/SKILL.md` by its absolute path and request setup for
the desired providers. After discovery, use the native skill names from the chat
input. No global installation or user-specific absolute symlink is required.
