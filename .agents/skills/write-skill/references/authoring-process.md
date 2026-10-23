# Authoring process

The order to write an ad-hoc skill in, and the structural choices that come up before the prose does.

## Process

1. **Gather requirements.** Ask about: the task or domain the skill covers; the specific use cases it should handle; whether it needs executable scripts or only instructions; reference material to include.
2. **Draft the skill.** `SKILL.md` with the instructions, a reference file per piece of heavy reference, a script where a deterministic operation is worth one.
3. **Review with Ruaridh.** Present the draft and ask: does this cover the use cases, is anything missing or unclear, should any part be more or less detailed.

The skill is his, so the draft is his to redirect. An ad-hoc skill that never got read back is a skill he will not reach for.

## Capture the intent first

The conversation may already contain the workflow the skill is meant to capture: "turn this into a skill". If so, extract the answers from the history first: the tools used, the sequence of steps, the corrections he made, the input and output formats observed. He fills the gaps and confirms before the next step.

Four questions:

1. What should the skill let an agent do?
2. When should it trigger, in his words?
3. What is the expected output?
4. Does it need test cases? Skills with objectively checkable outputs (file transforms, data extraction, fixed steps) can be tested; skills with subjective outputs (writing style, a way of thinking) usually cannot.

No skill evals yet: Ruaridh's decision, 2026-10-22. Question 4 is about whether he wants a manual run-through, not about wiring an eval harness. `testing-skills.md` holds the method for when that changes.

## Skill structure

```
skill-name/
├── SKILL.md           # Main instructions (required)
├── references/        # Detailed docs, read on demand
├── scripts/           # Utility scripts, where a deterministic operation needs one
└── assets/            # Files used in output (templates, fonts)
```

Keep it flat: one skill, one directory, named for the skill.

- `SKILL.md` holds the steps and the reference every branch needs. The **150-line rule** is the ceiling for it: past that, disclose reference behind a pointer or split the skill.
- A separate file for heavy reference (roughly 100 lines or more: API docs, a comprehensive syntax guide) and for a reusable tool.
- Inline what a reader needs at that point: the principles, the short code patterns, anything under about 50 lines.
- A reference file over about 300 lines gets a table of contents at the top, so an agent can see whether its answer is in there before reading it.

## Progressive disclosure

The three-level loading system, in the order an agent meets it:

1. **Metadata** (name and description): in context always.
2. **`SKILL.md` body**: in context whenever the skill triggers, and the 150-line rule keeps this cheap.
3. **Bundled resources**: read only when a pointer fires, and scripts can run without being read at all.

Reference files are pointed at from `SKILL.md` with the condition for reading them, never force-loaded. Keep the pointers in the body, at the point where the branch happens.

**Organise by variant** when one skill covers several domains: `cloud-deploy/SKILL.md` for the workflow and the choice, `references/aws.md`, `gcp.md`, `azure.md` beside it, so only the relevant reference is read.

## Writing patterns

Prefer the imperative. Say what to do, and leave out the argument for it unless the rule is confusing without one.

**Define an output format** when the skill's output must have a shape. State the exact template and say it is exact:

```markdown
## Report structure

Use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Worked examples** earn their tokens when the shape is easier to see than to describe. Mark the input and the output:

```markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

One excellent example beats several mediocre ones. Choose the language the use case actually runs in, and keep the example complete and runnable, from a real scenario, with comments that say why. Do not implement the same thing in five languages, do not write fill-in-the-blank templates, and do not invent contrived examples.

## Writing style

Explain why a rule matters rather than piling on musts. Write for an agent that is already capable: the skill adds what it does not already know and nothing else. Keep the skill general rather than narrowly tied to the one example that prompted it. Start with a draft, then read it again with fresh eyes and cut.

The **principle of no surprise**: a skill must not contain anything that would surprise the person who asked for it if they read it, and never anything designed to mislead a reader or to exfiltrate, escalate or hide what an agent is doing.

## Checklist before it lands

- [ ] The description says when to use it, in his words, with the words he would search for.
- [ ] `SKILL.md` is within the 150-line rule, and anything longer is behind a pointer.
- [ ] Every branch is covered by the body or a named reference.
- [ ] No time-sensitive statement ("currently", "soon", "as of the last release").
- [ ] One name per thing, used everywhere.
- [ ] One concrete example rather than several abstract ones.
- [ ] References are pointed at from the body, one level deep.
- [ ] A script exists where the operation is deterministic, and is invoked through its interpreter (`bash scripts/tool.sh`, `node scripts/tool.js`), never by bare path.
- [ ] Frontmatter format: `bin/skill-lint`'s business, not this checklist's.
