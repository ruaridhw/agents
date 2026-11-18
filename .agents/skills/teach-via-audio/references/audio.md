# Audio gotchas

Each of these was hit for real.

- **One long request rushes.** A single request for a six-minute script sped up and sounded rushed in places. The script sends one request per paragraph and passes `previous_text` and `next_text`, so tone carries across the joins.
- **Break tags do not fix it.** `<break time="1.5s"/>` (maximum three seconds) works on v2 models, but many in one generation make the voice unstable, speeding it up included. Real silence between clips does the job. The script makes it with ffmpeg `anullsrc`, concatenates, and re-encodes to mono 44.1 kHz at 128k so the joins are clean.
- **Silences that worked.** Two point two seconds before each heading and one point five after it, two seconds after the title, and zero point eight between paragraphs. Each is a flag (`--gap-*`).
- **Settings that worked.** `eleven_multilingual_v2`, speed 0.9 (allowed range 0.7 to 1.2), stability 0.6, similarity boost 0.75.
- **Length.** At default speed with no pauses, nine hundred and thirty-eight words ran six minutes thirty-four. At speed 0.9 with pauses, seven hundred and forty-nine words ran six minutes nineteen. Budget about one hundred and twenty words a minute with the pauses in, check the file with `ffprobe` (the script prints the duration and the words per minute), and trim the script if it is over target.
- **The cache.** Each paragraph's audio is keyed by a hash of voice, text, neighbouring text and settings. Changing a pause re-stitches with no API calls. Editing one paragraph re-renders that paragraph and the two beside it, because their context changed. Delete `.cache/` to force a full render.
- **Choosing a voice.** `build_audio.py --list-voices --use-case informative_educational` lists teaching voices, and `--accent british` narrows by accent (both filter on the voice's labels). Offer the user two or three, or keep the default. A voice change re-renders everything.
- **Key handling.** The key stays out of repo files, scripts and command history. The script reads `ELEVENLABS_API_KEY`, then a session cache in the temp directory with mode 0600, then runs `--key-cmd` once and caches its output there. If the key cannot be fetched, the user can set the variable in their own shell.
