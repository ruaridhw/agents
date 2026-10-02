# Serve and collect a review

Prerequisites: `plannotator` with `annotate --gate --json --result-file` support,
plus authenticated Tailscale when the operator is on another machine. Check
`plannotator annotate --help` before launching if the installed version differs.
The result file's parent must exist and the file must not; choose fresh paths for
each review so an older decision cannot approve a newer wave.

Launch in the background (replace paths, then retain the PID):

```sh
PLANNOTATOR_REMOTE=0 PLANNOTATOR_SKIP_BROWSER_OPEN=1 \
  plannotator annotate <review.html> --gate --json \
  --result-file <decision.json> > <session.log> 2>&1 &
review_pid=$!
```

Read `<session.log>` until it prints its listening URL; take the actual port from
that output, not a guessed default. If you need a fixed port, add
`PLANNOTATOR_PORT=<available-port>` and still verify the printed port. Confirm the
session started before offering a URL. Plannotator is a loopback annotation
backend, not a separate public preview server; keep remote mode off and expose
it privately through the tailnet:

```sh
tailscale serve --bg --http=<tailnet-port> http://127.0.0.1:<printed-port>
```

Use an unused tailnet port and the machine's actual tailnet name/IP. Give the
operator `http://<tailnet-host>:<tailnet-port>/` and an IP fallback. Read
`tailscale serve status` and smoke-test that URL through the tailnet IP; verify
that the annotation UI, not just the raw HTML, loads. On a local desktop, the
printed loopback URL is sufficient. If a project's security policy forbids
loopback backends, use its approved private forwarding mechanism or ask for
help; broad binding is not a workaround. The review content is private; avoid
public sharing/funnel.

Wait for the operator rather than killing the session to obtain a result. With
`--result-file`, exit 0 means approved, 1 means annotated/dismissed, and 2 means
a gate/startup/result-write failure. Read the actual decision JSON:

- `approved`: process any feedback notes before handing off to publication.
- `annotated`: apply the feedback and obtain approval of the revised wave.
- `dismissed`, missing file or launch failure: approval remains outstanding.

`feedback` is optional raw Markdown, not structured per-ticket data. Use quoted
spans and visible ticket/spec/source context to map annotations. Retain the
input, rendered page and decision together as review evidence.

Once the session has ended, remove only the forwarding entry you created:
`tailscale serve --http=<tailnet-port> off`.
Never reset other sessions' Tailscale configuration. A pending background process
is an active human review, not a completed gate.
