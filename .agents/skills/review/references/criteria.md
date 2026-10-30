# Review criteria

What a reviewer judges a diff against. `SKILL.md` holds the procedure; this file holds the standards, so a reviewer that cannot run the procedure (a PR bot loading rule files, a pane with no skill) can still be pointed at the criteria alone.

## The spec is a vision document

The spec says what the software must do; it does not enumerate every input, environment or condition the software will meet. For behaviour the spec is silent on, judge by what a reasonable person using this software would expect: that expectation is a requirement, and silence is not permission. Grade such a finding by its effect on that person, not by whether the spec names the trigger.

## Standards sources

Search the repo for every file that documents how code should be written. When `CODING_STANDARDS.md` or `CONTRIBUTING.md` exists, it must be on the list. `.agents/` files count where they carry rules (a build loop's commit rules, a tracker's comment rules), and a documented `AGENTS.md` rule is a standard.

When the repo has `.agents/review.md`, it names, per surface (a path pattern), the checks that must run on every review of a diff touching that surface and the rules that are hard violations there. Its rules join the standards sources as documented repo rules. Findings from the checks it names are Act-on findings.

## Documented rules are hard violations

A finding that cites a documented repo rule (file and the rule) is a hard violation unless another documented rule contradicts it. It ranks with the Act-on findings rather than disappearing among the smells. Skip anything tooling already enforces.

## Smell baseline

The Standards axis always carries a fixed set of Fowler code smells (_Refactoring_, ch.3), which applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.
