---
id: 011
title: Create Failure and Retry Strategy Skill
stage: general
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: none
labels: ["skill-creation", "retry", "dead-letter-queue", "idempotency", "circuit-breaker", "resilience", "dapr"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/failure-retry-strategy/skills.md
tests:
  - none
---

## Prompt

make another skills.md file in my skills folder Skill: Failure & Retry Strategy

Purpose:
Define retries, DLQs, and idempotency.

Input:
Service + event type
Output:
Resilience rules
Used By:
Notification Agent, Dapr Agent

## Response snapshot

Created the Failure & Retry Strategy skill at `.claude/skills/failure-retry-strategy/skills.md`. The skill provides a four-category error classification system (Transient, Rate-Limited, Permanent, Unknown) with a decision tree, five named retry policies (aggressive, standard, patient, critical, none) with tuned parameters for each, a complete DLQ strategy with message envelope, retention, alerting, and reprocessing modes, four idempotency patterns (Event ID Dedup, Idempotent Upsert, Conditional State Check, Transactional Outbox) with store selection guidance, per-dependency circuit breaker and timeout configurations, a Dapr resiliency YAML integration template, a pre-built service+event resilience matrix covering all Todo app services (notification, analytics, search-indexer, recurrence, reminder), a reusable rule definition template, validation checklist, and common mistakes table.

## Outcome

- Impact: New skill added to `.claude/skills/` giving the Notification Scheduler and Dapr Integration agents a systematic lookup for resilience rules per service+event combination
- Tests: none
- Files: 1 file created (.claude/skills/failure-retry-strategy/skills.md)
- Next prompts: Apply rules to a new consumer implementation; validate Dapr resiliency YAML generation matches the skill's catalog policies
- Reflection: Aligned retry policies with Notification Scheduler agent's default (exponential backoff, 5 retries, 5m window). Connected DLQ naming to Kafka Event Architect's internal topic convention. Mapped idempotency patterns to Dapr state store components from dapr-component-authoring skill. Ensured circuit breaker settings complement the resiliency YAML patterns already defined.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS - covers all three dimensions (retries, DLQs, idempotency) requested in the spec, aligns with both consuming agents
- Prompt variant: baseline
- Next experiment: Validate the resilience matrix by tracing a todo.reminder.fired event through the notification-svc failure path end-to-end
