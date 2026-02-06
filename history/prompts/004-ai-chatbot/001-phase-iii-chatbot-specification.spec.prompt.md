---
id: 001
title: Phase III Chatbot Specification
stage: spec
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: 004-ai-chatbot
branch: 004-ai-chatbot
user: null
command: /sp.specify
labels: ["spec", "phase-iii", "ai-chatbot", "natural-language", "chat-ui"]
links:
  spec: specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-ai-chatbot/spec.md
  - specs/004-ai-chatbot/checklists/requirements.md
tests:
  - null
---

## Prompt

Phase III Todo AI Chatbot

Project: Phase III – AI-Powered Todo Chatbot
Integration Target: Existing Phase II Full-Stack Todo Application (Backend + Frontend)

1. Primary Objective

Integrate a fully-functional AI chatbot into the existing Todo application that:

Understands natural language commands

Adds, updates, deletes, completes, and lists tasks

Fetches user-related task info via authenticated backend APIs

Is fully stateless on the server

Uses OpenAI Agents SDK and communicates with OpenAI API

Provides user-friendly frontend interaction via ChatKit and a Chat Icon

2. Absolute Priorities

Backend Integration First

AI Agent SDK communicates with OpenAI API using OPENAI_API_KEY

All task operations go through existing FastAPI endpoints / MCP tools

Authentication enforced via BETTER_AUTH_SECRET and Better Auth

Frontend Chat UI

Add chat icon/button that toggles chat interface

Use OpenAI ChatKit for conversation

Maintain Phase II layout integrity (do not break existing todo UI)

Support responsive design, loading, error states, and offline fallback

Security & Secrets

All secrets are loaded via .env (OPENAI_API_KEY, BETTER_AUTH_URL, BETTER_AUTH_SECRET, DATABASE_URL)

Frontend only receives public-safe environment variable (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)

3. Functional Requirements (Frontend + Backend)

Frontend

Chat icon visible on all pages

Clicking opens chat modal or drawer

Chat uses ChatKit, handles:

Input messages

Loading / typing indicator

Error messages

Optional: Dark mode and animations

Chat messages show:

AI response

Task confirmations (added, deleted, completed, updated)

Chat history synced with backend per user

Backend / Agent

FastAPI endpoint /api/{user_id}/chat:

Receives conversation_id (optional) + message

Calls OpenAI Agent SDK with MCP tools

Returns:

conversation_id

response string

tool_calls executed

MCP tools for tasks:

add_task, list_tasks, update_task, delete_task, complete_task

Agents validate user ownership via JWT

Data Handling

Conversation stored in DB (Neon PostgreSQL)

Stateless server: any restart resumes conversation using DB

AI cannot mutate data outside tools + authenticated user context

4. Technology Stack (Strict)
Layer    Technology / Requirement
Backend    FastAPI, Python 3.13+, SQLModel, MCP SDK, OpenAI Agents SDK
Frontend    Next.js 16+, TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons, Framer Motion, OpenAI ChatKit
Database    Neon Serverless PostgreSQL
Authentication    Better Auth (JWT)
AI API    OpenAI API (via OPENAI_API_KEY)
Environment    .env (backend), NEXT_PUBLIC_OPENAI_DOMAIN_KEY (frontend)

5. Agent & Tool Rules

AI cannot bypass backend validation

MCP tools are single-purpose and stateless

AI must always confirm actions in chat

AI must clarify ambiguous requests

AI logs tool calls and responses for traceability

6. Spec-Driven Rules

All AI integration must be spec-driven

/sp.specify defines:

Agent behavior

MCP tools integration

Frontend Chat UI & icon

Future updates should extend spec; do not overwrite Phase II frontend or backend

## Response snapshot

Created comprehensive Phase III AI Chatbot specification at `specs/004-ai-chatbot/spec.md` with:

**7 User Stories (P1-P7)**:
1. Natural Language Task Creation (P1) - Core chatbot value
2. Chat Interface Access (P2) - Entry point for all interactions
3. List Tasks via Chat (P3) - Read operations
4. Complete Tasks via Chat (P4) - Status updates
5. Update Tasks via Chat (P5) - Task modifications
6. Delete Tasks via Chat (P6) - Destructive actions
7. Conversation Persistence (P7) - UX enhancement

**24 Functional Requirements** covering:
- Chat Interface (FR-001 to FR-006)
- AI Task Operations (FR-007 to FR-013)
- Security & Authorization (FR-014 to FR-017)
- Data & Persistence (FR-018 to FR-021)
- Integration (FR-022 to FR-024)

**10 Success Criteria** with measurable outcomes

**3 Key Entities**: Conversation, Message, ToolCall

**Quality Checklist**: All items passed validation

## Outcome

- ✅ Impact: Complete Phase III specification created
- 🧪 Tests: N/A - Specification document
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: Run /sp.plan to generate implementation plan
- 🧠 Reflection: User input was comprehensive, no clarifications needed

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All checklist items PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to /sp.plan
