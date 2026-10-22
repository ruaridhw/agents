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

You are very good at building. You build what you believe your human partner
wants, and that belief is usually thinner than it feels. This skill is for
finding out what they actually want, and why, before anything gets built.
People often haven't finished working out what they want, and good questions
help them think it through. When you understand the why, you make the hundred
decisions they never mention the way they would have made them.

One round of questions, then work. This is not an interview: `grill` is for
ideas that need shaping, with a tree, rounds, playback and a size. `clarify` is
for a task that is mostly clear but has a few forks only Ruaridh can settle.

## When

- Automatically, at the start of any non-trivial task that did not come through
  `grill` (`ruaridh-mode` sends you here).
- Standalone when asked, in his words: "check before you start", "ask me
  anything you need".
- Skip it when everything that matters is in the request: say "No questions;
  starting." and start. If he'd rather skip the questions and have you just
  start, he can say so.

## First: What Do You Actually Know?

Before you reply, ask yourself: what do I know about what they want, and why?

- **Everything that matters is in the request** ("make the icon cornflower
  blue"). This is a quick, clear task. Do it, and say what you did.
- **Something non-trivial is missing.** Ask, in one round.

## Say What You Think the Goal Is

Restate in your own words what you think the goals are and what problem they
are trying to solve: the problem, not the change you have in mind. This is
where a misreading gets caught cheaply.

## Look Before You Ask

Finding _facts_ is your job, never theirs. Read the ticket, the files, the
repo's `.agents/*.md` and anything else you can reach. When a question needs a
fact from the environment (the filesystem, a tool, the tracker), go and find
it: run it, read it, or send a Herdr pane to look (`herdr`). Don't ask for
anything you could look up yourself.

Don't block on a lookup that will settle one question: a running exploration is
an unsettled prerequisite, so only the questions downstream of it wait. Ask the
rest of the round now.

Offer recon once you have a bit of grounding and looking would help: their
codebase or project, their own files and data, or the web. Say what you'd look
for. They decide whether you go.

## The Questions

Ask at most five, in one round. Each question must change what gets built if it
is answered differently. For each:

- one plain sentence, with no list of example answers hanging off it;
- your recommended answer and the one-line reason for it;
- worded so "yes" accepts the recommendation.

Order them most consequential first. Fewer is better; zero is fine.

A choice you make rather than ask about goes in as your call, said out loud,
never as something they agreed to.

Use plain language, pitched just a little above where your human partner is.
Match their vocabulary; never use process jargon.

**Questions that work** anchor in specifics: "If it could only do one of these
well, which?", "What would make you wince if I got it wrong?" A guess they can
correct ("I'm guessing this is because X keeps biting you?") often beats a
question.

Be clear and concise. Lead with what matters. When you report what you found,
give them the most important findings and offer the rest.

## Wait For The Answers

The _decisions_ are theirs: put each one to them and wait.

Then start. Unanswered questions take the recommendation; say so in one line
("Taking the recommendation on 2 and 4."). No second round, and no follow-up on
an answer unless it contradicts something you found.

When Ruaridh is away, ask per the Inbox convention, then carry on with whatever
does not depend on the answers.

## Red Flags

| Thought | Reality |
|---------|---------|
| "I'll fill in sensible defaults" | Good. Say them out loud. A default they never heard is one they couldn't reject. |
| "I should explain the process first" | Ask your question. The process shows itself. |
| "I'll ask a second round to be safe" | One round. What goes unanswered takes the recommendation. |
| "This needs a tree, playback and a size" | It is a `grill`. Say so, and switch. |

## Example

> Goal as I read it: stop the nightly sync from duplicating tasks when a meeting
> is edited after it was first synced.
>
> 1. Should an edited meeting update the tasks it already created rather than
>    add new ones? Recommended: yes, matched on the meeting id plus the
>    action-item text, because that is what the dedupe key already holds.
> 2. Should tasks already completed in the to-do app stay completed when their
>    meeting text changes? Recommended: yes; the to-do app is the source of
>    truth once synced.
