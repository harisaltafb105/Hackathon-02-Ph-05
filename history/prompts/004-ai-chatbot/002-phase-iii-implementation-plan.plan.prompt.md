---
id: 002
title: Phase III Implementation Plan
stage: plan
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: 004-ai-chatbot
branch: 004-ai-chatbot
user: null
command: /sp.plan
labels: ["plan", "phase-iii", "ai-chatbot", "architecture", "mcp-tools"]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chatbot/plan.md
  - specs/004-ai-chatbot/research.md
  - specs/004-ai-chatbot/data-model.md
  - specs/004-ai-chatbot/quickstart.md
  - specs/004-ai-chatbot/contracts/chat-api.yaml
  - specs/004-ai-chatbot/contracts/mcp-tools.md
tests:
  - null
---

## Prompt

Phase III: Todo AI Chatbot Integration
Plan Objective

Generate a clear, sequential, spec-driven execution plan to integrate an AI-powered Todo chatbot into the existing Phase II Full-Stack Todo application, using:

OpenAI Agents SDK + OpenAI API

MCP Server (Official SDK)

Existing FastAPI + SQLModel backend

Existing Next.js frontend (Phase II)

The plan must ensure zero breaking changes to Phase II and clean extensibility.

Planning Constraints (Non-Negotiable)

Phase II backend and frontend must not be rewritten

Chatbot is an additive module inside the same repository

Server remains stateless

All state persists in Neon DB

Authentication via Better Auth JWT

Secrets loaded strictly from .env

No manual coding by user

Every step must reference specs from /specs

Planning Phases (Required Order)
Phase 1 – Architecture Alignment & Validation
Phase 2 – MCP Server Design & Tool Mapping
Phase 3 – OpenAI Agent Design
Phase 4 – Chat API Endpoint Implementation
Phase 5 – Database Extension Plan
Phase 6 – Frontend Chat UI Integration
Phase 7 – Environment & Security Plan
Phase 8 – Validation & Acceptance Criteria

## Response snapshot

Generated comprehensive Phase III implementation plan with 6 artifacts:

**Plan Artifacts Created**:
1. `research.md` - Architecture validation, technology decisions, integration patterns
2. `data-model.md` - Database schema for Conversation, Message, ToolCall entities
3. `contracts/chat-api.yaml` - OpenAPI spec for chat endpoints
4. `contracts/mcp-tools.md` - MCP tool interface contracts (5 tools)
5. `quickstart.md` - Development setup guide
6. `plan.md` - 8-phase implementation plan with dependencies

**Implementation Phases**:
1. Database Schema Extension (3 new tables)
2. MCP Tool Implementation (5 tools)
3. OpenAI Agent Configuration
4. Chat API Endpoint (4 endpoints)
5. Frontend Chat Button & Drawer
6. Chat Message Components
7. Conversation Persistence
8. Error Handling & Polish

**Constitution Check**: All 13 principles validated and passed

**Key Decisions**:
- Stateless agent per request
- MCP tools wrap existing CRUD logic
- User isolation via JWT context
- Frontend floating chat button + drawer

## Outcome

- ✅ Impact: Complete Phase III implementation plan created with all design artifacts
- 🧪 Tests: N/A - Planning document
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, 2 contracts)
- 🔁 Next prompts: Run /sp.tasks to generate implementation tasks
- 🧠 Reflection: Comprehensive planning with constitution compliance verified

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check - 13/13 PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.tasks for task generation
