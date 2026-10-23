# Source playbooks

`research` spawns one investigator per available evidence category, each reading a single source-specific playbook below. The playbooks are concrete for the connectors that exist here. Adapt one for a different connector in the same category.

| Category | Playbook | The connector it documents |
|---|---|---|
| Source control history | [`sources/code-archaeology.md`](./sources/code-archaeology.md) | git, `gh` (pull requests, reviews, commits) |
| Issue / ticket tracker | [`sources/tracker.md`](./sources/tracker.md) | kata or GitHub Issues, per `.agents/tracker.md` |
| Agent history | [`sources/agentsview.md`](./sources/agentsview.md) | AgentsView (`agentsview session search`) |
| Long-form documents | [`sources/notion.md`](./sources/notion.md) | Notion |
| Real-time team chat | [`sources/slack.md`](./sources/slack.md) | Slack |
| Meeting notes | [`sources/granola.md`](./sources/granola.md) | Granola (synced into Notion) |
| Infrastructure observability | [`sources/datadog.md`](./sources/datadog.md) | Datadog |
| Error / exception tracking | [`sources/sentry.md`](./sources/sentry.md) | Sentry |

Cross-cutting:

- [`sources/incident-postmortem.md`](./sources/incident-postmortem.md). Add this if the target code looks defensive (null checks, retry, timeout, rate limit, feature flag, egress guard, OOM handler).

The product-analytics-warehouse category is not wired here: no analytics warehouse is reachable from this environment, so there is no playbook for it. A repo that gains one gets a playbook beside these, following the shape of `sources/datadog.md`.
