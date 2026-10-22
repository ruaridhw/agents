"""The verify decision-trail writer: header, cell cleaning, formula prefix, usage."""

from __future__ import annotations

import subprocess
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / ".claude"
    / "skills"
    / "verify"
    / "scripts"
    / "log.sh"
)
HEADER = "ts\tphase\tdecision\twhy\tevidence\tresult"


def run(*args):
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def rows(logfile):
    return logfile.read_text().splitlines()


def test_usage_error_without_six_arguments():
    result = run("only", "five", "args", "here", "thanks")

    assert result.returncode == 1
    assert "usage: log.sh <logfile> <phase> <decision> <why>" in result.stderr


def test_header_is_written_once_and_a_row_follows(tmp_path):
    logfile = tmp_path / "decisions.tsv"

    run(str(logfile), "build", "ran the suite", "prove green", "commit abc123", "green")
    run(str(logfile), "ship", "held the merge", "proof missing", "abc4", "open")

    lines = rows(logfile)
    assert lines[0] == HEADER
    assert len(lines) == 3
    assert lines[1].count("\t") == 5
    assert lines[1].split("\t")[1:] == [
        "build",
        "ran the suite",
        "prove green",
        "commit abc123",
        "green",
    ]
    assert lines[2].split("\t")[1] == "ship"


def test_missing_parent_directory_is_created(tmp_path):
    logfile = tmp_path / "nested" / "scratch" / "abc4.tsv"

    result = run(str(logfile), "start", "took over", "pickup", "run 7", "open")

    assert result.returncode == 0
    assert logfile.exists()


def test_tabs_newlines_and_carriage_returns_stay_inside_cells(tmp_path):
    logfile = tmp_path / "decisions.tsv"

    run(
        str(logfile),
        "build",
        "two\tcells",
        "line\nbreak",
        "carriage\rreturn",
        "result",
    )

    line = rows(logfile)[1]
    assert line.count("\t") == 5
    assert "\n" not in line and "\r" not in line
    assert "two cells" in line


def test_cells_that_look_like_a_formula_get_a_quote_prefix(tmp_path):
    logfile = tmp_path / "decisions.tsv"

    for index, dangerous in enumerate(["=1+1", "+1", "-1", "@cmd"]):
        run(str(logfile), "build", dangerous, "why", "evidence", f"result{index}")

    decisions = [row.split("\t")[2] for row in rows(logfile)[1:]]
    assert decisions == ["'=1+1", "'+1", "'-1", "'@cmd"]


def test_a_plain_leading_character_is_not_prefixed(tmp_path):
    logfile = tmp_path / "decisions.tsv"

    run(str(logfile), "build", "commit abc123", "why", "evidence", "green")

    assert rows(logfile)[1].split("\t")[2] == "commit abc123"


def test_timestamp_is_iso8601_utc(tmp_path):
    logfile = tmp_path / "decisions.tsv"

    run(str(logfile), "build", "one", "why", "evidence", "green")

    stamp = rows(logfile)[1].split("\t")[0]
    assert stamp.endswith("Z")
    assert len(stamp) == len("2026-05-24T09:02:00Z")
