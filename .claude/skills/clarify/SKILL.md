---
name: clarify
description: Ask the few questions that would change what gets built, once, before starting non-trivial work. Use at the start of any non-trivial task that did not come through grill, or when asked to "check before you start" or "ask me anything you need".
upstream:
  - repo: superpowers
    path: skills/brainstorming/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: pstack
    path: pstack/skills/in-your-own-words/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/productivity/grilling/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
---

# clarify

One round of questions, then work. This is not an interview: `grill` is for ideas that need shaping. `clarify` is for a task that is mostly clear but has a few forks only Ruaridh can settle.

## When

- Automatically, at the start of any non-trivial task that did not come through `grill` (`ruaridh-mode` sends you here).
- Standalone when asked.
- Skip it when everything that matters is in the request: say "No questions; starting." and start.

## Steps

1. **Look before you ask.** Read the ticket, the files, the repo's `.agents/*.md` and anything else you can reach. A question whose answer is in the code, the tracker or the history is your job, not his. If running something would answer it (behaviour, output, timing, whether a test separates the options), run it instead of asking.
2. **Say what you think the goal is**, in one sentence of your own words: the problem he is solving, not the change you have in mind. This is where a misreading gets caught cheaply.
3. **Ask at most five questions**, each one that would change what gets built if answered differently. For each:
   - one plain sentence, no list of examples hanging off it;
   - your recommended answer and the one-line reason;
   - word it so "yes" accepts the recommendation.
   Order them most consequential first. Fewer is better; zero is fine.
4. **Wait for the answers**, then start. Unanswered questions take the recommendation; say so in one line ("Taking the recommendation on 2 and 4.").

Where Ruaridh is not in the chat, send the questions as one Plannotator Inbox message with a `:::question` block per question (recommended answer marked, `Holds up:` naming the work that waits), then carry on with whatever does not depend on them.

## What not to do

- No decision tree, no second round, no follow-ups on the answers unless an answer contradicts something you found.
- No sizing the work and no playback of the design: if the task turns out to need either, it is a `grill`; say so and switch.
- No questions about preferences that do not change the result, and no questions you could answer by looking.
- No process talk. Ask the question.

## Example

> Goal as I read it: stop the nightly sync from duplicating tasks when a meeting is edited after it was first synced.
>
> 1. Should an edited meeting update the tasks it already created rather than add new ones? Recommended: yes, matched on the meeting id plus the action-item text, because that is what the dedupe key already holds.
> 2. Should tasks already completed in the to-do app stay completed when their meeting text changes? Recommended: yes; the to-do app is the source of truth once synced.
