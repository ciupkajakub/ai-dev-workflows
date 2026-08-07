#!/bin/sh

# shellcheck disable=SC2016 # Backticks below are literal Markdown syntax.

set -eu

repo_root=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
blueprint="$repo_root/feature_execution_blueprint.md"
readme="$repo_root/README.md"

require_text() {
  expected=$1
  if ! grep -Fq -- "$expected" "$blueprint"; then
    echo "missing v2 contract: $expected" >&2
    exit 1
  fi
}

reject_text() {
  retired=$1
  if grep -Fq -- "$retired" "$blueprint"; then
    echo "retired stop policy still present: $retired" >&2
    exit 1
  fi
}

require_text 'Blueprint revision: `2.1.0`'
require_text 'Workflow schema: `2`'
require_text 'Blueprint digest: `<sha256>`'
require_text 'continuation_mode: batch_to_verified_outcome'
require_text 'progress_checkpoint_minutes: 10'
require_text 'same_root_cause_no_progress_limit: 3'
require_text 'Do not ask the user to say `continue`, `fix`, or invoke section 13'
require_text 'invoke section 13 in repair-and-close mode immediately'
require_text 'Mode: repair_and_close unless the request explicitly says audit_only.'
require_text '## Impact map'
require_text 'visual rubric'
require_text 'Integration evidence values:'
require_text 'Release evidence values:'
require_text 'does not run automatically'
require_text 'only sanitized, reproducible failure classes.'
require_text 'A passing structure test alone is insufficient.'
require_text 'only the comparable baseline-versus-candidate'
require_text 'they are not behavioral agent evidence'
require_text 'usability without steering, and regression evaluability'
require_text 'the agent under evaluation cannot be its own judge'
require_text 'more than one declared variable group changed'
require_text 'avoidable user-intervention rate is at most 10%'
require_text 'target 220 lines or fewer for FEATURE.md'
require_text 'IMPLEMENTATION.md targets 360 lines or fewer'
require_text 'Keep this file near 70 lines or fewer'
require_text 'exceeds about 300 lines'

reject_text 'max_turn_elapsed_minutes'
reject_text 'max_task_estimated_minutes'
reject_text 'max_environment_recovery_cycles'
reject_text 'max_validation_remediation_cycles'
reject_text 'long_running_task_requires_approval'
reject_text 'Never continue to another task in the same turn.'
reject_text 'section 13 pending'

if grep -Eq 'B[0-9]{3}-like|[0-9]+% B[0-9]{3}/B[0-9]{3} baseline' "$blueprint"; then
  echo "project-specific evaluation history leaked into section 14" >&2
  exit 1
fi

section_11_count=$(grep -c '^## 11\. Execute The Next Task$' "$blueprint")
if [ "$section_11_count" -ne 1 ]; then
  echo "expected one canonical section 11, found $section_11_count" >&2
  exit 1
fi

if grep -Eq 'hard 12-minute|one task per turn|section 13 pending' "$readme"; then
  echo "README still documents retired runtime behavior" >&2
  exit 1
fi

example_root="$repo_root/example/ai-workflow"
example_files="
$example_root/AGENTS.md
$example_root/work/B001-example-feature/FEATURE.md
$example_root/work/B001-example-feature/IMPLEMENTATION.md
$example_root/work/B001-example-feature/PROGRESS.md
$example_root/work/B001-example-feature/PROGRESS_STATE.md
"
blueprint_digest=$(shasum -a 256 "$blueprint" | awk '{print $1}')
for example_file in $example_files; do
  if ! grep -Fq -- 'Workflow schema: `2`' "$example_file" &&
     ! grep -Fq -- 'Workflow schema: 2' "$example_file"; then
    echo "example lacks workflow schema: $example_file" >&2
    exit 1
  fi
  if ! grep -Fq -- "$blueprint_digest" "$example_file"; then
    echo "example has stale blueprint digest: $example_file" >&2
    exit 1
  fi
done

if ! grep -Fq -- 'continuation_mode: batch_to_verified_outcome' \
  "$example_root/work/B001-example-feature/IMPLEMENTATION.md"; then
  echo "example implementation lacks v2 continuation policy" >&2
  exit 1
fi

check_line_budget() {
  file=$1
  max_lines=$2
  actual=$(wc -l < "$file" | tr -d ' ')
  if [ "$actual" -gt "$max_lines" ]; then
    echo "example exceeds line budget ($actual > $max_lines): $file" >&2
    exit 1
  fi
}

check_line_budget "$example_root/work/B001-example-feature/FEATURE.md" 220
check_line_budget "$example_root/work/B001-example-feature/IMPLEMENTATION.md" 360
check_line_budget "$example_root/work/B001-example-feature/PROGRESS_STATE.md" 70
check_line_budget "$example_root/work/B001-example-feature/PROGRESS.md" 300

if [ ! -x "$repo_root/bin/feature-execution" ]; then
  echo "reference harness entry point is not executable" >&2
  exit 1
fi

"$repo_root/bin/feature-execution" doctor "$example_root" \
  --blueprint "$blueprint" >/dev/null
python3 -m json.tool "$repo_root/schemas/agent_turn.schema.json" >/dev/null
python3 -m json.tool "$repo_root/eval/cases/v1/catalog.json" >/dev/null

echo "v2 outcome-driven runtime contract present"
