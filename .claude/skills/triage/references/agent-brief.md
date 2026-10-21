# Agent brief

Posted as a comment when an issue moves to `ready-for-agent` (or `ready-for-human`). It is the contract; the original body and discussion are context. Write it to survive days in the queue while the code moves.

- Describe interfaces, types, behaviour and config shapes; never file paths or line numbers.
- Say what the system should do, not how to implement it.
- Acceptance criteria are concrete and each independently checkable; they become the ticket's Done-when.
- Say what is out of scope, so the agent does not gold-plate.
- For a PR, "current behaviour" is the state of the diff and the brief says what is left to do to it.

```markdown
## Agent brief

**Category:** bug / enhancement
**Summary:** one line

**Current behaviour:** what happens now (for a bug, the broken behaviour).
**Desired behaviour:** what should happen after, including edge cases and errors.
**Key interfaces:**
- `TypeName`: what changes and why
**Acceptance criteria:**
- [ ] checkable criterion
**Out of scope:**
- adjacent thing not to touch
**Verified:** confirmed / failed / not reproduced, with the code path or command.
```

For `ready-for-human`, add **Why not delegated:** judgment calls, external access, design decisions or manual testing.
