---
id: 008
title: Create Dapr Component Authoring Skill
stage: general
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: none
labels: ["skill-creation", "dapr", "component-yaml", "infrastructure", "kubernetes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/dapr-component-authoring/skills.md
tests:
  - none
---

## Prompt

kindly make another skills.md file in my skills folder Skill: Dapr Component Authoring

Purpose:
Generate portable Dapr component YAMLs.

Input:
Infra choice (Kafka, DB, Secrets)
Output:
Validated Dapr components
Used By:
Dapr Integration Agent

## Response snapshot

Created the Dapr Component Authoring skill at `.claude/skills/dapr-component-authoring/skills.md`. The skill provides a complete component catalog with local and production YAML variants for 8 component types (Kafka pub/sub, Redis state store, PostgreSQL state store, local file secret store, Kubernetes secret store, cron input binding, SMTP output binding, HTTP webhook output binding), plus resiliency policy templates, declarative subscription configuration, file organization conventions, a portability matrix, naming conventions, validation checklist, and common authoring mistakes reference.

## Outcome

- Impact: New skill added to `.claude/skills/` enabling systematic generation of validated Dapr component YAML files for use by the Dapr Integration Agent
- Tests: none
- Files: 1 file created (.claude/skills/dapr-component-authoring/skills.md)
- Next prompts: Use the skill when configuring Dapr components for new services; pair with the event-driven-feature-mapping skill for end-to-end feature-to-infrastructure mapping
- Reflection: Aligned component patterns with Dapr Integration Agent conventions. Included both local and production variants for every component to ensure environment portability. Referenced project-specific infrastructure (Neon PostgreSQL, Kafka/Redpanda) from the constitution.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS - follows skill format conventions, covers all infrastructure choices mentioned in input requirements
- Prompt variant: baseline
- Next experiment: Validate skill usage by having the Dapr Integration Agent generate components from this skill's templates for a real service
