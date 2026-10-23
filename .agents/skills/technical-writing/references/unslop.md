# Unslop

Edit text to remove AI patterns. Scan for the patterns below, then rewrite. Preserve meaning and match the intended tone.

## Overview

AI copy fails in a specific way: it performs the shape of good writing without doing the work. The patterns below are load-bearing when they carry information and dead weight when they don't. This is the pass that finds the dead ones.

**Core test for every flagged line: does it survive deletion?** If cutting it loses nothing a reader needed, it was decoration. Cut it.

## The pass

- **Draft without self-censoring.** Editing while drafting produces stiff copy.
- **Re-read the finished draft against the catalog.** Not from memory, scan the list.
- **For each hit: quote the exact line, name the tell, then cut or rewrite.** Quoting is the mechanism. You cannot fix a line you haven't isolated.
- **Re-read the rewrites.** A fix commonly plants a fresh tell, most often a triplet or a kicker.
- **Emit the fixed copy only.**

**Do not narrate the pass.** No "I've tightened this" preamble, no list of what you cut. Announcing the edit is itself a tell. Show quoted findings only when the reader asked for a review of the copy, or when a cut removed something substantive they may want back.

## Patterns to detect and fix

Rule numbers are stable ids that other skills cite. A removed rule leaves a gap. This is `technical-writing`'s final pass, and `review` runs it on prose; it is not a separate skill, so no rule here is dropped from the numbering. Rules merged in from another source are numbered from 100 and never renumber the ones above them.

### Content

3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...". Delete or expand with real sources. The participial tail is the same tell at the end of a clause: "...shipped Tuesday, underscoring the team's commitment", "...ensuring seamless delivery". A clause ending that way is almost always restating what came before it. Cut the tail, or promote it to a sentence with a real subject. The word list collects the usual tails.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue". Name the source or delete. "Studies show", "many argue", "it's widely regarded" and "analysts predict" are the same move: invented credibility standing in for a citation. Name the source, link it, or drop the claim.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant. Replace with plain words. The puffery register belongs here too: leverage, unlock, empower, navigate, streamline, elevate, harness, drive, enable, transform; seamless, robust, rich, comprehensive, holistic; ecosystem, framework, journey, space, realm, paradigm, synergy, deep dive. The word list groups them by family.
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features". Say "is" or "has". "functions as", "operates as", "represents", "marks", "constitutes", "maintains", "offers" and "provides" are the same avoidance. The word list carries the full set.
9. **"Not just X, but Y."** State the point directly instead. The same shape with a full stop is "That's not X. That's Y." Keep only the Y.
10. **Rule of three.** Don't force ideas into groups of three. Use the natural number. Two or five is fine; always three is the tell. Add the third item only when it is a third fact.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale. List topics directly. A range whose ends nobody measured is the same tell in numbers: "5 to 10 minutes", "30 to 50% faster". A number you did not measure means you never did the thing. Cut the number or go and measure it, and keep any range you did measure.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). If a thought needs separation, end the sentence or use a comma. The ban is deliberate and is not relaxed for a punchy beat: an em dash in most paragraphs is doing emphasis work that a comma or a full stop should do.
14. **Colon overuse.** Colons are fine before a list or example, not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Use straight quotes.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" Remove. "Great question!", "I'm glad you asked" and "Hope this helps!" are the warmth garnish around the same emptiness, and the fix is not to start later but to delete the sentence.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly. Praise for the question says nothing about the work, so drop it and answer.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". Delete "It is important to note that". Throat-clearing is the same filler at the front of a paragraph: "Here's the thing", "Let me be clear", "First and foremost", "At its core", "When it comes to". Start at the first sentence that carries a fact.
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may". A stack of hedges is the same rule: "it's worth noting that, generally speaking, in most cases" says it three times. Say it once, or don't say it.
25. **Generic conclusions.** "The future looks bright." State specific plans or facts. The recap ending is the same habit: "In short", "In summary", "Ultimately", "At the end of the day", "The bottom line is". Stop on the last real point.

### Jargon

