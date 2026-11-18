---
name: teach-via-audio
description: "Teach a topic as a narrated voicenote (MP3) made with the ElevenLabs API. Use when asked to explain something \"as audio\", \"as a voicenote\" or \"for my commute\", to make an audio onboarding or walkthrough, or to continue a series of spoken episodes."
---

# teach-via-audio

A sibling of `teach`, not a mode of it. `teach` is a curated near-copy of two upstreams and its job is understanding through a conversation or a workspace of lessons. This skill is the same goal through a different medium, with its own constraints (one pass, no interruption, no visuals) and its own tooling, so it points at `teach` for the craft and keeps only what changes for the ear.

Examples of the ask:

- "Teach me how our payment retries work, as a five-minute voicenote for my commute."
- "Explain the TLS handshake simply, then in more depth, as audio."
- "Make an audio onboarding to this repo's deploy pipeline."
- "Explain how a warehouse stock reconciliation works between two systems."

## Steps

1. **Ask who is listening, why and for how long.** One question, skipped for what is already stated. Completion: you can say the listener, the one-sentence mission and the target minutes.
2. **Read the sources.** Facts come from the repo, docs or system, not memory (`teach`'s rule). In a series, read `NOTES.md` first. Completion: every claim in the script traces to something you read, or is said aloud as a guess.
3. **Write the script** to `<workspace>/NN-<slug>.md` by `references/script-craft.md`. In a code repo the workspace is `.scratch/teach/<topic>/` (gitignored), as `teach` does; elsewhere, the directory the user names. `examples/script.md` shows the format. Completion: `scripts/build_audio.py <script> --dry-run` reports lint clean and a length within ten percent of target.
4. **Get the key.** The script needs `ELEVENLABS_API_KEY`. If it is not set, ask the user how to fetch it, for example the command their password manager's CLI uses to print it, then pass that as `--key-cmd`. The script caches the key for the session in a temp file with mode 0600, so the password manager is asked once, not per call. Completion: a `--list-voices` call succeeds.
5. **Pick a voice.** Default, or `--list-voices --use-case informative_educational` and let the user choose. Skip on a later episode of a series: reuse the voice in `NOTES.md`.
6. **Render.** Copy `scripts/build_audio.py` into the workspace, so the episode can be rebuilt later, and run it there on the script. Voice, model, speed and the gaps are flags; the defaults are the settings that worked (`references/audio.md`). Completion: the MP3 exists and the printed duration is within ten percent of target. Over target, trim the script and re-render, since the cache makes that cheap; never fix length by raising the speed.
7. **Hand over.** Give the MP3's absolute path, its length and the one-sentence takeaway. Offer to play it on request and never start playback unasked.
8. **Update `NOTES.md`** with the voice, what the episode covered, what episode two opens with, and any pacing or style correction the listener gave, in their words.

## Rules

- No secret in a tracked file, commit or reply. The key lives in the environment or the 0600 session cache only.
- The script, MP3, script copy, `NOTES.md` and `.cache/` stay in `.scratch/teach/<topic>/`. A repo never tracks them; an episode the user wants kept is moved on their request.
- Everything in `references/script-craft.md` applies to the script's prose, and `technical-writing`'s unslop pass is for documents, so it does not run on a spoken script.

## References

- `references/script-craft.md`: who is listening, the episode shape, writing for the ear, the length budget, series.
- `references/audio.md`: why one request per paragraph, the silences and settings that worked, caching, voices, key handling.
- `teach`: the underlying craft (smallest complete answer first, layers, mission, trusted sources, a series' records).
