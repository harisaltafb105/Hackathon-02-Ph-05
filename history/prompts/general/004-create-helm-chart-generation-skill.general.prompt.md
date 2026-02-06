---
id: 004
title: Create Helm Chart Generation Skill
stage: general
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: none
labels: ["skills", "helm", "kubernetes", "charts", "deployment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/helm-chart-generation/skills.md
tests:
  - none
---

## Prompt

create a helm chart generation skill

## Response snapshot

Created `.claude/skills/helm-chart-generation/skills.md` with comprehensive Helm chart generation skill documentation including:
- Purpose: Generate production-ready Helm charts from application specifications
- Capabilities: Chart structure generation, template generation, values management, best practices enforcement
- Output examples: Complete chart structure, Chart.yaml, values.yaml, _helpers.tpl templates
- Warnings for chart, values, and template anti-patterns
- Generation checklist for verification
- Common Helm functions reference table
- Minikube compatibility section with specific considerations and example values

## Outcome

- Impact: Added new skill documentation for Helm chart generation workflows
- Tests: N/A - documentation file
- Files: 1 file created (.claude/skills/helm-chart-generation/skills.md)
- Next prompts: Use this skill when generating Helm charts for Kubernetes deployments
- Reflection: Skill provides comprehensive guidance for Helm chart creation with practical examples

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
