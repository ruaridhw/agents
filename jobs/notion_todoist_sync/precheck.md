Cheap pre-check — decide whether the full reconciliation is needed. Do not
create, update, or modify anything.

Query the Notion Tasks data source
(`collection://${NOTION_TASKS_DATA_SOURCE_ID}`) once: count rows whose
`Status` is not `Done` and not `Cancelled`, and rows with a non-empty
`Todoist ID` whose `Status` is not `Done`/`Cancelled`. Then query the Meetings
data source (`collection://${NOTION_MEETINGS_DATA_SOURCE_ID}`) for rows dated
within the last 7 days.

If there are **no** open task rows, **no** open synced (Todoist ID) rows, and
**no** meetings from the last 7 days, nothing needs reconciling.

Reply with a single word as your entire final message: `NO_WORK` if nothing
needs reconciling, `WORK` otherwise. If you cannot determine the answer,
reply `WORK`.
