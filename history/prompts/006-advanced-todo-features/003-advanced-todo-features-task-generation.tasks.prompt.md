---
id: 003
title: Advanced Todo Features Task Generation
stage: tasks
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 006-advanced-todo-features
branch: 006-advanced-todo-features
user: user
command: /sp.tasks
labels: ["tasks", "priority", "tags", "search", "filter", "sort", "due-dates", "reminders", "recurring-tasks", "backend", "frontend", "mcp-tools"]
links:
  spec: specs/006-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-advanced-todo-features/tasks.md
tests:
  - none
---

## Prompt

/sp.tasks — Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.

## Response snapshot

Generated comprehensive tasks.md at `specs/006-advanced-todo-features/tasks.md` with 90 tasks across 11 phases. Phase 1 (Setup) has 12 tasks covering model extension and schema updates across `backend/models.py` and `backend/schemas.py`. Phase 2 (Foundational) has 4 tasks for the pagination breaking change across backend and frontend. Phases 3-10 cover all 8 user stories (US1: Priority 9 tasks, US2: Tags 10 tasks, US3: Search 5 tasks, US4: Filter 8 tasks, US5: Sort 6 tasks, US6: Due Dates 8 tasks, US7: Reminders 8 tasks, US8: Recurring 9 tasks). Phase 11 (Integration & Regression) has 11 tasks covering full integration flows and regression safety. Tasks organized by user story with [P] parallel markers and [Story] labels. Dependency graph documented with recommended single-developer execution sequence and MVP delivery point after US1+US2.

## Outcome

- Impact: Complete task breakdown ready for `/sp.implement` — 90 tasks across 11 phases covering all 8 user stories, 50 FRs, 13 success criteria
- Tests: none (task generation phase — test tasks defined within tasks.md)
- Files: 1 file created (tasks.md)
- Next prompts: Run `/sp.analyze` to validate cross-artifact consistency; run `/sp.implement` to begin executing tasks; consider committing current spec artifacts
- Reflection: Tasks follow the template's user-story-first organization. Each story can be implemented and tested independently after Phase 1+2 setup. The recommended execution sequence reorders US4 (Filter) before US3 (Search) because filters use priority+tag concepts from US1+US2. 8 tasks marked [P] for parallel execution within phases. Cross-story parallelism documented for team scenarios. MVP delivery point identified after US1+US2 (priority + tags).

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS — all 90 tasks traceable to spec FRs and plan steps, user story organization matches spec US1-US8, dependency ordering respects file conflicts (same-file tasks sequential), parallel markers only on different-file tasks
- Prompt variant: baseline
- Next experiment: Run /sp.analyze to validate that tasks.md, plan.md, and spec.md are fully consistent before implementation
