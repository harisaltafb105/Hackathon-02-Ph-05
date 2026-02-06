# Action Confirmation & Response Skill

## Overview
This skill generates clear, friendly, human-like confirmations after MCP tool execution. It transforms raw tool results into conversational responses that inform users about what happened.

## Purpose
Generate clear, friendly, human-like confirmations after tool execution by:
- Confirming what action was taken
- Reflecting task title or ID
- Handling errors gracefully
- Keeping responses short and conversational

## Response Format

### Success Response
```
✅ "<Friendly confirmation message reflecting the action and task details>"
```

### Warning Response
```
⚠️ "<Explanation of issue with helpful suggestion>"
```

### Error Response
```
❌ "<Brief error explanation with recovery options>"
```

## Response Templates by Action

### 1. ADD Action Confirmations

**Success:**
```
✅ "Task '{title}' has been added to your list."
✅ "Got it! '{title}' is now on your to-do list."
✅ "Added '{title}' to your tasks."
✅ "Done! I've added '{title}' for you."
```

**With Priority:**
```
✅ "Task '{title}' has been added with {priority} priority."
✅ "Added '{title}' as a {priority}-priority task."
```

**With Due Date:**
```
✅ "Task '{title}' has been added, due {due_date}."
✅ "Got it! '{title}' is scheduled for {due_date}."
```

**Error Cases:**
```
⚠️ "I couldn't add that task — the title seems to be empty. What would you like to call it?"
❌ "Something went wrong while adding your task. Want to try again?"
```

### 2. LIST Action Confirmations

**Success (with results):**
```
📋 "Here are your {count} {status} tasks:"
📋 "You have {count} tasks{status_filter}:"
📋 "Found {count} tasks matching your request:"
```

**Success (no results):**
```
✨ "You're all caught up! No {status} tasks right now."
📭 "No tasks found. Want to add one?"
✨ "Your task list is empty — nice work!"
```

**Filtered Results:**
```
📋 "Here are your {count} pending tasks:"
✅ "You've completed {count} tasks:"
📋 "Showing {count} high-priority tasks:"
```

**Error Cases:**
```
⚠️ "I had trouble loading your tasks. Let me try again..."
❌ "Couldn't retrieve your tasks right now. Please try again in a moment."
```

### 3. UPDATE Action Confirmations

**Title Update:**
```
✅ "Task updated! '{old_title}' is now '{new_title}'."
✅ "Got it — renamed to '{new_title}'."
```

**Priority Update:**
```
✅ "Task '{title}' is now {priority} priority."
✅ "Updated! '{title}' priority set to {priority}."
```

**Due Date Update:**
```
✅ "Task '{title}' is now due {due_date}."
✅ "Rescheduled '{title}' to {due_date}."
```

**Multiple Fields:**
```
✅ "Task '{title}' has been updated with your changes."
✅ "All done! Updated {field_count} fields for '{title}'."
```

**Error Cases:**
```
⚠️ "I couldn't find task #{task_id}. Want me to show your current tasks?"
⚠️ "No task matches '{title}' — did you mean something else?"
❌ "Couldn't update that task. Please check the task ID and try again."
```

### 4. DELETE Action Confirmations

**Success:**
```
🗑️ "Task '{title}' has been removed from your list."
✅ "Done! '{title}' has been deleted."
🗑️ "Removed task #{task_id} from your list."
```

**With Undo Hint:**
```
🗑️ "Task '{title}' deleted. (This can't be undone)"
✅ "Removed '{title}' from your tasks."
```

**Error Cases:**
```
⚠️ "I couldn't find that task — want me to show your pending tasks?"
⚠️ "Task #{task_id} doesn't exist. Maybe it was already deleted?"
❌ "Couldn't delete that task. Please verify the task ID."
```

### 5. COMPLETE Action Confirmations

**Success:**
```
🎉 "Nice work! '{title}' is now complete."
✅ "Task '{title}' marked as done!"
🎉 "'{title}' — checked off! Great job."
✅ "Done! '{title}' is complete."
```

**With Stats:**
```
🎉 "'{title}' complete! You've finished {completed_count} tasks today."
✅ "Another one done! {remaining_count} tasks left to go."
```

**Already Complete:**
```
ℹ️ "'{title}' was already marked as complete."
✅ "That task is already done — you're on top of things!"
```

**Error Cases:**
```
⚠️ "I couldn't find that task — want me to show your pending tasks?"
⚠️ "Task #{task_id} doesn't exist. Show your current tasks?"
❌ "Couldn't mark that task as complete. Please try again."
```

## Error Handling Patterns

