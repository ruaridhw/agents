#!/usr/bin/env python3
"""Render a draft ticket wave as one offline, annotatable HTML document (stdlib only)."""

import argparse
import base64
import datetime
import html
import json
import re
import sys
from pathlib import Path
from string import Template
from urllib.parse import quote

LIST = re.compile(r"^( *)([-*+] |\d+\. )(.*)$")
TABLE_RULE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?$")


def normalize_markdown(text):
    """Separate lists from prose and expand two-space nesting, leaving fences intact."""
    out, prev, fence = [], "", None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker[1][0]
            fence = None if fence == token else token
        elif fence is None:
            match = LIST.match(line)
            if match:
                line = "    " * (len(match[1]) // 2) + line.lstrip()
                if (
                    prev.strip()
                    and not LIST.match(prev)
                    and not prev.startswith("    ")
                ):
                    out.append("")
            elif line.startswith("  ") and prev.strip():
                line = "    " * ((len(line) - len(line.lstrip())) // 2) + line.lstrip()
        out.append(line)
        prev = line
    return "\n".join(out)


def inline(text):
    """Escape raw HTML; links/images remain visible text rather than active resources."""
    parts = re.split(r"(`[^`\n]+`)", text)
    result = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            result.append(f"<code>{html.escape(part[1:-1])}</code>")
            continue
        part = html.escape(part)
        part = re.sub(r"!?\[([^\]]*)\]\(([^)]+)\)", r"\1 (\2)", part)
        part = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", part)
        part = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", part)
        result.append(part)
    return "".join(result)


def cells(line):
    return [inline(cell.strip()) for cell in line.strip().strip("|").split("|")]


def render_list(lines, start):
    first = LIST.match(lines[start])
    if first is None:
        raise ValueError("Expected a list item")
    indent = len(first[1])
    ordered = first[2][0].isdigit()
    tag = "ol" if ordered else "ul"
    attr = f' start="{int(first[2].split(".")[0])}"' if ordered else ""
    out, index = [f"<{tag}{attr}>"], start
    while index < len(lines):
        match = LIST.match(lines[index])
        if not match or len(match[1]) != indent or match[2][0].isdigit() != ordered:
            break
        item = [match[3]]
        index += 1
        while index < len(lines) and (
            lines[index].startswith(" " * (indent + 4)) or not lines[index].strip()
        ):
            item.append(lines[index][indent + 4 :] if lines[index].strip() else "")
            index += 1
        out.append(f"<li>{blocks(item)}</li>")
    out.append(f"</{tag}>")
    return "".join(out), index


def render_table(lines, start):
    head = "".join(f"<th>{cell}</th>" for cell in cells(lines[start]))
    out, index = [f"<table><thead><tr>{head}</tr></thead><tbody>"], start + 2
    while index < len(lines) and "|" in lines[index] and lines[index].strip():
        row = "".join(f"<td>{cell}</td>" for cell in cells(lines[index]))
        out.append(f"<tr>{row}</tr>")
        index += 1
    out.append("</tbody></table>")
    return "".join(out), index


def special(lines, index):
    line = lines[index]
    return (
        not line.strip()
        or LIST.match(line)
        or re.match(r"^(#{1,6} |```|~~~|>)", line)
        or (
            index + 1 < len(lines)
            and "|" in line
            and TABLE_RULE.match(lines[index + 1])
        )
    )


def render_code(lines, start):
    fence, code, index = lines[start][:3], [], start + 1
    while index < len(lines) and not lines[index].startswith(fence):
        code.append(lines[index])
        index += 1
    return "<pre><code>" + html.escape(
        "\n".join(code) + "\n"
    ) + "</code></pre>", index + 1


def blocks(lines):
    out, index = [], 0
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
        elif line.startswith(("```", "~~~")):
            chunk, index = render_code(lines, index)
            out.append(chunk)
        elif match := re.match(r"^(#{1,6}) (.*)$", line):
            level = len(match[1])
            out.append(f"<h{level}>{inline(match[2])}</h{level}>")
            index += 1
        elif LIST.match(line):
            chunk, index = render_list(lines, index)
            out.append(chunk)
        elif (
            index + 1 < len(lines)
            and "|" in line
            and TABLE_RULE.match(lines[index + 1])
        ):
            chunk, index = render_table(lines, index)
            out.append(chunk)
        elif line.startswith(">"):
            quoted = []
            while index < len(lines) and lines[index].startswith(">"):
                quoted.append(lines[index][1:].lstrip())
                index += 1
            out.append(f"<blockquote>{blocks(quoted)}</blockquote>")
        else:
            paragraph = [line.strip()]
            index += 1
            while index < len(lines) and not special(lines, index):
                paragraph.append(lines[index].strip())
                index += 1
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
    return "\n".join(out)


def md(text):
    return blocks(normalize_markdown(text).splitlines())


def require_fields(value, fields, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    for field in fields:
        if not isinstance(value.get(field), str):
            raise ValueError(f"{label}.{field} must be a string")


def require_list(value, label):
    if not isinstance(value, list):
        raise ValueError(f"{label} must be an array")
    return value


def validate_ticket(ticket, index):
    label = f"tickets[{index}]"
    require_fields(ticket, ("key", "title", "body", "action", "rulings"), label)
    if not ticket["key"].strip():
        raise ValueError(f"{label}.key must be nonempty")
    rank, priority = ticket.get("rank"), ticket.get("priority")
    if type(rank) is not int or rank < 0:
        raise ValueError(f"{label}.rank must be a nonnegative integer")
    if type(priority) is not int or priority not in range(4):
        raise ValueError(f"{label}.priority must be an integer from 0 to 3")
    if not re.fullmatch(r"create|update \S+", ticket["action"]):
        raise ValueError(f"{label}.action must be create or update <ref>")
    if "due" not in ticket:
        raise ValueError(f"{label}.due must be an ISO date or null")
    if ticket["due"] is not None:
        if not isinstance(ticket["due"], str):
            raise ValueError(f"{label}.due must be an ISO date or null")
        datetime.date.fromisoformat(ticket["due"])
    require_fields(ticket.get("spec"), ("label", "markdown"), f"{label}.spec")
    if not all(
        isinstance(ref, str)
        for ref in require_list(ticket.get("related"), f"{label}.related")
    ):
        raise ValueError(f"{label}.related must contain strings")
    for source in require_list(ticket.get("sources"), f"{label}.sources"):
        require_fields(
            source,
            ("ref", "from", "class", "point", "quote", "conflicts"),
            f"{label}.source",
        )


def validate(data):
    require_fields(data, ("title", "eyebrow", "intro"), "page")
    keys, ranks = set(), set()
    for index, ticket in enumerate(require_list(data.get("tickets"), "tickets")):
        validate_ticket(ticket, index)
        if ticket["key"] in keys or ticket["rank"] in ranks:
            raise ValueError("Ticket keys and ranks must be unique")
        keys.add(ticket["key"])
        ranks.add(ticket["rank"])
    for action in require_list(data.get("other_actions", []), "other_actions"):
        require_fields(action, ("ref", "action", "markdown"), "other_action")
    for panel in require_list(data.get("panels", []), "panels"):
        require_fields(panel, ("title", "markdown"), "panel")


def source_html(ticket):
    parts = [
        (
            '<div class="src"><p class="src-ref">'
            f'<span class="mono">{html.escape(source["ref"])}</span> '
            f'<span class="src-from">{html.escape(source["from"])} · {html.escape(source["class"])}</span></p>'
            f'<div class="src-point">{md(source["point"])}</div>'
            f"<blockquote>{md(source['quote'])}</blockquote>"
            f'<div class="src-meta">Conflicts with: {md(source["conflicts"])}</div></div>'
        )
        for source in ticket["sources"]
    ]
    if not parts:
        parts.append('<p class="none">No source rows supplied.</p>')
    if ticket["rulings"]:
        parts.append(
            f'<div class="rulings"><p class="lbl">Operator rulings</p>{md(ticket["rulings"])}</div>'
        )
    return "\n".join(parts)


def ticket_html(ticket):
    key = quote(ticket["key"], safe="")
    priority = ticket["priority"]
    values = (
        ("Rank", str(ticket["rank"])),
        ("Priority", f'<span class="pill p{priority}">P{priority}</span>'),
        ("Due", html.escape(ticket["due"] or "—")),
        ("Kata", html.escape(ticket["action"])),
        ("Spec ref", html.escape(ticket["spec"]["label"])),
        ("Related", html.escape(", ".join(ticket["related"]) or "—")),
    )
    boxes = "".join(
        f"<div><dt>{label}</dt><dd>{value}</dd></div>" for label, value in values
    )
    return f"""<section class="ticket pri{priority}" id="t-{key}" aria-labelledby="h-{key}">
<dl class="boxes">{boxes}</dl>
<h2 id="h-{key}">{html.escape(ticket["title"])}</h2>
<div class="cols">
<article class="col body"><p class="lbl">Ticket body — what goes into kata</p>{md(ticket["body"])}</article>
<article class="col spec"><p class="lbl">{html.escape(ticket["spec"]["label"])}</p>
{md(ticket["spec"]["markdown"])}</article>
</div>
<div class="source"><p class="lbl">Source — what was said or ruled</p>{source_html(ticket)}</div>
</section>"""


def font_assets(assets):
    faces = (
        ("inter-display-semibold.woff2", "Inter Display", 600),
        ("inter-semibold.woff2", "Inter", 600),
        ("lato-regular.woff2", "Lato", 400),
    )
    styles = []
    for filename, family, weight in faces:
        encoded = base64.b64encode((assets / "fonts" / filename).read_bytes()).decode()
        styles.append(
            "@font-face {\n"
            f'  font-family: "{family}";\n'
            "  font-style: normal;\n"
            f"  font-weight: {weight};\n"
            "  font-display: swap;\n"
            f'  src: url("data:font/woff2;base64,{encoded}") format("woff2");\n'
            "}\n"
        )
    notices = "\n\n".join(
        (assets / "fonts" / filename).read_text(encoding="utf-8")
        for filename in ("LICENSE-Inter.txt", "LICENSE-Lato.txt")
    )
    return "\n".join(styles), "<!-- Bundled font licences:\n" + notices.replace(
        "--", "—"
    ) + "\n-->"


def render(data):
    validate(data)
    tickets = sorted(data["tickets"], key=lambda ticket: ticket["rank"])
    assets = Path(__file__).resolve().parent.parent / "assets"
    css = (assets / "triage.css").read_text(encoding="utf-8")
    fonts, notices = font_assets(assets)
    # IDs are encoded keys; fragments need another encoding for the browser's decoding pass.
    nav = "".join(
        f'<li><a href="#t-{quote(quote(t["key"], safe=""), safe="")}">'
        f'<span class="num">{t["rank"]}</span> '
        f'<span class="pill p{t["priority"]}">P{t["priority"]}</span> {html.escape(t["title"])}</a></li>'
        for t in tickets
    )
    rows = "".join(
        f'<tr><td class="mono">{html.escape(a["ref"])}</td><td>{html.escape(a["action"])}</td>'
        f"<td>{md(a['markdown'])}</td></tr>"
        for a in data.get("other_actions", [])
    )
    panels = "".join(
        f'<section class="panel" id="panel-{i}" aria-labelledby="panel-title-{i}">'
        f'<h2 id="panel-title-{i}">{html.escape(p["title"])}</h2>{md(p["markdown"])}</section>'
        for i, p in enumerate(data.get("panels", []))
    )
    panel_nav = "".join(
        f'<li><a href="#panel-{i}">{html.escape(p["title"])}</a></li>'
        for i, p in enumerate(data.get("panels", []))
    )
    markup = (assets / "page.html").read_text(encoding="utf-8")
    # Commented slots let HTML/CSS/JS formatters parse the source template normally.
    markup = re.sub(r"<!-- (\$[a-z_]+) -->", r"\1", markup)
    markup = markup.replace("/* $styles */", "$styles").replace(
        "/* $theme_script */", "$theme_script"
    )
    return Template(markup).substitute(
        page_title=html.escape(data["title"]),
        eyebrow=html.escape(data["eyebrow"]),
        intro=md(data["intro"]),
        styles=fonts + css,
        font_licenses=notices,
        theme_script=(assets / "theme.js").read_text(encoding="utf-8"),
        ticket_nav=nav,
        panel_nav=panel_nav,
        tickets="\n".join(ticket_html(t) for t in tickets),
        action_rows=rows,
        panels=panels,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Draft wave JSON")
    parser.add_argument("output", type=Path, help="Self-contained HTML destination")
    args = parser.parse_args()
    try:
        if args.input.resolve() == args.output.resolve():
            raise ValueError("Input and output must be different files")
        page = render(json.loads(args.input.read_text(encoding="utf-8")))
        args.output.write_text(page, encoding="utf-8")
    except (OSError, ValueError, RecursionError) as error:
        parser.exit(2, f"render_triage: {error}\n")
    sys.stdout.write(f"{args.output}: {len(page.encode('utf-8'))} bytes\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
