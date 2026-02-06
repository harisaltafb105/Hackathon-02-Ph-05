---
id: 002
title: Create Action Confirmation Skill
stage: general
date: 2026-01-14
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: null
user: null
command: null
labels: ["skill", "action-confirmation", "response-generation", "ux"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/action-confirmation/skills.md
tests:
  - null
---

## Prompt

create a skill in my skills folder Action Confirmation & Response Skill

Purpose:
Generate clear, friendly, human-like confirmations after tool execution.

Skill responsibilities:

Confirm what action was taken

Reflect task title or ID

Handle errors gracefully

Keep responses short and conversational

Example output:

✅ "Task 'Buy groceries' has been added to your list."
⚠️ "I couldn't find that task — want me to show your pending tasks?"

## Response snapshot

Created Action Confirmation & Response Skill at `.claude/skills/action-confirmation/skills.md` with comprehensive documentation including:
- Response templates for all 5 actions (add, list, update, delete, complete)
- Success, warning, and error response formats with emoji prefixes
- Error handling patterns for not found, permission, validation, and system errors
- Tone guidelines (do's and don'ts for conversational responses)
- Context-aware responses (time-based, streak recognition, first-time user)
- Batch operation response templates
- Response selection logic with TypeScript interfaces
- Integration example code

## Outcome

- ✅ Impact: Added new skill for generating user-friendly action confirmations
- 🧪 Tests: N/A - Documentation skill
- 📁 Files: 1 file created (.claude/skills/action-confirmation/skills.md)
- 🔁 Next prompts: Integrate with error-translator agent, Add response variation logic
- 🧠 Reflection: Comprehensive response templates created with friendly tone guidelines

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Integrate with tool execution pipeline
