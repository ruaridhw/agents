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

    def test_header_splits_kind_from_title(self):
        self.assertIn('<p class="eyebrow">Build spec</p>', self.page)
        self.assertIn(
            "<h1>Cutting the thumbnail service's cost per image</h1>", self.page
        )
        self.assertIn('<span class="notice">Internal only</span>', self.page)

    def test_marks_become_pills_with_a_legend(self):
        self.assertIn('class="mark mark-v"', self.page)
        self.assertIn('class="mark mark-r"', self.page)
        self.assertIn('class="mark mark-i"', self.page)
        self.assertIn('class="legend"', self.page)

    def test_register_rows_are_anchors_and_open_table_is_tinted(self):
        for rid in ("R1", "S1", "O1"):
            self.assertIn(f'<tr id="{rid}">', self.page)
        self.assertIn('class="data open"', self.page)

    def test_contents_rail_lists_sections_and_numbered_subsections(self):
        self.assertIn('<a href="#s4">Phase A: skip unchanged images</a>', self.page)
        self.assertIn('<a href="#s4-2">Steps</a>', self.page)

    def test_nested_lists_keep_their_types(self):
        self.assertRegex(self.page, r"<ol><li><strong>Hash the source\.</strong>")
        self.assertRegex(self.page, r"<ul><li>same hash and preset")
        self.assertRegex(self.page, r"<ol><li>the skip share;</li>")

    def test_ladder_scales_bars_to_the_largest_value(self):
        self.assertIn('style="width:100.0%"', self.page)
        self.assertIn("$0.013", self.page)

    def test_bold_first_cell_is_a_lead_row(self):
        self.assertIn('<tr class="lead">', self.page)

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
