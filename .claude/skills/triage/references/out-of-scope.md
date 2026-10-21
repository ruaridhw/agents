# `.out-of-scope/`

Persistent record of rejected enhancement requests: why, so the reasoning survives the closed issue, and so a repeat request surfaces the earlier decision instead of re-arguing it.

- One file per concept (`.out-of-scope/dark-mode.md`), not per issue. Kebab-case name someone would recognise.
- Written as a short design note: what is not supported, why (scope, a technical constraint, a strategic choice; durable reasons, not "too busy"), and `## Prior requests` listing every issue that asked.
- Read every file during triage step 1. Match by concept, not keyword. On a match, surface it: "This resembles `.out-of-scope/<x>.md`, rejected because <reason>. Still the same call?" Confirm → add the issue to Prior requests and close. Reconsider → update or delete the file and triage normally. Distinct → triage normally.
- Write only for rejected enhancements (issues or PRs). Never for "already implemented": that would poison the dedupe with false rejections; point to where it lives instead.
