---
id: 007
title: Create Event-Driven Feature Mapping Skill
stage: general
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: none
labels: ["skill-creation", "event-driven", "kafka", "dapr", "feature-mapping"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/event-driven-feature-mapping/skills.md
tests:
  - none
---

## Prompt

kindly make a skill in my skills folder Skill: Event-Driven Feature Mapping

Purpose:
Map Todo features → Kafka events → Dapr APIs.

Input:
Feature spec, event schema
Output:
Producer/consumer responsibilities
Used By:
Advanced Features Agent, Kafka Agent

## Response snapshot

Created the Event-Driven Feature Mapping skill at `.claude/skills/event-driven-feature-mapping/skills.md`. The skill provides a comprehensive 5-step mapping process (Feature Decomposition → Event Classification → Producer Assignment → Consumer Assignment → Dapr API Binding), reference mappings for all Todo feature tiers (Basic CRUD, Intermediate, Advanced), four Dapr-specific integration patterns (Pub/Sub, Jobs API, Service Invocation, Output Binding), a reusable feature-to-event mapping template, validation checklist, common mistakes table, and naming convention quick references.

## Outcome

- Impact: New skill added to `.claude/skills/` enabling systematic mapping of Todo features to Kafka events and Dapr APIs for use by Advanced Features Architect and Kafka Event Architect agents
- Tests: none
- Files: 1 file created (.claude/skills/event-driven-feature-mapping/skills.md)
- Next prompts: Use the skill when designing new Todo features with event-driven integration; run `/sp.adr` if Kafka/Dapr architecture decisions meet significance threshold
- Reflection: Followed existing skill conventions (Markdown reference document, structured sections, validation checklist). Aligned event naming with Kafka Event Architect agent conventions and Dapr API patterns with dapr-integration agent patterns.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS - follows skill format conventions, aligns with existing agent patterns
- Prompt variant: baseline
- Next experiment: Validate skill usage by running a feature mapping exercise with the Advanced Features Architect agent
