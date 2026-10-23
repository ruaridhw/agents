---
name: teach
description: "Teach a topic over multiple sessions in a workspace of lessons and reference documents, or explain a body of work plainly in one conversation so the person actually understands it. Use when asked to \"teach me\", \"help me learn X\", \"explain this so I really get it\", or to explain a change, subsystem or decision at a person's pace."
upstream:
  - repo: mattpocock
    path: skills/productivity/teach/SKILL.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/teach/MISSION-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/teach/RESOURCES-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/teach/LEARNING-RECORD-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: mattpocock
    path: skills/productivity/teach/GLOSSARY-FORMAT.md
    sha: 49dd158d1076134a641b33efb035946536778336
  - repo: pstack
    path: pstack/skills/teach/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
  - repo: pstack
    path: pstack/skills/how/SKILL.md
    sha: 2f8377461fd533f5af782e1fd643783b1067b847
---

# teach

Two shapes of teaching, and the same goal in both: the person understands, not that anything gets changed.

- **A curriculum over sessions.** A topic learned properly takes more than one sitting, and the work is stateful: a mission, trusted resources, lessons, and a record of what has been learned. That is the workspace below.
- **An explanation in one conversation.** "Explain this change to me", "help me understand this subsystem". That is the body-of-work shape further down, and it runs `research` rather than building a workspace.

Pick the shape from the ask. "Teach me Rust" is the first; "explain how this cache works" is the second; "teach me this subsystem" is the second with a reference document or two as the artefact.

## The teaching workspace

Treat the workspace directory as the teaching workspace. Paths (`./lessons/`, `./reference/` and the rest) resolve from there; only the `references/*-format.md` links resolve from this skill's folder. In a code repo, the workspace is `.scratch/teach/<topic>/`, which is gitignored, so lessons never land in the repository. Ruaridh names the directory when he wants it elsewhere.

The state of the learning is captured there in several files:

- **`MISSION.md`**: the *reason* he is interested in the topic. Every teaching decision is grounded in it. Format: `references/mission-format.md`.
- **`./reference/*.html`**: the reference materials, the compressed learnings from the lessons: cheat sheets, reference algorithms, syntax, poses, glossaries. They are the raw units of learning, they should be beautiful documents that print out well, and they are designed for quick reference.
- **`RESOURCES.md`**: the resources that ground the teaching in contextual knowledge, or that build knowledge and wisdom. Format: `references/resources-format.md`.
- **`./learning-records/*.md`**: what he has learned. Loosely the equivalent of architectural decision records: non-obvious lessons and key insights that may need revising later or that drive future sessions. They are what the zone of proximal development is calculated from. Titled `0001-<dash-case-name>.md`, the number incrementing each time. Format: `references/learning-record-format.md`.
- **`./lessons/*.html`**: the lessons. A **lesson** is a single, self-contained HTML output that teaches one tightly scoped thing tied to the mission. It is the primary unit of teaching.
- **`./assets/*`**: reusable **components** shared across lessons.
- **`NOTES.md`**: a scratchpad for preferences about how he wants to be taught, and working notes.

The workspace's glossary is not the repo's. A teaching workspace has its own `GLOSSARY.md`, in the format of `references/glossary-format.md`, and it is a record of compressed knowledge rather than the project's domain model (`domain` owns that one).

### Philosophy

To learn at a deep level, a person needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly relevant interactive lessons devised by the teacher, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before `RESOURCES.md` is well populated, the focus is finding high-quality resources that build knowledge. Never trust parametric knowledge.

Some topics need more skills than knowledge. Learning theoretical physics is more knowledge-based; yoga is more skills-based.

**Fluency versus storage strength.** Split two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge.
- **Storage strength**: long-term retention.

Fluency can give an illusory sense of mastery, but storage strength is the real goal. Design lessons that build long-term retention through desirable difficulty: retrieval practice (recall from memory), spacing (practice distributed over time), and interleaving (mixing related topics in practice, for skills only).

### Lessons

A lesson is the main thing produced: the unit in which knowledge and skills reach him. Each lesson is one self-contained HTML file, saved to `./lessons/` and titled `0001-<dash-case-name>.html`, the number incrementing each time.