### Not Found Errors
```typescript
interface NotFoundResponse {
  icon: "⚠️";
  message: string;
  suggestion: string;
  action_hint?: string;
}
```

**Templates:**
```
⚠️ "I couldn't find that task — want me to show your pending tasks?"
⚠️ "No task matches '{reference}'. Here's what I can find..."
⚠️ "Task not found. Did you mean one of these?"
```

### Permission Errors
```
🔒 "You don't have access to that task."
⚠️ "That task belongs to another user."
```

### Validation Errors
```
⚠️ "The task title can't be empty. What should I call it?"
⚠️ "That doesn't look like a valid date. Try something like 'tomorrow' or 'next Monday'."
⚠️ "Priority should be high, medium, or low."
```

### System Errors
```
❌ "Something went wrong on my end. Please try again."
❌ "I'm having trouble right now. Give me a moment and try again."
⚠️ "Temporary issue — your request didn't go through. Try once more?"
```

## Tone Guidelines

### Do's
- Keep it conversational and friendly
- Use contractions (I've, you're, can't)
- Be concise — one sentence is ideal
- Include the task title/ID for clarity
- Offer helpful next steps on errors
- Use appropriate emoji sparingly

### Don'ts
- Don't be overly formal or robotic
- Don't use technical jargon
- Don't write lengthy paragraphs
- Don't leave users confused about what happened
- Don't blame the user for errors
- Don't overuse exclamation marks

## Response Selection Logic

```typescript
interface ToolResult {
  success: boolean;
  action: 'add' | 'list' | 'update' | 'delete' | 'complete';
  data?: {
    task_id?: string;
    title?: string;
    count?: number;
    [key: string]: any;
  };
  error?: {
    code: string;
    message: string;
  };
}

function generateConfirmation(result: ToolResult): string {
  if (result.success) {
    return selectSuccessTemplate(result.action, result.data);
  } else {
    return selectErrorTemplate(result.action, result.error);
  }
}

function selectSuccessTemplate(action: string, data: any): string {
  const templates = SUCCESS_TEMPLATES[action];
  // Select template based on available data fields
  // Interpolate values into template
  return interpolate(template, data);
}

function selectErrorTemplate(action: string, error: any): string {
  const templates = ERROR_TEMPLATES[error.code] || GENERIC_ERROR;
  // Select appropriate error template
  // Add helpful suggestion based on error type
  return interpolate(template, { ...error, suggestion: getSuggestion(error) });
}
```

## Context-Aware Responses

### Time-Based Greetings
```
// Morning (5am-12pm)
✅ "Good morning! '{title}' has been added."

// Afternoon (12pm-5pm)
✅ "'{title}' added to your afternoon tasks."

// Evening (5pm-9pm)
✅ "Added '{title}' for this evening."

// Night (9pm-5am)
✅ "'{title}' added — get some rest!"
```

### Streak Recognition
```
🔥 "5 tasks completed today! '{title}' done."
⭐ "You're on a roll! '{title}' marked complete."
🎯 "Another one down! {remaining} tasks left."
```

### First-Time User
```
👋 "Welcome! Your first task '{title}' has been added."
✅ "Great start! '{title}' is on your list."
```

## Batch Operation Responses

### Multiple Tasks Added
```
✅ "Added {count} tasks to your list."
📝 "All {count} tasks have been created."
```

### Multiple Tasks Completed
```
🎉 "Awesome! {count} tasks marked as complete."
✅ "Done! Checked off {count} tasks."
```

### Multiple Tasks Deleted
```
🗑️ "Removed {count} tasks from your list."
✅ "Deleted {count} tasks."
```

## Integration Example

```typescript
// After tool execution
async function respondToUser(toolResult: ToolResult): Promise<string> {
  // 1. Determine response type
  const responseType = toolResult.success ? 'success' : 'error';

  // 2. Get appropriate template
  const template = getTemplate(toolResult.action, responseType, toolResult);

  // 3. Interpolate data
  const message = interpolateTemplate(template, toolResult.data);

  // 4. Add emoji prefix
  const emoji = getEmoji(responseType, toolResult.action);

  // 5. Add suggestion if error
  const suggestion = responseType === 'error'
    ? getSuggestion(toolResult.error)
    : '';

  return `${emoji} ${message}${suggestion ? ' ' + suggestion : ''}`;
}
```

## Testing Checklist

- [ ] All success templates render correctly
- [ ] Error templates include helpful suggestions
- [ ] Task titles/IDs are properly reflected
- [ ] Emoji usage is consistent
- [ ] Tone is friendly and conversational
- [ ] Edge cases handled gracefully
- [ ] Batch operations summarized correctly
- [ ] No technical jargon in user-facing messages
