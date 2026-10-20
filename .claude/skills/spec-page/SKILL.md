---
name: spec-page
description: >-
  Use when a Markdown spec, plan or decision document should become a styled
  single-file HTML page for reading, sharing or annotated review.
---

# Render a spec page

The Markdown is the source; the page is generated beside it and never edited by
hand. The page gives a long, table-heavy spec a sticky contents rail, an optional
cost ladder, pills for fact marks, tinted open questions and linkable decision ids,
in light and dark themes, with no network dependencies.

Resolve this skill's directory as `<skill-dir>`.

## Steps

1. **Shape the source.** Read the conventions in the docstring of
   `<skill-dir>/scripts/spec_page.py`. The renderer picks them up from ordinary
   Markdown: the `Kind: Title` H1, the status line before the first H2, `Mark`
   columns, `Open` tables and `R1`/`S1`/`O1` ids. Bring the spec onto them where
   it already means the same thing, and leave its wording alone.
   [examples/spec.md](examples/spec.md) uses every one.
   Done when each feature the spec needs has its convention in the source.
2. **Add a ladder only when the spec ranks stages by one number**, such as cost
   per phase. Write the JSON in the shape of [examples/ladder.json](examples/ladder.json),
   taking every value from the spec's own tables so the two cannot disagree.
3. **Render:**

       python3 <skill-dir>/scripts/spec_page.py SPEC.md [-o SPEC.html] [--notice "Internal only"] [--ladder ladder.json]

   In a repository, commit a thin wrapper beside the spec that pins its notice and
   ladder, so anyone can regenerate the page with one command.
4. **Verify in a browser** at about 1400px and 375px wide, in light and dark.
   Done when the page has zero horizontal overflow, no console errors, and every
   section, table row and list item of the source appears in order.
5. **Review.** To collect annotations, open the HTML **file path** in Plannotator
   (`plannotator annotate SPEC.html --gate --json`), never its `http://` URL:
   Plannotator sends a URL that isn't on localhost through a third-party
   converter. Apply feedback to the Markdown, re-render, and reopen the session.

## Changing the design

Keep colours as tokens on `:root`, with the dark set under
`prefers-color-scheme`. Then run `python3 <skill-dir>/tests/test_spec_page.py`
and repeat step 4 on the example.
