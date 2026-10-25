---
name: spec-page
description: >-
  Use when a Markdown spec, plan or decision document should become a styled
  single-file HTML page for reading, sharing or annotated review, such as a
  long or table-heavy draft at the to-spec gate.
---

# Render a spec page

The Markdown is the source; the page is generated beside it and never edited by
hand. The page gives a long, table-heavy spec a sticky contents rail, tinted open
items with a count in the header, linkable row ids and an optional cost ladder,
in light and dark themes, with no network dependencies.

Resolve this skill's directory as `<skill-dir>`.

## Steps

1. **Check the source.** A spec in the `to-spec` template
   (`to-spec/references/spec-template.md`) renders as written: the facts line
   under the title, every section in the rail, the Decisions table, the
   Acceptance cases and the Open items. The docstring of
   `<skill-dir>/scripts/spec_page.py` lists the optional extras (fact marks, row
   ids, lead rows); use one only where the spec already means the same thing,
   and leave its wording alone. [examples/spec.md](examples/spec.md) is a
   template-shaped spec that uses each.
   Done when every feature the spec needs has its convention in the source.
2. **Add a ladder only when the spec ranks stages by one number**, such as cost
   per phase. Write the JSON beside the spec in the shape of
   [examples/ladder.json](examples/ladder.json), taking every value from the
   spec's own tables so the two cannot disagree.
3. **Render** beside the source:

       python3 <skill-dir>/scripts/spec_page.py .scratch/specs/<date>-<slug>.md [--notice "Internal only"] [--ladder ladder.json]

   The page lands next to the Markdown as `<date>-<slug>.html` (`-o` to change it).
4. **Verify in a browser** at about 1400px and 375px wide, in light and dark.
   Done when the page has zero horizontal overflow, no console errors, and every
   section, table row and list item of the source appears in order.
5. **Review.** To collect annotations, open the HTML **file path** in Plannotator
   (`plannotator annotate <date>-<slug>.html --gate --json`), never its `http://`
   URL: Plannotator sends a URL that isn't on localhost through a third-party
   converter. Apply feedback to the Markdown, re-render, and reopen the session.
   The Markdown stays the file that is edited and approved.

## Changing the design

Keep colours as tokens on `:root`, with the dark set under
`prefers-color-scheme` and `[data-theme="dark"]`. Then run
`python3 <skill-dir>/tests/test_spec_page.py` and repeat step 4 on the example.
