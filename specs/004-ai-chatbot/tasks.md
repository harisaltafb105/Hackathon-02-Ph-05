# Implementation Tasks: Phase III AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot
**Generated**: 2026-01-15
**Plan Reference**: [plan.md](./plan.md)
**Spec Reference**: [spec.md](./spec.md)

---

## Task Format

```
- [ ] [TaskID] [Priority] [Story] Description
      └── File: path/to/file.ext
      └── Test: Description of test case
      └── Depends: TaskID(s)
```

**Priority Levels**: P1 (Critical) → P7 (Nice-to-have)
**Story References**: Maps to User Stories from spec.md

---

## Phase 1: Project Setup & Dependencies

> **Goal**: Configure project dependencies and environment for Phase III development.

- [x] [T001] [P1] [Setup] Add OpenAI and MCP SDK dependencies to backend
      └── File: `backend/pyproject.toml`
      └── Test: `uv pip list | grep -E "openai|mcp"` shows both packages
      └── Depends: None

- [x] [T002] [P1] [Setup] Add OPENAI_API_KEY to environment configuration
      └── File: `backend/.env.example`
      └── Test: Backend starts without missing env var errors
      └── Depends: None

- [x] [T003] [P1] [Setup] Create chat module directory structure in backend
      └── File: `backend/chat/__init__.py`, `backend/chat/agent.py`, `backend/chat/tools.py`, `backend/chat/service.py`
      └── Test: `python -c "from backend.chat import agent, tools, service"` succeeds
      └── Depends: T001

- [x] [T004] [P2] [Setup] Create chat components directory structure in frontend
      └── File: `frontend/components/chat/index.ts`
      └── Test: Directory exists with index.ts
      └── Depends: None

- [x] [T005] [P2] [Setup] Add frontend chat UI dependencies (ChatKit or AI SDK)
      └── File: `frontend/package.json`
      └── Test: Using existing framer-motion and radix-ui components
      └── Depends: T004

---

## Phase 2: Database Schema Extension

> **Goal**: Add conversation persistence tables without breaking Phase II.
> **Data Model Reference**: [data-model.md](./data-model.md)

- [x] [T006] [P1] [P7] Add MessageRole enum to models
      └── File: `backend/models.py`
      └── Test: `from backend.models import MessageRole` succeeds
      └── Depends: T003

- [x] [T007] [P1] [P7] Add Conversation SQLModel class
      └── File: `backend/models.py`
      └── Test: Conversation table created in database on startup
      └── Depends: T006

- [x] [T008] [P1] [P7] Add Message SQLModel class with conversation relationship
      └── File: `backend/models.py`
      └── Test: Message table created with FK to conversations
      └── Depends: T007

- [x] [T009] [P1] [P7] Add ToolCall SQLModel class with message relationship
      └── File: `backend/models.py`
      └── Test: tool_calls table created with FK to messages
      └── Depends: T008

- [x] [T010] [P1] [P7] Add ChatRequest and ChatResponse Pydantic schemas
      └── File: `backend/schemas.py`
      └── Test: Schema validation works for sample request/response
      └── Depends: T006

- [x] [T011] [P1] [P7] Add ToolCallResponse and ConversationSummary schemas
      └── File: `backend/schemas.py`
      └── Test: `from backend.schemas import ToolCallResponse, ConversationSummary` succeeds
      └── Depends: T010

- [x] [T012] [P1] [P7] Verify database tables created on startup
      └── File: `backend/database.py` (no changes, verification only)
      └── Test: Tables auto-created via SQLModel.metadata.create_all()
      └── Depends: T009

---

## Phase 3: MCP Tool Implementation

> **Goal**: Create stateless MCP tools that wrap existing CRUD logic.
> **Contract Reference**: [contracts/mcp-tools.md](./contracts/mcp-tools.md)

- [x] [T013] [P1] [P1] Implement ToolContext dataclass for user isolation
      └── File: `backend/chat/tools.py`
      └── Test: ToolContext properly carries user_id, session, conversation_id
      └── Depends: T012

