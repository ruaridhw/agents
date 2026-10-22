# Copy-review word list

The vocabulary rotates. "Delve" and "tapestry" were 2023 markers and have faded; "core," "modern," "showcasing," and "highlighting" replaced them. Treat these lists as a starting scan, not a ban list. The test is always whether the word carries information.

## Copula avoidance ([kill list #11](copy-review.md#kill-list))

Replace with *is*, *are*, *has*:

serves as · stands as · functions as · operates as · represents · marks · constitutes · boasts · features · maintains · offers · provides

## Participial tails ([kill list #10](copy-review.md#kill-list))

A clause ending in one of these is almost always restating what came before it:

underscoring · highlighting · emphasizing · showcasing · reflecting · symbolizing · demonstrating · ensuring · fostering · cultivating · reinforcing · contributing to · paving the way for · setting the stage for · marking a shift in

## Puffery vocabulary ([kill list #18](copy-review.md#kill-list))

**Verbs:** leverage · unlock · empower · navigate · streamline · elevate · harness · drive · enable · transform · revolutionize · delve

**Adjectives:** seamless · robust · vibrant · rich · profound · intricate · pivotal · crucial · vital · groundbreaking · cutting-edge · comprehensive · holistic · meticulous · enduring · renowned

**Nouns:** ecosystem · landscape · framework · journey · space · realm · tapestry · testament · paradigm · synergy · game-changer · deep dive

## Signpost and hedge tics ([kill list #6](copy-review.md#kill-list), [#13](copy-review.md#kill-list))

**Openers:** Here's the thing · Let me be clear · It's important to note that · At its core · When it comes to · In today's fast-paced world · Let's unpack this · Let's dive in · First and foremost

**Hedges:** generally speaking · in most cases · it's worth noting · that said · while it may vary · arguably · to some extent · results may vary

**Warmth garnish:** Great question! · I'm glad you asked · Hope this helps! · Let me know if you'd like me to go deeper

**Closers:** In short · In summary · In conclusion · Ultimately · At the end of the day · The bottom line is · Remember that

## Borrowed authority ([kill list #12](copy-review.md#kill-list))

industry experts say · studies show · research suggests · it's widely regarded · many argue · observers have noted · analysts predict · trade publications report · sources indicate

Name the source, link it, or drop the claim.

## Worked example

**Draft:**

> Here's the thing: our new caching layer isn't just a performance tweak. It's a rethink of how the API serves data. Fast. Predictable. Cheap. Think of it as the Redis of request handling — less a bucket, more a pipeline. Industry benchmarks suggest response times drop by 30 to 50%, underscoring the value of edge-first architecture. It's worth noting that, generally speaking, results may vary. In short, the future of latency belongs to teams that cache closer to the user.

**The pass:**

| Quoted line | Tell | Action |
| --- | --- | --- |
| "Here's the thing:" | #6 throat-clearing | delete |
| "isn't just a performance tweak. It's a rethink" | #1 not X, that's Y | keep the Y |
| "Fast. Predictable. Cheap." | #7 always three, #2 stuck fragments | delete; none is a claim |
| "the Redis of request handling" | #5 X is the Excel of Y | name the job |
| "less a bucket, more a pipeline" | #3 empty metaphor pair | say the action |
| "Industry benchmarks suggest" | #12 borrowed authority | no source exists |
| "30 to 50%" | #8 fake range | never measured — cut |
| "underscoring the value of edge-first architecture" | #10 participial tail | delete |
| "It's worth noting that, generally speaking, results may vary" | #13 hedge stack | delete |
| "In short," | #9 recap ending | delete |
| "the future of latency belongs to teams..." | #15 pseudo-profound kicker | delete |

**Rewrite:**

> The new caching layer moves response assembly to the edge. Reads that used to hit Postgres resolve from a regional cache, so the API answers without a round trip to the primary region. We haven't benchmarked the latency change yet.

89 words to 44. Note what the pass forced: deleting the invented range left a hole, and the only honest patch was admitting the benchmark hasn't been run. That is the point of #8 — a fabricated number is usually covering for work nobody did.
