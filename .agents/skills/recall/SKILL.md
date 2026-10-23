---
name: recall
description: "Rebuild recent working context on a topic from the agent history, git, the forge and the tracker, and hand back a tight current-state brief. Use for \"recall my work on X\", \"catch me up\", \"what have I been working on\", \"where did I leave off\", before starting or resuming work, or when a coordinator needs the state of a line of work in one screen."
upstream:
  - repo: pstack
    path: pstack/skills/recall/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/ketchup/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: self
    path: .agents/skills/searching-shared-agentsview-history/SKILL.md
    sha: a5d5d8a99ef29eaeab5050e3c974cdfc340c7612
---

# recall

**Before you start or resume work, you rebuild the recent working context on a topic and hand back a tight capsule of where things stand now and what to do next.**

Keep it tight and on-topic. Read only what the in-scope threads need, then stop.

Your context lives in two records. The agent history holds what was done and decided while working. The shared record holds everything that happened around the same code under other names: the symptoms users keep reporting, the fixes that shipped and got reverted, the errors still firing in production. That second record is what `research` searches, across source control, the tracker, chat, documents and error tracking. A feature with a long bug tail keeps most of its story there, so don't reconstruct it from transcripts alone.

The two records are reached through:

- **AgentsView** for the history, through the collector, never by grepping session files (mechanics in `references/archive.md`; the search and citation workflow is `research`'s `references/sources/agentsview.md`).
- **git** for branches, commits, diffs against the base, and worktrees.
- **`gh`** for pull requests, their state, their checks and their review threads.
- **The tracker** for tickets, their states, and what `.agents/tracker.md` says about reading them.

1. **Classify, then route.** One specific prior session to resume is `handoff`'s pickup half, not this. Turning habits into a durable skill is `retro`'s business. A human-readable summary of work for someone else is a different task. Recall loads working context across recent sessions before you act. If Ruaridh already gave you a full state capsule (paths, branch, the change), use it and skip the mining.
2. **Lock the scope before searching.** Pin the window ("recent" is a real range; default the last seven days), the topic if named, and the workspace (default the active one; never read another project's history without being asked). State the scope back in one line. Never quietly turn "all" into "recent N".
3. **Fan out across the agent history.** For more than a couple of sessions, spawn parallel explorers through `herdr` on the `cheap` role, each taking a slice of the corpus, and give each the same target and the rule that a snippet is a lead: search first, then read only the matching sessions and only their relevant regions, skipping the current session and obvious noise (a worker's own report, an eval run, a test session). Each returns one block per session: topic, the goal, decisions, open threads, struggles and corrections, and artefacts (pull requests, tickets, branches), each citing the session id and its ordinal range. For one or two sessions, skip the fan-out and search directly. The raw transcripts stay in the explorers; the main thread gets only their findings.
4. **Sweep the shared record whenever the topic names a feature, file, subsystem, area or bug.** This is the default, not a judgment call, and "my work on X" does not exempt it. Hand it to `research`, but steer the question from "why was this built this way" to "what is the current state, what has been tried and did not hold, and what are users still reporting". Reuse its per-source playbooks, run the investigators in parallel with the history mining, and inherit its posture: one investigator per source, null results are findings, skip an unreachable source and say so. Fold what comes back into the brief. Skip this step only for pure activity recall with no named target ("what did I do this week"), where the history and the live state are the entire answer.
5. **Verify against live state.** Take the pull requests, branches and tickets the mining and the sweep surfaced and check them: `git log` and `gh pr view` for state, the tracker's read commands for ticket state. When the answer hinges on what an agent actually did (the tools it ran, the files it read, the errors it hit), read the full session, not a trimmed summary.
6. **Write the brief to the contract below.** Group by thread. Stay on the named topic.

## Output contract

Lead with the capsule, then the thread status, then the problems, then the next move. Deeper detail goes below or gets cut.

- **Capsule.** At most five bullets. What this work is and where it stands overall.
- **Threads.** One line each, prefixed with exactly one status tag: `[merged #N]`, `[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`, `[reverted #N]`, or `[planned, not started]`. A thread with no tag is not done yet, so tag it.
- **Problems.** At most five, the recurring ones. Include the symptoms users keep reporting and any fix that shipped and was reverted, so the next attempt starts where the last one failed.
- **Next move.** The single most useful next action, concrete.

An adjacent feature or ticket stays out unless it blocks this one. When the capsule and thread lines outgrow a screen, cut detail before you cut threads. Cite history findings by session id and ordinal range, and shared-record findings by their source (pull-request number, ticket ref, document, error-tracker issue), and sanitize anything private before it leaves the session.

**The answer goes in chat**, not a file: a coordinator asking what happened needs it in the conversation, and the thread tags are what it routes on. Say where a longer artefact already lives (a summary, a spec, a pull request) instead of pasting it.

## Same-chat catch-up

The other shape: catch Ruaridh up on what changed **in this session** since his last message, and help him understand each change, not only where it stands. Notifications and worker results are not his messages. Assume he remembers his last message and nothing after it.

Use `bro`'s voice, not its task: plain words, short sentences, no jargon, like one person catching up another. Say what changed for him, not how you did it. Say "the tests pass", not "CI is green". Leave out hashes, file paths, commands, build numbers and test counts unless he needs one to act. Call each pull request, branch or agent by a name he would know, not a label you invented. If a fact needs context to make sense, give the context or leave the fact out.

### Gather what changed

Keep this turn read-only. Make visuals only from what you already have: do not change code, start an app or a job, or post anything. Collect your own work since that message, reports from workers, and messages from anyone else in this session. Check the current state of each pull request, check run or agent this session touched. Check each number you will show against the facts it comes from, and say so when you correct one.

An action item is a decision or step only Ruaridh can take: a product choice, an approval, an irreversible action, access you lack. Include any still waiting on him, even one raised before his last message. Work you can still do yourself is not an action item. Never make up a call to fill the reply. A step he did not ask for and the work does not need is not an action item, unless it is irreversible and waiting on him: give it one action line, no visual, and skip what happens if he does not answer.

### Write the reply

Keep the whole reply well under 150 words, not counting visuals. When something is easier to grasp as a picture than as sentences, draw it: how a design or system works, a stack of pull requests or a dependency chain with each one's state, a before and after of a fix, or options side by side. Never draw a status list or boxes with nothing connecting them. Never give a fact twice, in text or across visuals. Leave out work that changed nothing for him. When words run short, cut from what happened before you cut from the action items.

Open with one sentence that says how many things need him, or that nothing does. If nothing happened and nothing waits on him, say so and stop.

Then show what happened, pictures first. Embed inline the screenshots and videos the work produced, then any diagram that explains a change. Then sum up in one short bullet per thing he asked for: what came of it, and whether it is done, still running, failed, or not checked. Write each line the way you would say it out loud: "Search was slow from a missing index", not "Search review: done". Name any bug found and fixed on the way. Each line must stay true when read alone. Never mark something done that still waits on him, and leave out anything the action items say. Under the summary, give at most three short lines that change what he knows or must do. Then name in one line any work left that you can do yourself.

Then list the action items as plain bullets, never as a diagram or box. Give each two lines, or one for an unasked irreversible step: the decision with your recommendation and why, then what happens if he does not answer. Ask the call he owns, such as merge, approve, or pick. A step you would take first goes in your recommendation. So does anything that must happen first, and anything that cannot be undone. Write "unknown" for a part you do not know. Link to the detail.

Show a choice after the list. If the screenshots above already show its options, write each option's gain and cost under its screenshot instead of drawing a new visual; otherwise, compare the options side by side, with the current state when there is one. Give every option the work weighed, each with what it gets him and what it costs. Keep them out of the rest of the text.

### Visuals

A visual is a picture: a screenshot, a video, a Mermaid diagram, a chart or a generated image. A Markdown table is not a visual, even with before and after columns.

Keep each visual small enough to read at a glance: at most six boxes, with at most eight words in each. Write labels as plain words a person would say, not tags like "Tests: pass". A fact that needs a sentence belongs in the text, or nowhere.

Embed screenshots and videos inline when the change is visible, not only as links. If a visible change has none, mark its summary line "No screenshot yet", and say there what changed on screen. Draw diagrams and charts from facts you have: a Mermaid diagram for how things connect, a chart from a script in `.scratch/` for numbers. Never invent a number, and never draw or generate a picture of a screen you did not capture. Link only artefacts that exist.

## Rules

- The history is read through AgentsView only. Never grep session files, and never copy transcripts between machines (mechanics in `references/archive.md`).
- The tracker, the forge and the branches are the live state; a summary is evidence about the past, not about the present. Check the state you report.
- Every line that a reader could act on carries its tag or its citation. An untagged thread is an unfinished claim.
- This skill reads. It does not fix, merge, comment or file anything. If the next move is work, say the move and hand off to `implement` or `handoff`.
