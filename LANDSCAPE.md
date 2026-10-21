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
