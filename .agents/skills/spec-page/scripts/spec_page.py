"""Render a Markdown spec as one styled, self-contained HTML page.

    python3 spec_page.py SPEC.md [-o SPEC.html] [--notice TEXT] [--ladder ladder.json]

The Markdown stays the source: edit it, then re-run. Output is byte-stable for
the same inputs.

Supported Markdown: `#`-`###` headings, paragraphs, nested `-`/`1.` lists,
pipe tables, fenced blocks, `>` quotes, `**bold**`, `*italics*`, `` `code` ``,
`[links](url)` and `![images](path)`.

The page reads the spec template of `to-spec` as written:

- The H1 is the title; text between it and the first H2 is the header. A line of
  `Label: value` fields split by two or more spaces (`Spec issue: …   Date: …`)
  shows as labelled facts.
- `##` and `###` headings fill the contents rail.
- A table under `Open items` (or `Open`) is tinted as unresolved, and the header
  links to it with a count of its rows.

Optional extras, for a spec that already means the same thing:

- A table column headed `Mark` or `Source` turns a leading `V`, `I` or `R`
  followed by `:`, `,` or nothing into a Verified / Inference / Ruling pill; so
  does `(V` or `(I` in running text.
- A first cell that is or starts with an id like `R1`, `O3` or `A2.1` becomes an
  anchor (`page.html#O3`).
- A first cell in bold marks a lead row (a parent or headline row).
"""

import argparse
import html
import json
import pathlib
import re

LIST_ITEM = re.compile(r"^( *)([-*]|\d+\.) (.*)$")
MARK_PILL = re.compile(r"\((V|I)(?=[:,)])")
MARK_CELL = re.compile(r"^(V|R|I)(?=$|[:,])")
MARK_CLASS = {"V": ("v", "Verified"), "I": ("i", "Inference"), "R": ("r", "Ruling")}
NUMERIC_HEADERS = ("#", "P", "Deadline")
OPEN_HEADINGS = ("open", "open items", "open questions")
ROW_ID = re.compile(r"[A-Z]{1,3}\d+(?:\.\d+)*(?=\s|$)")
FACT = re.compile(r"([A-Z]\w*(?: \w+){0,2}): (\S.*)")
LINK = re.compile(r"(!?)\[([^\]]+)\]\(([^)\s]+)\)")


def safe_url(url):
    return "#" if re.match(r"(?i)\s*(javascript|data|vbscript):", url) else url


def link(m):
    text, url = m[2], html.escape(safe_url(html.unescape(m[3])))
    if m[1]:
        alt = text.replace('"', "&quot;")
        return f'<img src="{url}" alt="{alt}">'
    return f'<a href="{url}">{text}</a>'


def pill(mark):
    cls, label = MARK_CLASS[mark]
    return f'<span class="mark mark-{cls}" title="{label}">{mark}</span>'


def inline(text):
    """Escape and apply code, bold and italics; code spans stay literal."""
    out: list[str] = []
    for i, part in enumerate(re.split(r"(`[^`]*`)", text)):
        if i % 2:
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        s = html.escape(part, quote=False)
        s = LINK.sub(link, s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
        s = MARK_PILL.sub(lambda m: "(" + pill(m[1]), s)
        out.append(s)
    return "".join(out)


def slug(text):
    m = re.match(r"(\d+(?:\.\d+)?)\.?\s", text)
    if m:
        return "s" + m[1].replace(".", "-")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def split_row(line):
    cells = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in cells]


def is_numeric(header):
    return (
        header.startswith(("$", "£", "€", "×", "%"))
        or header in NUMERIC_HEADERS
        or header.lower().startswith("spend")
    )


def is_open(context):
    return re.sub(r"^\d+(\.\d+)*\.?\s", "", context).lower() in OPEN_HEADINGS


