# Design It Twice

When the work needs alternative interfaces for a chosen deepening candidate, use this parallel pane pattern. Based on "Design It Twice" (Ousterhout): your first idea is unlikely to be the best.

Uses the deep-module vocabulary in `domain`'s `references/deep-module-vocabulary.md`: **module**, **interface**, **seam**, **adapter**, **leverage**.

## Process

### 1. Frame the problem space

Before spawning the runners, write an explanation of the problem space for the chosen candidate, in the comparison file:

- The constraints any new interface would need to satisfy
- The dependencies it would rely on, and which category they fall into (see [`deepening.md`](./deepening.md))
- A rough illustrative code sketch to ground the constraints, not a proposal, just a way to make the constraints concrete

Put it in the comparison file, then immediately proceed to Step 2. Ruaridh reads and thinks while the runners work in parallel.

### 2. Spawn the runners

Spawn three or more Herdr panes in parallel through `herdr`, on the `builder` role, each in its own worktree or subdirectory. Each must produce a **radically different** interface for the deepened module.

Prompt each runner with a separate technical brief (file paths, coupling details, dependency category from [`deepening.md`](./deepening.md), what sits behind the seam). The brief is independent of the problem-space explanation in Step 1. Give each runner a different design constraint:

- Runner 1: "Minimize the interface: aim for 1–3 entry points max. Maximise leverage per entry point."
- Runner 2: "Maximise flexibility: support many use cases and extension."
- Runner 3: "Optimise for the most common caller: make the default case trivial."
- Runner 4 (if applicable): "Design around ports & adapters for cross-seam dependencies."

Include both the deep-module vocabulary and `GLOSSARY.md` vocabulary in the brief, so each runner names things consistently with the architecture language and the project's domain language.

Each runner outputs:

1. Interface (types, methods, params, plus invariants, ordering, error modes)
2. Usage example showing how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters (see [`deepening.md`](./deepening.md))
5. Trade-offs: where leverage is high, where it's thin

### 3. Present and compare

Present designs sequentially in the comparison file so each one can be absorbed, then compare them in prose. Contrast by **depth** (leverage at the interface), **locality** (where change concentrates), and **seam placement**.

After comparing, give your own recommendation: which design you think is strongest and why. If elements from different designs would combine well, propose a hybrid. Be opinionated: a strong read, not a menu.
