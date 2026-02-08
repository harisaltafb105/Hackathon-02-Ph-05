---
id: 009
title: Create Local-to-Cloud Promotion Skill
stage: general
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: none
labels: ["skill-creation", "cloud-promotion", "helm", "dapr", "kubernetes", "minikube", "zero-code-change"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/local-to-cloud-promotion/skills.md
tests:
  - none
---

## Prompt

kindly make another skills.md file in my skills folder Skill: Local-to-Cloud Promotion

Purpose:
Ensure zero-code-change migration from Minikube to cloud.

Input:
Helm charts, Dapr configs
Output:
Cloud-ready deployment plan
Used By:
Cloud Deployment Agent

## Response snapshot

Created the Local-to-Cloud Promotion skill at `.claude/skills/local-to-cloud-promotion/skills.md`. The skill establishes the zero-code-change principle as its foundation, defines a 4-stage promotion ladder (L1 Docker Compose → L2 Minikube → C1 Cloud Staging → C2 Cloud Production), provides detailed step-by-step processes for the L2→C1 and C1→C2 transitions covering Helm values overrides, Dapr component swaps, K8s Secrets creation, resiliency tuning, and deploy+validate commands. Includes a deployment diff report template, pre-flight checklists for both promotion boundaries, common blocker troubleshooting table, multi-environment file organization, and a final validation rule that blocks promotion if any application code differs across environments.

## Outcome

- Impact: New skill added to `.claude/skills/` providing the Cloud Deployment Agent with a systematic, repeatable process for promoting services from Minikube to cloud with zero application code changes
- Tests: none
- Files: 1 file created (.claude/skills/local-to-cloud-promotion/skills.md)
- Next prompts: Use the skill when promoting a service from local to cloud staging; validate against real Helm charts and Dapr configs
- Reflection: Aligned promotion ladder with Phase V orchestrator's 4-stage model. Ensured Dapr component naming convention matches dapr-component-authoring skill. Referenced Helm chart patterns from helm-chart-generation skill. Emphasized the zero-code-change invariant as a hard blocker throughout.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS - follows skill format conventions, aligns with cloud-k8s-deployer agent and phase-v-orchestrator promotion gates
- Prompt variant: baseline
- Next experiment: Execute a real L2→C1 promotion using the skill's checklist to validate completeness
