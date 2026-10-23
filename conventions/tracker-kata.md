# Tracker profile: kata

`setup-project` copies this profile into a repo's `.agents/tracker.md` and fills the
Project block. Skills read `.agents/tracker.md`, never this file.

## Project

- Project: `<kata project name>` (pass `--project` only when the workspace is not bound)
- Process label prefix: `<process:slug or none>`
- Extra labels this repo uses: `<list or none>`

## Refs

A ticket ref is a kata short id (`abc4`) or a qualified one (`kata#abc4`). Show a
ticket with `kata show <ref> --agent`; search with `kata search "<words>" --agent`.

## Creating

Search first; never create a duplicate. Every create carries an idempotency key.

```bash
kata create "<imperative title>" --body-file <path> \
  --parent <spec-ref> [--blocked-by <ref>]... \
  --label <kind> [--label <process label>] --priority 1|2|3 \
  --idempotency-key <spec-ref>/<slug> --agent
```

- Kinds: `spec` (the spec issue), `chore` (work with no failure behind it), `fix`
  (a finding with evidence), `client-blocker` (needs the other side to act).
- Priority: `1` high, `2` medium, `3` low. `0` and `4` are not used.
- `--parent` is containment only and does not gate readiness. `--blocked-by` is a
  real prerequisite: the blocker must finish first. `kata ready` lists open tickets
  with no open blocker.
- Never `kata delete` or `kata purge`.

## States

`open → merged → done`, or `open → wontfix`.

| State | How | Meaning |
| --- | --- | --- |
| `open` | default | not landed on the default branch |
| `merged` | `kata label add <ref> merged` + comment with PR and merge sha | landed; not yet proved |
| `done` | `kata close <ref> --done --message "<what was observed>" --commit <sha> --pr <url> --test "<cmd>"` | the ticket's Done-when was observed (see `.agents/prove-landed.md`) |
| `wontfix` | `kata close <ref> --wontfix --message "<rationale>"` | terminal; only with Ruaridh's yes |

`merged` is mandatory: no ticket goes from `open` straight to `done`. Closing asserts
the work is complete, so close as soon as the Done-when is observed, one ticket at a
time, never in a batch.

Stopping short is not a close: `kata label add <ref> needs-review` plus a comment saying
what was attempted and what remains.

When proof must wait for a real case, create a related (not child) ticket
`Verify <observable> live` with `--related <ref> --label needs-live-verification`,
then `kata schedule` it.

## Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`. One at a time;
replace, do not stack. `ready-for-human` also gets `kata notify <ref>`.

## Comments

Comment when a material finding or decision occurs (evidence, consequence, next
action), and before a PR or a handoff. Not a transcript of routine commands.

## Work signals

`kata meta set <ref> work.branch <branch>` when a branch is created for the ticket;
`work.attention <one line>` when it needs a human. Clear them when the ticket closes.
