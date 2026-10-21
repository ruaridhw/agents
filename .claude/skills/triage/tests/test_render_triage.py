"""Exercise the standalone renderer with Python stdlib unittest."""

import base64
import copy
import json
import re
import runpy
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts/render_triage.py"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)


def renderer():
    assert SCRIPT.is_file(), "The skill must include its renderer"
    return runpy.run_path(str(SCRIPT))


def draft():
    return {
        "title": "Example wave",
        "eyebrow": "Draft — nothing published",
        "intro": "Review each proposed action.",
        "tickets": [
            {
                "key": "later",
                "rank": 2,
                "priority": 2,
                "due": None,
                "title": "Update the checklist",
                "body": "## Done when\nThe checklist agrees.",
                "action": "update ex01",
                "related": ["ex02"],
                "spec": {"label": "Spec §2", "markdown": "Keep the checklist aligned."},
                "sources": [],
                "rulings": "",
            },
            {
                "key": "first",
                "rank": 1,
                "priority": 1,
                "due": "2030-01-02",
                "title": "Preserve the reference",
                "body": "## What\nRead the reference.\n- Keep it\n  - Include its label\n  - Include its value\n\n## Done when\nA fixture passes.",
                "action": "create",
                "related": [],
                "spec": {
                    "label": "Spec §1",
                    "markdown": "## Rule\nKeep **both** fields.",
                },
                "sources": [
                    {
                        "ref": "S1",
                        "from": "Example meeting 00:15",
                        "class": "decided",
                        "point": "Label and value travel together.",
                        "quote": "Keep both fields.",
                        "conflicts": "Old checklist",
                    }
                ],
                "rulings": "- Keep the label.",
            },
        ],
        "other_actions": [
            {
                "ref": "ex03",
                "action": "comment",
                "markdown": "Superseded rule recorded.",
            }
        ],
        "panels": [
            {"title": "Rollout", "markdown": "Review on a copy first."},
            {"title": "No ticket", "markdown": "Send the recap."},
        ],
    }


