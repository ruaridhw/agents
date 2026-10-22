# Skills landscape

One opinionated set of skills, curated from three upstream paradigms (mattpocock/skills, obra/superpowers, cursor/plugins `pstack`), an employer operator kit (the "kit", private, read through a local upstream entry) and this repo's own earlier skills (the `self` upstream).

Every curated skill lives in `.claude/skills/<name>/` and carries `upstream:` stamps in its frontmatter: one entry per feed, naming the upstream (a key of `UPSTREAMS.json`), the path in it and the sha the skill was written against. `bin/skill-upstream status` shows how far each feed has moved since; `bin/skill-upstream diff <skill>` shows the change. This file is the record `update-skills` reads when it decides what to take from that change: per skill, the opinion, and per feed what was taken and what was dropped. Nothing here is loaded into a session.

## Conventions

- **Frontmatter**: `name` (equal to the directory), `description` (when to use it, in the words a caller would say), `upstream:` stamps, and `disable-model-invocation: true` only on sub-skills that another skill calls. Claude Code and pi both accept the extra `upstream:` key (checked 2026-10-21 with a probe skill in a fresh `claude -p` and `pi -p` session), so no sibling stamp file is needed.
- **Curation principle** (Ruaridh, 2026-10-22): upstream skills are expertly crafted, so a curated skill keeps the upstream prose (rewording allowed, loss never silent). Edit only for the environment (tracker, Herdr, roles, paths, `.agents/*.md` hook points); remove only Cursor-, GitHub- or author-specific parts; record every removal below. No length ceiling. Private upstreams (the kit) contribute ideas only, never text. `update-skills` is the one ingest path; `bin/skill-lint` checks format only. The public upstreams are MIT; their notices are in `THIRD_PARTY_NOTICES.md`.
- **Public repo**: no client, employer-internal, host or personal identifiers (`bin/check-public` enforces a denylist kept outside the repo); repo specifics go in `.agents/*.md` convention files, never in a skill; models are named by role (`~/.config/agents/models.toml`), never inline.
- **Hook points**: general skills read `.agents/tracker.md`, `build-loop.md`, `prove-landed.md`, `deploy.md`, `design-review.md`, `domain.md` in the repo they run in. A missing file means the skill's default. Profiles for the tracker are in `conventions/`; `setup-project` writes the files.
- **One record**: the plan's separate `FEEDS.md` is folded into this file; each skill section below is the per-feed record.
- **Linking**: `linked-skills.txt` lists the curated names linked into `~/.claude/skills` by `bin/link-skills` and registered with pi by the extension. Names that collide with a plugin skill (`grill`, `to-spec`, `to-tickets`, `triage`, `implement`, `pr`, `handoff`) are written but not linked until the plugins are disabled at wave 3; `ruaridh-mode` names their paths so they are reachable meanwhile.

## Whole-landscape dispositions

- **Curated (wave 1)**: `ruaridh-mode`, `clarify`, `herdr`, `grill`, `to-spec`, `spec-review`, `to-tickets`, `triage`, `to-plan`, `implement`, `pr`, `handoff`, `setup-project`, `update-skills`, `rare-skills`.
- **Curated (wave 2, not yet written)**: `write-skill`, `tdd`, `debug`, `verify`, `review`, `ship`, `worktree`, `prototype`, `domain`, `research`, `recall`, `retro`, `technical-writing`, `teach`, `wizard`, `questionnaire`, `bro`, `arch`. `principles` waits for its own grilling.
- **Kept as shipped**: the employer's operator skills and kit (changed only through the kit's feedback channel); the Plannotator family; Anthropic artifact, dataviz and document skills; the effective-html family; browser; own scheduled-job skills (`morning`, `granola-notion`, `notion-todoist-tasks`).
- **Rare** (moved to `~/.agents/rare/`, reached through `rare-skills`): AWS, Cloudflare and other service skills.
- **Dropped**: mattpocock loop-me, caveman, request-refactor-plan, scaffold-exercises, migrate-to-shoehorn, setup-pre-commit, git-guardrails-claude-code, claude-handoff, setup-ts-deep-modules, writing-beats, writing-shape, writing-fragments, edit-article, and the loose find-skills, claude-code-peer-messaging, obsidian-vault; superpowers diagnosing-superpowers; pstack setup-pstack, poteto-agent, make-bot-ui, visual-parity, autopilot-full, autopilot-stack, eval, hillclimb, create/maintain-verification-skill, typescript-best-practices and the automations.
- **Retired own skills** (pointer files for one release): `herdr-agent-handoff` → `herdr` + `implement` + `handoff`; `kata-triage-artifact` → `triage`; `writing-build-spec` → `to-spec`; `adversarial-spec-review` → `spec-review`; `orchestrating-reviewed-build` → `implement`; `find-sibling-agents` → `herdr`.

