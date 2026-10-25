# docs/

What lives here, and where the rest of the documentation is.

| File | What |
| --- | --- |
| `landscape.html` | The shareable page for the curated skills: the chain, the gates and a pitch per skill. Generated; do not edit by hand. |
| `landscape.toml` | The hand-written copy on that page: hero, chain phases, families and one pitch per skill. Every curated skill in `LANDSCAPE.md` needs a family and a pitch here, and every name here must exist there. |
| `landscape.css` | The page's stylesheet, inlined at render time so the page is one file. |
| `memcap.slice.example` | A systemd user slice that caps memory for commands run through `bin/memcap`. Copy it to `~/.config/systemd/user/memcap.slice`. |

Regenerate the page with `bin/render-landscape` after editing `LANDSCAPE.md`, `landscape.toml` or `landscape.css`. The render fails when the two sources disagree, and pre-commit runs `bin/render-landscape --check` so a stale page cannot be committed.

The rest of the documentation:

- `../README.md`: what the repo is and how to install it.
- `../AGENTS.md`: the rules for working in this repo.
- `../LANDSCAPE.md`: the record behind every curated skill.
- `../conventions/`: the tracker profiles `setup-project` copies into a repo's `.agents/tracker.md`.
- `../.agents/skills/<name>/SKILL.md`: each skill, with its longer material under `references/`.
