# Input contract

The renderer takes UTF-8 JSON and an output path. It uses Python's standard
library; no project-specific environment or additional runtime packages are required.
Unknown fields are retained in your JSON but not rendered; keep publisher-specific
labels, idempotency keys and dependency edges there when needed.

## Page

Required: `title`, `eyebrow`, `intro` (strings), `tickets` (array).
`intro` is Markdown; title and eyebrow are plain text.
Optional arrays default to empty:

- `other_actions`: objects with `ref`, `action` (plain strings) and `markdown`.
  Use these for closes, comments and supersessions, including their rationale.
- `panels`: objects with `title` (plain string) and `markdown`. Use these for
  deployment gates, rollout and no-ticket dispositions.

## Ticket

Every ticket requires:

| Field | Value |
| --- | --- |
| `key` | Nonempty string, unique in the wave; stable annotation identity |
| `rank` | Unique nonnegative integer; sheets and index sort ascending |
| `priority` | Integer 0–3, displayed as P0–P3; passed through, not remapped |
| `due` | ISO date string, or `null` displayed as an em dash |
| `title` | Plain string |
| `body` | Exact proposed Kata body, as Markdown |
| `action` | `create` or `update <ref>` |
| `related` | Array of reference strings, possibly empty |
| `spec` | Object with plain `label` and `markdown` containing the implementing section |
| `sources` | Array of source objects, possibly empty |
| `rulings` | Markdown string, empty when there are no operator rulings |

Source fields are strings: `ref`, `from`, `class`, `point`, `quote`, `conflicts`.
`ref`, `from` and `class` are plain text; the rest support Markdown. Put timestamps
or document locations in `from`; keep quotes faithful to the source. An empty
source array shows “No source rows supplied.” An unresolved evidence gap belongs
in the spec or rulings too, rather than silently appearing as settled work.

## Rendering limits

The minimal Markdown subset supports paragraphs, ATX headings, `-`/`*`/`+`
bullets, numbered lists, fenced code, blockquotes, pipe tables, backtick inline
code, asterisk emphasis and strong text. Lists following prose gain a blank line;
two-space nesting/continuations become four spaces. Fenced code stays unchanged.
Use two-space indentation consistently in the input lists.

Raw HTML is escaped. Links and images become visible label/destination text,
not active URLs or fetched images. Other Markdown syntax remains literal text;
convert it into the supported subset in both canonical data and specs before
review if it obscures meaning. Inspect the rendered page before presenting it.

Fonts use local Cambria/Georgia, Helvetica/Arial and Liberation Mono/Menlo stacks.
The skill ships no font binaries: this avoids redistributing font files with
unverified licensing and keeps the skill lightweight. Offline layout and
serif/label/monospace roles survive; exact glyph metrics vary by machine.
