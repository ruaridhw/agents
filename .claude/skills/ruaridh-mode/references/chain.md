# The chain: branches and context

The branches on the way from idea to ship:

- **Does a question need running code to answer (state, business logic, a UI you have to see)?** Detour through `prototype` and bring the answer back to the thread.
- **Is this a multi-session build?** Yes: `to-spec`, then `to-tickets`, each ticket declaring its blocking edges, then `implement` per ticket or delegated across the ready frontier. No: `implement` right here.
- **Bugs and requests piling up**: `triage`. Triage is only for issues you didn't create; tickets `to-tickets` produced are already agent-ready.
- **A huge, foggy effort**: `to-plan --map` charts decision tickets until the way is clear, then hands off to `to-spec`; it never builds.

Keep `grill` → `to-spec` → `to-tickets` in one unbroken context window when you can, so the spec and tickets build on the same thinking. At a phase boundary, decide between continuing, clearing, a handoff, a Herdr pane and compacting with `references/phase-boundaries.md`.