- [x] [T014] [P1] [P1] Implement add_task MCP tool
      └── File: `backend/chat/tools.py`
      └── Test: `add_task({"title": "test"}, context)` creates task for user
      └── Depends: T013

- [x] [T015] [P1] [P3] Implement list_tasks MCP tool with filtering
      └── File: `backend/chat/tools.py`
      └── Test: `list_tasks({"status": "pending"}, context)` returns only pending tasks
      └── Depends: T013

- [x] [T016] [P1] [P5] Implement update_task MCP tool
      └── File: `backend/chat/tools.py`
      └── Test: `update_task({"task_id": "...", "title": "new"}, context)` updates title
      └── Depends: T013

- [x] [T017] [P1] [P4] Implement complete_task MCP tool
      └── File: `backend/chat/tools.py`
      └── Test: `complete_task({"task_id": "..."}, context)` marks task completed
      └── Depends: T013

- [x] [T018] [P1] [P6] Implement delete_task MCP tool
      └── File: `backend/chat/tools.py`
      └── Test: `delete_task({"task_id": "..."}, context)` removes task
      └── Depends: T013

- [x] [T019] [P1] [All] Create tool registry for agent registration
      └── File: `backend/chat/tools.py`
      └── Test: `get_tool_definitions()` returns list of 5 tool schemas
      └── Depends: T014, T015, T016, T017, T018

- [x] [T020] [P1] [All] Implement standardized error handling for tools
      └── File: `backend/chat/tools.py`
      └── Test: Invalid task_id returns `{"error": true, "code": "NOT_FOUND", ...}`
      └── Depends: T019

- [ ] [T021] [P2] [All] Write unit tests for all MCP tools
      └── File: `backend/tests/test_tools.py`
      └── Test: `pytest backend/tests/test_tools.py` passes with 100% tool coverage
      └── Depends: T020

---

## Phase 4: OpenAI Agent Configuration

> **Goal**: Configure stateless AI agent with tool bindings.

- [x] [T022] [P1] [All] Initialize OpenAI client with environment API key
      └── File: `backend/chat/agent.py`
      └── Test: Client initializes without error when OPENAI_API_KEY is set
      └── Depends: T002, T019

- [x] [T023] [P1] [All] Define agent system instructions (behavior rules)
      └── File: `backend/chat/agent.py`
      └── Test: System instructions include confirmation requirement, clarification rules
      └── Depends: T022

- [x] [T024] [P1] [All] Register MCP tools as OpenAI function definitions
      └── File: `backend/chat/agent.py`
      └── Test: Agent can see and describe all 5 tools
      └── Depends: T022, T019

- [x] [T025] [P1] [All] Implement run_agent(message, history, context) function
      └── File: `backend/chat/agent.py`
      └── Test: `run_agent("Show my tasks", [], context)` returns task list
      └── Depends: T024

- [x] [T026] [P1] [All] Implement tool call execution within agent run
      └── File: `backend/chat/agent.py`
      └── Test: Agent executes tool and returns result in response
      └── Depends: T025

- [x] [T027] [P1] [P7] Implement conversation history loading for context
      └── File: `backend/chat/agent.py`
      └── Test: Agent receives previous messages and maintains context
      └── Depends: T026

- [ ] [T028] [P2] [All] Write integration tests for agent with mock tools
      └── File: `backend/tests/test_agent.py`
      └── Test: `pytest backend/tests/test_agent.py` passes
      └── Depends: T027

---

## Phase 5: Chat API Endpoint

> **Goal**: Create stateless chat endpoint with persistence.
> **Contract Reference**: [contracts/chat-api.yaml](./contracts/chat-api.yaml)

- [x] [T029] [P1] [All] Create chat router module
      └── File: `backend/routers/chat.py`
      └── Test: Router imports without errors
      └── Depends: T027

