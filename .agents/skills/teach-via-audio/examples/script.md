# How payment retries work. Episode one: the whole thing.

Payment retries, in one sentence. When a charge fails for a reason that might pass, the system waits, tries again on a schedule, and gives up cleanly if the schedule runs out.

## Layer one. Two kinds of failure.

A card can fail for a reason that will not change, like a closed account. Or it can fail for a reason that might, like a bank that is briefly down. Retries exist only for the second kind. The first kind is final, and the customer is told straight away.

## Layer two. The loop.

Every failed charge lands in a retry queue with a due time. A worker wakes up, picks up everything that is due, and tries each charge again. If it works, the charge leaves the queue. If it fails for a passing reason, it goes back with a later due time. If it fails for a final reason, it leaves the queue and the customer is told.

## Layer three. One worked example.

Take a charge of forty pounds that fails on Monday morning because the bank is down. The schedule is one hour, then one day, then three days. At ten the retry fails again, so the charge waits a day. On Tuesday it succeeds. The customer never knew, and that is the point of the loop.

## Layer four. The whole thing again.

Payment retries, in one sentence. A passing failure is waited out on a schedule, and a final one is reported at once.
