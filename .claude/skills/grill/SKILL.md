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

Interview Ruaridh relentlessly until you reach a shared understanding. Map the idea as a **design tree**: every decision branches into the decisions that hang off it.

You are very good at building. You build what you believe he wants, and that belief is usually thinner than it feels. This skill is for finding out what he actually wants, and why, before anything gets built. People often have not finished working out what they want; good questions help them think it through. When you understand the why, you make the hundred decisions he never mentions the way he would have made them.

The session ends with a playback, a size and a route, not with code. It stands alone, and it is where `ruaridh-mode`'s chain starts for a project.

## Before the first question

**What do you actually know?** Before you reply, ask yourself: what do I know about what he wants, and why?

- **Everything that matters is in the request** ("make the icon cornflower blue"). This is a quick, clear task. Do it, and say what you did.
- **Something non-trivial is missing.** Start the conversation.

**Frame it, then shape it.** Before starting, ask how a top expert would approach this task (their raw sources, their real methods, an outside check that the result is right), what he is really after, and whether the task is over- or under-specified. Loosen the constraints that do not serve the goal as readily as you add ones that do, and leave the choices that are his open instead of deciding them. Fold in only what makes the work better, not bigger. Always keep one outside check that the result is right. Do not narrate this framing, and do not hand back a rewritten prompt.

**Look first.** Finding facts is your job, never his. Read what exists: the repo and its `.agents/*.md`, the related tickets per `.agents/tracker.md`, prior sessions (AgentsView), and anything he pointed at. When a frontier question needs a fact from the environment (filesystem, tools, a system's behaviour), send an explorer to a Herdr pane (`herdr`): do not ask him anything you could look up yourself. Do not block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the explorer to report; ask the rest of the frontier now. Where a term is doing real work and two of you mean different things by it, `domain` pins it and `.agents/domain.md` holds what the repo has already settled.

## Rounds

**Open with a way out.** The first line of round 1 is one line letting him know that if he would rather skip the questions and have you just start, he can say so. If he takes you up on it, this skill is done: state any significant how-it-gets-made choice (platform, language, medium) in one plain line, then do what he asked through the normal workflow. The opening question itself is an open one that gets him describing: a real moment or a concrete picture ("What's the moment you find yourself wishing this existed?"), never a menu.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you have not heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for his answers before the next round.

The _decisions_ are his: put each to him and wait.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round he answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

**Get him describing.** Open questions come first; his own words carry intent that your options cannot. Offer a short menu only when he is stuck. When he says "just guess" or "what do you think?", propose something concrete. A question is a single sentence with no list of example answers hanging off it. Use plain language, pitched just a little above where he is; match his vocabulary and never use process jargon. Be clear and concise, lead with what matters, and when you report what you found give him the most important findings and offer the rest.

**How it gets made.** Every project rests on choices about medium, tools, materials and resources: the platform, language and libraries for an app; the medium for a piece of art. Find out early which of those choices he wants to make, which he is handing to you, and what he already has to work with. Someone with strong views or skills will want to talk it through. Someone counting on you needs sensible defaults, said in plain words. When there is existing work, build on what it already uses. Any choice you make goes in the playback as your call, never as something he agreed to.

**Ground to cover.** This is territory, not a script. Never read these out as questions:

- what kind of thing this is, and what makes it special
- why now, and what success looks like to him
- goals, non-goals and anti-goals (what would make this a failure even if it technically works)
- prior art: what he has seen elsewhere, loved or hated
- current state: what exists now, what he has tried
- the details he cares about
- which "how it gets made" choices are his and which he is handing to you

**Questions that work** anchor in specifics: "Walk me through the last time...", "If it could only do one of these well, which?", "What would make you wince if I got it wrong?" A guess he can correct ("I am guessing this is because X keeps biting you?") often beats a question.

**Think wide privately.** Before you propose anything, come up with several ideas and drop the weak ones, including any that fight what he has told you about why. Show the comparison only when it helps him decide.

**Spike to feel things out.** Agentic work is waterfall, but very, very fast. A quick throwaway build is often the cheapest way to learn what he wants or whether something works. If running something would settle a question (behaviour, timing, output, layout), run it or build the spike instead of asking. Offer a spike when it would help; when he just wants to spike, get out of the way. Spikes get no tests or minimal ones, are not bulletproof, and skip the plan, implementation and review process. Bring what the spike taught you back into the conversation. A spike stays throwaway: keeping it is a new request.

## Show, don't tell

**Offer the visual companion just in time.** Offer it the first time one of these comes up, never upfront: something he will look at (a screen, a page, a printout, a sign); a layout or arrangement (of a screen, a room, a schedule); a flow or sequence of steps; options that would look different from each other; a structure that is easier to see than read (a diagram, a timeline, a map).

The offer is its own message with nothing else in it:

> "This might be easier if I show you. Want me to mock it up?"

If he declines, stay in text and do not offer again unless he raises it. Once he accepts, use it for mockups to react to, side-by-side options, and throwaway prototypes he can click.

It is a tool, not a mode: accepting it does not send every question to a mock. Decide per question: would he understand this better by seeing it? Requirements, scope, tradeoffs and conceptual choices stay in text, and a question about a UI topic is not automatically a visual question. Read `references/visual-companion.md` for what belongs in a mock and how to make one.

## Play it back

Play back as you go. As soon as you understand one part well enough to describe it (what it is for and who it serves, say, or how one piece behaves), describe that part back in about 200-300 words, then return to questions about the next part. Playback and questions alternate through the whole conversation; the last chunk covers whatever is left.

Mark anything you are guessing as your guess; only what he said goes in as his. End each chunk by asking what is wrong or missing.

Before you send a chunk, check it: does it describe something he will look at, like a page, a screen, a schedule or a printout? If so, and he has not had the offer yet, send the offer instead (its own message) and hold the chunk for the next message. Once he has accepted, put a mock next to the description.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until he confirms you have reached a shared understanding. A playback he has not confirmed is not approval.

## Size and route

Once you understand what he wants, pick a size and say it in plain words. He can override it.

| Size | The full description | Then |
| --- | --- | --- |
| A quick, clear task | the request itself | do it |
| A small change | in chat | `implement` with a ticket, created with `to-tickets` in its single-ticket form |
| A project with a written design | a spec, which `to-spec` writes from this conversation | `spec-review` when the stakes warrant it, then `to-tickets`, `to-plan`, `implement` |

If it grows mid-task, stop, say so, and step up a size.

If this is really several independent projects, say so, agree an order, and grill them one at a time.

Keep the grill, the spec and the tickets in one unbroken context where possible. `to-spec` writes from what was said here, so nothing gets re-asked.

## Away from the chat

When he is not in the chat, send each round as one Inbox message and wait for the reply before the next round: ask per the Inbox convention (`ruaridh-mode`, `references/tooling.md`). The visual companion waits for his answer to the offer; do not build mocks he has not asked to see.

## Red flags

| Thought | Reality |
| --- | --- |
| "I'll offer options to save him effort" | Options steer. Ask him to describe it first. |
| "I'll fill in sensible defaults" | Good. Say them out loud. A default he never heard is one he could not reject. |
| "I should explain the process first" | Ask your question. The process shows itself. |
| "He said sounds good to the idea" | Approval covers what you showed him. A description you have not played back is not approved. |
| "The spike works, I'll keep building on it" | Keeping it is a new request, back through the playback and the size call. |
| "The frontier looks empty, so I'll start" | Empty and confirmed are different. The route is named only after he confirms. |
| "I'll ask him for the fact" | Finding facts is your job; only decisions are his. |