- [x] [T030] [P1] [All] Implement POST /{user_id}/chat endpoint
      └── File: `backend/routers/chat.py`
      └── Test: POST returns ChatResponse with conversation_id and response
      └── Depends: T029

- [x] [T031] [P1] [P7] Implement GET /{user_id}/conversations endpoint
      └── File: `backend/routers/chat.py`
      └── Test: GET returns paginated list of user's conversations
      └── Depends: T029

- [x] [T032] [P1] [P7] Implement GET /{user_id}/conversations/{id} endpoint
      └── File: `backend/routers/chat.py`
      └── Test: GET returns conversation with messages
      └── Depends: T029

- [x] [T033] [P2] [P7] Implement DELETE /{user_id}/conversations/{id} endpoint
      └── File: `backend/routers/chat.py`
      └── Test: DELETE removes conversation and returns 204
      └── Depends: T029

- [x] [T034] [P1] [All] Implement ChatService for business logic
      └── File: `backend/chat/service.py`
      └── Test: Service creates conversation, stores messages, runs agent
      └── Depends: T030

- [x] [T035] [P1] [All] Implement user_id validation from JWT in chat endpoints
      └── File: `backend/routers/chat.py`
      └── Test: Request with mismatched user_id returns 403
      └── Depends: T034

- [x] [T036] [P1] [All] Register chat router in main application
      └── File: `backend/main.py`
      └── Test: `/api/{user_id}/chat` endpoint accessible
      └── Depends: T035

- [ ] [T037] [P2] [All] Write endpoint tests for chat API
      └── File: `backend/tests/test_chat.py`
      └── Test: `pytest backend/tests/test_chat.py` passes
      └── Depends: T036

---

## Phase 6: Frontend Chat Button & Drawer

> **Goal**: Add non-intrusive chat UI entry point.
> **Story Reference**: P2 - Chat Interface Access

- [x] [T038] [P2] [P2] Create ChatButton component with fixed position
      └── File: `frontend/components/chat/ChatButton.tsx`
      └── Test: Chat button visible in bottom-right corner when authenticated
      └── Depends: T005

- [x] [T039] [P2] [P2] Create ChatDrawer component with slide animation
      └── File: `frontend/components/chat/ChatDrawer.tsx`
      └── Test: Drawer slides in/out on toggle
      └── Depends: T038

- [x] [T040] [P2] [P2] Implement drawer open/close state management
      └── File: `frontend/context/chat-context.tsx`
      └── Test: Click button opens drawer, click close/outside closes
      └── Depends: T039

- [x] [T041] [P2] [P2] Add responsive styles (full-screen on mobile)
      └── File: `frontend/components/chat/ChatDrawer.tsx`
      └── Test: Drawer is full-screen on viewport < 768px
      └── Depends: T040

- [x] [T042] [P2] [P2] Add ChatButton to application layout
      └── File: `frontend/app/layout.tsx`
      └── Test: Chat button appears on all authenticated pages
      └── Depends: T041

- [x] [T043] [P2] [P2] Conditionally show ChatButton only when authenticated
      └── File: `frontend/components/chat/ChatButton.tsx`
      └── Test: Button hidden when user is not logged in
      └── Depends: T042

---

## Phase 7: Chat Message Components

> **Goal**: Implement conversation UI with messages.
> **Story References**: P1, P3, P4, P5, P6

- [x] [T044] [P1] [P1] Create ChatMessages component for message list
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Messages render with correct styling per role
      └── Depends: T043

- [x] [T045] [P1] [P1] Implement different message styling for user/assistant
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: User messages right-aligned, assistant left-aligned
      └── Depends: T044

- [x] [T046] [P2] [All] Display tool call results inline in messages
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Tool calls show as collapsible details in assistant messages
      └── Depends: T045

- [x] [T047] [P1] [P1] Implement auto-scroll to latest message
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: New messages automatically scroll into view
      └── Depends: T046

- [x] [T048] [P1] [P1] Create ChatInput component with send button
      └── File: `frontend/components/chat/ChatInput.tsx`
      └── Test: Input field with send button renders correctly
      └── Depends: T047

