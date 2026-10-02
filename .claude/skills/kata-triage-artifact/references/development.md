# Renderer development

Run `sh scripts/check.sh` from this skill directory. The checks require Python,
Node/npm and network access to npm (or cached packages); they pin Prettier,
Stylelint and HTML Validate versions. Rendering itself needs only Python's stdlib.

The check runs renderer tests, source formatting, CSS lint, JavaScript syntax and
HTML validation of the page template and both rendered examples. Generated HTML
is also prettified in a temporary directory. To format edited sources:

```sh
npm exec --yes --package prettier@3.8.1 -- prettier --write \
  '**/*.{css,html,js,json,md}' .htmlvalidate.json .stylelintrc.json
```

Python follows the repository's Ruff/ty pre-commit checks. Keep fonts bundled with
their licence records; test that outputs stay below Plannotator's 2MB limit and
fetch no external resources. Raw Markdown/code content must survive rendering.

`assets/page.html` is a readable, lintable skeleton. Commented `$slots` are
substituted once by the renderer; inserted data never becomes another template.
CSS and theme JavaScript are inlined into each output, as are font bytes/notices.

## Demo privacy

`examples/meeting-triage.json` demonstrates reference truncation, cached skips
before a read, and quantities duplicated across order lines. All records,
dialogue, references and dates are fictional; no original meeting quotes or
identifying source material is shipped.
