# Turning working conventions into a skill

A guided flow for turning Ruaridh's working conventions into a skill that agents follow. The output is normally a `-mode` skill tailored to him, or a section of `ruaridh-mode`. Because a curated skill is involved, the writing itself goes through `write-skill` (an ad-hoc skill) or `update-skills` (a curated one); this reference sequences the flow and keeps the guardrails.

## Flow

### 0. Check for an existing skill

Look for a `*-mode` skill (or the section of `ruaridh-mode`) that already covers the conventions, in the repo's `.claude/skills/` and in `~/.claude/skills/`. If one exists, confirm the intent (unless it was already said):

- Update the existing skill (the default for a repeat run)
- Start fresh (rare; ask why first)

An update changes the rest of the flow:

- Step 1 mines only the history since the skill was last edited (`git log -1 --format=%cI <path>`).
- Step 2 asks what has changed or is missing, not what to capture from zero.
- Step 4 edits the existing file in place. Preserve the sections that have not been contradicted, revise the ones with new evidence, and add sections only for genuinely new rules.

### 1. Mine the history

Mine AgentsView, scoped to the workspace the conventions are about, never across every project. Survey recent sessions for recurring patterns. For a big window, run parallel explorers in Herdr panes on the `cheap` role over slices of history (for example the last two to four weeks, split into three slices).

Each slice's explorer reads only the sessions in its slice and returns a short structured list of patterns with evidence pointers. The signals worth hunting:

- Response preferences (length, tone, format, "dumb it down" corrections)
- Delegation habits (workers, roles, specialised workflows, parallelism)
- Verification posture (what "done" means, unit tests versus a live repro, reviewers)
- Code and prose discipline (style, the rules cited, lint and format tools)
- Process conventions (worktrees, commits, pull requests, review and merge tooling)
- Meta preferences (fixing a skill mid-task, proposing a new one)

Cross-check across slices before elevating a signal. A pattern seen in two or more slices is high confidence. A lone signal is weak and usually gets dropped.

### 2. Ask directly

Mining misses intent that has not come up yet. Ask Ruaridh, in one or two questions with a handful of options each, then one free-form question for what the options missed. Away from chat, ask per the Inbox convention.

Don't dump twenty questions.

### 3. Cluster the findings

Group the combined signals into sections, using only the ones that apply:

- **Response style**: length, tone, format.
- **Autonomy**: how much to do without asking, when to use a connector.
- **Understand first**: which skills to reach for when scoping or investigating.
- **Workers**: default, parallelism, role-to-task, specialised workflows.
- **Prose and code discipline**: rules cited, lint tools, style guides.
- **Review and verify**: repro posture, verification skills, live-testing tools.
- **Process**: worktrees, commits, pull requests, review and merge tooling.
- **Skills**: authoring habits, fix-the-skill-first, proposing new ones.

`ruaridh-mode` shows the granularity. Read it for shape; its content is not the same as the conventions being captured.

### 4. Draft the skill

Use `write-skill` to author an ad-hoc skill, or `update-skills` for a curated one. Placement and frontmatter follow that skill's rules.

- Trigger the description on the name and the mode, not on generic keywords like "write code".
- `disable-model-invocation: true` only where the convention is a sub-skill that another skill calls; a mode skill Ruaridh invokes by name stays model-invocable.

### 5. Iterate on the prose

Apply the writing rules of `write-skill` and, where the output is client-facing, the unslop pass in `technical-writing`, to every line. Show the draft and take feedback. Expect several iterations, and cut hard: a mode skill is not a manual.

### 6. Land it

Work in a worktree on a branch, commit, and open a pull request with `pr`. Do not push to the default branch directly.

## Guardrails

- **Don't overfit to one session.** A preference stated once and contradicted another time is noise. Require multiple instances before codifying it.
- **Don't be clever.** Restating another skill's contents, inventing metaphors, or writing "poetic" prose for an agent reader is cost without benefit. Keep it operational.
- **Reference, don't inline.** Another skill the conventions rely on appears as a path reference, not a pasted excerpt.
- **Keep sections minimal.** Add a section only for a specific, non-default rule. "Communicate clearly" is not a section; "short paragraphs, tables when comparing options, bullets only when items are genuinely parallel" is.
- **Name conventions generically.** Use "Ruaridh" or "he" in the environment's prose and "the user" in anything generic, never a second name.
- **Don't force symmetry.** If there is no process rule worth writing down, skip the Process section entirely.

## Evaluation

A mode skill is subjective output; a benchmark loop is not useful here. Vibe-check: does it read like him, and did it miss anything? Then ship. Run a description-optimisation loop only if the trigger accuracy turns out to be a problem in practice.

## When not to use

- A task-specific skill rather than working conventions: `write-skill` alone, no mining required.
- One narrow workflow (for example "how I write commit messages"): a regular skill, not a mode skill.
