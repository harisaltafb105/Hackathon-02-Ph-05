---
id: 004
title: Phase V Constitution Amendment
stage: constitution
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "phase-v", "event-driven", "kafka", "dapr", "cloud-deployment", "cicd", "observability"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

Phase V (Advanced Cloud Deployment)

You are operating under a strict Spec-Driven, Agentic Development Constitution for Phase V of the Full-Stack Todo Application with AI Chatbot.

Core Objective: Transform the existing Phase IV Kubernetes-deployed Todo AI Chatbot into a production-grade, event-driven, cloud-native system by implementing: Advanced Todo features, Event-driven architecture using Kafka, Full Dapr runtime integration, Local (Minikube) and Cloud (AKS / GKE / OKE) deployments, CI/CD, monitoring, and observability. This phase must extend Phase IV, not replace it.

Foundational Constraints (Non-Negotiable): No manual coding (all implementation via Claude Code / Agentic Dev Stack), mandatory workflow (/sp.specify → /sp.plan → /sp.tasks → /sp.implement), Phase IV artifacts are authoritative (Helm charts, Docker images, K8s manifests must be reused and extended), single repository same folder structure.

Architectural Principles: Event-Driven First (Kafka backbone, no synchronous coupling for state changes), Dapr as Abstraction Layer (Pub/Sub, State Management, Service Invocation, Jobs API, Secrets Management — app code talks only to Dapr HTTP APIs).

Feature Governance: Recurring tasks, due dates, reminders, priorities, tags, search/filter/sort — all must emit domain events, no silent state mutations.

Kafka Governance: Topics are contracts (task-events, reminders, task-updates), schemas explicit and versionable, backward compatibility preferred, provider flexibility (Redpanda/Strimzi local, Redpanda Cloud/Confluent cloud), switching providers requires no code changes.

Deployment Constitution: Local first cloud second, Minikube → cloud promotion, supported targets AKS/GKE/OKE, reuse Phase IV Helm charts, Dapr enabled cluster-wide.

Secrets & Security: No hardcoded secrets, prefer K8s Secrets and Dapr Secrets API.

CI/CD: GitHub Actions mandatory, build/push/deploy/rollback pipeline.

Observability: Monitoring, logging, event flow health, retry/idempotency/resilience for async flows.

Agent Governance: Specialized agents for orchestration, advanced features, Kafka, Dapr, notification, cloud deployment, CI/CD. Agents decide within domain; cross-cutting decisions escalated to Orchestrator.

Quality Bar: Clean separation of concerns, event-driven thinking, cloud portability, Dapr abstraction, spec-driven discipline. Invalid if not traceable to spec → plan → agent action.

## Response snapshot

Amended constitution from v3.0.0 to v4.0.0. Added 8 new NON-NEGOTIABLE principles (XX-XXVII): Event-Driven First, Dapr Abstraction Layer, Feature Event Governance, Kafka Schema Governance, Local-First Cloud Promotion, CI/CD Pipeline Mandate, Observability and Reliability, Phase V Agent Sovereignty. Updated Principle XVI to include Phase V cloud promotion ladder. Added Phase V Technology Stack (Kafka, Dapr, AKS/GKE/OKE, GitHub Actions), Phase V Agent Roles (7 agents), Phase V Success Definition (11 criteria), Phase V Explicit Out-of-Scope. Extended Quality Gates, Deployment Architecture, Security Standards, and Development Workflow with Phase V additions. All 4 dependent templates verified compatible. Sync Impact Report embedded in HTML comment at top of constitution.

## Outcome

- Impact: MAJOR version bump (3.0.0 → 4.0.0) — 8 new NON-NEGOTIABLE principles governing Phase V event-driven cloud-native architecture
- Tests: none
- Files: 1 file updated (.specify/memory/constitution.md)
- Next prompts: Begin Phase V feature work with `/sp.specify` for advanced features; consider `/sp.adr` for Kafka provider selection (Redpanda vs Strimzi) and cloud target selection (AKS vs GKE vs OKE)
- Reflection: Preserved all 19 existing principles unchanged. Phase V additions are strictly additive — no existing principles redefined except XVI which was scoped to include Phase V cloud promotion alongside its existing Phase IV local-only scope. All Phase IV out-of-scope items (cloud, CI/CD, monitoring, service mesh) are now brought into Phase V scope through new dedicated principles.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): manual review PASS — all 27 principles present, no unresolved placeholders, version/dates correct, templates verified compatible
- Prompt variant: baseline
- Next experiment: Run /sp.specify for first Phase V feature to validate constitution gates are enforceable by agents
