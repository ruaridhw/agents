"""Render the morning brief: brief.json + template.html.j2 → latest.html.

The agent authors content (headline, terrain SVG, items, sections); the
template owns all chrome. Called by run_job via JobSpec.post_render, or
standalone: python -m runner.render_brief [brief.json] [latest.html].

Contract is deliberately loose: unknown keys are ignored, missing keys drop
their block. Gathered text is autoescaped; `[text](url)` inside sentences
becomes a link. terrain_svg/extra_css are model-authored (never gathered
text) and lightly sanitised before being trusted.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup, escape

from .config import LOGS_DIR, REPO_ROOT

TEMPLATE_DIR = REPO_ROOT / "jobs" / "morning_brief"
DEFAULT_JSON = LOGS_DIR / "morning_brief" / "brief.json"
DEFAULT_HTML = LOGS_DIR / "morning_brief" / "latest.html"

_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
_SVG_BANNED = re.compile(r"<\s*script|on[a-z]+\s*=|javascript:", re.IGNORECASE)


def md_links(text: str) -> Markup:
    """Escape text, then turn [label](https://url) into anchors."""
    out: list[str] = []
    pos = 0
    for m in _MD_LINK.finditer(text or ""):
        out.append(str(escape(text[pos : m.start()])))
        out.append(f'<a href="{escape(m.group(2))}">{escape(m.group(1))}</a>')
        pos = m.end()
    out.append(str(escape((text or "")[pos:])))
    return Markup("".join(out))


def _sanitise_markup(value: str, *, context: str) -> Markup:
    if _SVG_BANNED.search(value or ""):
        raise ValueError(f"{context} contains disallowed markup (script/event handler)")
    return Markup(value or "")


def render(json_path: Path = DEFAULT_JSON, html_path: Path = DEFAULT_HTML) -> Path:
    data = json.loads(json_path.read_text())
    if not data.get("headline"):
        raise ValueError(
            "brief.json has no headline — refusing to render an empty page"
        )

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
    env.filters["md_links"] = md_links
    html = env.get_template("template.html.j2").render(
        day_date=data.get("day_date"),
        headline=data.get("headline"),
        terrain_svg=_sanitise_markup(
            data.get("terrain_svg", ""), context="terrain_svg"
        ),
        acts=data.get("acts") or [],
        needs_attention=data.get("needs_attention") or [],
        resolved=data.get("resolved") or [],
        empty_line=data.get("empty_line"),
        sections=data.get("sections") or [],
        footer_line=data.get("footer_line"),
        extra_css=_sanitise_markup(data.get("extra_css", ""), context="extra_css"),
    )
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html)
    return html_path


def render_default() -> None:
    """post_render hook for the morning_brief job."""
    render()


def main() -> None:
    json_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_JSON
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_HTML
    print(render(json_path, html_path))


if __name__ == "__main__":
    main()
