# Descriptive commit message prompt

Use this prompt when you want an AI assistant to write a concise commit message for local changes.

Implementation commits should be scoped to one verified `B###/T###` task from a batch `IMPLEMENTATION.md`.

Do not use `PRODUCT_BACKLOG.md` or `WORK_INDEX.md` as the commit unit for execution work. Those files may be included in a task commit only when their status/history updates belong to the verified task.

## Prompt

````md
Write a descriptive commit message for my current local changes.

First inspect the diff enough to understand:

- what changed
- why the change was needed
- why this implementation approach was chosen over obvious alternatives
- which `B###/T###` task from `IMPLEMENTATION.md` this commit completes, if this is execution work

Use this format:

```text
<type>: <short summary>

<sentences explaining what changed, why, and the reasoning behind the chosen implementation.>
```

Rules:

- Keep it concise and practical.
- Use past tense or present tense consistently.
- Prefer `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, or `perf` as the type.
- Do not list files mechanically.
- Do not mention irrelevant implementation details.
- Do not invent motivation that is not visible from the diff or provided context.
- If the reasoning is unclear, say what assumption the message is based on.
````
