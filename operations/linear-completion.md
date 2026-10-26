---
role: authored
---
# Guide: Complete Linear Tasks

Use this guide whenever work tracked by a Linear issue is finished, including
a Beat, an Arc, or an issue that existed only to ask a question. It owns the
completion record and removal procedure. The task's own acceptance rules still
decide when its work is complete; [Working in Sagas](sagas.md) owns plans,
hand-over, progress, merges and holds. Connector and UI mechanics belong to
the [Linear runbook](../tools/linear.md).

## Record completion, then remove the issue

The owner's direction of 21 October 2026 is to remove completed tasks from
Linear instead of setting their issues to Done, while retaining every completed
task ID in a separate artifact. On 26 October 2026 the owner gave standing
authorization to remove Linear tasks whenever needed, including older Done
issues, without asking permission. Linear is a backup and convenient view;
the artifacts are the source of truth. Preserve authoritative work and relevant
discussion before removal and use recoverable deletion. Removing an unfinished
issue does not complete its work: preserve its pending work in its authoritative
file. Permanent purging still needs an explicit request.

Linear's Free plan limits non-archived issues. Keeping completed work in the
artifact lets agents recognize it after its issue has been removed. `Done`
remains a valid outcome in local task files and progress reports; it is no
longer the final action on the Linear issue.

## The completion archive

The private records live under `~/Artifacts/sagas/completed-linear-tasks/`,
shared by all projects and tools. The small index at
`~/Artifacts/sagas/completed-linear-tasks.md` links to the record files; it
holds no task rows. Keep one row per workspace and issue identifier across the
whole folder; the same identifier in another workspace is a different record.
The archive stays in the private Sagas repository, including tasks outside a
Saga. Never put its task records into the public Mycel corpus.

### Weekly files, at most 100 tasks each

Use the task's actual completion time to choose its ISO week, Monday through
Sunday in Europe/Madrid. Name the first file `YYYY-Www-01.md`; within the same
week use `-02.md`, `-03.md` and so on. Each file holds at most 100 task records
in total, across all workspace sections. Start the next part before adding a
101st record, and use a new week's first file when that completion week changes.
For an unknown historical completion date use `undated-01.md` and later parts;
do not invent a completion date from the import or deletion time.

Before adding a task, search every record file for its workspace and ID. Update
an existing row in place, even when its removal is verified in a later week.
Append new rows to the last part of the appropriate week that has room. Do not
renumber older parts or move existing records merely because removal happens
later. Add a link to each new file in the index; never duplicate its task rows
there. Keep a task's completion notes in the same file as its row.

Each row keeps the identifier, issue UUID, title, project, actual completion
time when known, original URL, local task or decision file when one exists,
and removal state. Use `not recorded` for an unknown historical completion time;
never substitute the date the row was collected. Removal is `retained` while
the issue still exists, `pending` once removal is intended, and the verified
UTC deletion time after success. These values distinguish recorded completion
from confirmed removal. Keep the original ID and URL after deletion.

Details needed by later work belong in the existing task's hand-over or decision
file. When there is no such file, add a short section under that issue's ID in
its weekly record file and link the row to it. Preserve the result, acceptance
evidence or code references, prerequisite IDs, and any discussion needed by
unfinished tasks before removing their only Linear record.

## Finish a task

1. **Verify the workspace and completion.** Read the live issue, its children,
   prerequisite relations and relevant comments. Apply the task's acceptance
   rules. A parent with unfinished children stays in Linear; finish and record
   its completed children individually. A canceled task is not a completed one.
2. **Keep what later work needs.** Finish the task file and hand-over, mark its
   local progress Done, and record its prerequisite IDs and any dependent work
   outside Linear. Update the Arc, Saga or decision source as its guide says.
   A comment that an existing workflow requires is also preserved in the local
   hand-over or decision record before its issue is removed.
3. **Record the ID before deletion.** Search the completion archive and add or
   update the row in the appropriate weekly file, with removal `pending`. Create
   and index a new part when needed; never exceed 100 records or add a duplicate.
   Commit and push the record file, any index change and changed task/progress
   files, with Git's existing identity. If another agent changed the records, combine both sets
   of rows and retry; never overwrite its records or force-push.
4. **Remove the issue.** Once the saved record is durable, use Linear's ordinary
   recoverable delete. Do not set the issue to Done as a substitute, and do not
   purge it. Delete a completed parent only after all its children have been
   completed, recorded and removed, so deletion cannot remove unfinished work.
5. **Verify and record the removal.** Confirm it is absent from the normal issue
   list and present in Recently deleted, or use an explicit successful deletion
   result plus a normal-list read-back. Record the actual UTC deletion time,
   commit and push. Report completion and removal separately if either failed.

Completed IDs already recorded in the archive are finished prerequisites even
when Linear can no longer return their issues. Read their local task files and
hand-over. A missing issue without a completion record is unknown, not proof
that its work was finished. If live state shows a recorded task reopened, resolve
the discrepancy before treating it as complete; retain its history and record
the reopening beside that task's original row.

## Resume and publication

- If the record cannot be saved or pushed, leave the issue in place.
- If deletion is unavailable or fails, leave removal `pending`, report the
  outstanding removal and retry later. Do not claim capacity was released.
- If a run ends after deleting an issue but before recording the deletion time,
  inspect Recently deleted before retrying; never create a replacement issue.
- Publish changes to surviving issues, project pages and documents. Skip issue
  copies whose removal was confirmed in a record file. A stale mapping or a
  failed lookup must never recreate a completed task.
- For progress tools, search all weekly files, not just the index or newest
  week, and merge their completed IDs into the status input
  as Done, including tasks absent from Linear. Keep live reopened issues out of
  that merge until their recorded history is reconciled.

Linear normally retains deleted issues for 30 days before permanent removal.
The durable record is the private archive and task files, rather than that
recovery window. [Linear deletion documentation](https://linear.app/docs/delete-archive-issues)
and [archived-issue allowance](https://linear.app/startups) were checked on
21 October 2026.
