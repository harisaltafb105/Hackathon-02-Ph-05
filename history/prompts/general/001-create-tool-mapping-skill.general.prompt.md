---
id: 001
title: Create Tool Mapping Skill
stage: general
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: null
user: null
command: null
labels: ["skill", "tool-mapping", "mcp", "intent-classification"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/tool-mapping/skills.md
tests:
  - null
---

## Prompt

create a skill in my skills folder Tool Mapping Skill

Purpose:
Convert user's natural language into the correct MCP tool call.

Skill responsibilities:

Identify user intent (add, list, update, delete, complete)

Extract task references (task id, title, status)

Choose correct MCP tool

Prepare clean parameters for tool execution

Output format:

Intent: <add|list|update|delete|complete>
Tool: <tool_name>
Parameters: { ... }
Confidence: high | medium | low

## Response snapshot

Created Tool Mapping Skill at `.claude/skills/tool-mapping/skills.md` with comprehensive documentation including:
- Intent classification for 5 operations (add, list, update, delete, complete)
- Trigger phrase patterns for each intent
- TypeScript parameter interfaces
- Example mappings with confidence levels
- Edge case handling strategies
- Task reference resolution by ID, title, or position
- Integration pattern with sample code
- Error handling and testing checklist

## Outcome

- ✅ Impact: Added new skill for natural language to MCP tool mapping
- 🧪 Tests: N/A - Documentation skill
- 📁 Files: 1 file created (.claude/skills/tool-mapping/skills.md)
- 🔁 Next prompts: Implement intent-resolver agent integration, Add unit tests for mapping logic
- 🧠 Reflection: Comprehensive skill documentation created following existing patterns

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Integrate with intent-resolver agent