## ruaridh-mode

**Opinion.** The one entry point, always loaded: the skill-check rule, intake (classify what arrived and say so), the chain with its branches, gates and build loops, judgment (ask or run, autonomy, no is an answer), twelve general non-negotiables and the Inbox convention. Three bodies: full (`SKILL.md`, interactive top-level sessions), slim (`references/slim.md`, spawned workers) and coordinator (`references/coordinator.md`, sessions that own a long-running goal). Delegation, reply and comment rules sit in `references/delegation.md`, the phase-boundary tree in `references/phase-boundaries.md`, tool and machine rules in `references/tooling.md`, with host-specific values in a private `~/.config/agents/tooling.local.md`. Installed as the Claude SessionStart hook (`hooks/session-start`) and the pi extension (`.pi/extensions/ruaridh-mode.ts`).

Decisions:

- **Body selection.** A hook cannot see the first prompt, and `HERDR_ENV=1` is set in every Herdr pane including interactive ones, so the spawner sets `RUARIDH_MODE=worker` on the pane (`herdr tab create --env` / `herdr pane split --env`) and the hook or extension injects the slim body. The full body also carries a `<WORKER-STOP>` block keyed on a `ruaridh-mode: worker` brief line, for workers spawned without the env marker (superpowers' `<SUBAGENT-STOP>` pattern).
- **Coordinator body** is a reference the full body sends the session to, not a third injected body: nothing in the environment says a session owns a long-running goal.
- **Not-yet-curated steps** (`debug`, `tdd`, `review`, `verify`, `ship`, `prototype`, `research`) are mapped to the plugin skills that cover them until wave 2, so the chain is usable now.
- **Colliding names** are reached by path from the bootstrap header's skills directory, so `to-spec` means the curated skill even while the plugin's `to-spec` is installed.
- **Inbox convention** (Ruaridh, 2026-10-22): defined once here (section 5) with mechanics in `tooling.md`: away means question blocks and messages with attachments, thread `<repo> · <ticket or spec ref>`; other skills say "ask per the Inbox convention". Workers never write to the Inbox.
- **`(aimsg) ` prefix and DONE notice** (Ruaridh, 2026-10-22): non-negotiable 11 and the slim body's step 9.

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `using-superpowers` | The rule (check skills before any response or action, including clarifying questions; announce "Using X to Y"; checklist → todos); skill priority (process skills first); the full red-flag table, every row kept with intake wording; user instructions take precedence; session-start injection; the subagent-stop pattern (as `<WORKER-STOP>`) | The 1%-chance invocation pressure and the `<EXTREMELY-IMPORTANT>` / "you MUST" register (Ruaridh's wave 1 decision); "before plan mode, brainstorm" (brainstorming is split into `clarify` / `grill`, which intake routes to); per-harness tool reference files (author's multi-harness support; this environment has two harnesses, wired by the hook and extension) |
| superpowers `.pi/extensions/superpowers.ts` | The extension shape exactly: `resources_discover`, re-arm on `session_start` and `session_compact`, disarm on `agent_end`, marker check, insertion after compaction summaries, tool mapping | `pi.skills` in `package.json` (the extension registers only `linked-skills.txt` names instead) |
| pstack `poteto-mode` | Routing by classifying the task (its playbook list mapped onto intake rows: investigation, bug fix, perf, prototype, refactoring, babysit and shipping, pause and pickup, multi-phase plan, orchestrate, authoring a skill); the ask-or-run trigger in full (observable facts are not the human's to answer; read-only investigations answer from evidence; under a full-autonomy grant decide, act and report, apply a default for a call only the operator can make and say what he could say instead; named gates still pause); Autonomy (just do it / always pause / session overrides / no is an acceptable answer); broken skill mid-task; decision trail for long or unattended work; Subagents (as Herdr workers: background, file pointers, model by role and difficulty, you own every worker's work, second opinion = same brief on another model, fresh workers by default with consolidated scope, resume only for state that lives in the worker); Writing the reply (short declarative sentences, terse is not dropping content, frame impact for consumer and maintainer, never fabricate a link, every claim labelled); Comments (only a non-obvious why; no phase-narrating comments in scripts) | Principle citations and the principle list (principles wait for their own grilling, Ruaridh's decision); the todolist-copy ritual (Ruaridh's wave 1 decision; each playbook is its own skill here); Cursor `Task` defaults, `subagent_type`, model slugs, reasoning-level and fast-mode tuning (Cursor- and author-specific; roles in `models.toml` instead); `/setup-pstack`, Custom Mode and `figure-it-out` routing (author tooling); skill triggers for `how`, `architect`, `swarm`, `arena`, `interrogate`, `unslop`, `deslop`, `no-comments`, `technical-writing`, `benchmark-checklist`, control-ui/cli, bugbot triage (author's or Cursor's skills; their curated counterparts `review`, `verify`, `technical-writing` arrive in wave 2 and the chain names them); the no-long-dash and no-mid-sentence-colon reply rules (author's house style; `technical-writing` owns style in wave 2); hillclimb, eval, visual parity, autopilot, worktree-cleanup playbooks (dropped from the landscape in wave 0); the PR-link format line (GitHub-specific; `pr` owns it) |
| pstack `poteto-help` | The idea of a plain index of what exists (the curated list and the fallback table) | The rest: pstack installation, `/setup-pstack`, Custom Modes, Cursor guide pages, the pstack skill table and "fix a run" table (all pstack- or Cursor-specific); `references/prompting.md` and `recipes.md` (advice to a human on wording pstack prompts, not agent behaviour) |
| mattpocock `ask-matt` | Main flow plus on-ramps as the chain shape, with its branches (settle in conversation or prototype; multi-session build or not; triage only issues you didn't create; huge foggy effort maps, then hands to the spec, never builds); "read a skill before stating what it does or recommending a skip"; context hygiene (keep grill → spec → tickets in one window); skip planning when tickets are small | Codebase-health and vocabulary sections (`domain`, `arch` in wave 2); standalone catalogue entries for skills not curated here (`wait-what`, `writing-for-agents`; `teach`, `wizard`, `research`, `questionnaire` arrive in wave 2); `grill-with-docs` glossary statefulness (moves to `domain`, wave 2); the setup precondition (`setup-project`); `retro` closing the loop (wave 2); `/clear` between tickets (implement delegates instead); its `agents/openai.yaml` (author host config) |
| mattpocock `ask-matt/PHASE-BOUNDARIES.md` | The whole tree as `references/phase-boundaries.md`: five options, the ordered questions, primary vs secondary sources, judgement calls; subagent → Herdr worker, `/handoff` → `handoff`, AFK → unattended | The smart-zone link (author's course site); Claude → Codex as the harness example (pi here) |
| mattpocock `chief-of-staff` | The coordinator body: DRI stance, longer-term thinking, two tracks; all work in workers, background, sparse communication through context pointers; schedules; write history not the present (dated claims, cite the commit, supersede rather than rewrite); strategic view in full (pit of success, data sources, no workarounds, relentless environment improvement) | The wiki-as-memory (Ruaridh's wave 1 decision: the tracker, `.scratch/` and handoff summaries are the record, history comes from AgentsView); its lint schedule (no wiki to lint) |
| own rule sources (home and project AGENTS.md files, the constitution, general memories) | The twelve non-negotiables; `tooling.md` (git, stacked PRs, Herdr, pi, Plannotator and the Inbox mechanics, AgentsView) | Host names, collector URLs, token paths, tailnet recipes (moved to the private local tooling file) |

## clarify

**Opinion.** One round, at most five questions that would each change what gets built, each with a recommended answer worded so "yes" accepts it. A one-sentence restatement of the goal first. No tree, no sizing, no playback: when the task needs those it is a `grill`. Runs by default before non-trivial work that did not come through `grill`; Inbox question blocks when Ruaridh is away. superpowers' `brainstorming` is the spine, read for the reason to ask at all rather than only the mechanics: you build what you believe he wants, and that belief is thinner than it feels. Its interview machinery is `grill`'s, so the copy keeps the opening, the "what do you actually know?" check and the question craft, and hands the rest of the conversation to the skill that owns it. pstack supplies the restatement step and mattpocock the answer format.

Decisions:

- One round, at most five questions, none of them optional process: fewer is better, zero is fine (wave 1).
- Every question carries a recommended answer worded so "yes" accepts it (wave 1).
- A question whose answer is in the code, the tracker or the history is the agent's job; run what would settle it instead of asking (wave 1).
- Unanswered questions take the recommendation, said in one line; no second round and no follow-ups unless an answer contradicts a finding (wave 1).
- When Ruaridh is away, the round goes out per the Inbox convention and independent work carries on; the mechanics live in `ruaridh-mode` and its `references/tooling.md`, not here (wave 1 redo: wave 1 restated the message format).
- The dropped areas stay dropped: sizing, playback, the written design, the hard gate and the visual companion belong to `grill` and `to-spec`, and `clarify` names the switch instead of half-doing them (wave 1; re-checked against the full upstream text in the redo).
- superpowers' red-flag table is kept where it applies (sensible defaults said out loud, explaining the process) and rows that only make sense with the dropped areas are not (wave 1 redo).

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `skills/brainstorming/SKILL.md` | The opening on why asking is worth it, including that people often haven't worked out what they want and that understanding the why settles the hundred decisions they never mention; "What do you actually know?" first check (quick task → just do it); the opt-out line (they can say skip the questions and just start); one-sentence questions with no example lists; plain language, no process jargon, clear and concise; look before asking (recon); questions anchored in specifics and a guess they can correct; the rule that a choice you make goes in as your call, never as something they agreed to; the applicable red-flag rows | The conversation loop: open describing questions, one question per message, "get them describing", and the ground-to-cover list — that is `grill`'s interview, `clarify` runs one round. The "how it gets made" paragraph apart from that rule (platform, language, medium; whose choice each one is) — `grill` asks it, while here the default goes into the recommendation. Playback chunks — `grill` plays back, `clarify` has nothing shaped to play back. Sizing the work, stepping up a size, and the several-independent-projects call — `grill` ends with a size; `clarify` names the switch instead. The written design, its `docs/.../specs` location and the builder check — `to-spec` writes and gates the spec. The `<HARD-GATE>` approval rule — the gate belongs after the spec, not after questions. The visual companion section and `visual-companion.md` — `grill` offers it, and mockups need a shaped idea. `scripts/` (the companion server) — the author's own companion tooling, replaced by `plannotator annotate` mocks in `grill`. `builder-check-prompt.md` — the builder check is part of the written design, which `to-spec` owns. The red-flag rows on offering options, on "sounds good" as approval, and on keeping a spike — they only mean something with the open-describing loop, the written description or spikes, all dropped |
| pstack `pstack/skills/in-your-own-words/SKILL.md` | Restate in your own words what you think the goals are and what problem they are trying to solve, before acting | Its `disable-model-invocation` slash-command framing — the author's host wrapper; here it is one step of a round, not the whole skill |
| mattpocock `skills/productivity/grilling/SKILL.md` | Recommended answer per question; "yes" accepts the recommendation wording; facts are the agent's job, never the user's, looked up without blocking the rest of the round; the decisions are the user's, put each and wait | The design tree, the frontier, rounds and the per-round question format, and "done when the frontier is empty" — `grill` owns the interview. Its sibling `agents/openai.yaml` — the author's config for another host |

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

## to-plan

**Opinion.** Ephemeral `.scratch/plans/<date>-<slug>.md`, one task per ticket in dependency order, steps from `.agents/build-loop.md`, acceptance cited from the spec and never invented (a missing case goes back onto the spec issue). Not gated. Ends by proposing inline or delegated (with the split) and waiting for the pick. `--map` charts work bigger than a session as decision tickets.

| Feed | Taken | Dropped |
| --- | --- | --- |
| superpowers `writing-plans` | Write only the decisions the builder cannot make; file map first; task right-sizing; step granularity and what a step contains; Global constraints and Review focus sections; Interfaces consumes/produces; self-review (coverage, step scan, type consistency, proportion); propose an execution method with one-sentence reason and wait | `docs/superpowers/plans` location; superpowers sub-skill handoffs; checkbox-tracking instruction for agentic workers |
| pstack `multi-phase-plan` playbook | Skip the plan when the change is obvious; settle forks by prototype before writing; explore in subagents returning pointers not dumps; one section per PR with its own evidence; hand back and stop until the explicit go | Ten-lane swarm verification, perf gates, cloud VMs, check-plan script, Cursor control skills (the verification lane per PR waits for `verify` in wave 2) |
| mattpocock `wayfinder` | Map mode: destination, map as an index issue, decision tickets as children with native edges, claim-first, frontier, fog of war, out of scope, refer by name, hand off to the spec | Its tracker-operations doc and `wayfinder:` labels (tracker kinds instead); 100K-token sizing language |

## implement

**Opinion.** Fetch the ticket and state its title, worktree named by ticket, run the plan's tasks or derive one from the ticket. Inline: progress ledger, continuous execution, `Ruling:` lines, four stops, completion contract, one reviewer-role pass at the end. Delegated: Herdr builders with the brief template (GOAL / SCOPE / CONTEXT / ACCEPTANCE / VERIFY / TIMEBOX / FORBIDDEN / REPORT / STANDING); the coordinator never writes code, reviews every diff, and runs a reviewer on each integrated phase. Marks `merged` after `pr` lands and `done` after `.agents/prove-landed.md` passes. Absorbs own `orchestrating-reviewed-build` (pointer file for one release) and the brief/roster half of `herdr-agent-handoff`.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `implement` | Fetch the ticket and state its title; ask when ambiguous; build at agreed seams; typecheck and single tests often, the full suite at the end; review before done | Committing to the current branch (worktree per ticket instead) |
| mattpocock `implement-spec` | Tickets as a task graph worked by frontier; sparse communication through context pointers; implementers in the background in their own worktrees; refill as the frontier moves | One integration branch and a merger subagent (one PR per ticket on a stack instead); draft PR closing everything |
| superpowers `executing-plans` | Inline mode: ledger as the record, trust it after compaction, continuous execution, rulings not stalls, the four stops, completion contract, final fresh review, re-grade by effect, one fix pass with failing tests, deferred minors, "Rulings I made" | Its workspace scripts (`sdd-workspace`, `task-start`, `task-done`); `.superpowers/sdd` location |
| superpowers `subagent-driven-development` | Pre-flight interface scan; fix rounds back to the same implementer, then fresh; reviewer findings gated by the coordinator | A reviewer per task (one per integrated phase instead); Agent-tool dispatch |
| superpowers `dispatching-parallel-agents` | Independent domains in parallel, focused self-contained prompts, integrate and verify after | Agent-tool mechanics |
| pstack `feature` | Throughput checkpoint (blocking first steps, independent workstreams, shared mutable state, smallest safe decomposition); delegate code-writing with a specific scope; verify on the matching surface | Architect/arena/interrogate steps (wave 2 `arch`, `review`); Cursor model defaults |
| pstack `refactoring` | Pin behaviour before moving structure; subtract before adding (left for `tdd`/`arch` in wave 2 to expand) | The rest of the playbook (wave 2) |
| pstack `orchestrate` | The brief template and its rules (a field you cannot fill means unscoped; pointers not copies; upstream reports pasted in full; collapse for tiny units); rolling window, not blocking batches; respawn fresh, never resume-chain a muddled brief; coordinator never writes code | The `orch` store and CLI, cloud workers, sub-coordinators, ledger TSVs, frontier JSON (the tracker and the herdr ledger carry this) |
| self `orchestrating-reviewed-build` | One workstream, worktree and branch per builder; shared contracts first, risky switch last; reviewer on the integrated phase with findings to the coordinator; done only when evidence matches, not merge state | Its isolated-QA, acceptance-file and production-gate steps (wave 2 `verify` and `ship`, and repo `prove-landed.md` / `deploy.md`) |
| self `herdr-agent-handoff` | Brief and roster conventions for delegated work | Model tables (roles in `models.toml`); pane mechanics (`herdr`); file shapes (`handoff`) |

## pr

**Opinion.** One PR per ticket on the previous ticket's branch; gitmoji imperative title; the wave 0 body (Why / What changed / Scope / Evidence before → after / Merge danger: door and blast radius / Verification, then `Ticket:` and `Stack:`); no `Closes #N` because merged is not done; merge only with Ruaridh's yes, by the async recipe, base first, then adopt remote heads.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `pr` | Smallest-visual summary (diff-sketches, trees, mermaid, pseudocode); before/after evidence ranking; one-way/two-way door and blast radius | GLOSSARY wording (wave 2 `domain`); the exact heading order (wave 0 body instead) |
| pstack `opening-a-pr` | One-minute briefing body; Why / What changed / Scope / Verification sections; open ready never draft; narrow PRs; stacks as base-branch chains; don't babysit on open; keep shas and genealogy out of the body | Conventional Commits titles (gitmoji instead); amend-into-previous-commit; deslop/no-comments/technical-writing hooks; Origin and built-in PR tools |
| superpowers `finishing-a-development-branch` | Tests green before anything; confirm the base; keep-as-is and local-merge options; discard only on explicit request | The fixed three-option menu as the default (PR is the default here) |
| own rule sources (stacked-PR memories, home AGENTS.md) | The merge recipe: async endpoint, `.details.uuid`, `merge_method=merge`, base first, retargeted children re-run checks, adopt remote heads, never `--onto` with a local parent sha, hand-built chains are not stacks, retarget before deleting a base | Repo names and dates |

## handoff

**Opinion.** Pause: triggered by "stop", near-spent context or a session ending with work in flight; `wip:` commit, summary file in `.herdr-handoffs/`, panes closed through `herdr` with their sessions recorded, ticket comment and `work.attention`. Pickup: triggered by intake finding a summary or `work.branch`; rebuild from the trail, name the resume point, verify only what the next step depends on, resume recorded panes. Owns the summary and raw-log shapes every worker writes.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `handoff` | Reference other artifacts by path instead of duplicating; redact secrets; tailor to what the next session is for | Writing to `$TMPDIR` (`.herdr-handoffs/` in the repo instead); "suggested skills" section (intake routes) |
| pstack `pause-safely` | Explicit-only pause, never on "keep going"; safe boundary; nothing irreversible; one `wip:` commit with broken-tree note; resume note sections (intent, progress, state, next step, key files, gotchas); pause reply shape | `/tmp` resume note; Cursor restart trigger |
| pstack `session-pickup` | Trail is authoritative; rebuild operational state; diff done vs pending; name the resume point; verify inherited claims on the real artifact; route the rest to the owning skill | Cursor transcript paths and cloud-agent URLs (AgentsView instead) |
| self `herdr-agent-handoff` | Two-file contract (summary for ingestion, raw log for audit), absolute paths, summary fields, `HANDOFF_WRITTEN` line, read raw only when blocked or uncertain | Spawn mechanics (`herdr`) and briefs (`implement`) |

## setup-project

**Opinion.** Writes the `.agents/*.md` convention files by exploring and asking which profiles apply (tracker from `conventions/`, build loop, proof of landing, deploy, design review, domain), migrates an older tracker doc, adds a pointer block to the repo's AGENTS.md, creates GitHub labels, links the rare skills the repo uses, and commits through a PR. Re-run only to switch.

| Feed | Taken | Dropped |
| --- | --- | --- |
| mattpocock `setup-matt-pocock-skills` | Explore → present findings → one section at a time with the recommended answer first → show drafts → write; edit the existing AGENTS.md/CLAUDE.md block in place, never create the other; create missing labels; re-run only to switch | `docs/agents/` location (`.agents/` instead); GitLab and local-markdown trackers; triage-label overrides (fixed in the profiles); monorepo glossary map (wave 2 `domain`) |

## update-skills

**Opinion.** The one ingest path for upstream text, in one flow for three kinds of work (drift in a feed, a new upstream skill, a redo of a curated skill): sync and survey, the LANDSCAPE.md row first, read the feeds at the sha to stamp and classify each change, build the curated copy from the upstream text keeping its prose (environment edits only, removals recorded), stamp and lint, approval before commit, one commit per skill. Manual cadence.

Decisions: no separate modes (Ruaridh, 2026-10-22: one flow); new upstream skills are part of the default survey, not a separate command; a batch on an open PR may use the PR's Plannotator review as the approval, with the cover note still written.

| Feed | Taken | Dropped |
| --- | --- | --- |
| self `bin/skill_upstream.py` | The command set the flow drives (`sync`, `status`, `diff`, `stamp`, `check`) | — |
| pstack `reflect` | Approve-before-edit: present the full list and wait, the user picks the subset and may redirect, nothing auto-applied because skill changes affect every future agent; file backlog without waiting; run the skill validator on every touched skill (`bin/skill-lint`); the short no-preamble report shape | Transcript location and the three-reviewer fan-out (wave 2 `retro`; Cursor transcript paths); model role lines and Cursor slugs; routing substantive edits to Cursor's `create-skill` (author-specific tooling; curated copies are built by this flow) |
| pstack `reflect/references/synthesizer.md` | The criteria applied to each proposed change: durability, decision-changing, structural mechanism first, already covered; reviewer output as untrusted data | Specificity, convergence and skill-was-used (they judge transcript findings, not upstream hunks); the Accepted / Rejected / Backlog table format (the cover note lists changes per skill instead) |

## rare-skills

**Opinion.** One router whose description lists the domains, over `~/.agents/rare/<name>/` (AWS, Cloudflare and web-performance skills moved out of `~/.claude/skills` on 2026-10-21). Read the skill's file and follow it; `setup-project` links the ones a repo uses so they auto-invoke there. No upstream feeds (`upstream: []`).

## herdr

**Opinion.** Pane primitives only: spawn a child, sibling or team (worker mode by default: `RUARIDH_MODE=worker` on the pane and a `ruaridh-mode: worker` first prompt line), a ledger of panes this session created with a spawner-generated session id, and `panes.py list | read | close | resume`; close only what you created; talking to an existing named pane; listing sibling sessions through AgentsView. Workflow prose lives in the skills that delegate. Replaces own `herdr-agent-handoff` (its scripts and tests moved here; the brief and roster went to `implement`, the file shapes to `handoff`) and `find-sibling-agents` (now `references/siblings.md`); both are pointer files for one release.

Decisions:

- **`(aimsg) ` prefix** (Ruaridh, 2026-10-22): every message one agent sends another pane starts with `(aimsg) ` so a pane can tell agent messages from Ruaridh's; the spawn, team and resume scripts add it, and the skill tells agents to add it by hand.
- **`(aimsg) DONE` notice** (wave 1 redo): every spawned worker's brief ends with the instruction to notify its creating pane, `herdr agent prompt <creator> "(aimsg) DONE <name> <summary path>"`. `done_notice` in `spawn_worker.py` and `spawn_team.py` builds that line from `HERDR_PANE_ID` and appends it to every prompt in the invocation (nothing is appended when the variable is unset), so a creator that spawned with `--no-wait`, or a coordinator, waits for that prompt instead of polling summary files.
- **Session ids are the spawner's** (wave 1): lean pi workers run without extensions, so Herdr cannot report their session; the spawners generate the id and pass it with `--session-id` (pi and Claude both accept it), which makes `panes.py resume` deterministic.
- **Model choice is a role** (wave 1): the upstream's inline model table moved to `~/.config/agents/models.toml` (`main`, `reviewer`, `builder`, `cheap`, `spec-reviewer`); the skill keeps the upstream's use-case table with roles in the model column.
- **Upstream prose kept** (wave 1 redo): the copy starts from the upstream text again. The sibling reference keeps `Branch evidence`, `Adjusting the list`, `Picking a sibling with the most context later` and the whole rationalization table, reversing wave 1's condensation; the curation principle has no length ceiling.

Environment edits, not removals: the upstream's absolute script path became `scripts/` beside the skill; the model ids and the Codex Sol placeholder became roles; "Pi integrates results" is "you integrate the result"; the Inbox is referred to, not restated.

| Feed | Taken | Dropped |
| --- | --- | --- |
| self `herdr-agent-handoff` | Semantics (sibling / child / team); preconditions and the installed binary as the syntax authority; one named tab per invocation in the caller's workspace and cwd, first agent in the tab's root pane, further members split from that root so no empty shell is left; the single-worker helper's behaviour; `--lean` with its measured ~14.3k to ~3.8k first-turn baseline and the exact-skill-path rule for lean briefs; `team.json`, the roster and the coordinator's integration step; the model-choice doctrine (choose by task, do not clone the caller's model, strongest reasoning for high stakes, check availability, stop rather than silently weakening); the manual contract and its shell example; every coordination rule (absolute handoff paths, explicit pane ids, non-overlapping tasks, `blocked` panes read before input, never close what you did not create); "read raw logs only when the summary says blocked or uncertain, or exact evidence is needed" | The hard-coded `~/.agents/skills/herdr-agent-handoff/scripts/...` path: the scripts live in `scripts/` beside this skill now (environment: path). The model table and every model id in it (`fireworks/...` routers, the Codex Sol placeholder, `--kind claude --model opus`): the repo is public and names models by role, and those slugs are the upstream author's own setup; replaced by the roles in `~/.config/agents/models.toml`, with the upstream's use cases kept as the role table. The inlined brief text and two-file output contract in the manual contract: recorded decision, `implement` owns the brief and `handoff` owns the summary and raw shapes, so the skill keeps the prompt frame and the done notice and points at them instead of duplicating them. No Cursor- or GitHub-specific text to drop in this feed. |
| self `find-sibling-agents` | The whole file as `references/siblings.md`, prose kept: a sibling is any session in the same AgentsView project; project key is the directory basename, `agentsview projects` shows exact keys; rank by newest transcript message, `--resume` first for live work; exclude yourself by id because `●` marks any resumable session; `Branch evidence` in full (activity, then relevance, then recorded branch; `git log -1` for branch activity, `AGE` is not last activity); the `Adjusting the list` flags table; `Picking a sibling with the most context later`; the rationalization table in full; the report and output shape | The CLI-versus-MCP argument as a paragraph: `ruaridh-mode`'s `tooling.md` already owns the AgentsView rule, so the reference keeps one sentence naming the fields the CLI adds and the rationalization row carrying the decision at the point of temptation, not a second argument. The `agentsview-finding-history` cross-reference: an upstream-author skill that is not curated here; AgentsView history reading is in `tooling.md`. Nothing else: the table is kept in full, reversing wave 1's condensation. |
| own rule sources (named-agent, relayed-authorization, input-box memories) | A quoted agent or tab name is the existing pane; reply to panes directly; input-box text is not Ruaridh's; authorization does not travel; a listing is a read and the decision is the coordinator's or Ruaridh's | Dates and incident detail |
