---
id: 005
title: Create AI-Assisted Infra Debugging Skill
stage: general
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: none
labels: ["skills", "kubernetes", "debugging", "kubectl", "kagent", "infrastructure"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/ai-infra-debugging/skills.md
tests:
  - none
---

## Prompt

create a skills.md file in my skills folder AI-Assisted Infra Debugging Skill

Purpose
Diagnose infra issues using kubectl-ai + kagent outputs.

Capabilities

Read pod logs & events

Correlate failures (CrashLoop, ImagePullBackOff)

Suggest minimal corrective action

Output

Root cause

Fix recommendation

Confidence level

## Response snapshot

Created `.claude/skills/ai-infra-debugging/skills.md` with comprehensive AI-assisted infrastructure debugging skill documentation including:
- Purpose: Diagnose infra issues using kubectl-ai + kagent outputs
- Capabilities: Reading pod logs/events, correlating failures, suggesting minimal corrective actions
- Failure correlation tables for CrashLoopBackOff, ImagePullBackOff, and other common failures
- Output format templates: Root cause analysis, fix recommendation, confidence level assessment
- Diagnostic workflows for common scenarios (CrashLoop, ImagePull, Pending pods)
- kagent integration guidance and signal interpretation
- Common fix patterns with YAML examples
- Escalation criteria for human operator involvement
- Quick reference tables for exit codes and pod conditions

## Outcome

- Impact: Added new skill documentation for AI-assisted Kubernetes infrastructure debugging
- Tests: N/A - documentation file
- Files: 1 file created (.claude/skills/ai-infra-debugging/skills.md)
- Next prompts: Use this skill when debugging Kubernetes infrastructure issues with kubectl-ai and kagent
- Reflection: Skill provides structured approach to infra debugging with confidence levels for recommendations

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
