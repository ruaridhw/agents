---
name: grill
description: Interview Ruaridh relentlessly about an idea, plan or decision until there is a shared understanding, then size it and name the route. Use for vague asks, "grill me", "stress-test this", "what should we do about X", or any idea that has to be shaped before it can be specified.
upstream:
  - repo: mattpocock
    path: skills/productivity/grilling/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: mattpocock
    path: skills/productivity/grill-me/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: mattpocock
    path: skills/engineering/grill-with-docs/SKILL.md
    sha: 5beb35b040e3de97e54fa9e386d7e42d15c295c2
  - repo: superpowers
    path: skills/brainstorming/SKILL.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: superpowers
    path: skills/brainstorming/visual-companion.md
    sha: b739a8af570e10a95898f2bdf6cec97467fa6c12
  - repo: pstack
    path: pstack/skills/sharpen/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# grill

Shape an idea by interview. Facts are your job; decisions are his. The session ends with a playback, a size and a route, not with code.

## Start

1. **Look first.** Read what exists: the repo, its `.agents/*.md`, related tickets, prior sessions (AgentsView) and anything he pointed at. Send explorers to Herdr panes (`herdr`) for anything broad, and do not block on them: only questions downstream of an open lookup wait.
2. **Offer the visual companion** in its own one-line message when seeing would help more than reading: a screen, a layout, a flow, options that would look different. If he accepts, build single-file HTML mocks in `.scratch/mocks/` and open each with `plannotator annotate <file>` in the background; his annotations come back as answers. If he declines, stay in text and do not offer again.

## Rounds

Map the idea as a design tree: every decision branches into the decisions that hang off it. The **frontier** is every decision whose prerequisites are settled.

- Ask the whole frontier in one round. Number each question, give your recommended answer, and word it so "yes" accepts the recommendation.
- A question that depends on another open question in this round waits for a later round.
- Each round's answers move the frontier; recompute it and ask again.
- Cover the ground, but never read it out as a checklist: why now and what success looks like; goals, non-goals and anti-goals (what would make it a failure even if it technically works); constraints; prior art; what exists now; the details he cares about; which "how it gets made" choices are his and which he is handing to you.
- A guess he can correct ("I'm guessing this is because X keeps biting you?") often beats a question.
- If running something would settle a question (behaviour, timing, output, layout), run it or build a throwaway spike instead of asking. A spike stays throwaway; keeping it is a new request.

Format:

```
❓ **Q1 · <title>**: <question, with choices if any>

➡️ <recommended answer, one line of reason>
```

Where he is not in the chat, send each round as one Plannotator Inbox message with one `:::question` block per question, and wait for the reply before the next round.

## Playback

When the frontier is empty, play the whole thing back in plain words, a part at a time if it is long: what it is for and who it serves, the decisions as he made them, the calls you made (marked as your guesses), what is left open. End by asking what is wrong or missing. Nothing is settled until he confirms the playback.

## Size and route

Say the size in plain words; he can override it.

| Size | Route |
| --- | --- |
| Quick task | do it |
| Small change | `implement` with a ticket (create it with `to-tickets` in its single-ticket form) |
| Project | `to-spec`, which writes the spec from this conversation; then `spec-review` if the stakes warrant it, `to-tickets`, `to-plan`, `implement` |

If it is really several independent projects, say so, agree an order, and grill them one at a time. Keep the grill, the spec and the tickets in one unbroken context where possible; `to-spec` writes from what was said here.

## Red flags

| Thought | Reality |
| --- | --- |
| "I'll offer options to save him effort" | Options steer. Get him describing first; offer a menu only when he is stuck. |
| "I'll fill in sensible defaults" | Fine, said out loud. A default he never heard is one he could not reject. |
| "He said sounds good" | Approval covers what you showed. An unwritten playback is not approved. |
| "The spike works, I'll build on it" | Keeping it is a new request. |