A lesson should be **beautiful**, with clean, readable typography and layout, because he will return to it later to review. Think Tufte.

The lesson should be short and completable very quickly: a learner's working memory is small and the lesson stays inside it. But each lesson gives one tangible win to build on. It is tied directly to the mission, and it sits in his zone of proximal development.

Every lesson:

- links, through HTML anchors, to the other lessons and reference documents it relates to.
- recommends a **primary source** to read or watch: the highest-quality, highest-trust resource found on that topic.
- carries a reminder to ask follow-up questions. The agent is his teacher.

Lessons can be opened for him (a `file://` link, or the path when the browser is on another machine).

### Assets

Lessons are built from reusable **components**, stored in `./assets/`: stylesheets, quiz widgets, simulators, diagram helpers, and anything else a second lesson could reuse.

Reuse is the default, not the exception. Before authoring a lesson, read `./assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link to it; never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns: every lesson links it, so the lessons look like one consistent course rather than a pile of one-offs. As the workspace grows, so should the component library.

### The mission

Every lesson is tied to the mission, the reason he is interested in the topic.

If he is unclear about the mission, or `MISSION.md` is not populated, the first job is to question him on why he wants to learn this. Failing to understand the mission means knowledge acquisition is not grounded in real-world goals: lessons feel abstract, and there is no way to judge what he should do next.

Missions change as skills and knowledge develop. That is normal: update `MISSION.md` and add a learning record that captures the change, and confirm with him before changing the mission.

### Zone of proximal development

Each lesson should feel like being challenged "just enough".

He may name an exact thing he wants to learn. If he does not, work out his zone of proximal development from his `learning-records`, from the right next thing for his mission, and teach the most relevant thing that fits.

### Knowledge

Lessons are designed around a skill he is going to learn. The knowledge in the lesson is only what is required to acquire that skill: knowledge first, then practice through an interactive feedback loop.

Knowledge comes first from trusted resources, tracked in `RESOURCES.md`. Lessons are littered with citations, links to external resources backing up any claim, which is what makes a lesson trustworthy.

For acquiring knowledge, difficulty is the enemy. It eats working memory that understanding needs.

### Skills

If knowledge is about acquisition, skills are about durability and flexibility: making the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills are taught through interactive lessons, with several tools available:

- Interactive lessons, using quizzes and light in-browser tasks.
- Lessons that guide him through a list of real-world steps to take (yoga poses, for instance).

Each rests on a **feedback loop** where he gets feedback on his performance, as tight as possible, immediate and ideally automatic.

For quizzes, each answer is the same number of words (and characters, if possible). Vary which position holds the correct answer across questions. Give no clue through formatting or order.

### Acquiring wisdom

Wisdom comes from real-world interaction: testing skills outside the learning environment.

When he asks a question that seems to need wisdom, the default is to attempt an answer, then ultimately to delegate to a **community**: a place, online or offline, where he can test his skills in the real world. A forum, a subreddit, a class, a local interest group.

Find high-reputation communities he can join. If he says he does not want to join a community, respect it.

### Reference documents

While creating lessons, create reference documents too. Lessons can link to them, and they track the raw units of knowledge useful across lessons.

Lessons are rarely revisited; reference documents are. They are the compressed essence of the lesson, in a format designed for quick reference.

Some topics lend themselves to reference: syntax and code snippets for programming, algorithms and flowcharts for processes, poses and sequences for yoga, exercises and routines for fitness, glossaries for any topic with its own nomenclature.

Glossaries in particular are essential. Once one exists, every lesson adheres to it.

### `NOTES.md`

Preferences about how he wants to be taught, and anything to keep in mind, are recorded here, so they can be referred back to when designing lessons or working with him.

## Explaining a body of work

**Explain what a thing is, how it works, and why it is built that way, in one plain account at his pace. The goal is that he understands it, not that anything changes.**

This shape sits on top of `research`, which owns the how and the why. Get bearings on what the work is and what it touches, run `research`'s how-mode for how it works and its why-mode for why it is that way, then blend what they find into one plain explanation. Those are real skill runs that do their own digging. Lead with what matters to him and go deeper when he asks. Reword freely for teaching, with one exception: keep the why-mode's confidence language intact, because its hedges are findings, not style.

1. **Decide the few things he should walk away understanding.** Choose them from why he is asking (about to change it, reviewing it, debugging it, new to it) and what he already knows, both read from the conversation rather than quizzed out of him. Skip what he plainly knows. Put the depth where his question is.
2. **Let `research` do the work; don't redo it.** Read the code to get oriented, then run the how-mode and the why-mode in parallel panes and combine the results. Match the size to the question: both for a subsystem, one for a small change. Keep the why-mode narrow by default, since its full sweep is slow: put the narrowing in the ask itself (a scoped question, git plus a source or two) so it records the skipped categories per its own contract. Widen it only when the reasons are the point.
3. **Start with a plain definition.** Name the thing and say what it is in general terms, the way a senior engineer would say it out loud, with its common name if it has one. Then tie it to the case in front of him ("in X, we use this to …") and build from there: how it works, the deeper reasons, the edge cases. For each part, explain the idea so it clicks: the problem it solves, and how it actually works. Walk through what happens as he does the thing (opens a long chat, scrolls up) when that is what makes it land. Listing functions and constants is reference, not teaching. Don't print framing labels ("the one idea to hold onto", "the key insight", "at its core", "TL;DR"). Give the smallest complete answer first, a sentence or two rather than a dense paragraph, then stop. Add layers when he asks. Never a wall of text.
4. **Keep it a conversation, not a lecture or a performance.** Offer to go deeper or move on, and follow his lead. No quizzes, no pacing theatre. Don't print "Pause", don't ask him to say it back, don't announce "the sentence to nail", and don't flag a part as important or hard ("here is the part worth slowing down on", "this is the tricky part"). Just say it. When you would pause, stop and let him respond. Running one-shot with no live human, deliver it cleanly and put any offer to go deeper at the end.
5. **Show, don't only tell, and build the picture up diagram by diagram.** Open the diff, the code or the debugger when that is the fastest way to land it. Draw when a picture lands faster than words. For anything with three or more moving parts, do not draw one diagram with all of them at once: draw a short series where each diagram redraws the last and adds a single part, so he watches the system assemble. A single all-at-once diagram, especially one saved for the end, is reference, not teaching. To teach a flow from A to B to C, draw it three times: A to B, then redraw and add C, then redraw and add the return edge or the next piece. Match the medium to the idea, and use both kinds when both help. A Mermaid diagram fits a flow or structure where the labels carry the meaning. When the idea is spatial (layout, overlap, scroll position, a before and after), a generated marker-on-whiteboard-style image with a few short labels lands faster than prose, since image models garble long text. The build-up rule holds for generated images too. A single simple point needs no figure.

## Voice

Write every response in plain spoken English, the way you would explain it to a colleague. Be tight, not terse. Cut filler and hedging, keep the part that makes it click. State the concrete mechanism, not a metaphor, a framing, or a preview of what is coming.

This is the target density: "Virtualization runs in two parts, one for rendering and one for loading from disk. When an item scrolls out past the buffer, both its DOM node and its in-memory data are evicted."

Normal sentence case. No em dashes. Prefer periods over commas, and keep each sentence to one or two commas. If clauses pile up, split them. Give each concept one name and keep it. Avoid mirror sentences ("A without B, or B without A") and tidy closers ("the rest follows", "it all falls out"). The words in these steps are directions, not labels to print: don't echo the structure as headers or stock phrases.

Run the unslop pass from `technical-writing` over anything long enough to be read as a document, such as a lesson's prose or a reference document.

## Rules

- The explanation is the reply, never a report about what was delivered. Lead with the main point, then the plain account of what it is, how it works and why, and the threads worth chasing with `research`.
- A lesson is tied to the mission. No mission, no lesson: ask why first.
- Never trust parametric knowledge when a trusted resource exists, and cite the resource in the lesson.
- The workspace is `.scratch/teach/<topic>/` inside a repo, so lessons and notes never land in the repository, unless he names another directory.
- Do not write lessons into `docs/` or commit them. A lesson he wants kept is a request to move it, and it becomes a normal document with `technical-writing`'s standard applied.
