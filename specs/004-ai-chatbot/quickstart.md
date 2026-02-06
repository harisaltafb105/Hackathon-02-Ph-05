# Quickstart: Phase III AI Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-14
**Prerequisites**: Phase II Todo Application running

## Overview

This guide covers setting up and running the AI chatbot integration locally.

---

## 1. Prerequisites Checklist

Before starting, ensure:

- [ ] Phase II backend is running (`backend/`)
- [ ] Phase II frontend is running (`frontend/`)
- [ ] Neon PostgreSQL database is accessible
- [ ] Better Auth is configured
- [ ] OpenAI API key obtained

---

## 2. Environment Setup

### Backend (.env)

Add to `backend/.env`:

```bash
# Existing Phase II variables
DATABASE_URL=postgresql://...@neon.tech/...
BETTER_AUTH_SECRET=your-better-auth-secret
BETTER_AUTH_URL=http://localhost:3000

# New Phase III variables
OPENAI_API_KEY=sk-...your-openai-api-key
```

### Frontend (.env.local)

```bash
# Existing Phase II variables (no changes needed)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 3. Install Dependencies

### Backend

```bash
cd backend

# Add OpenAI and MCP dependencies
uv add openai mcp

# Verify installation
uv pip list | grep -E "openai|mcp"
```

### Frontend

```bash
cd frontend

# Add ChatKit (OpenAI's chat UI library)
npm install @openai/chatkit

# If ChatKit not available, use alternative
npm install ai @ai-sdk/openai  # Vercel AI SDK alternative
```

---

## 4. Database Migration

The new tables (conversations, messages, tool_calls) are created automatically on startup.

```bash
cd backend

# Start backend to run migrations
uv run python -m uvicorn backend.main:app --reload

# Verify tables created
# Check Neon console or run:
# SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
```

Expected new tables:
- `conversations`
- `messages`
- `tool_calls`

---

## 5. Start Development Servers

### Terminal 1: Backend

```bash
cd backend
uv run python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd frontend
npm run dev
```

---

## 6. Verify Chat Endpoint

### Test with curl

```bash
# Get a valid JWT token from Better Auth (use browser dev tools after login)
TOKEN="your-jwt-token"
USER_ID="your-user-id"

# Send a chat message
curl -X POST "http://localhost:8000/api/${USER_ID}/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to test the chatbot"}'
```

Expected response:
```json
{
  "conversation_id": "uuid",
  "response": "I've added 'test the chatbot' to your task list.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {"title": "test the chatbot"},
      "result": {"id": "uuid", "title": "test the chatbot", "completed": false},
      "success": true
    }
  ]
}
```

---

## 7. Frontend Chat UI

After Phase III implementation, the chat will be accessible via:

1. Click the chat icon (bottom-right of screen)
2. Chat drawer opens
3. Type a message and press Enter
4. AI responds with task operations

---

## 8. Common Issues

### Issue: "Invalid or expired token"

**Cause**: JWT token is missing or expired

**Fix**:
1. Log in again on the frontend
2. Get fresh token from browser storage
3. Verify `BETTER_AUTH_SECRET` matches between frontend and backend

### Issue: "Failed to connect to OpenAI"

**Cause**: OpenAI API key invalid or network issue

**Fix**:
1. Verify `OPENAI_API_KEY` in `.env`
2. Check API key is active at platform.openai.com
3. Ensure outbound HTTPS is not blocked

### Issue: "Database table not found"

**Cause**: Migrations haven't run

**Fix**:
1. Restart backend to trigger `create_all()`
2. Check Neon dashboard for table creation
3. Verify `DATABASE_URL` is correct

### Issue: Chat drawer doesn't open

**Cause**: Frontend component not mounted

**Fix**:
1. Clear browser cache
2. Check console for JavaScript errors
3. Verify ChatButton component is in layout

---

## 9. Development Tips

### Testing Chat Flow

1. Start with simple commands: "Show my tasks"
2. Test task creation: "Add a task called test"
3. Test completion: "Mark test as done"
4. Test error handling: "Delete task 99999"

### Debugging Tool Calls

Check backend logs for tool call details:
```bash
# Backend logs show tool invocations
[INFO] Tool call: add_task with params: {"title": "test"}
[INFO] Tool result: {"id": "uuid", "title": "test", ...}
```

### Testing User Isolation

1. Create two test users
2. Add tasks for each user via chat
3. Verify User A cannot see User B's tasks
4. Verify tool calls are logged with correct user_id

---

## 10. Next Steps

After basic setup is verified:

1. **Implement remaining features** per tasks.md
2. **Add frontend chat components** with ChatKit
3. **Test conversation persistence** across sessions
4. **Run acceptance tests** from spec.md

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `uv run python -m uvicorn backend.main:app --reload` | Start backend |
| `npm run dev` | Start frontend |
| `curl -X POST .../chat` | Test chat endpoint |
| Check Neon console | Verify database tables |

**Quickstart Status**: ✅ Ready for development