- [x] [T049] [P1] [P1] Implement Enter to send, Shift+Enter for newline
      └── File: `frontend/components/chat/ChatInput.tsx`
      └── Test: Enter sends message, Shift+Enter adds newline
      └── Depends: T048

- [x] [T050] [P1] [All] Implement loading/disabled state during send
      └── File: `frontend/components/chat/ChatInput.tsx`
      └── Test: Input disabled and shows spinner while waiting for response
      └── Depends: T049

- [x] [T051] [P1] [All] Create chat-api.ts client module
      └── File: `frontend/lib/chat-api.ts`
      └── Test: sendMessage, getConversations, getConversationHistory functions exist
      └── Depends: T036

- [x] [T052] [P1] [All] Implement sendMessage API call with JWT
      └── File: `frontend/lib/chat-api.ts`
      └── Test: API call includes Authorization header, returns ChatResponse
      └── Depends: T051

- [x] [T053] [P1] [P7] Implement getConversations and getConversationHistory
      └── File: `frontend/lib/chat-api.ts`
      └── Test: Both functions return expected data structures
      └── Depends: T052

- [x] [T054] [P1] [All] Integrate API client with ChatDrawer state
      └── File: `frontend/context/chat-context.tsx`
      └── Test: Sending message updates UI with response
      └── Depends: T053

- [ ] [T055] [P2] [All] Test end-to-end message flow
      └── File: Manual testing
      └── Test: Send "Add a task test" → task created → confirmation shown
      └── Depends: T054

---

## Phase 8: Conversation Persistence

> **Goal**: Enable conversation continuity across sessions.
> **Story Reference**: P7 - Conversation Persistence

- [x] [T056] [P2] [P7] Store conversation_id in localStorage
      └── File: `frontend/context/chat-context.tsx`
      └── Test: conversation_id persists after browser refresh
      └── Depends: T054

- [x] [T057] [P2] [P7] Load conversation history on drawer open
      └── File: `frontend/context/chat-context.tsx`
      └── Test: Previous messages display when drawer opens
      └── Depends: T056

- [x] [T058] [P2] [P7] Handle new conversation vs continuing existing
      └── File: `frontend/context/chat-context.tsx`, `frontend/components/chat/ChatMessages.tsx`
      └── Test: New user sees welcome message, returning user sees history
      └── Depends: T057

- [ ] [T059] [P3] [P7] Display conversation list (optional for MVP)
      └── File: `frontend/components/chat/ConversationList.tsx`
      └── Test: User can see and switch between past conversations
      └── Depends: T058

- [ ] [T060] [P2] [P7] Implement message pagination for long conversations
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Load older messages on scroll up with 100+ messages
      └── Depends: T057

- [ ] [T061] [P2] [P7] Test persistence across browser sessions
      └── File: Manual testing
      └── Test: Close browser, reopen, history intact
      └── Depends: T060

- [ ] [T062] [P2] [P7] Test persistence across server restarts
      └── File: Manual testing
      └── Test: Restart backend, history still loads
      └── Depends: T061

---

## Phase 9: Error Handling & Polish

> **Goal**: Graceful degradation and user experience polish.

- [x] [T063] [P2] [All] Implement AI service unavailable error handling
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Show retry message when API returns 503
      └── Depends: T054

- [x] [T064] [P2] [All] Implement token expired error handling
      └── File: `frontend/lib/chat-api.ts`
      └── Test: Prompt re-login when API returns 401
      └── Depends: T063

- [x] [T065] [P2] [All] Implement task not found error handling
      └── File: `backend/chat/tools.py`
      └── Test: AI suggests "list tasks" when task not found
      └── Depends: T064

- [x] [T066] [P2] [All] Add typing indicator while AI responds
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Animated dots shown during API call
      └── Depends: T065

- [x] [T067] [P3] [All] Add loading skeleton for history loading
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: Skeleton shown while fetching conversation history
      └── Depends: T066

