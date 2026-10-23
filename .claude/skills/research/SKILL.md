---
name: research
description: "Investigate a question against primary sources and return a cited answer: why a piece of code has its shape, how a subsystem works, or what the docs and API facts actually are. Use when asked to research a topic, explain a subsystem, find out why something is the way it is, gather docs or API facts, or delegate the reading legwork while you keep working."
upstream:
  - repo: pstack
    path: pstack/skills/why/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/why/references/epistemics.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/why/references/investigator-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/why/references/source-playbook.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/why/references/synthesizer-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/why/references/sources
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/how/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/how/references/explorer-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/how/references/explainer-prompt.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/engineering/research/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
---

# research

Investigate a question against **primary sources** and answer it with citations. Never a secondary write-up of the source that owns the claim: official docs, the source code itself, specs, first-party APIs, the commit and review that made the change, the ticket that forced it, the session that decided it. Follow every claim back to the source that owns it.

Two questions arrive here, and they take the same shape:

- **Why** does this exist in this form? Motivation, rationale, trade-offs, an external constraint, a regression, a postmortem, a data-backed threshold. The `why` half.
- **How** does this work? A code walkthrough, a mental model of a subsystem before changing it, a placement or ownership question. The `how` half.

Answer the why with history and the how with the code, and never mix the two: code shows what a thing does, not why it exists.

**You do the reading through explorers.** Spawn them and keep working while they read. Each one owns one evidence category and returns gathered evidence, not a conclusion. A synthesizer weighs what comes back; do not pre-judge it.

## Operating posture

Operate as a **careful, cautious and precise investigator**. Be honest about what you know versus what you are inferring. Read `references/epistemics.md` for the full confidence framework and the phrasing guide; the synthesizer must follow it too.

The short version, which the answer you produce is judged against:

- Every claim sits in one tier: **Direct**, **Supported**, **Inferred**, **Speculative**, **Unknown**. The tier picks the section and the phrasing.
- A Direct or Supported claim carries a citation immediately beside it: a commit, a pull-request number, a ticket ref, a file and line, a document, a session id with ordinals.
- An Inferred claim is hedged and shows the chain. A Speculative one is marked as a guess.
- "Unknown" is a real answer. Name what was searched.
- A hypothesis embedded in the question ("I assume it's for performance?") is one candidate among others, never a conclusion to validate.

Read `references/epistemics.md` before writing any answer that will be acted on.

## Step 1. Understand the target and the question

The **target** is usually a chunk of code, a pattern, a feature, a named decision or a subsystem. The **question** is usually a rationale, a trade-off, a motivating edge case, an external constraint, dead code, a broad history sweep, or a walkthrough before a change.

If the target is vague ("why do we do it this way?" with no clear referent), make your best guess from the conversation (open files, recent edits, what was just discussed). Say your interpretation in one line so the reader can redirect, then proceed.

A question with a short answer, fully answerable from one or two files, is answered in chat. Everything else writes a file.

## Step 2. Establish the code anchor

Before spawning anyone, build the seed context inline: file paths and line ranges, key symbols, the last few commits that touched the target, pull-request numbers from merge commits, and any linked ticket refs.

```bash
git blame -L <start>,<end> <file>        # last touch per line
git log --follow -p -- <file>            # full history through renames
git log --oneline -20 -- <file>          # recent commits, PR numbers visible
git log -1 --format=%B <commit>          # PR number from the subject
```

Then pull the body and discussion of any substantive commit's pull request: `gh pr view <number> --json title,body,author,createdAt,mergedAt,labels,closingIssuesReferences,comments,reviews`. Ticket refs come from the commit bodies and the branch names; read them through the commands `.agents/tracker.md` names.

This anchor goes to every investigator and to the synthesizer. For a how-question it is the files and entry points instead of the history.

## Step 3. Discover the sources

**Default to the full parallel investigation.** The goal is a complete coverage map, not a minimal one. Document the null; do not skip the search.

List what is reachable in this session, and map each connector to one evidence category:

