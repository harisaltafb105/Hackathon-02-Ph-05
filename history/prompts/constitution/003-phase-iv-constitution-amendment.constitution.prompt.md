---
id: 003
title: Phase IV Constitution Amendment
stage: constitution
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: system
command: /sp.constitution
labels: ["phase-iv", "kubernetes", "deployment", "infrastructure", "constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

Project: Phase IV – Local Kubernetes Deployment
System: Cloud-Native Todo Application with AI Chatbot
Scope: Deployment & Infrastructure Automation (Local Only)

1. Purpose & Authority

This constitution governs Phase IV only.

Phase IV's sole purpose is to containerize, deploy, and operate the already-implemented:

Full-stack Todo Application (Phase II)

Todo AI Chatbot (Phase III)

using local cloud-native infrastructure.

No application logic, UI, API behavior, or AI logic may be redesigned or rewritten in this phase.

This constitution overrides all assumptions from earlier phases only in matters of deployment and infrastructure.

2. Non-Negotiable Principles

Infrastructure-Only Phase

Phase IV must not introduce new features.

No frontend or backend business logic changes.

No schema or API redesign.

Spec-Driven Infrastructure

All infrastructure decisions must follow:

spec → plan → tasks → implement


No ad-hoc CLI experimentation without spec backing.

Local-First Cloud-Native

Deployment target is local Minikube only.

No cloud providers (AWS/GCP/Azure).

No production deployment assumptions.

Stateless Services

Frontend, backend, MCP server, and AI services must remain stateless.

Persistent state is allowed only in the database.

Reproducibility

A fresh machine must be able to reproduce the deployment using specs alone.

No hidden steps, no manual tweaks.

3. Mandatory Technology Stack

Containerization

Docker (Docker Desktop)

Docker AI Agent (Gordon) — preferred

Fallback: Standard Docker CLI if Gordon unavailable

Orchestration

Kubernetes (Minikube)

Packaging

Helm Charts (required)

AI-Assisted DevOps

kubectl-ai (required)

kagent (required)

Applications Deployed

Phase II Backend (FastAPI)

Phase III MCP Server

Phase III AI Agent Service

Frontend Application

4. Tooling Rules (CRITICAL)

Docker AI Usage

Use Docker AI Agent (Gordon) for:

Dockerfile generation

Image optimization

Build troubleshooting

If unavailable, explicitly document fallback usage.

Kubernetes AI Usage

Use kubectl-ai for:

Deployments

Scaling

Debugging pod failures

Use kagent for:

Cluster health analysis

Resource optimization insights

Documentation Source Rule (MANDATORY)

All installations, commands, and configurations MUST reference
MCP Server Context 7 documentation

No guessing, no outdated instructions.

Any dependency or tool install must be aligned with Context 7.

5. Deployment Architecture Rules

Each major component must be deployed as a separate Kubernetes Deployment:

frontend

backend

MCP server

AI agent service

Services must be exposed via Kubernetes Services.

Ingress may be enabled if required (Minikube-compatible).

Environment variables must be injected via:

Helm values

Kubernetes secrets (no hardcoding)

6. Environment & Secrets Handling

.env files are NOT committed

Secrets such as:

OPENAI_API_KEY

DATABASE_URL

BETTER_AUTH_SECRET

Must be passed via:

Helm values

Kubernetes secrets

The absence of secrets during spec/plan stages must NOT break implementation

7. Agent Governance

All actions must be performed through assigned agents:

Deployment Orchestrator

Containerization Agent

Helm Chart Agent

Kubernetes Operations Agent

Cluster Intelligence Agent

Minikube Environment Agent

Agents may:

Execute

Validate

Optimize

Agents may NOT:

Modify application behavior

Introduce new features

Skip spec validation

8. Failure Handling Policy

Any failure must be:

Diagnosed via kubectl-ai or kagent

Explained with root cause

Fixed using the smallest possible change

Silent retries or destructive resets without explanation are forbidden.

9. Success Criteria (Phase IV Completion)

Phase IV is considered SUCCESSFUL only when:

All services run on Minikube

Pods are healthy and restart-safe

Frontend communicates with backend and AI chatbot

MCP tools function correctly via deployed services

Deployment is reproducible from specs

No manual steps are required post-implementation

10. Explicit Out-of-Scope

Cloud hosting

CI/CD pipelines

Production hardening

Monitoring stacks

## Response snapshot

Constitution amended from v2.0.0 to v3.0.0 with Phase IV deployment principles. Added 6 new non-negotiable principles (XIV-XIX) covering infrastructure-only constraints, spec-driven infrastructure, local-first cloud-native deployment, reproducibility, AI-assisted DevOps sovereignty, and failure diagnosis protocol. Added Phase IV technology stack, agent roles, success definition, and explicit out-of-scope sections.

## Outcome

- ✅ Impact: Major version bump (2.0.0 → 3.0.0) reflecting 6 new non-negotiable principles for Phase IV
- 🧪 Tests: N/A (constitution document)
- 📁 Files: .specify/memory/constitution.md updated
- 🔁 Next prompts: /sp.specify for Phase IV deployment features, /sp.plan for deployment implementation
- 🧠 Reflection: Phase IV principles successfully integrated while preserving all Phase II and III constraints

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, version incremented correctly
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate agent definitions match constitution roles