- [x] [T068] [P3] [P2] Add drawer slide animation CSS
      └── File: `frontend/components/chat/ChatDrawer.tsx`
      └── Test: Smooth slide-in/out animation on open/close
      └── Depends: T067

- [x] [T069] [P3] [All] Add message fade-in animation
      └── File: `frontend/components/chat/ChatMessages.tsx`
      └── Test: New messages fade in smoothly
      └── Depends: T068

---

## Phase 10: Final Validation & Acceptance

> **Goal**: Verify all acceptance criteria from spec.md are met.

### Functional Validation

- [ ] [T070] [P1] [P1] Validate: Add task via chat
      └── Test: "Add buy groceries" → Task created, confirmed in chat
      └── Depends: T055

- [ ] [T071] [P1] [P3] Validate: List tasks via chat
      └── Test: "Show my tasks" → Task list displayed
      └── Depends: T055

- [ ] [T072] [P1] [P4] Validate: Complete task via chat
      └── Test: "Mark buy groceries done" → Status updated
      └── Depends: T055

- [ ] [T073] [P1] [P5] Validate: Update task via chat
      └── Test: "Rename buy groceries to shopping" → Title changed
      └── Depends: T055

- [ ] [T074] [P1] [P6] Validate: Delete task via chat
      └── Test: "Delete shopping" → Task removed
      └── Depends: T055

### Security Validation

- [ ] [T075] [P1] [All] Validate: User A cannot see User B's tasks
      └── Test: Two users, each only sees own tasks
      └── Depends: T055

- [ ] [T076] [P1] [All] Validate: User A cannot modify User B's tasks
      └── Test: Attempt to complete other user's task fails
      └── Depends: T075

- [ ] [T077] [P1] [All] Validate: Unauthenticated requests return 401
      └── Test: Request without token returns 401
      └── Depends: T076

- [ ] [T078] [P1] [All] Validate: Invalid user_id in path returns 403
      └── Test: user_id mismatch in URL vs JWT returns 403
      └── Depends: T077

### Reliability Validation

- [ ] [T079] [P2] [P7] Validate: Server restart preserves conversation history
      └── Test: Restart backend, history loads correctly
      └── Depends: T062

- [ ] [T080] [P2] [P7] Validate: Browser refresh preserves current conversation
      └── Test: Refresh page, conversation continues
      └── Depends: T079

- [ ] [T081] [P2] [P7] Validate: Large conversation (100+ messages) loads correctly
      └── Test: Create 100+ message conversation, verify performance
      └── Depends: T080

### UX Validation

- [ ] [T082] [P2] [All] Validate: AI confirms actions before execution
      └── Test: AI says "I'll add..." before creating task
      └── Depends: T055

- [ ] [T083] [P2] [All] Validate: AI asks clarification for ambiguous requests
      └── Test: "groceries" prompts "Do you want to add a task?"
      └── Depends: T082

- [ ] [T084] [P2] [All] Validate: Error messages are user-friendly
      └── Test: Errors display helpful message, not stack traces
      └── Depends: T083

- [ ] [T085] [P2] [All] Validate: Loading indicator shows while AI responds
      └── Test: Typing indicator visible during API call
      └── Depends: T084

---

## Summary

| Phase | Tasks | Priority Range | Est. Complexity |
|-------|-------|----------------|-----------------|
| Phase 1: Setup | T001-T005 | P1-P2 | Low |
| Phase 2: Database | T006-T012 | P1 | Medium |
| Phase 3: MCP Tools | T013-T021 | P1-P2 | High |
| Phase 4: Agent | T022-T028 | P1-P2 | High |
| Phase 5: Chat API | T029-T037 | P1-P2 | High |
| Phase 6: UI Button/Drawer | T038-T043 | P2 | Medium |
| Phase 7: Message Components | T044-T055 | P1-P2 | High |
| Phase 8: Persistence | T056-T062 | P2-P3 | Medium |
| Phase 9: Polish | T063-T069 | P2-P3 | Low |
| Phase 10: Validation | T070-T085 | P1-P2 | Low |