26. **Abstract metaphor nouns.** Substrate (base), wedge, wedge in (add), vector (way, method), locus, vantage, nexus, primitive as a noun, harness as a metaphor, surface as in "API surface", bedrock, scaffolding as a metaphor, modality, paradigm, gold-plating (more than the job needs), ratchet as a metaphor (the mechanism's real name, or a limit that only tightens), evacuate for moving code (move out), endgame (the last phase), north star, flywheel. These read as technical but usually have a plainer concrete word. Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number, and "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong.
31. **Prefer the plain word.** "utilize" and "leverage" become "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer. The puffery verbs go the same way: "unlock" and "empower" become what the reader can now do, "streamline" becomes the step that went away, and "seamless" has to say which gap the reader no longer sees.
32. **Mannered prose.** Metaphor or flourish where a literal phrase exists: aphorisms ("wire it or delete it"), rhetorical fragments for effect, personified code ("the plan holds it"), figurative verbs ("rides along", "stands on"), stock framing phrases. "A dial worth turning" becomes "a parameter worth varying". Say what you mean. Rule 26 covers the metaphor nouns. The empty metaphor pair is the same flourish: "less a hammer, more a scalpel", "less a bucket, more a pipeline". Neither half names an action, so say what it does.
33. **Over-compression.** Dropped articles, verbless fragments, symbol-speak, and abbreviations that make the reader decode instead of read. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad date, exits with code 2, and writes nothing." Write whole sentences with their articles and verbs, and spell out arrows and abbreviations.

### Shape

These came in with a second source and start at 100, so the ids above never move when another source is merged.

100. **Two short bits stuck together.** "Fast. Simple." Pick the one that carries the claim, or write the sentence that earns both. Two clipped fragments in a row are rhythm standing in for content.
101. **Clapping for itself.** "And that matters." "That's the part everyone misses." The sentence praises the point instead of making it. Delete it.
102. **X is the Excel of Y.** "the Redis of request handling". Comparing the thing to a famous product borrows that product's credibility and says nothing about what this one does. Name the job.
103. **False balance.** "Critics argue X, supporters maintain Y, and the truth is somewhere in between." Two positions and a shrug is not a position. Take one and defend it, or cut the paragraph.
104. **Pseudo-profound kicker.** "The real question isn't what it does, it's what we do with it." Written to be quoted, not read. Delete it.
105. **Rhetorical question you then answer.** "So what does this mean? It means..." Delete the question, keep the answer.
106. **Orphaned "this".** "This matters because..." with no clear noun before it. Name the thing the sentence is about.
107. **Cadence uniformity.** Every sentence 12 to 18 words, every bullet the same length, every section the same shape. Vary it, or cut what is only there for symmetry.
108. **The product's word for the reader's thing.** "Every support email enters the pipeline and becomes a ticket", to a reader who calls it a complaint, a refund, or an order that went wrong. Use the noun the reader uses in their own meetings. The product's internal noun (ticket, pipeline, workflow, module, workspace, instance) belongs only next to a screen that labels it that way, and never in a heading.
109. **Stamped template.** The same sentence shape on every page: "A home for every X", "Every X becomes a Y", "Meet your new Z". One instance was written and the rest were filled in. Write each from its own subject.

## Calibration: don't overcorrect

Scrubbing every pattern produces a different artificial voice. These are tells because they are **empty**, not because the shape is banned.

- A contrast that carries real information stays. "It's not a rewrite, it's a config change" is a fact.
- Three things is right when there are exactly three things.
- Em dashes stay banned (rule 13). A dash that feels punchy is still a dash, so use a comma or a new sentence.
- Keep any number you actually measured, and keep the range if the range is real.
- Never apply this to quoted text, the user's own writing unless they asked for it, code, identifiers, or established domain and API terms.
- If a rewrite is longer or vaguer than the original, keep the original.

## Red flags: run the pass again

- You wrote a closing paragraph and it doesn't add a fact.
- You reached for a third item to round out a pair.
- You wrote a number you didn't get from a tool, a file, or the user.
- You used *serves as*, *underscores*, or *highlights*.
- A sentence sounds strong and you can't say what it claims.
- You're describing something as "not just" anything.
- A person in the reader's job would not say the sentence out loud about their own work.

## Rationalizations

| Excuse | Reality |
| --- | --- |
| "It's only a PR body" | Short copy is where the tells are most visible. Run the pass. |
| "The rhythm needs the third item" | Rhythm is what the third item is for. That's the tell. |
| "The range is roughly right" | Roughly right is invented. Cut it or measure it. |
| "The reader needs a summary" | If they need one, the body failed. Fix the body. |
| "It reads flat without the kicker" | Flat and true beats resonant and empty. |
| "I'll just soften it with a hedge" | Hedges hide that you don't know. Say what you know. |
