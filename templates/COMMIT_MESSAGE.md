# Commit message prompt

Goal: Write a concise commit message grounded in the current diff and selected
verified task.

Inspect enough evidence to identify what changed, why it was needed, the reason
for the chosen approach, and the relevant `B###/T###` task.

Output:

```text
<type>: <short summary>

<what changed, why, and the decision rationale>
```

Use one of `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, or `perf` when it
fits. Do not list files mechanically, add unsupported motivation, or include
irrelevant detail. State a visible assumption when the rationale is uncertain.