**Total Tasks**: 85
**Critical Path**: T001 → T006 → T013 → T022 → T029 → T044 → T055 (core flow)

---

## Parallel Execution Opportunities

```
Timeline:
────────────────────────────────────────────────────────────────────

Phase 1 (Setup)
    ├── Backend: T001, T002, T003 ─────────────────┐
    └── Frontend: T004, T005 ──────────────────────┤
                                                   │
Phase 2 (Database): T006-T012 ◄────────────────────┘
                     │
Phase 3 (MCP Tools): T013-T021 ◄────────────────────────┐
                     │                                  │
Phase 4 (Agent): T022-T028 ◄────────────────────────────┤
                     │                                  │
Phase 5 (Chat API): T029-T037 ─────┐                    │
                                   │  (parallel)        │
Phase 6 (UI Button/Drawer): T038-T043 ◄─────────────────┤
                                   │                    │
                                   └───┬────────────────┘
                                       │
Phase 7 (Message Components): T044-T055 ◄──────────────────
                     │
Phase 8 (Persistence): T056-T062
                     │
Phase 9 (Polish): T063-T069
                     │
Phase 10 (Validation): T070-T085
```

**Parallel Groups**:
1. **T001-T003** (backend setup) || **T004-T005** (frontend setup)
2. **T029-T037** (backend API finalization) || **T038-T043** (frontend UI shell)

---

## Dependencies Graph

```
T001 (deps) ──┬──► T003 (chat module) ──► T006 (models)
              │
T002 (env) ───┴──► T022 (agent init)

T006 ──► T007 ──► T008 ──► T009 ──► T012 (DB complete)
     │
     └──► T010 ──► T011 (schemas)

T012 ──► T013 (ToolContext) ──┬──► T014 (add_task)
                              ├──► T015 (list_tasks)
                              ├──► T016 (update_task)
                              ├──► T017 (complete_task)
                              └──► T018 (delete_task)
                                        │
                                        ▼
T019 (registry) ◄───────────────────────┴──► T020 (errors)
        │
        ▼
T022 (agent) ──► T023 ──► T024 ──► T025 ──► T026 ──► T027 ──► T028
        │
        ▼
T029 (router) ──► T030-T033 (endpoints) ──► T034-T036 ──► T037

T005 ──► T038 ──► T039 ──► T040 ──► T041 ──► T042 ──► T043
                                                        │
                                                        ▼
T036 ──► T051 ──► T052 ──► T053 ──► T054 ◄──────────────┘
                                        │
                                        ▼
T044 ──► T045 ──► T046 ──► T047 ──► T048 ──► T049 ──► T050 ──► T055

T055 ──► T056 ──► T057 ──► T058 ──► T059 ──► T060 ──► T061 ──► T062

T055 ──► T063 ──► T064 ──► T065 ──► T066 ──► T067 ──► T068 ──► T069

T055 ──► T070-T085 (validation tasks)
```

---

## Task Checklist Quick Reference

### Backend Tasks (T001-T037)
- [ ] T001-T003: Setup & dependencies
- [ ] T006-T012: Database models & schemas
- [ ] T013-T021: MCP tool implementations
- [ ] T022-T028: Agent configuration
- [ ] T029-T037: Chat API endpoints

### Frontend Tasks (T004-T005, T038-T069)
- [ ] T004-T005: Setup & dependencies
- [ ] T038-T043: Chat button & drawer
- [ ] T044-T055: Message components & API client
- [ ] T056-T062: Conversation persistence
- [ ] T063-T069: Error handling & polish

### Validation Tasks (T070-T085)
- [ ] T070-T074: Functional validation
- [ ] T075-T078: Security validation
- [ ] T079-T081: Reliability validation
- [ ] T082-T085: UX validation

---

**Tasks Status**: ✅ Complete - Ready for `/sp.implement`
