---
id: 001
title: Advanced Todo Features Specification
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 006-advanced-todo-features
branch: 006-advanced-todo-features
user: user
command: /sp.specify
labels: ["specification", "priority", "tags", "search", "filter", "sort", "due-dates", "reminders", "recurring-tasks", "phase-v"]
links:
  spec: specs/006-advanced-todo-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-advanced-todo-features/spec.md
  - specs/006-advanced-todo-features/checklists/requirements.md
tests:
  - none
---

## Prompt

/sp.specify — Generate a precise, implementation-ready specification for completing ONLY the Intermediate and Advanced feature set of an already working Full-Stack Todo Application with an AI Chatbot. This specification is intentionally feature-scoped and infrastructure-agnostic — no Kafka, Dapr, K8s, cloud, CI/CD, or monitoring.

Intermediate Features: Priority levels (none/low/medium/high/urgent), tags/labels, search across tasks, filter by status/priority/tags/due date, sort by priority/due date/created/title.

Advanced Features: Due dates (YYYY-MM-DD, overdue detection), reminders (scheduling logic only — no notification delivery), recurring tasks (recurrence logic only — FREQ=DAILY|WEEKLY|MONTHLY with RRULE subset).

Baseline: Existing Task model (id, title, description, completed, created_at, updated_at, user_id), existing CRUD endpoints, existing AI Chatbot with MCP tools, FastAPI + SQLModel + Neon PostgreSQL, Next.js frontend, Better Auth JWT.

## Response snapshot

Created feature specification at `specs/006-advanced-todo-features/spec.md` with 8 user stories (P1-P4), 50 functional requirements across 10 categories (Priority, Tags, Search, Filtering, Sorting, Pagination, Due Dates, Reminders, Recurring Tasks, AI Chatbot Integration), 2 key entities (extended Task + new Reminder), 4 new API endpoints, modified existing endpoints with query parameters for search/filter/sort/pagination, 13 success criteria with performance targets, 9 database index requirements, and 8 edge cases. Created quality checklist at `specs/006-advanced-todo-features/checklists/requirements.md` — all checks PASS.

## Outcome

- Impact: New feature specification ready for `/sp.plan` — covers all intermediate (priority, tags, search, filter, sort) and advanced (due dates, reminders, recurring tasks) features with 50 functional requirements
- Tests: none (specification phase — tests defined in acceptance scenarios)
- Files: 2 files created (spec.md, checklists/requirements.md)
- Next prompts: Run `/sp.plan` to create the implementation plan for 006-advanced-todo-features; consider `/sp.adr` for recurrence rule format decision (simplified RRULE vs custom format)
- Reflection: Maintained strict infrastructure agnosticism — zero references to Kafka, Dapr, K8s, or cloud. Aligned with existing Task model and API patterns from 003-backend-api spec. Included AI Chatbot integration requirements (FR-090 through FR-096) to extend Phase III capabilities. Paginated response format is a breaking change to the GET tasks endpoint that must be handled carefully during implementation. The recurrence_group_id design links recurring task instances without requiring a separate RecurrenceRule table — simpler but less flexible.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell create-new-feature script had positional parameter error with prompts directory creation, but branch and spec directory were created successfully
- Graders run and results (PASS/FAIL): manual review PASS — 50 FRs traceable to 8 user stories, all acceptance scenarios in Given/When/Then, infrastructure agnosticism verified, quality checklist all-pass
- Prompt variant: baseline
- Next experiment: Run /sp.plan to validate that the 50 FRs can be decomposed into an implementable plan within existing codebase constraints
