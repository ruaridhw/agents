# Skills landscape

One opinionated set of skills, curated from three upstream paradigms (mattpocock/skills, obra/superpowers, cursor/plugins `pstack`), an employer operator kit (the "kit", private, read through a local upstream entry) and this repo's own earlier skills (the `self` upstream).

Every curated skill lives in `.claude/skills/<name>/` and carries `upstream:` stamps in its frontmatter: one entry per feed, naming the upstream (a key of `UPSTREAMS.json`), the path in it and the sha the skill was written against. `bin/skill-upstream status` shows how far each feed has moved since; `bin/skill-upstream diff <skill>` shows the change. This file is the record `update-skills` reads when it decides what to take from that change: per skill, the opinion, and per feed what was taken and what was dropped. Nothing here is loaded into a session.

## Conventions

- **Frontmatter**: `name` (equal to the directory), `description` (when to use it, in the words a caller would say), `upstream:` stamps, and `disable-model-invocation: true` only on sub-skills that another skill calls. Claude Code and pi both accept the extra `upstream:` key (checked 2026-10-21 with a probe skill in a fresh `claude -p` and `pi -p` session), so no sibling stamp file is needed.
- **Interim write-skill rules** (until `write-skill` is curated in wave 2): about 150 lines, references split into `references/`; imperative prose; the case first, then the steps; no history or "we used to"; no client, employer, host or personal identifiers (the repo is public; `bin/check-public` enforces a denylist kept outside it); repo specifics go in `.agents/*.md` convention files, never in a skill; models are named by role (`~/.config/agents/models.toml`), never inline.
- **Hook points**: general skills read `.agents/tracker.md`, `build-loop.md`, `prove-landed.md`, `deploy.md`, `design-review.md`, `domain.md` in the repo they run in. A missing file means the skill's default. Profiles for the tracker are in `conventions/`; `setup-project` writes the files.
- **Linking**: `linked-skills.txt` lists the curated names linked into `~/.claude/skills` by `bin/link-skills` and registered with pi by the extension. Names that collide with a plugin skill (`grill`, `to-spec`, `to-tickets`, `triage`, `implement`, `pr`, `handoff`) are written but not linked until the plugins are disabled at wave 3; `ruaridh-mode` names their paths so they are reachable meanwhile.

## Whole-landscape dispositions

- **Curated (wave 1)**: `ruaridh-mode`, `clarify`, `herdr`, `grill`, `to-spec`, `spec-review`, `to-tickets`, `triage`, `to-plan`, `implement`, `pr`, `handoff`, `setup-project`, `update-skills`, `rare-skills`.
- **Curated (wave 2, not yet written)**: `write-skill`, `tdd`, `debug`, `verify`, `review`, `ship`, `worktree`, `prototype`, `domain`, `research`, `recall`, `retro`, `technical-writing`, `teach`, `wizard`, `questionnaire`, `bro`, `arch`. `principles` waits for its own grilling.
- **Kept as shipped**: the employer's operator skills and kit (changed only through the kit's feedback channel); the Plannotator family; Anthropic artifact, dataviz and document skills; the effective-html family; browser; own scheduled-job skills (`morning`, `granola-notion`, `notion-todoist-tasks`).
- **Rare** (moved to `~/.agents/rare/`, reached through `rare-skills`): AWS, Cloudflare and other service skills.
- **Dropped**: mattpocock loop-me, caveman, request-refactor-plan, scaffold-exercises, migrate-to-shoehorn, setup-pre-commit, git-guardrails-claude-code, claude-handoff, setup-ts-deep-modules, writing-beats, writing-shape, writing-fragments, edit-article, and the loose find-skills, claude-code-peer-messaging, obsidian-vault; superpowers diagnosing-superpowers; pstack setup-pstack, poteto-agent, make-bot-ui, visual-parity, autopilot-full, autopilot-stack, eval, hillclimb, create/maintain-verification-skill, typescript-best-practices and the automations.
- **Retired own skills** (pointer files for one release): `herdr-agent-handoff` → `herdr` + `implement` + `handoff`; `kata-triage-artifact` → `triage`; `writing-build-spec` → `to-spec`; `adversarial-spec-review` → `spec-review`; `orchestrating-reviewed-build` → `implement`; `find-sibling-agents` → `herdr`.

