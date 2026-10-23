---
name: bro
description: "The three one-line course corrections: restate the last message in plain language (\"bro\"), re-pitch it when it did not land (\"wait, what?\"), or go up a layer and map the modules and callers (\"zoom out\"). Use when asked to say it again plainly, when the reader did not follow, or when they need the wider picture before the detail."
upstream:
  - repo: pstack
    path: pstack/skills/bro/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: mattpocock
    path: skills/productivity/wait-what/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/zoom-out/SKILL.md
    sha: 801a01cc7d265e06dd9dbcef5a4c471add05a0b3
---

# bro

Three one-line prompts, one skill. Each is a course correction on the last thing said. Nothing else changes: no new work, no new findings, no plan. Answer the correction and stop.

Reach for the branch the words ask for. "Bro", "say that again", "in English" is the restate. "Wait, what?", "I don't follow", "that didn't land" is the re-pitch. "Zoom out", "I don't know this area", "where does this sit" is the layer up.

## Restate

Restate your last message. Stop using jargon and speak coherently. State it more simply and concisely, like one human talking to another.

Same content, plainer words, shorter. Cut the internal names, the file paths and the tool names unless one of them is the point. Cut every hedge and every restatement of the question. If the message was an answer, the restate leads with the answer; if it was a plan, the restate says the plan in the order the work happens. Do not add anything the first message did not say.

## Re-pitch

Stop. That last message did not land: re-pitch it.

Give a little bit of context first: what the message was responding to, and what it was trying to do. Then say it again in Simplified Technical English: short sentences, one idea each, plain verbs, active voice, no idiom and no metaphor. Use the ubiquitous language, which is the repo's `GLOSSARY.md` (the path `.agents/domain.md` names when it differs); the terms there are the ones the reader already knows.

A re-pitch is not a longer version of the same message. It changes the shape: context, then the point, then the detail that makes the point usable. `technical-writing`'s STE and Global English layers are the standard it is held to, and its unslop pass is the last thing before sending.

## Zoom out

Go up a layer of abstraction.

Give a map of all the relevant modules and callers, using the project's domain glossary vocabulary. Name the module, say what it does in one line, and say who calls it. Draw the map when the relationships carry the meaning, with `domain`'s deep-module words (module, interface, seam, adapter) rather than "component", "service" or "boundary".

Then say where the thing being discussed sits on that map, and what the reader would need to read next to understand it. Nothing here is new work: a `zoom out` is answered from what is already known, and a genuine gap in the map is named as a gap rather than filled with a guess.

## Rules

- One correction, one reply. No preamble, no apology, no explanation of what changed.
- The content is the same content. New findings belong in a new answer, not smuggled into a restate.
- The reader's vocabulary wins: the repo's `GLOSSARY.md`, or the client's terms, over any synonym of your own.
- Plain language is the whole point. A restate that is longer than the message it replaces has failed.
- Nothing is filed, committed or messaged. This skill rewrites a reply, and that is all.
