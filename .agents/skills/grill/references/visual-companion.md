# Visual companion

Mockups, diagrams and options for showing instead of describing, without a server: one self-contained HTML file per screen in `.scratch/mocks/`, opened for annotation.

## When to use

Decide per-question, not per-session. The test: **would he understand this better by seeing it than reading it?**

**Use a mock** when the content itself is visual:

- **UI mockups** — wireframes, layouts, navigation structures, component designs
- **Architecture diagrams** — system components, data flow, relationship maps
- **Side-by-side visual comparisons** — comparing two layouts, two colour schemes, two design directions
- **Design polish** — when the question is about look and feel, spacing, visual hierarchy
- **Spatial relationships** — state machines, flowcharts, entity relationships rendered as diagrams

**Stay in the terminal** when the content is text or tabular:

- **Requirements and scope questions** — "what does X mean?", "which features are in scope?"
- **Conceptual A/B/C choices** — picking between approaches described in words
- **Tradeoff lists** — pros and cons, comparison tables
- **Technical decisions** — API design, data modelling, architectural approach selection
- **Clarifying questions** — anything where the answer is words, not a visual preference

A question *about* a UI topic is not automatically a visual question. "What kind of wizard do you want?" is conceptual — use the terminal. "Which of these wizard layouts feels right?" is visual — use the mock.

## The loop

1. Write one self-contained HTML file to `.scratch/mocks/` with a semantic name: `platform.html`, `visual-style.html`, `layout.html`. Never reuse a filename; each screen gets a fresh file, and an iteration appends a version suffix (`layout-v2.html`). Inline the CSS and any script: the file has to stand alone, because there is no frame template to fill in.
2. Open it in the background with `plannotator annotate <path>`, give him the link, and end your turn with a brief text summary of what is on the page and what you want from him ("Showing 3 layout options for the homepage; take a look and tell me which feels right"). Run it in the background and wait for the completion notification; the port changes, so read the link from its output rather than assuming one.
3. On your next turn, his annotations are the answer. Merge them with anything he wrote in the terminal; the terminal message is the primary feedback.
4. Iterate or advance. If the feedback changes the current screen, write a new file (`layout-v2.html`); only move to the next question when the current step is validated.
5. Unload when returning to the terminal: when the next step does not need a mock (a clarifying question, a tradeoff discussion), do not open another one, so he is not left staring at a resolved choice while the conversation has moved on.

Mocks are working files: `.scratch/mocks/` is gitignored and skills never clean it, so he can go back to one later.

## Design tips

- **Scale fidelity to the question** — wireframes for layout, polish for polish questions.
- **Explain the question on the page** — "Which layout feels more professional?" not just "Pick one".
- **Iterate before advancing** — if feedback changes the current screen, write a new version.
- **2-4 options max** per screen.
- **Use real content when it matters** — for a photography portfolio, use actual images. Placeholder content obscures design issues.
- **Keep mockups simple** — focus on layout and structure, not pixel-perfect design.
