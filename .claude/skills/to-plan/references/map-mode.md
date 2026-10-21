# Map mode

For an effort too big and too foggy for one session. The map charts the way to a named destination (usually a spec) as decision tickets on the tracker; each ticket resolves a question; when nothing is left to decide, hand off to `to-spec`.

1. **Name the destination** in one or two lines: the spec, decision or change this effort is finding its way to.
2. **Create the map issue** (kind `map`, title `Map: <effort>`): body sections `## Destination`, `## Notes` (domain, skills to consult, standing preferences), `## Decisions so far` (one line per closed ticket: name, link, gist), `## Not yet specified` (in-scope fog that cannot be ticketed yet), `## Out of scope`. The map is an index: a decision lives only in its ticket.
3. **Create decision tickets** as children of the map (kind `decision`), each `## Question` sized to one session, typed `research`, `prototype`, `grill` or `task`, with native blocked-by edges. No triage labels: these are decisions, not build work.
4. **Work the frontier** one ticket per session: claim it (assign it) first, resolve it with the matching skill, write the answer into the ticket, close it, add its gist to the map, graduate fog into new tickets as the frontier moves.
5. **Refer by name**, never by bare id, in everything Ruaridh reads.
6. **Hand off** when the way is clear: `to-spec` collapses the map's decisions into a spec. Do not loop straight into `implement` unless the effort turned out small.
