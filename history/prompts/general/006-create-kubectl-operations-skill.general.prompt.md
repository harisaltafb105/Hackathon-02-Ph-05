---
id: 006
title: Create Kubectl Operations Skill
stage: general
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: none
labels: ["skills", "kubernetes", "kubectl", "operations", "cluster-management"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/kubectl-operations/skills.md
tests:
  - none
---

## Prompt

create a kubectl operations skill

## Response snapshot

Created `.claude/skills/kubectl-operations/skills.md` with comprehensive kubectl operations skill documentation including:
- Purpose: Execute Kubernetes cluster operations with safety-first practices
- Capabilities: Resource management, workload operations, service/networking, configuration
- Core commands reference: Context/namespace, resource viewing, deployment ops, pod ops, service ops, ConfigMap/Secret ops
- Safety practices: Pre-operation checks, safe delete patterns, rollback readiness
- Troubleshooting patterns: Pod not starting, service not accessible, high resource usage
- Minikube-specific operations: Start/stop, dashboard, addons, image loading, tunneling
- Output formatting: JSONPath queries, filtering by labels/fields
- Quick reference tables: Resource short names, common flags, dangerous commands

## Outcome

- Impact: Added comprehensive kubectl operations skill for Kubernetes cluster management
- Tests: N/A - documentation file
- Files: 1 file created (.claude/skills/kubectl-operations/skills.md)
- Next prompts: Use this skill when performing kubectl operations on Kubernetes clusters
- Reflection: Skill emphasizes safety practices and includes Minikube-specific guidance for local development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
