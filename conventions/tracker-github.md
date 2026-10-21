# Tracker profile: GitHub Issues

`setup-project` copies this profile into a repo's `.agents/tracker.md` and fills the
Project block. Skills read `.agents/tracker.md`, never this file.

## Project

- Repository: `<owner/repo>`
- Extra labels this repo uses: `<list or none>`

## Refs

A ticket ref is `#N` in this repo or `owner/repo#N`. Show with
`gh issue view N --comments`; search with `gh issue list --search "<words>" --state all`.

## Creating

Search open and closed issues first; never create a duplicate. GitHub has no
idempotency header, so the key goes in the body as a last line
`<!-- key: <spec-ref>/<slug> -->` and is searched before every create
(`gh issue list --search "<spec-ref>/<slug> in:body" --state all`).

```bash
gh issue create --title "<imperative title>" --body-file <path> \
  --label <kind> --label priority:<1|2|3>
```

Then attach it under the spec issue as a sub-issue, and add real prerequisites as
blocked-by edges:

```bash
child_id=$(gh api repos/<owner>/<repo>/issues/<N> --jq .id)
gh api -X POST repos/<owner>/<repo>/issues/<spec-N>/sub_issues -F sub_issue_id="$child_id"
gh api -X POST repos/<owner>/<repo>/issues/<N>/dependencies/blocked_by -F issue_id=<blocker-id>
```

If the dependencies endpoint is unavailable, write `## Blocked by` with the refs in
the body instead.

- Kinds: `spec`, `chore`, `fix`. Priority labels `priority:1..3`.

## States

`open → merged → done`, or `open → wontfix`.

| State | How |
| --- | --- |
| `open` | default |
| `merged` | label `merged` + comment with the PR and merge sha; keep the issue open (do not use `Closes #N` in PR bodies) |
| `done` | `gh issue close N --reason completed --comment "<what was observed>"` |
| `wontfix` | `gh issue close N --reason "not planned" --comment "<rationale>"`, only with Ruaridh's yes |

Stopping short: label `needs-review` and a comment with what remains.

## Triage labels

`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`. One at a time.
`ready-for-human` also gets an `@`-mention of the owner in a comment.

## Work signals

A comment `work.branch: <branch>` when a branch is created; label `needs-attention`
plus a comment when a human is needed.
