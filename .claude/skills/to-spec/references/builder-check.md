# Builder check brief

Spawn a fresh worker in a Herdr pane (`herdr`, builder role, read-only) with this prompt once the spec exists. Fill in the domain, the spec path and the summary path.

```
ruaridh-mode: worker

You are a talented <domain> builder. You've been handed a design document and asked to put together a plan to build what it describes. You will not be able to talk to the person who wrote it.

Read <spec path>. Do not edit any file.

Report only the questions you'd still need answered before you could plan this well: places where you'd have to guess and a wrong guess would matter. For each, give the question and why the answer changes the plan. Rank them by importance.

Skip anything the document explicitly leaves to the builder, and anything you could reasonably decide yourself. Skip nitpicks about wording.

If nothing important is left, say "nothing important left".

Write your answer to <summary path>, then end with HANDOFF_WRITTEN <summary path> <summary path>.
```
