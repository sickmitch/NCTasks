# Nextcloud Tasks Desktop
**Proof of concept.**<br />
Visualizing take count of priority, due and parent-son relation.<br />
The entrypoint is **cal_visualizer.sh**.

## Roadmap
- [x] New Task
- [x] Add action selector
  - [x] Delete Task
  - [x] Add/Change Status
  - [x] Add/Change Due
  - [ ] Due Hour
  - [x] Add/Change Prio
  - [x] Change Summary - To check the empty case
  - [x] Add Secondary Tasks
- [ ] Clean Code (In Process)

## Known problems
- [ ] Can't have duplicates or same beginning of the string for summary (TEST will be confused with TESTERINO in the UID extraction)
- [ ] Can submit tasks without summary if not entered during change summary action
- [ ] Can't delete directly tasks created by NCTasks from Nextcloud browser UI, only if completed can be bulky erased, possible problems are:
  - different ID, i use nctasks@ID instead of only numeric
  - incomplete .ics structure
  - .ics field origin not standard