1. **Source control history**: git and `gh`. Always available, always searched.
2. **Issue and ticket tracker**: kata or GitHub Issues, per the repo's `.agents/tracker.md`.
3. **Agent history**: AgentsView, when the question is about a decision made while working rather than one written down.
4. **Long-form documents**: Notion.
5. **Real-time team chat**: Slack.
6. **Meeting notes**: Granola.
7. **Infrastructure observability**: Datadog.
8. **Error and exception tracking**: Sentry.

Source control is the only guaranteed one; the rest are searched when their connector is reachable. A connector that could fit two categories goes in the one holding its primary evidence, and ambiguous cases are recorded in the coverage map.

Pick each source's playbook from `references/source-playbook.md`; that file also says which upstream playbooks have no counterpart here and how to adapt one.

### When to skip an investigator

Only with an **explicit, written justification** in the final Sources Consulted. Two valid reasons:

- **No connector is available for that category** in this environment. Flag it as a gap, not a choice: "Real-time team chat skipped. No Slack connector was reachable, so the conversational record was not searchable."
- **The source is provably irrelevant**, not just probably. A high bar: "Error and exception tracking skipped. The target is a build-time script with no runtime code path."

If the scope assessment suggests a single-commit trivial target whose pull-request description already holds the complete answer, answer inline **only after** confirming all the reachable category searches would be redundant. Say so. This should be rare.

## Step 4. Spawn the investigators

Spawn one investigator per reachable category, all at once, through `herdr`. Each one owns exactly one connector; never ask one explorer to cover two.

- Take the pane from `herdr`'s model table: the `cheap` role for reading, searching and quoting, and the `builder` role when the work needs tools the cheap role cannot hold (an MCP connector's write-capable session, a long tool-heavy crawl). Roles come from `~/.config/agents/models.toml`; never name a model id.
- Every investigator is read-only in what it writes: no files, no commits, no writes to a connector. A pane with connector access still writes nothing.
- The prompt is `references/investigator-prompt.md` filled in, plus the category's playbook from `references/sources/`, plus `references/sources/incident-postmortem.md` **if the target code looks defensive** (null checks, retry logic, timeout handling, rate limiting, feature flags, egress guards, OOM handlers), plus the code anchor and the original question.
- Each returns the investigator output shape in that prompt: what it searched, direct evidence, indirect evidence, contradictions, gaps, further leads. Evidence only, no verdict.

The roster, one per category, and what each is best at:

1. **Source control** (git history, `gh` pull requests, code comments, tests): *implementation-time rationale captured during review*. Always spawn.
2. **The tracker** (kata or GitHub Issues, per `.agents/tracker.md`): *the product or business forcing function*. Strongest when the why is external to engineering.
3. **Agent history** (AgentsView): *the decision taken while working*, the one nobody wrote into a document afterwards.
4. **Long-form documents** (Notion): *long-form design rationale*, written out before it became code.
5. **Real-time team chat** (Slack): *deliberation that never reached a doc*. Especially important when the source control, ticket and document trail is thin.
6. **Meeting notes** (Granola): *the meeting where an option was ruled out.* Usually second order: better than inference, weaker than a spec.
7. **Infrastructure observability** (Datadog): *infrastructure and runtime reality that motivated the code*. Strongest when the target reacts to an infra signal (timeouts, retries, rate limits, circuit breakers).
8. **Error and exception tracking** (Sentry): *the exceptions and error trajectories that motivated defensive or corrective code*. Strongest for catch blocks, null guards, type checks and retries.

A category returning nothing is a finding, and is written up as one: "no evidence in the ticket tracker" is different from "the ticket tracker was not searched".

## Step 5. Synthesize

One synthesizer, in a Herdr pane, taking the session's own role: the weighing and the prose are judgment, so it runs on the same role as the coordinator rather than an explorer's.

It gets the investigator findings (including nulls and justified skips), the code anchor, the original question, `references/epistemics.md` and `references/synthesizer-prompt.md`.

