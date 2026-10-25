"""Render the worked example and check the conventions the page promises."""

import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts/spec_page.py"
EXAMPLE = SKILL / "examples/spec.md"
LADDER = SKILL / "examples/ladder.json"
render = runpy.run_path(str(SCRIPT))["render"]


class Balance(HTMLParser):
    VOID = {"meta", "br", "img", "hr", "input", "link"}

    def __init__(self):
        super().__init__()
        self.stack, self.ids = [], []

    def handle_starttag(self, tag, attrs):
        self.ids += [v for k, v in attrs if k == "id"]
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        assert self.stack and self.stack[-1] == tag, (
            f"</{tag}> closes <{self.stack[-1] if self.stack else None}>"
        )
        self.stack.pop()


class SpecPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = render(
            EXAMPLE.read_text(),
            "spec.md",
            "Internal only",
            json.loads(LADDER.read_text()),
        )

    def test_tags_balance_and_ids_are_unique(self):
        parser = Balance()
        parser.feed(self.page)
        self.assertEqual(parser.stack, [])
        self.assertEqual(len(parser.ids), len(set(parser.ids)))

    def test_every_template_section_is_a_heading_in_order_and_in_the_rail(self):
        ids = [
            "intent",
            "goals-non-goals-anti-goals",
            "constraints",
            "decisions",
            "left-to-the-builder",
            "acceptance",
            "design",
            "out-of-scope",
            "open-items",
            "further-notes",
        ]
        positions = [self.page.index(f'<h2 id="{hid}">') for hid in ids]
        self.assertEqual(positions, sorted(positions))
        for hid in ids:
            self.assertIn(f'<a href="#{hid}">', self.page)
        self.assertIn('<li class="sub"><a href="#skip-unchanged-images">', self.page)

    def test_header_keeps_the_title_whole_and_shows_the_facts(self):
        self.assertIn(
            "<h1>Skip unchanged images in the thumbnail service</h1>", self.page
        )
        self.assertIn("<span><b>Spec issue</b> (once published)</span>", self.page)
        self.assertIn("<span><b>Date</b> 2026-01-12</span>", self.page)
        self.assertIn('<span class="notice">Internal only</span>', self.page)
        self.assertIn('<a href="#open-items">2 open items</a>', self.page)
        page = render("# Retries: back off\n\n## Intent\n\nWhy.\n")
        self.assertIn("<h1>Retries: back off</h1>", page)

    def test_decisions_table_keeps_its_columns_and_rows(self):
        table = self.page.split('<h2 id="decisions">')[1].split("<h2")[0]
        for col in ("Decision", "Source", "Consequence"):
            self.assertIn(f'<th scope="col">{col}</th>', table)
        self.assertEqual(table.count("<tr>"), 5)

    def test_open_items_are_tinted_and_anchored(self):
        section = self.page.split('<h2 id="open-items">')[1].split("<h2")[0]
        self.assertIn('class="data open"', section)
        for rid in ("O1", "O2"):
            self.assertIn(f'<tr id="{rid}">', section)
        self.assertIn("Consequence if unresolved", section)

    def test_acceptance_cases_are_anchors(self):
        for rid in ("A1", "A3", "M2"):
            self.assertIn(
                f'<tr id="{rid}"><th scope=row class="rid">{rid}</th>', self.page
            )

    def test_marks_become_pills_and_the_legend_lists_only_those_used(self):
        self.assertIn('class="mark mark-v"', self.page)
        self.assertIn('class="mark mark-r"', self.page)
        legend = self.page.split('class="legend"')[1].split("</div>")[0]
        self.assertIn("Verified", legend)
        self.assertNotIn("Inference", legend)
        page = render(
            "# T\n\n## Decisions\n\n| Decision | Source |\n| --- | --- |\n| x | I think so |\n"
        )
        self.assertNotIn('class="mark mark-i"', page)

    def test_repeated_headings_get_unique_ids(self):
        page = render("# T\n\n## A\n\n### Phase\n\n## B\n\n### Phase\n")
        self.assertIn('<h3 id="phase">', page)
        self.assertIn('<h3 id="phase-2">', page)

    def test_links_render_and_unsafe_schemes_are_dropped(self):
        page = render(
            "# T\n\nSee [the issue](https://example.com/1) and [x](javascript:alert(1)).\n"
        )
        self.assertIn('<a href="https://example.com/1">the issue</a>', page)
        self.assertNotIn("javascript:", page)

    def test_nested_lists_keep_their_types(self):
        page = render(
            "# T\n\n## Steps\n\n1. **Hash.**\n2. Compare:\n   - same: skip;\n   - else: render.\n"
            "3. Measure:\n   1. the skip share;\n"
        )
        self.assertRegex(page, r"<ol><li><strong>Hash\.</strong>")
        self.assertRegex(page, r"<ul><li>same: skip;")
        self.assertRegex(page, r"<ol><li>the skip share;</li>")

    def test_ladder_scales_bars_to_the_largest_value(self):
        self.assertIn('style="width:100.0%"', self.page)
        self.assertIn("$0.013", self.page)

    def test_bold_first_cell_is_a_lead_row(self):
        page = render("# T\n\n| Step | $ |\n| --- | --- |\n| **All** | 1 |\n")
        self.assertIn('<tr class="lead">', page)

    def test_cli_output_is_byte_stable(self):
        with tempfile.TemporaryDirectory() as tmp:
            outs = []
            for n in (1, 2):
                out = Path(tmp) / f"{n}.html"
                cmd = [
                    sys.executable,
                    str(SCRIPT),
                    str(EXAMPLE),
                    "-o",
                    str(out),
                    "--ladder",
                    str(LADDER),
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                outs.append(out.read_bytes())
            self.assertEqual(outs[0], outs[1])


if __name__ == "__main__":
    unittest.main()
