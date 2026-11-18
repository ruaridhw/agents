#!/usr/bin/env python3
"""Render a voicenote script to MP3 with ElevenLabs, one paragraph per request.

    build_audio.py SCRIPT.md [flags]       render SCRIPT.mp3 beside the script
    build_audio.py SCRIPT.md --dry-run     lint the script and estimate length; no API call
    build_audio.py --list-voices           list voices (filter with --accent, --use-case)

Script format: blank-line-separated paragraphs. "# " is the title and "## " a
section heading; both are spoken. Headings get long silences around them and
paragraphs a short gap, made with real silence rather than break tags. Each
paragraph's audio is cached, keyed by voice, model, settings and text, so a
changed pause re-stitches with no API calls and an edited paragraph re-renders
alone. Stdlib only; needs ffmpeg and ffprobe on PATH.

API key: ELEVENLABS_API_KEY, else a session cache file (mode 0600). With
--key-cmd "<shell command that prints the key>" the key is fetched once and
cached, so a password manager is not asked on every run.
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://api.elevenlabs.io/v1"
DEFAULT_VOICE = "Xb7hH8MSUJpSbSDYk0k2"  # Alice, a premade British educator voice
DEFAULT_MODEL = "eleven_multilingual_v2"
WORDS_PER_MINUTE = 120  # spoken pace once the pauses are in, at speed 0.9
KEY_CACHE = Path(tempfile.gettempdir()) / f"elevenlabs_key_{os.getuid()}"


def get_key(key_cmd=None, cache=KEY_CACHE):
    """Environment first, then the 0600 session cache, then --key-cmd, cached."""
    if os.environ.get("ELEVENLABS_API_KEY", "").strip():
        return os.environ["ELEVENLABS_API_KEY"].strip()
    if cache.exists() and cache.read_text().strip():
        return cache.read_text().strip()
    if not key_cmd:
        sys.exit(
            "No ElevenLabs key. Set ELEVENLABS_API_KEY, or pass --key-cmd "
            "'<command that prints the key>' once to cache it for the session."
        )
    key = subprocess.check_output(key_cmd, shell=True, text=True).strip()
    if not key:
        sys.exit("--key-cmd printed nothing.")
    fd = os.open(cache, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(key)
    return key


def parse(text):
    """Blocks to (kind, text): kind is title, heading or para."""
    out = []
    for block in text.split("\n\n"):
        block = block.strip()
        if not block:
            continue
        kind = (
            "title"
            if block.startswith("# ")
            else "heading"
            if block.startswith("## ")
            else "para"
        )
        out.append((kind, block.lstrip("# ").strip()))
    return out


def lint(parts):
    """Ear-unfriendly patterns: things the voice reads badly or not at all."""
    issues = []
    for i, (kind, text) in enumerate(parts, 1):
        where = f"block {i} ({text[:30]!r})"
        if re.search(r"\([^)]*\)", text):
            issues.append(f"{where}: parentheses")
        if re.search(r"(?m)^\s*([-*]|\d+[.)])\s", text):
            issues.append(f"{where}: list markers")
        if re.search(r"\d", text):
            issues.append(f"{where}: digits; write numbers as words")
        if re.search(r"[`*_]|https?://", text):
            issues.append(f"{where}: markdown or URL")
    return issues


def word_count(parts):
    return sum(len(t.split()) for _, t in parts)


def plan(parts, gaps):
    """The stitch order: ("say", index) or ("pause", seconds)."""
    steps = []
    for i, (kind, _) in enumerate(parts):
        if kind == "heading" and i:
            steps.append(("pause", gaps["heading_before"]))
        steps.append(("say", i))
        if i + 1 < len(parts) and parts[i + 1][0] != "heading":
            steps.append(
                (
                    "pause",
                    {
                        "title": gaps["title_after"],
                        "heading": gaps["heading_after"],
                    }.get(kind, gaps["para"]),
                )
            )
    return steps


def tts(text, prev, nxt, voice, model, settings, cache, key):
    body = {
        "text": text,
        "model_id": model,
        "voice_settings": settings,
        "previous_text": prev,
        "next_text": nxt,
    }
    digest = hashlib.sha256(
        json.dumps([voice, body], sort_keys=True).encode()
    ).hexdigest()[:16]
    f = cache / f"{digest}.mp3"
    if not f.exists():
        req = urllib.request.Request(
            f"{API}/text-to-speech/{voice}?output_format=mp3_44100_128",
            data=json.dumps(body).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json"},
        )
        f.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return f


def silence(sec, cache):
    f = cache / f"sil_{sec:.2f}.mp3"
    if not f.exists():
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=mono",
                "-t",
                str(sec),
                "-b:a",
                "128k",
                str(f),
            ],
            check=True,
        )
    return f


def duration(path):
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "csv=p=0",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def list_voices(key, accent, use_case):
    req = urllib.request.Request(f"{API}/voices", headers={"xi-api-key": key})
    for v in json.load(urllib.request.urlopen(req, timeout=60))["voices"]:
        labels = v.get("labels", {})
        if accent and accent.lower() not in labels.get("accent", "").lower():
            continue
        if use_case and use_case.lower() not in labels.get("use_case", "").lower():
            continue
        print(
            f"{v['voice_id']}  {v['name']}  {labels.get('accent', '-')}  "
            f"{labels.get('use_case', '-')}  {v.get('description') or ''}".rstrip()
        )


def render(script, args, key):
    parts = parse(Path(script).read_text())
    gaps = {
        "title_after": args.gap_title,
        "heading_before": args.gap_before_heading,
        "heading_after": args.gap_after_heading,
        "para": args.gap_para,
    }
    settings = {
        "stability": args.stability,
        "similarity_boost": args.similarity,
        "speed": args.speed,
    }
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    files = []
    for step, val in plan(parts, gaps):
        if step == "pause":
            files.append(silence(val, cache))
            continue
        kind, text = parts[val]
        prev = parts[val - 1][1] if val else ""
        nxt = parts[val + 1][1] if val + 1 < len(parts) else ""
        files.append(tts(text, prev, nxt, args.voice, args.model, settings, cache, key))
        print(f"{val + 1}/{len(parts)} {kind}: {text[:50]}", flush=True)
    lst = cache / "concat.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in files))
    out = Path(args.out) if args.out else Path(script).with_suffix(".mp3")
    # Re-encode so mono silences and voice clips join cleanly.
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-ac",
            "1",
            "-ar",
            "44100",
            "-b:a",
            "128k",
            str(out),
        ],
        check=True,
    )
    secs = duration(out)
    print(
        f"{out}: {secs // 60:.0f}m{secs % 60:02.0f}s, {word_count(parts)} words, "
        f"{word_count(parts) / (secs / 60):.0f} wpm"
    )


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("script", nargs="?")
    p.add_argument("--out", help="output MP3 (default: beside the script)")
    p.add_argument(
        "--cache", default=".cache", help="per-paragraph audio cache directory"
    )
    p.add_argument("--voice", default=DEFAULT_VOICE)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--speed", type=float, default=0.9, help="0.7 to 1.2")
    p.add_argument("--stability", type=float, default=0.6)
    p.add_argument("--similarity", type=float, default=0.75)
    p.add_argument(
        "--gap-title", type=float, default=2.0, help="seconds after the title"
    )
    p.add_argument("--gap-before-heading", type=float, default=2.2)
    p.add_argument("--gap-after-heading", type=float, default=1.5)
    p.add_argument("--gap-para", type=float, default=0.8)
    p.add_argument(
        "--key-cmd",
        help="shell command that prints the API key; cached for the session",
    )
    p.add_argument(
        "--dry-run", action="store_true", help="lint and estimate length only"
    )
    p.add_argument("--list-voices", action="store_true")
    p.add_argument("--accent", help="with --list-voices: filter by labels.accent")
    p.add_argument("--use-case", help="with --list-voices: filter by labels.use_case")
    a = p.parse_args(argv)
    if a.list_voices:
        return list_voices(get_key(a.key_cmd), a.accent, a.use_case)
    if not a.script:
        p.error("a script path is required")
    if a.dry_run:
        parts = parse(Path(a.script).read_text())
        words = word_count(parts)
        pauses = sum(
            v
            for s, v in plan(
                parts,
                {
                    "title_after": a.gap_title,
                    "heading_before": a.gap_before_heading,
                    "heading_after": a.gap_after_heading,
                    "para": a.gap_para,
                },
            )
            if s == "pause"
        )
        print(
            f"{words} words, about {words / WORDS_PER_MINUTE:.1f} minutes at {WORDS_PER_MINUTE} wpm "
            f"({pauses:.0f}s of pauses planned)"
        )
        issues = lint(parts)
        print("\n".join(issues) if issues else "lint clean")
        return 1 if issues else 0
    render(a.script, a, get_key(a.key_cmd))


if __name__ == "__main__":
    sys.exit(main())