Its output is the structure in `references/synthesizer-prompt.md`: The Question, The Code in Question, What We Found, What We Can Reasonably Infer, Competing Hypotheses, What We Don't Know, Sources Consulted, Confidence Summary. Keep the confidence separation intact, and keep Sources Consulted as one line per category, including the ones that returned nothing or were skipped, with the reason.

After Sources Consulted, if the question is a precursor to changing this code, convert the lineage findings into a Preserve / Change / Avoid / Risk constraint set for planning the change. That set is what `to-spec` and `arch` want.

## Step 6. Present

Present the synthesizer's output. Light edits for clarity or for context from the conversation are fine; **do not rewrite the confidence language**. Then say where the file is.

## Output

- **A file** when the answer is long enough to be read twice, cited later, or handed to another skill: `.scratch/research/<YYYY-MM-DD>-<slug>.md` at the root of the repo the question belongs to, gitignored there. Cite each claim's source inline. Write one file per question, never a directory of fragments.
- **Chat** when the answer is a short read: name the tiers inline, cite the session, commit or file, and stop. Offer the file when the answer went past a screen.
- A repo with its own convention for such notes wins over the default path; say where you put the file when you follow it.

## How-mode: how does X work

Answers of the form "how does this work", a walkthrough before changing something, and placement or ownership questions ("where should this live", "which package owns this", "is this the right layer"). The answer is an architectural explanation at the level of a senior engineer onboarding onto the subsystem: enough to build a working mental model, not so much that it reads like annotated source code.

### 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore; the reader can redirect.

- **Simple** (one module, a small utility, a narrow question such as "how does function X work"): no explorers. One explainer explores and explains in a single pass, from `references/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning several files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

### 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers at once through `herdr`, each with `references/explorer-prompt.md` and its angle filled in, on the `cheap` role (or `builder` where the angle needs connector tools). Read-only.

### 3. Synthesize (complex only)

Once all explorers have returned, one explainer takes `references/explainer-prompt.md` with every explorer's findings filled in.

### 4. Present

Present the explainer's output, with light edits. Do not substantially rewrite it.

The explanation uses the sections in `references/explainer-prompt.md`, dropping the ones that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.

A how-answer that also needed history ("it is layered this way because the first version shared a database") runs the why investigation for that part rather than guessing at it.

## Delegating the reading

The whole point of the background agent is that you keep working while it reads. Two consequences:

- State what you are doing while the explorers run, and leave them to it. Do not poll a pane to check on it; `herdr` sends the done notice.
- Do not start re-reading the same sources yourself. If a finding looks thin, send the explorer a narrower question.

## Common failure modes

- **Recency bias.** Assuming the most recent commit is authoritative. The current shape is often the accretion of many earlier decisions. Trace back.
- **Mechanics read as motivation.** A commit changing a limit from 50 to 100 shows the change, not why. The reason lives in the message, the description, the review or the ticket.
- **Ancestry for an answer.** A confident story assembled from code style. Say what the evidence supports and no more.
- **A missing gap section.** If nothing was unknown, either the evidence was unusually complete or something is being swept under the rug. Look again before concluding the first.
- **A skipped source with no line in Sources Consulted.** Every category the roster names gets a line, whether searched or not.

## Rationalizations to refuse

| Rationalization | Reality |
| --- | --- |
| "The question is small, so I'll skip the explorers." | Small questions are answered inline from the code, which is fine. Deciding *why* without reading the history is not. |
| "I know why this is here." | Then cite it. If it cannot be cited, it is Inferred at best. |
| "The reader wants a confident answer." | The value of the answer is its honesty. A reader takes it to the original author, and should know what is known, what is inferred and what is missing. |
| "One source is enough." | One source is a pass when it is the source that owns the claim. It is a miss when another category would have answered it and nobody looked. |
| "This PR says it, so it's the reason." | The description is one account. The ticket, the review and the chat may say something else. Surface the contradiction. |
| "There's nothing in the tracker, so there's no reason." | Absence of evidence in one category is a gap, not a null result. Search a second one before saying the reason is unrecorded. |
