# Forensics: a diagnosis, not a fix

Two shapes of diagnosis that both end in a cited cause rather than a patch. Use them when the deliverable is the answer to "why is this happening", or when the fix is not yours to make. Route the fix back to `debug`'s fix half, or to `implement` as a ticket, once the cause is known.

Both keep the throughput checkpoint to one line: `throughput checkpoint: n/a, read-only forensics`.

## Runtime forensics

**You own the diagnosis. Instrument the live process, don't theorize from source.** The deliverable is a cited diagnosis, not a fix.

1. Capture the live signal on the matching surface: a CPU profile for a spinning process, a heap snapshot for a leak, a CDP trace for a visual glitch. A real artifact, not a guess.
2. Reduce the artifact to the smoking gun: the function on the hot path, the retainer chain from the leaked object to a GC root, the loop firing without input. Parse large artifacts in a Herdr pane (`herdr`, the `cheap` role) and keep the reduced finding in this session; the raw artifact is bulk, the finding is what matters.
3. Prove the mechanism before believing it. Inject instrumentation via CDP eval on the running process, or hotfix the live code without reloading, to confirm the hypothesis cheaply.
4. Map the finding back to source: file, symbol, the line that allocates or schedules.
5. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only forensics`.

**Reply:** the signal captured, the reduced finding, how you proved the mechanism, the source location, artifact paths. No fix unless asked. Hand back to `debug`'s fix half or to `implement` once the cause is known.

## Trace forensics

**You own the diagnosis from the artifact.**

Distinct from runtime forensics, which instruments the live process. Here the capture already exists. The artifact is a fixed dataset, read it, don't re-run it. Keep tooling generic: a DevTools or trace parser for cpuprofile and `.json.gz`, a text editor for a spindump, your heap tooling for a heapsnapshot.

1. Identify the format and load it with the right tool. Parse large artifacts in a Herdr pane (`cheap` role) and keep the reduced finding in the main thread.
2. Transform the raw artifact into a form you can query. Dump the trace or heap snapshot into sqlite, one row per sample, frame, or node. Reach the queryable shape before you read.
3. Narrow to the cause. Query for the frames that hold the most time and walk the call tree to the hot path. For a leak, follow the retainer chain from the leaked object to a GC root. For a spindump, find the thread stuck on-CPU or blocked and its wait reason.
4. Attribute to source. Map the hot frame to file, symbol, and line via the artifact's own symbols. A frame with no source mapping is not yet a diagnosis. Resolve the symbols, or say plainly the artifact does not carry them.
5. If you have a paired capture, diff the before and after artifacts to confirm. Otherwise, mark the finding as the strongest hypothesis the artifact supports, not a confirmed cause.
6. Hand back a cited diagnosis, no fix unless asked. Route to `debug`'s fix half or to `implement` once the cause is known. Throughput checkpoint stays one line: `throughput checkpoint: n/a, read-only forensics`.

**Reply:** the artifact and format, the reduced finding, the source location, the artifact paths, and whether a paired capture confirmed it.

## Redaction

Everything here shows artifacts. Redact every secret first: `<REDACTED>` in its place, and only the lines that carry the signal. If redaction leaves too little to diagnose, say so and ask for more.