class RenderTriageTest(unittest.TestCase):
    def setUp(self):
        self.renderer = renderer()
        self.draft = draft()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.tmp_path = Path(self.temp.name)

    def test_ranked_sections_show_the_whole_review(self):
        renderer = self.renderer
        draft = self.draft
        page = Page()
        page.feed(renderer["render"](draft))
        tickets = [
            attrs
            for tag, attrs in page.tags
            if tag == "section" and "ticket" in attrs.get("class", "").split()
        ]
        assert [t["id"] for t in tickets] == ["t-first", "t-later"]
        assert sum((tag == "article" for tag, _ in page.tags)) == 4
        text = " ".join(page.text)
        for expected in [
            "Rank",
            "Priority",
            "Due",
            "Kata",
            "Spec ref",
            "Related",
            "2030-01-02",
            "update ex01",
            "Spec §1",
            "S1",
            "Example meeting 00:15",
            "decided",
            "Keep both fields.",
            "Old checklist",
            "Operator rulings",
            "Superseded rule recorded.",
            "Rollout",
            "Send the recap.",
        ]:
            assert expected in text
        nav_links = [attrs["href"] for tag, attrs in page.tags if tag == "a"]
        assert nav_links[:2] == ["#t-first", "#t-later"]
        assert all((link.startswith("#") for link in nav_links))
        assert not any(
            (
                tag in {"details", "iframe", "img", "link"} or "hidden" in attrs
                for tag, attrs in page.tags
            )
        )
        assert not any(("src" in attrs for _, attrs in page.tags))

    def test_markdown_normalizes_lists_without_touching_code(self):
        renderer = self.renderer
        text = "Before list\n- Parent\n  - Child\n    - Grandchild\n\n```text\n  - literal\n```"
        result = renderer["md"](text)
        page = Page()
        page.feed(result)
        assert sum((tag == "ul" for tag, _ in page.tags)) == 3
        assert "<p>Before list</p>" in result
        assert "<pre><code>  - literal\n</code></pre>" in result
        assert (
            renderer["normalize_markdown"]("Before\n- Parent\n  - Child")
            == "Before\n\n- Parent\n    - Child"
        )

    def test_markdown_tables_quotes_and_ordered_lists(self):
        renderer = self.renderer
        result = renderer["md"](
            "| Field | Value |\n| --- | --- |\n| A | `B` |\n\n3. Third\n4. Fourth\n\n> Quoted **words**"
        )
        assert "<th>Field</th>" in result
        assert "<td><code>B</code></td>" in result
        assert '<ol start="3">' in result
        assert "<blockquote><p>Quoted <strong>words</strong></p></blockquote>" in result

    def test_input_cannot_inject_html_or_network_resources(self):
        renderer = self.renderer
        draft = self.draft
        draft["tickets"][0]["key"] = 'a" onmouseover="bad'
        draft["tickets"][0]["title"] = '<img src="https://example.invalid/pixel">'
        draft["tickets"][0]["body"] = (
            "<script>alert(1)</script>\n\n[Evidence](https://example.invalid/doc)\n\n![image](https://example.invalid/img)"
        )
        result = renderer["render"](draft)
        page = Page()
        page.feed(result)
        assert not any(
            (tag == "img" or "onmouseover" in attrs for tag, attrs in page.tags)
        )
        assert sum((tag == "script" for tag, _ in page.tags)) == 1
        assert all((attrs.get("href", "#").startswith("#") for _, attrs in page.tags))
        ids = {attrs["id"] for _, attrs in page.tags if "id" in attrs}
        assert all(
            (
                unquote(attrs["href"][1:]) in ids
                for tag, attrs in page.tags
                if tag == "a"
            )
        )
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in result
        assert "Evidence (https://example.invalid/doc)" in result
        assert "default-src 'none'" in result

    def test_invalid_input_is_refused(self):
        renderer = self.renderer
        draft = self.draft
        for mutation in (
            "duplicate-key",
            "duplicate-rank",
            "missing-spec",
            "bad-action",
            "bool-rank",
            "bad-priority",
            "bad-source",
        ):
            with self.subTest(mutation=mutation):
                draft = copy.deepcopy(self.draft)
                if mutation == "duplicate-key":
                    draft["tickets"][1]["key"] = "later"
                elif mutation == "duplicate-rank":
                    draft["tickets"][1]["rank"] = 2
                elif mutation == "missing-spec":
                    del draft["tickets"][0]["spec"]
                elif mutation == "bad-action":
                    draft["tickets"][0]["action"] = "close ex01"
                elif mutation == "bool-rank":
                    draft["tickets"][0]["rank"] = True
                elif mutation == "bad-priority":
                    draft["tickets"][0]["priority"] = "urgent"
                else:
                    draft["tickets"][1]["sources"][0]["quote"] = None
                with self.assertRaises(ValueError):
                    renderer["render"](draft)

    def test_cli_renders_example_without_site_packages(self):
        tmp_path = self.tmp_path
        out = tmp_path / "review.html"
        result = subprocess.run(
            [
                sys.executable,
                "-S",
                str(SCRIPT),
                str(SKILL / "examples/triage.json"),
                str(out),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stderr
        page = Page()
        page.feed(out.read_text())
        assert (
            sum(
                (
                    tag == "section" and "ticket" in attrs.get("class", "").split()
                    for tag, attrs in page.tags
                )
            )
            == 2
        )
        assert re.search(r"prefers-color-scheme:\s*dark", out.read_text())

    def test_output_embeds_licensed_fonts_without_network_access(self):
        page = self.renderer["render"](self.draft)
        fonts = re.findall(r"data:font/woff2;base64,([A-Za-z0-9+/=]+)", page)
        self.assertEqual(len(fonts), 3)
        for font in fonts:
            self.assertEqual(base64.b64decode(font)[:4], b"wOF2")
        self.assertIn("font-src data:", page)
        self.assertIn("SIL OPEN FONT LICENSE", page)
        self.assertLess(len(page.encode("utf-8")), 2_000_000)

    def test_cli_invalid_input_preserves_existing_output(self):
        tmp_path = self.tmp_path
        draft = self.draft
        invalid = copy.deepcopy(draft)
        invalid["tickets"][0]["action"] = "delete all"
        src, out = (tmp_path / "invalid.json", tmp_path / "review.html")
        src.write_text(json.dumps(invalid))
        out.write_text("previous review")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(src), str(out)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 2
        assert "action" in result.stderr
        assert out.read_text() == "previous review"


if __name__ == "__main__":
    unittest.main()
