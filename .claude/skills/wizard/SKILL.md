---
name: wizard
description: "Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning, credentials, CI secrets, an unfamiliar third-party dashboard, a one-off migration or cutover. Use when a procedure is manual, tedious to repeat and tedious to re-explain, and the agent cannot do the steps itself."
upstream:
  - repo: mattpocock
    path: skills/engineering/wizard/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/wizard/template.sh
    sha: 49dd158d1076134a641b33efb035946536778336
---

# wizard

A **wizard** is a bash script that walks a human, step by step, through a manual procedure that is tedious to do by hand and tedious to re-explain to an agent every time. It opens each URL, says exactly what to click and copy, captures the values, writes them where they belong (`.env`, GitHub secrets), confirms at every stage, and shows how many stages are left. It might configure third-party services, run a one-off migration, or move the project from one state to another.

Don't invoke it for steps the agent can perform itself.

The delightful UX is already solved by `template.sh`, beside this skill: stage-by-stage progress, confirmation gates, cross-platform URL opening (including WSL), hidden secret entry, idempotent `.env` upserts, `gh secret` / `gh variable` writes, and a closing summary. **The job here is only to scope the procedure and author its stages.** The library above the `STAGES` marker is identical in every wizard; that consistency is the point, so never hand-edit it.

A wizard is ephemeral by default: built for one run, saved to a scratch or `scripts/` path, deleted when the job is done. Commit it only when Ruaridh wants a repeatable setup path that should live in the repo.

## Process

### 1. Scope the procedure

Work out every manual step the human must take and every value that gets captured along the way. Read the repo first; don't ask cold:

- For setup: `.env`, `.env.example`, `.env.*`, `README`, `docker-compose*`, framework config, and `.github/workflows/*` (every `secrets.*` / `vars.*` reference is a value the wizard must produce).
- For a migration or transition: the current state, the target state, and the irreversible actions between them.

Then show the ordered list of stages and the values each produces, and confirm: he may add, drop or reorder.

**Done when:** every stage is named in order, and for each captured value you know (a) where the human gets it, (b) where it is written (`.env`, a GitHub secret, both, or nowhere; some stages are pure actions), and (c) whether it is secret (hidden entry) or public.

### 2. Map each stage's journey

For each stage, write the precise path a human follows: which URL to open, what to do there, where a value is shown, which variable it fills. For example: "Dashboard → Developers → API keys → Reveal test key → copy". Where you do not actually know the current UI or the exact command, say so and ask Ruaridh or check the docs: never invent steps that may not exist.

**Done when:** every stage traces to concrete instructions a stranger could follow.

### 3. Author the wizard

Copy `template.sh` from this skill's directory to the target path. Replace the example stage with one `stage` per step, in dependency order. Use the library helpers: `stage`, `say` / `step`, `open_url`, `ask` / `ask_secret`, `write_env`, `set_secret` / `set_var`, `pause` / `confirm`. Set `TOTAL_STAGES` to the number of stages you wrote.

Hold the bar the template sets: open the URL before asking for its value, use `ask_secret` for anything secret, `write_env` every persisted value, `set_secret` only the values CI actually needs, and `confirm` before any irreversible action. Each `stage` clears the screen so only the current step is visible: keep a stage to one focused task so nothing the human needs scrolls away. Don't touch the library above the marker.

If the target path is inside this repo, the wizard belongs in `.scratch/wizards/<date>-<slug>.sh` while it is ephemeral. A wizard that stays goes in `scripts/`, with a README line pointing at it.

### 4. Verify and hand off

- `bash -n <script>`; run `shellcheck` if it is available.
- `chmod +x <script>`.
- Don't run it end to end yourself: it opens browsers and blocks on human input. Trace it statically instead: every value from step 1 is captured and lands where step 1 said, and every `set_secret` name exactly matches a `secrets.*` reference in CI.
- Tell him how to run it. If it is a repeatable setup path, commit it and link it from the README, so the next person runs the script instead of asking an agent.

## Rules

- A wizard is for a human's steps, never a wrapper around steps the agent could take itself.
- Every value has a destination decided before the script is written. A value with nowhere to land is a stage that should be dropped.
- Never invent a UI path or a command. An unknown step is asked about, or written as a `pause` that tells the human what to check and come back.
- The library above `STAGES` is not edited. A missing helper is a reason to talk it through, not to fork the template.
- A secret is captured with `ask_secret` and written where CI reads it, and is never echoed into a log or a summary.