def table(lines, context, seen):
    head, _, *body = lines
    cols = split_row(head)
    mark_col = next((i for i, c in enumerate(cols) if c in ("Mark", "Source")), None)
    numeric = [is_numeric(c) for c in cols]
    cls = (
        "data"
        + (" open" if is_open(context) else "")
        + (" wide" if len(cols) >= 4 else "")
    )
    out: list[str] = [f'<div class="table-wrap"><table class="{cls}"><thead><tr>']
    out += [
        f'<th{" class=num" if numeric[i] else ""} scope="col">{inline(c)}</th>'
        for i, c in enumerate(cols)
    ]
    out.append("</tr></thead><tbody>")
    for row in body:
        cells = split_row(row)
        m = ROW_ID.match(cells[0])
        rid = m[0] if m and m[0] not in seen else None
        if rid:
            seen[rid] = 1
        attrs = (f' id="{rid}"' if rid else "") + (
            ' class="lead"' if cells[0].startswith("**") else ""
        )
        out.append(f"<tr{attrs}>")
        for i, c in enumerate(cells):
            body_html = inline(c)
            if i == mark_col and (m := MARK_CELL.match(c)):
                body_html = pill(m[1]) + " " + inline(c[1:].lstrip(":, "))
            tag = "th scope=row" if i == 0 else "td"
            klass = ' class="num"' if i < len(numeric) and numeric[i] else ""
            if i == 0 and (ROW_ID.fullmatch(c) or re.fullmatch(r"`[^`]*`", c)):
                klass = ' class="rid"'
            out.append(f"<{tag}{klass}>{body_html}</{tag.split()[0]}>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def unique(hid, seen):
    n = seen.get(hid, 0)
    seen[hid] = n + 1
    return f"{hid}-{n + 1}" if n else hid


def blocks(lines, seen, context=""):
    """Render a run of Markdown lines; returns (html, headings).

    `seen` counts the ids already used on the page, so every id stays unique.
    """
    out, heads, i = [], [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith("<!--"):
            i += 1
        elif line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            code = html.escape("\n".join(lines[i + 1 : j]))
            out.append(f'<div class="flow"><pre>{code}</pre></div>')
            i = j + 1
        elif m := re.match(r"(#{1,3}) (.*)", line):
            level, text = len(m[1]), m[2]
            hid = unique(slug(text), seen)
            heads.append((level, hid, text))
            context = text
            out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
            i += 1
        elif line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            out.append(table(lines[i:j], context, seen))
            i = j
        elif line.startswith(">"):
            j = i
            while j < len(lines) and lines[j].startswith(">"):
                j += 1
            quoted = [re.sub(r"^> ?", "", q) for q in lines[i:j]]
            out.append(f"<blockquote>{blocks(quoted, seen, context)[0]}</blockquote>")
            i = j
        elif LIST_ITEM.match(line):
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                if nxt.strip() and not nxt.startswith(" ") and not LIST_ITEM.match(nxt):
                    break
                if not nxt.strip():
                    k = j + 1
                    while k < len(lines) and not lines[k].strip():
                        k += 1
                    if k >= len(lines) or not (
                        lines[k].startswith(" ") or LIST_ITEM.match(lines[k])
                    ):
                        break
                j += 1
            out.append(listing(lines[i:j], seen))
            i = j
        else:
            j = i
            while (
                j < len(lines)
                and lines[j].strip()
                and not re.match(r"#|\||```|>", lines[j])
                and not LIST_ITEM.match(lines[j])
            ):
                j += 1
            out.append(
                f"<p>{inline(' '.join(part.strip() for part in lines[i:j]))}</p>"
            )
            i = j
    return "\n".join(out), heads


def listing(lines, seen):
    first = LIST_ITEM.match(lines[0])
    assert first, lines[0]
    base = len(first[1])
    tag = "ol" if first[2][0].isdigit() else "ul"
    items: list[list[str]] = []
    for line in lines:
        m = LIST_ITEM.match(line)
        if m and len(m[1]) == base:
            items.append([m[3]])
        else:
            items[-1].append(
                line[base + 2 :] if line.startswith(" " * (base + 2)) else line.strip()
            )
    out: list[str] = [f"<{tag}>"]
    for item in items:
        while item and not item[-1].strip():
            item.pop()
        lead = []
        while item and item[0].strip() and not LIST_ITEM.match(item[0]):
            lead.append(item.pop(0).strip())
        rest, _ = blocks(item, seen)
        out.append(f"<li>{inline(' '.join(lead))}{rest}</li>")
    out.append(f"</{tag}>")
    return "".join(out)


def ladder(spec):
    """A ranked bar list: one row per stage, bars scaled to the largest value."""
    rows, unit = spec["rows"], spec.get("unit", "")
    digits = spec.get("decimals", 2)
    top = max(r["value"] for r in rows) or 1
    items: list[str] = []
    for r in rows:
        width = max(r["value"] / top * 100, 1.2)
        name = f'<span class="lk">{inline(r["key"])}</span><span class="ln">{inline(r["label"])}</span>'
        name = (
            f'<a href="#{r["anchor"]}">{name}</a>'
            if r.get("anchor")
            else f'<span class="lname">{name}</span>'
        )
        items.append(
            f'<li>{name}<span class="lbar"><span style="width:{width:.1f}%"></span></span>'
            f'<span class="lv">{unit}{r["value"]:,.{digits}f}</span><span class="lw">{inline(r.get("aside", ""))}</span></li>'
        )
    note = f'<p class="fine">{inline(spec["note"])}</p>' if spec.get("note") else ""
    return (
        f'<section class="ladder" aria-labelledby="ladder-h"><h2 id="ladder-h" class="quiet">{inline(spec["title"])}</h2>'
        f"<ol>{''.join(items)}</ol>{note}</section>"
    )


DARK = """
    color-scheme: dark;
    --paper: #121211; --surface: #1a1a19; --rule: #383835; --grid: #2a2a28;
    --ink: #f0efec; --ink-2: #c3c2b7; --ink-3: #9a988f; --accent: #6da7ec;
    --v: #4cc44c; --v-wash: #183318; --i: #e0b45a; --i-wash: #3a2e14; --r: #8fbdf2; --r-wash: #1a2c44;
    --warn: #ef9a5a; --warn-wash: #3a2416; --alert: #e66767;
"""

CSS = (
    """
:root {
  color-scheme: light;
  --paper: #f7f6f2; --surface: #fcfcfb; --rule: #dedcd5; --grid: #ebe9e3;
  --ink: #1b1b19; --ink-2: #52514e; --ink-3: #75736d; --accent: #2a78d6;
  --v: #0a7d0a; --v-wash: #e3f1e1; --i: #8a5a00; --i-wash: #f7ecd2; --r: #1c5cab; --r-wash: #e1ecf9;
  --warn: #b5530f; --warn-wash: #fbeee3; --alert: #b42f2f;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {"""
    + DARK
    + """  }
}
:root[data-theme="dark"] {"""
    + DARK
    + """}
* { box-sizing: border-box; }
html { scroll-padding-top: 16px; }
body { margin: 0; background: var(--paper); color: var(--ink);
  font: 15px/1.6 ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.page { max-width: 1240px; margin: 0 auto; padding: 40px 24px 64px; display: grid;
  grid-template-columns: 220px minmax(0, 1fr); gap: 0 48px; }
nav.toc { position: sticky; top: 24px; align-self: start; max-height: calc(100vh - 48px); overflow-y: auto;
  font-size: 13px; padding-right: 4px; }
nav.toc summary { font-weight: 600; color: var(--ink-2); cursor: pointer; list-style: none; margin-bottom: 8px; }
nav.toc summary::-webkit-details-marker { display: none; }
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc li { margin: 0; max-width: none; }
nav.toc a { display: block; padding: 4px 8px; color: var(--ink-2); text-decoration: none; border-left: 2px solid var(--rule); }
nav.toc a:hover { color: var(--ink); border-left-color: var(--ink-3); }
nav.toc a[aria-current="true"] { color: var(--ink); border-left-color: var(--accent); font-weight: 600; }
nav.toc .sub a { padding-left: 20px; font-size: 12.5px; }
main { min-width: 0; }
header { border-bottom: 2px solid var(--ink); padding-bottom: 18px; margin-bottom: 8px; }
h1 { font-size: 32px; line-height: 1.15; margin: 0 0 12px; letter-spacing: -0.015em; }
.notice { display: inline-block; font-size: 13px; font-weight: 600; color: var(--alert);
  border: 1px solid currentColor; border-radius: 3px; padding: 1px 8px; margin-right: 10px; }
.meta { color: var(--ink-2); font-size: 14px; }
.meta p { margin: 0 0 6px; max-width: none; }
.facts { display: flex; flex-wrap: wrap; gap: 4px 20px; }
.facts b { font-weight: 600; color: var(--ink-3); margin-right: 4px; }
.open-count a { display: inline-block; font-size: 13px; font-weight: 600; color: var(--warn); background: var(--warn-wash);
  border-radius: 3px; padding: 1px 8px; text-decoration: none; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; font-size: 13px; color: var(--ink-2); }
h2 { font-size: 21px; margin: 52px 0 8px; padding-top: 16px; border-top: 1px solid var(--rule); letter-spacing: -0.005em; }
h2.quiet { font-size: 13px; font-weight: 600; color: var(--ink-2); border: 0; margin: 24px 0 10px; padding: 0; }
h3 { font-size: 16px; margin: 30px 0 6px; }
main > p, main li { max-width: 74ch; }
ul, ol { padding-left: 22px; }
li { margin: 4px 0; }
li > ul, li > ol, li > p { margin-top: 4px; }
main a { color: var(--accent); }
img { max-width: 100%; height: auto; }
blockquote { margin: 12px 0; padding: 2px 16px; border-left: 3px solid var(--rule); color: var(--ink-2); }
code { font: 12.5px ui-monospace, SFMono-Regular, Menlo, monospace; background: var(--grid); padding: 1px 4px; border-radius: 3px;
  overflow-wrap: anywhere; }
strong { font-weight: 650; }
.mark { display: inline-block; min-width: 18px; text-align: center; font: 600 11px/17px ui-monospace, SFMono-Regular, Menlo, monospace;
  border-radius: 3px; padding: 0 4px; vertical-align: 1px; }
.mark-v { color: var(--v); background: var(--v-wash); }
.mark-i { color: var(--i); background: var(--i-wash); }
.mark-r { color: var(--r); background: var(--r-wash); }
.ladder { margin: 6px 0 4px; }
.ladder ol { list-style: none; padding: 0; margin: 0; border: 1px solid var(--rule); background: var(--surface); }
.ladder li { display: grid; grid-template-columns: minmax(0, 300px) minmax(80px, 1fr) 62px 88px; align-items: center;
  gap: 14px; padding: 9px 14px; margin: 0; max-width: none; border-top: 1px solid var(--grid); }
.ladder li:first-child { border-top: 0; }
.ladder a, .ladder .lname { color: inherit; text-decoration: none; display: flex; gap: 10px; align-items: baseline; min-width: 0; }
.ladder a:hover .ln { text-decoration: underline; }
.lk { font-weight: 700; min-width: 52px; font-variant-numeric: tabular-nums; }
.ln { color: var(--ink-2); font-size: 13.5px; }
.lbar { height: 12px; background: var(--grid); border-radius: 2px; overflow: hidden; }
.lbar span { display: block; height: 100%; background: var(--accent); }
.ladder li:last-child .lbar span { background: var(--v); }
.lv { font-weight: 650; text-align: right; font-variant-numeric: tabular-nums; }
.lw { color: var(--ink-3); font-size: 13px; text-align: right; font-variant-numeric: tabular-nums; }
.fine { font-size: 12.5px; color: var(--ink-3); margin: 8px 0 0; max-width: 90ch; }
.table-wrap { overflow-x: auto; margin: 12px 0 16px; border: 1px solid var(--rule); background: var(--surface); }
table { border-collapse: collapse; width: 100%; font-size: 13.5px; line-height: 1.5; }
table.wide { min-width: 720px; }
th, td { padding: 7px 12px; border-bottom: 1px solid var(--grid); text-align: left; vertical-align: top; }
tbody tr:last-child > * { border-bottom: 0; }
thead th { font-size: 12.5px; color: var(--ink-2); font-weight: 600; border-bottom: 1px solid var(--rule); vertical-align: bottom; background: var(--paper); }
tbody th { font-weight: 400; }
td { min-width: 12ch; }
tbody th.rid { white-space: nowrap; font-weight: 600; }
th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.lead > * { background: var(--paper); }
tr:target > * { background: var(--r-wash); }
table.open tbody tr > th:first-child { box-shadow: inset 3px 0 0 var(--warn); }
table.open tbody tr > * { background: var(--warn-wash); }
.flow { overflow-x: auto; margin: 12px 0 16px; border: 1px solid var(--rule); background: var(--surface); padding: 14px 16px; }
.flow pre { margin: 0; font: 12.5px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; color: var(--ink); }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
footer { margin-top: 56px; padding-top: 14px; border-top: 1px solid var(--rule); font-size: 12.5px; color: var(--ink-3); }
@media (max-width: 980px) {
  .page { display: block; padding: 24px 16px 48px; }
  nav.toc { position: static; max-height: none; border: 1px solid var(--rule); background: var(--surface); padding: 10px 12px; margin-bottom: 20px; }
  nav.toc summary { margin: 0; }
  nav.toc details[open] summary { margin-bottom: 8px; }
  h1 { font-size: 25px; }
  .ladder li { grid-template-columns: minmax(0, 1fr) 62px; gap: 4px 12px; }
  .ladder .lbar { grid-column: 1 / -1; grid-row: 2; }
  .ladder .lw { display: none; }
}
@media print { body { background: #fff; } nav.toc { display: none; } .page { display: block; } .table-wrap, .flow { break-inside: avoid; } }
"""
)

JS = """
(() => {
  const toc = document.querySelector('nav.toc');
  const det = toc.querySelector('details');
  const mq = matchMedia('(max-width: 980px)');
  const sync = () => { det.open = !mq.matches; };
  sync(); mq.addEventListener('change', sync);
  const links = new Map([...toc.querySelectorAll('a')].map(a => [a.hash.slice(1), a]));
  const heads = [...document.querySelectorAll('main h2[id], main h3[id]')].filter(h => links.has(h.id));
  if (!heads.length) return;
  let current;
  const mark = () => {
    let pick = heads[0];
    for (const h of heads) { if (h.getBoundingClientRect().top < 120) pick = h; else break; }
    if (pick === current) return;
    if (current) links.get(current.id).removeAttribute('aria-current');
    current = pick; links.get(pick.id).setAttribute('aria-current', 'true');
  };
  addEventListener('scroll', mark, { passive: true }); mark();
  toc.addEventListener('click', e => { if (e.target.closest('a') && mq.matches) det.open = false; });
})();
"""


def facts(line):
    """`Label: value` fields split by two or more spaces, or None."""
    parts = []
    for part in re.split(r" {2,}", line.strip()):
        m = FACT.fullmatch(part)
        if m is None:
            return None
        parts.append(m)
    spans = "".join(f"<span><b>{inline(m[1])}</b> {inline(m[2])}</span>" for m in parts)
    return f'<p class="facts">{spans}</p>'


def header(lines, seen):
    out, run = [], []
    for line in lines + [""]:
        fact = facts(line) if line.strip() else None
        if fact is None and line.strip():
            run.append(line)
            continue
        if run:
            out.append(blocks(run, seen)[0])
            run = []
        if fact:
            out.append(fact)
    return "\n".join(out)


def render(md, source_name="the Markdown source", notice="", ladder_spec=None):
    lines = md.splitlines()
    h1 = next((n for n, line in enumerate(lines) if line.startswith("# ")), None)
    if h1 is None:
        raise SystemExit("the source needs an H1 title")
    title = lines[h1][2:].strip()
    first_h2 = next(
        (n for n in range(h1 + 1, len(lines)) if lines[n].startswith("## ")), len(lines)
    )
    seen: dict[str, int] = {"ladder-h": 1}
    intro = header(lines[h1 + 1 : first_h2], seen)
    body, heads = blocks(lines[first_h2:], seen)
    toc = []
    for level, hid, text in heads:
        if level in (2, 3):
            label = re.sub(r"^\d+(\.\d+)?\.?\s", "", text)
            toc.append(
                f'<li class="{"sub" if level == 3 else ""}"><a href="#{hid}">{inline(label)}</a></li>'
            )
    open_rows = sum(
        t.count("<tr") - 1
        for t in re.findall(r'<table class="data open.*?</table>', body)
    )
    open_id = next((hid for _, hid, text in heads if is_open(text)), None)
    open_link = (
        f'<p class="open-count"><a href="#{open_id}">{open_rows} open item{"s" if open_rows != 1 else ""}</a></p>'
        if open_id and open_rows
        else ""
    )
    legend = "".join(
        f"<span>{pill(k)} {v[1]}</span>"
        for k, v in MARK_CLASS.items()
        if f"mark mark-{v[0]}" in intro + body
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
<nav class="toc" aria-label="Contents"><details open><summary>Contents</summary><ol>{"".join(toc)}</ol></details></nav>
<main>
<header>
<h1>{inline(title)}</h1>
<div class="meta">{f'<span class="notice">{inline(notice)}</span>' if notice else ""}{intro}{open_link}</div>
{f'<div class="legend" aria-label="Fact marks">{legend}</div>' if legend else ""}
</header>
{ladder(ladder_spec) if ladder_spec else ""}
{body}
<footer>Generated from <code>{html.escape(source_name)}</code>. Edit the Markdown, not this page.</footer>
</main>
</div>
<script>{JS}</script>
</body>
</html>
"""


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("source", type=pathlib.Path, help="the Markdown spec")
    p.add_argument(
        "-o", "--out", type=pathlib.Path, help="default: the source with .html"
    )
    p.add_argument(
        "--notice",
        default="",
        help="a short boxed warning in the header, e.g. an audience limit",
    )
    p.add_argument(
        "--ladder",
        type=pathlib.Path,
        help="JSON for the ranked bar list under the header",
    )
    args = p.parse_args()
    out = args.out or args.source.with_suffix(".html")
    spec = json.loads(args.ladder.read_text()) if args.ladder else None
    page = render(args.source.read_text(), args.source.name, args.notice, spec)
    out.write_text(page)
    print(f"wrote {out} ({len(page):,} bytes)")


if __name__ == "__main__":
    main()
