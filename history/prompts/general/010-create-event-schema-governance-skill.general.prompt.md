---
id: 010
title: Create Event Schema Governance Skill
stage: general
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: none
labels: ["skill-creation", "kafka", "schema-governance", "event-versioning", "compatibility", "breaking-changes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/event-schema-governance/skills.md
tests:
  - none
---

## Prompt

make another skills.md file in my skills folder Skill: Event Schema Governance

Purpose:
Prevent breaking changes in Kafka events.

Input:
Event definitions
Output:
Versioned schema contracts
Used By:
Kafka Event Architecture Agent

## Response snapshot

Created the Event Schema Governance skill at `.claude/skills/event-schema-governance/skills.md`. The skill defines the frozen canonical event envelope, four compatibility modes (BACKWARD, FORWARD, FULL, NONE) with default assignments per event classification, a three-tier change classification system (Safe/Minor/Breaking) with concrete examples for each, a four-step schema review process (Classify → Check Compatibility → Validate Structure → Consumer Impact Assessment), a four-phase breaking change migration runbook (Prepare → Dual-Publish → Consumer Cutover → Deprecation) with tracking template, schema registry patterns with subject naming conventions, a reusable schema definition template with field inventory and change history, reference schemas for four Todo application events (task.created, task.completed, task.priority-changed, reminder.fired), a governance checklist tiered by change severity, and a common violations table.

## Outcome

- Impact: New skill added to `.claude/skills/` providing the Kafka Event Architect Agent with a systematic process for preventing breaking schema changes and safely evolving event contracts
- Tests: none
- Files: 1 file created (.claude/skills/event-schema-governance/skills.md)
- Next prompts: Apply the governance process to a real schema change; validate the review checklist against existing event definitions in the project
- Reflection: Aligned envelope structure with Kafka Event Architect agent's existing standard. Referenced compatibility modes and versioning strategy from the agent's methodology. Connected consumer impact assessment to the event-driven-feature-mapping skill's producer/consumer tables. Included concrete Todo app reference schemas to make the skill immediately actionable.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS - follows skill format conventions, aligns with kafka-event-architect agent schema validation and versioning rules
- Prompt variant: baseline
- Next experiment: Run a simulated schema change through the review process to validate the classification and compatibility checking steps
