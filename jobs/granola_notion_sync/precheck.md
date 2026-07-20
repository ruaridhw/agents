Cheap pre-check — decide whether a full sync run is needed. Do not create,
update, or modify anything.

1. List my Granola meetings from the last 7 days (`list_meetings`) where
   ${GRANOLA_ACCOUNT_EMAIL} is the note creator and an AI summary exists.
2. Query the Notion Meetings data source
   (`collection://${NOTION_MEETINGS_DATA_SOURCE_ID}`) for the `Granola ID`
   column.
3. If every meeting from step 1 already has a row with its Granola ID, there
   is nothing to sync.

Reply with a single word as your entire final message: `NO_WORK` if nothing
needs syncing, `WORK` otherwise. If you cannot determine the answer, reply
`WORK`.
