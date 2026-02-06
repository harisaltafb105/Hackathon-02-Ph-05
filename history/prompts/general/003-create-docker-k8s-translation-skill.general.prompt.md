---
id: 003
title: Create Docker to Kubernetes Translation Skill
stage: general
date: 2026-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: user
command: /agents
labels: ["skills", "docker", "kubernetes", "translation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/docker-kubernetes-translation/skills.md
tests:
  - none
---

## Prompt

create a skills.md file in my skills folder Docker → Kubernetes Translation Skill

Purpose
Translate application runtime needs into container + K8s primitives.

Capabilities

Identify required ports, env vars, volumes

Decide Deployment vs Service vs Ingress

Ensure stateless containers

Output

Valid container + K8s mapping

Warnings for anti-patterns

## Response snapshot

Created `.claude/skills/docker-kubernetes-translation/skills.md` with comprehensive Docker to Kubernetes translation skill documentation including:
- Purpose section defining the skill's goal
- Capabilities covering resource identification, K8s resource type decisions, and container best practices
- Output examples showing valid container + K8s mapping in YAML format
- Warnings for both container and K8s anti-patterns
- Translation checklist for verification
- Common mappings table for Docker-to-Kubernetes concept translation

## Outcome

- Impact: Added new skill documentation for Docker to Kubernetes translation workflows
- Tests: N/A - documentation file
- Files: 1 file created (.claude/skills/docker-kubernetes-translation/skills.md)
- Next prompts: Use this skill when containerizing applications or generating K8s manifests
- Reflection: Skill follows existing skills.md format pattern from other skills in the folder

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
