# Writing the script

The craft of explaining is `teach`'s: its one-conversation shape (the smallest complete answer first, layers on request, a plain definition before detail) and its mission and resources discipline for a series. This file is what changes when the listener cannot interrupt, cannot look back and is hearing it once.

## Before writing

- **Who is listening?** Ask once. If the listener is the user, use their acronyms freely, but say once what each stands for and what the thing actually is.
- **Why, and for how long?** The mission is the reason they are listening (a commute, an onboarding, a meeting tomorrow). It decides what is cut. A first episode is five to six minutes. Later episodes go longer and deeper.
- **Facts come from sources, not memory.** Read the repo, the docs or the system before writing. Cite the source in your reply, never in the spoken script. A claim you could not check is either cut or said aloud as a guess.

## Shape of an episode

1. **The whole thing in one sentence**, first. Then detail, layer by layer.
2. **Spoken signposts.** Each `## ` heading is read aloud, so name the layer: "Layer two. The loop." The listener cannot see structure, so the headings are the structure.
3. **Simple first, then deeper.** Each layer adds one idea and leans on the last. A layer that needs two new ideas is two layers.
4. **One worked example** with concrete numbers, followed end to end. Put it after the loop is understood, not before.
5. **Close by restating the one sentence.** The listener's last memory should be the first.
6. **Tight scope.** One episode teaches one thing. What is left over is the next episode's opening line, not a rushed last section.

## Writing for the ear

- Short sentences. One idea each.
- No parentheses, no bullet lists, no tables, no code, no URLs, no markdown emphasis. The voice reads them badly or reads the symbols.
- Write numbers as words: "forty pounds", "three days". Spell out acronyms on first use and say them as they are spoken.
- Say the thing again in different words at the hard step. On paper that is padding. In audio it is the rewind button.
- Prefer concrete nouns to abstractions, and the active voice.
- Read it aloud in your head. A sentence you run out of breath on gets split.

## Length budget

About one hundred and twenty spoken words per minute once the pauses are in (at speed 0.9). So five minutes is roughly six hundred words. `build_audio.py --dry-run` estimates it and lints the script; the real check is the rendered file's length, and a script that runs over is trimmed, not sped up.

## Series

Keep a `NOTES.md` in the workspace: the listener's pacing and style preferences, what each episode covered, and what the next one opens with. Read it before writing episode two. Update it after every episode, with the listener's own corrections in their words.