## ruaridh-mode

**Opinion.** The one entry point, always loaded: intake (classify what arrived and say so), the chain with its gates and build loops, and twelve general non-negotiables. Three bodies: full (`SKILL.md`, interactive top-level sessions), slim (`references/slim.md`, spawned workers) and coordinator (`references/coordinator.md`, sessions that own a long-running goal). Tool and machine rules sit in `references/tooling.md`, with host-specific values in a private `~/.config/agents/tooling.local.md`. Installed as the Claude SessionStart hook (`hooks/session-start`) and the pi extension (`.pi/extensions/ruaridh-mode.ts`).

Decisions made while building:

- **Body selection.** A hook cannot see the first prompt, and `HERDR_ENV=1` is set in every Herdr pane including interactive ones, so the spawner sets `RUARIDH_MODE=worker` on the pane (`herdr tab create --env` / `herdr pane split --env`) and the hook or extension injects the slim body. The full body also carries a `<WORKER-STOP>` block keyed on a `ruaridh-mode: worker` brief line, for workers spawned without the env marker (superpowers' `<SUBAGENT-STOP>` pattern).
- **Coordinator body** is a reference the full body sends the session to, not a third injected body: nothing in the environment says a session owns a long-running goal.
- **Not-yet-curated steps** (`debug`, `tdd`, `review`, `verify`, `ship`, `research`) are mapped to the plugin skills that cover them until wave 2, so the chain is usable now.
- **Colliding names** are reached by path from the bootstrap header's skills directory, so `to-spec` means the curated skill even while the plugin's `to-spec` is installed.

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `using-superpowers` | Session-start injection; the red-flag table form; the subagent-stop pattern (as `<WORKER-STOP>`); "skill check before any action" as the intake-first rule | The 1%-chance invocation pressure and "you MUST" register; per-harness tool reference files; brainstorming as the forced first step |
| superpowers `.pi/extensions/superpowers.ts` | The extension shape exactly: `resources_discover`, re-arm on `session_start` and `session_compact`, disarm on `agent_end`, marker check, insertion after compaction summaries, tool mapping | `pi.skills` in `package.json` (the extension registers only `linked-skills.txt` names instead) |
| pstack `poteto-mode` | Routing by classifying the task into a playbook; a non-negotiables section; autonomy split (reversible proceeds, irreversible pauses); "no is an acceptable answer"; ask only what no experiment settles (red flag) | Cursor `Task` defaults and model slugs; principle citations (principles deferred); playbooks-inside-the-router (each is its own skill here); todolist-copy ritual; deslop / control-ui hooks |
| pstack `poteto-help` | The idea of a plain index of what exists (the curated list and the fallback table) | The full help catalogue |
| mattpocock `ask-matt` | Main flow plus on-ramps as the chain shape; "triage only issues you didn't create"; skip planning when tickets are small | Context-hygiene and phase-boundary advice (`handoff` owns pausing); `grill-with-docs` glossary statefulness (moves to `domain`, wave 2) |
| mattpocock `chief-of-staff` | Coordinator stance: DRI, two tracks (tactical, strategic), all work in subagents, sparse communication through context pointers, propose schedules, relentless environment fixes | The wiki-as-memory (the tracker and `.scratch/` are the record; history comes from AgentsView) |
| own rule sources (home and project AGENTS.md files, the constitution, general memories) | The twelve non-negotiables; `tooling.md` (git, stacked PRs, Herdr, pi, Plannotator, AgentsView) | Host names, collector URLs, token paths, tailnet recipes (moved to the private local tooling file) |

## clarify

**Opinion.** One round, at most five questions that would each change what gets built, each with a recommended answer worded so "yes" accepts it. A one-sentence restatement of the goal first. No tree, no sizing, no playback: when the task needs those it is a `grill`. Runs by default before non-trivial work that did not come through `grill`; Inbox question blocks when Ruaridh is away.

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `brainstorming` | "What do you actually know?" first check (quick task → just do it); single-sentence questions with no example lists; look before asking (recon) | The conversation loop, open describing questions, playback chunks, sizing, the written design, the visual companion and the hard gate (all `grill` or `to-spec`) |
| pstack `in-your-own-words` | Restate the user's goal and problem in your own words before acting | Restating as the whole skill |
| mattpocock `grilling` | Recommended answer per question; "yes accepts the recommendation" wording; facts are the agent's job | Rounds and the frontier (`grill`) |

## grill

**Opinion.** mattpocock's rounds-with-a-frontier interview, with superpowers' ground to cover, playback with guesses marked, and the size call at the end; ends by naming the route, never by building. Visual companion offered once, at the start, when seeing would help. Usable standalone. Inbox question blocks per round when Ruaridh is away.

Decision made while building: the visual companion is single-file HTML mocks in `.scratch/mocks/` opened with `plannotator annotate`, not superpowers' companion server, so it survives the plugin being disabled and the annotations come back as answers.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `grilling` | Design tree, frontier, whole-frontier rounds, numbered questions with a recommended answer, "yes accepts", facts are the agent's job via non-blocking lookups, done when the frontier is empty and confirmed | Its exact emoji format (kept, slightly condensed) |
| mattpocock `grill-me`, `grill-with-docs` | One entry point instead of two wrappers | The glossary and ADR side (`domain`, wave 2, called when a term is contested) |
| superpowers `brainstorming` | Ground to cover (goals / non-goals / anti-goals, prior art, how-it-gets-made ownership); guess-to-correct questions; spike instead of asking, spikes stay throwaway; playback with guesses marked; the size table; several projects → one at a time; red flags | One question per message; the written design and builder check (`to-spec`); the hard gate wording; `docs/superpowers/specs` location |
| superpowers `brainstorming/visual-companion.md` | When to offer (its own message, once, just in time) and what belongs visually | The local companion server and its scripts |
| pstack `sharpen` | Ask what he is really after and whether the task is over- or under-specified before shaping it | Silent self-framing with no interview |

## to-spec

**Opinion.** No interview. Reconcile the sources, write `.scratch/specs/<date>-<slug>.md` in the wave 0 shape, builder check by a fresh Herdr worker (answered / my call / his; only "his" asked, once), Plannotator gate, offer `spec-review`, then publish the spec issue from the possibly amended file and hand to `to-tickets`. Acceptance is decided here. Replaces own `writing-build-spec`, which is now a pointer file for one release.

Decision made while building: the design-review gate stays an open item (Ruaridh's choice); `to-spec` fills the Design section and follows `.agents/design-review.md` where a repo has one, otherwise flags the Design section in the gate message.

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `brainstorming` | Written-design contents (intent, goals / non-goals / anti-goals, constraints, decided how, left to the builder); the three-pile builder check and one round of questions; "tell him which calls were yours" | Committing specs under `docs/superpowers/specs`; the conversation phase (`grill`) |
| superpowers `brainstorming/builder-check-prompt.md` | The brief nearly verbatim, as `references/builder-check.md`, run in a Herdr pane | Agent-tool dispatch |
| self `writing-build-spec` | Source reconciliation with dispositions; correction-beats-note authority order with superseded decisions recorded; decided vs undecided with owned open items; per-workstream case + expected result, owned proof gaps; tracker dispositions recorded not mutated; the pre-handoff audit | Its free-form layout (replaced by the template); the explicit pointer to the old review skill |
| mattpocock `to-spec` | No interview, synthesis only; highest-seam testing decision; prototype-snippet exception; publish to the tracker | User-story lists; `ready-for-agent` on the spec; Problem/Solution headings |

## spec-review

**Opinion.** The spec-reviewer role (Fable by default) in a sibling Herdr pane, read-only by class with one write destination: a sibling review file in `.scratch/specs/`. The author answers each question from the decision history (amend, reject with source, escalate); escalations become Open items; passes repeat until every disposition is inspected. The spec issue is created after this step, from the amended file. Replaces own `adversarial-spec-review` (pointer file for one release).

| Feed | Taken | Dropped |
| --- | --- | --- |
| self `adversarial-spec-review` | Nearly all of it: authority order, access by class not allowlist, evidence-cited questions that could change a build choice, grouped defects, amend / reject / escalate, no round limit, complete vs incomplete verdict | The generic "independent agent" fallback (Herdr is the mechanism; a self-review is labelled); review-folder wording (one sibling file) |

## to-tickets

**Opinion.** Tracer-bullet tickets sized to one session, `## Done when` copied from the spec's Acceptance (a missing case goes back onto the spec issue, never invented), parent = the spec issue, `blocked-by` only for real prerequisites, labels and priority from `.agents/tracker.md`, idempotency key `<spec-ref>/<slug>`. Writes the wave file, hands it to `triage` for the gate, then publishes in dependency order (kata `--parent`, GitHub sub-issues). Re-running is a no-op. Also turns evidenced bugs into fix tickets.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `to-tickets` | Vertical tracer-bullet slices; prefactor first; expand–migrate–contract for wide refactors; blocking edges; publish blockers first so edges reference real ids; sub-issues of the parent (the 2026-10-06 change); `ready-for-agent`; no file paths; never close the parent | The in-chat "quiz the user" loop (replaced by the triage gate); local `.scratch/<feature>/issues/` files; GitLab/Linear branches |
| kit `new-ticket` | Search first, stable idempotency key, `## What / ## Why now / ## Done when`, priority 1–3, Done-when as one observable not a design, stopping short = `needs-review` + comment | Employer-specific labels and run metadata; the close-at-merge rule (replaced by `open → merged → done`, see the kit feedback report) |
| kit `new-fix` | Fix shape (Symptom / Evidence verbatim / Why it happens / Fix); evidence required for a fix; name every observed case; don't generalise past the evidence; tell lookalike symptoms apart | Run-id specifics and `source_runs` metadata; client-blocker kind (kept only in the kata profile) |

## triage

**Opinion.** Two inputs. Inbound issues: mattpocock's two categories and five states, verify-before-grilling, agent briefs, triage notes, `.out-of-scope/`; state labels from `.agents/tracker.md`; `needs-info` goes to the Inbox when the reporter is Ruaridh; `ready-for-human` notifies (`kata notify` on kata); never `wontfix` without his yes. Proposed waves from `to-tickets`: rendered as the self-contained HTML page and gated in Plannotator; publishing stays with `to-tickets`. Absorbs own `kata-triage-artifact` (renderer, assets, tests now under `triage/`; the old name is a pointer file for one release).

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `triage` | Roles and transitions; the three attention buckets; gather → recommend → verify → grill → apply; redundancy and prior-rejection checks; AI disclaimer on comments; trusted quick overrides; resume from triage notes | External-PR discovery rules; `domain-modeling` call (wave 2 `domain`); GitHub-only label wording |
| mattpocock `triage/AGENT-BRIEF.md` | Durable, behavioural briefs with checkable criteria and out-of-scope; the template, condensed, plus a Verified line | The long worked examples |
| mattpocock `triage/OUT-OF-SCOPE.md` | One file per concept, durable reasons, prior requests, concept matching, never for already-implemented | The long example file |
| self `kata-triage-artifact` | All of it: wave JSON contract, renderer, fonts and theme, tests, the background Plannotator gate with a fresh decision file, annotation mapping and re-gating | The kata-only wording (any tracker now) |
