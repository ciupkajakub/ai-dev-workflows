# Install in an application

Use this procedure for an authorized `workflow-setup` request in an application
repository. It installs instruction files and discovery links, not an agent runner.

1. Resolve the source package's real path and the target application repository.
   Inspect existing workflow and skill locations. Do not install this package into
   itself or overwrite another skill with the same name.
   Before an update, compare the existing package with its recorded commit when
   available. Preserve and reconcile local differences before replacing files.
2. For a new installation, copy `feature_execution_blueprint.md`, `LICENSE`, and
   the complete `skills/` directory together into `ai-workflow/tooling/` in the
   application. Preserve this layout so relative references remain valid. Record
   the source package repository, full commit and blueprint revision in
   `ai-workflow/AGENTS.md`. Record the local source checkout path there when
   available, as an optional verification location rather than a dependency.
   Install the package contents from that exact Git commit. Do not label a copy
   of uncommitted source changes with the HEAD commit.
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
   skill references can be read from the canonical directories. Compare the full
   canonical package with its recorded source commit using
   [check_package.py](check_package.py):

   ```sh
   python3 -B ai-workflow/tooling/skills/check_package.py --source <source-checkout> --commit <recorded-source-commit>
   ```

   Replace both placeholders with the actual checkout path and commit. The checker
   reads Git and package files without modifying them or accessing the network.
   A mismatch must be reconciled before claiming a verified installation; preserve
   local edits rather than silently overwriting them. Exit 0 confirms integrity,
   1 reports differences, and 2 means verification could not
   run. An intact older installation may still report an available update.
   If the source checkout or commit is unavailable, report integrity and
   currentness as unverified. Report the blueprint revision, recorded source commit,
   checked source HEAD and comparison result after setup or an authorized update.
   Confirm the five names appear in a fresh provider session when possible.
   If not checked, report discovery as pending. Do not invoke delivery merely to
   test the menu entry.

Keep the installed package and discovery links in the application's version
control so teammates and remote checkouts use the same instructions. Commit or
publish them only under the applicable authorization. There is no automatic
update: changing this source repository does not change an installed snapshot.
An explicit update request follows this procedure for the requested source commit,
preserves project instructions and batch documents, and rechecks the copied files.

For the initial bootstrap, an operator can point the application's agent at the
source `skills/workflow-setup/SKILL.md` by its absolute path and request setup for
the desired providers. After discovery, use the native skill names from the chat
input. No global installation or user-specific absolute symlink is required.
