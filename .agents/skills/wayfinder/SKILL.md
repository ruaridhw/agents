---
name: wayfinder
description: Chart a foggy effort too big for one session as a shared map of decision tickets on the tracker, resolve them one at a time until the way to the destination is clear, then hand off to to-spec. Use when work is too big and foggy for one session, when asked to "map this out", "chart the way" or "wayfind", or when intake routes a loose idea whose route is not visible yet.
upstream:
  - repo: mattpocock
    path: skills/engineering/wayfinder/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/engineering/wayfinder/agents/openai.yaml
    sha: 49dd158d1076134a641b33efb035946536778336
---

# wayfinder

**Announce at start:** "Using wayfinder to chart this effort as a map of decision tickets."

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **shared map** on the repo's issue tracker, then works its **decision tickets** (questions whose resolution is a decision, not slices of a build to execute) one at a time until the route is clear.

The destination varies per effort, and naming it is the first act of charting: it shapes every ticket. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

## When to reach for it

The trigger is narrow. The effort must be larger than one agent session can hold, and the route to the destination must be unclear. The split is sessions, not size:

| What you have in front of you | What runs |
| --- | --- |
| A well-scoped change you can settle in one sitting | `clarify`, then `implement` |
| An idea that needs an interview, with the route already clear | `grill`, then `to-spec` |
| A big effort whose route is still fog | this map |
| A thread where the deciding is already done | `to-spec`, skipping the map |
| A map that has cleared | `to-spec`, then `to-tickets` and `implement` |

Greenfield is not a requirement. On legacy and half-built code much of the fog is "what is already true here" rather than "what should we do", and a map is often more useful there, not less.

It plans and does not build. Every ticket asks a question, and the answer is a decision, not a slice of a build. The map is finished when nothing is left to decide before someone builds the thing. That rule is what separates a map ticket from an implementation ticket, and it is the one agents break most often: the pull to just do the work is the signal that you have reached the edge of the map and it is time to hand off.

## The map

The map is a single issue on the repo's tracker, kind `map`, the canonical artifact; its tickets are child issues, kind `decision`. The map is an **index, not a store**: a decision lives in exactly one place, its ticket, so the map gists it and links, never restates it. A session loads the map at low resolution and zooms into individual tickets when it needs them.

`references/map-mode.md` is the whole of it, and it is the thing to read before the first tracker write: plan, don't do; refer by name, never a bare id; the map body's five sections (Destination, Notes, Decisions so far, Not yet specified, Out of scope); tickets sized to one session and claimed by assignment before any work; blocking through the tracker's native relation, with the frontier as the open, unblocked and unclaimed children; the four ticket types with which are HITL and which AFK; fog of war and the fog-or-ticket test; out of scope; and both invocation modes, **chart the map** and **work through the map**.

**The tracker and its operations:** `.agents/tracker.md` names the tracker, its kinds and its exact create, parent and blocked-by commands. Without it, ask Ruaridh to run `setup-project`. Research tickets run in Herdr panes (`herdr`, cheap role) through `research`.

## Hand off

When the way is clear, `to-spec` collapses the map's decisions into a spec, and the map is done. Do not loop straight into `implement` unless the effort turned out small enough for one plan.
