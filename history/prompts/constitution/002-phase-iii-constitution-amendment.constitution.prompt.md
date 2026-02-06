---
id: 002
title: Phase III Constitution Amendment
stage: constitution
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: null
user: null
command: /sp.constitution
labels: ["constitution", "phase-iii", "ai-chatbot", "mcp", "governance"]
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

Project: Phase III – AI-Powered Todo Chatbot
System Type: Additive AI Layer over Existing Full-Stack Todo Application (Phase II)

1. Core Principle (Non-Negotiable)

Phase III is a strict extension of the Phase II Full-Stack Todo Application.

Existing frontend, backend, APIs, database schema, and authentication MUST NOT be broken

No refactor of Phase II unless explicitly required for chatbot integration

Chatbot logic must remain isolated, modular, and detachable

Phase II must continue to work even if chatbot is disabled

2. Architectural Authority

Backend remains the single source of truth

AI has no direct database access

All task mutations must go through:
Agent → MCP Tool → FastAPI → Database

Chatbot cannot bypass:

Authentication

Authorization

Business rules

3. Technology Lock (Strict)

The following technologies are mandatory:

Backend: Python FastAPI

AI Layer: OpenAI Agents SDK

Tool Interface: Official MCP SDK

Database: Neon PostgreSQL

ORM: SQLModel

Authentication: Better Auth

AI Provider: OpenAI API (via API Key)

Frontend Chat UI: OpenAI ChatKit

No alternative frameworks, SDKs, or shortcuts are allowed.

4. Environment & Secrets Handling

All secrets must be loaded via .env

Required environment variables:

OPENAI_API_KEY

BETTER_AUTH_URL

BETTER_AUTH_SECRET

DATABASE_URL

No secrets hardcoded in:

Specs

Code

Prompts

Frontend uses only public-safe env variables

Backend owns all privileged credentials

5. Stateless Server Law

FastAPI server must remain fully stateless

No in-memory session or conversation state

Conversation continuity must be restored only from database

Any server restart must not affect chatbot continuity

6. MCP Tool Sovereignty

MCP server exposes only task-related tools

Each MCP tool:

Is stateless

Performs exactly one responsibility

Validates user_id ownership

AI agent cannot invent tools

Tool outputs must be deterministic and auditable

7. Agent Behavior Constraints

AI agents must:

Act only through MCP tools

Confirm actions in natural language

Handle ambiguity by clarification

AI must never:

Execute destructive actions silently

Guess task IDs without verification

Leak internal system details

Modify tasks of another user

8. Authentication & Authorization

User identity is derived from Better Auth

Chat endpoint must validate:

Authenticated user

User ownership of conversation and tasks

AI receives user_id only from backend context

User identity must never be inferred from chat text

9. Data Integrity Rules

All writes must be transactional

Partial failures must rollback safely

Duplicate tasks must be handled gracefully

Deleted tasks must not reappear in chat context

10. Frontend Integration Rules

Chat UI is an additive feature

Existing Todo UI remains unchanged

Chatbot UI must:

Use ChatKit

Support loading, error, retry states

Degrade gracefully if backend is unavailable

No frontend logic duplication of backend rules

11. Spec-Driven Development Law

No implementation without:

/sp.specify

/sp.plan

/sp.tasks

Specs are append-only

Updates must be done via new spec revisions

No retroactive spec rewriting

12. Safety & Failure Discipline

Errors must be:

Logged

User-friendly

Non-destructive

AI hallucinations must be prevented via tool-only execution

If unsure, AI must respond with clarification, not action

13. Scalability & Maintainability

System must support:

Horizontal scaling

Multiple concurrent users

Future agent expansion

Chatbot must be removable without breaking core app

14. Success Definition

Phase III is successful if:

Users can manage todos via natural language

All actions are correctly persisted

Conversation resumes after restart

Phase II remains fully functional

AI acts as an assistant, not a system owner

15. Final Constitutional Law

The AI chatbot is a controlled assistant, not an authority.
The backend is the authority.
The database is the memory.

## Response snapshot

Updated constitution from v1.0.0 to v2.0.0 with comprehensive Phase III governance:

**Added Principles (VII-XIII)**:
- VII: Phase III Additive Extension - Non-breaking extension rules
- VIII: Architectural Authority - Backend as source of truth, Agent → MCP → FastAPI → DB chain
- IX: Stateless Server Law - No in-memory state, DB-based conversation continuity
- X: MCP Tool Sovereignty - Single-responsibility tools with user_id validation
- XI: Agent Behavior Constraints - Tool-only execution, clarification over action
- XII: Data Integrity & Safety - Transactional writes, graceful error handling
- XIII: Final Constitutional Law - AI is assistant, backend is authority, DB is memory

**Updated Sections**:
- Phase III Technology Stack (OpenAI Agents SDK, MCP SDK, ChatKit)
- Phase III Agent Roles (6 new agents)
- Phase III Success Definition
- Quality Gates with Phase III checkpoints

**Version Bump Rationale**: MAJOR (1.0.0 → 2.0.0) due to addition of 7 new NON-NEGOTIABLE principles that fundamentally extend governance structure.

## Outcome

- ✅ Impact: Constitution updated with comprehensive Phase III AI governance
- 🧪 Tests: N/A - Governance document
- 📁 Files: 1 file modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Create Phase III feature specs, Define MCP tool contracts
- 🧠 Reflection: Major version bump appropriate given 7 new non-negotiable principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase III spec creation with /sp.specify
