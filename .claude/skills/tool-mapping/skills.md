# Tool Mapping Skill

## Overview
This skill converts natural language user input into the correct MCP tool call for task management operations. It acts as the translation layer between human intent and machine-executable tool invocations.

## Purpose
Convert user's natural language into the correct MCP tool call by:
- Identifying user intent (add, list, update, delete, complete)
- Extracting task references (task id, title, status)
- Choosing the correct MCP tool
- Preparing clean parameters for tool execution

## Output Format
```
Intent: <add|list|update|delete|complete>
Tool: <tool_name>
Parameters: { ... }
Confidence: high | medium | low
```

## Intent Classification

### 1. ADD Intent
**Trigger phrases:**
- "add a task", "create a task", "new task"
- "add", "create", "make", "new"
- "I need to", "remind me to", "don't forget"

**MCP Tool:** `add_task`

**Parameter extraction:**
```typescript
interface AddTaskParams {
  title: string;        // Required: extracted from user input
  description?: string; // Optional: additional context
  priority?: string;    // Optional: high, medium, low
  due_date?: string;    // Optional: ISO date format
}
```

**Examples:**
| User Input | Mapped Output |
|------------|---------------|
| "Add a task to buy groceries" | Intent: add, Tool: add_task, Parameters: { title: "buy groceries" }, Confidence: high |
| "Create task: review PR #123" | Intent: add, Tool: add_task, Parameters: { title: "review PR #123" }, Confidence: high |
| "I need to call mom tomorrow" | Intent: add, Tool: add_task, Parameters: { title: "call mom", due_date: "tomorrow" }, Confidence: medium |

### 2. LIST Intent
**Trigger phrases:**
- "show tasks", "list tasks", "my tasks"
- "what are my tasks", "show me", "list", "display"
- "pending tasks", "all tasks", "completed tasks"

**MCP Tool:** `list_tasks`

**Parameter extraction:**
```typescript
interface ListTasksParams {
  status?: 'pending' | 'completed' | 'all';  // Optional: filter by status
  limit?: number;                             // Optional: max results
}
```

**Examples:**
| User Input | Mapped Output |
|------------|---------------|
| "Show my tasks" | Intent: list, Tool: list_tasks, Parameters: {}, Confidence: high |
| "List all completed tasks" | Intent: list, Tool: list_tasks, Parameters: { status: "completed" }, Confidence: high |
| "What do I have pending?" | Intent: list, Tool: list_tasks, Parameters: { status: "pending" }, Confidence: high |

### 3. UPDATE Intent
**Trigger phrases:**
- "update task", "edit task", "change task"
- "modify", "rename", "update", "change"
- "set priority", "change due date"

**MCP Tool:** `update_task`

**Parameter extraction:**
```typescript
interface UpdateTaskParams {
  task_id: string;       // Required: task identifier
  title?: string;        // Optional: new title
  description?: string;  // Optional: new description
  priority?: string;     // Optional: new priority
  due_date?: string;     // Optional: new due date
  status?: string;       // Optional: new status
}
```

**Examples:**
| User Input | Mapped Output |
|------------|---------------|
| "Update task #5 title to 'Review docs'" | Intent: update, Tool: update_task, Parameters: { task_id: "5", title: "Review docs" }, Confidence: high |
| "Change the priority of task 3 to high" | Intent: update, Tool: update_task, Parameters: { task_id: "3", priority: "high" }, Confidence: high |
| "Rename 'groceries' to 'weekly shopping'" | Intent: update, Tool: update_task, Parameters: { title: "weekly shopping" }, Confidence: medium |

### 4. DELETE Intent
**Trigger phrases:**
- "delete task", "remove task", "cancel task"
- "delete", "remove", "cancel", "get rid of"

**MCP Tool:** `delete_task`

**Parameter extraction:**
```typescript
interface DeleteTaskParams {
  task_id: string;  // Required: task identifier
}
```

**Examples:**
| User Input | Mapped Output |
|------------|---------------|
| "Delete task #42" | Intent: delete, Tool: delete_task, Parameters: { task_id: "42" }, Confidence: high |
| "Remove the groceries task" | Intent: delete, Tool: delete_task, Parameters: { title: "groceries" }, Confidence: medium |
| "Cancel task 7" | Intent: delete, Tool: delete_task, Parameters: { task_id: "7" }, Confidence: high |

### 5. COMPLETE Intent
**Trigger phrases:**
- "complete task", "mark complete", "finish task"
- "done", "finished", "completed", "mark as done"
- "check off", "tick off"

**MCP Tool:** `complete_task`

**Parameter extraction:**
```typescript
interface CompleteTaskParams {
  task_id: string;  // Required: task identifier
}
```

**Examples:**
| User Input | Mapped Output |
|------------|---------------|
| "Mark task #5 as complete" | Intent: complete, Tool: complete_task, Parameters: { task_id: "5" }, Confidence: high |
| "I finished the groceries task" | Intent: complete, Tool: complete_task, Parameters: { title: "groceries" }, Confidence: medium |
| "Done with task 12" | Intent: complete, Tool: complete_task, Parameters: { task_id: "12" }, Confidence: high |

## Confidence Levels

### High Confidence
- Explicit intent keyword present (add, delete, complete, etc.)
- Task ID explicitly provided (numeric identifier)
- Unambiguous command structure

### Medium Confidence
- Intent inferred from context
- Task referenced by title instead of ID
- Some ambiguity in parameters

### Low Confidence
- Multiple possible intents
- Missing required parameters
- Vague or incomplete input

## Edge Case Handling

### Ambiguous Input
When input is ambiguous, return low confidence and suggest clarification:
```
Intent: unknown
Tool: none
Parameters: {}
Confidence: low
Clarification needed: "Did you mean to add a new task or update an existing one?"
```

### Missing Required Parameters
When required parameters are missing:
```
Intent: delete
Tool: delete_task
Parameters: {}
Confidence: low
Missing: ["task_id"]
Clarification needed: "Which task would you like to delete? Please provide the task ID or title."
```

### Multiple Tasks Referenced
When user references multiple tasks:
```
Intent: complete
Tool: complete_task
Parameters: { task_ids: ["1", "2", "3"] }
Confidence: medium
Note: "Batch operation detected - will process sequentially"
```

## Task Reference Resolution

### By ID
- Pattern: `#\d+`, `task \d+`, `id:\d+`
- Resolution: Direct lookup by ID

### By Title
- Pattern: Quoted string, descriptive phrase
- Resolution: Fuzzy match against existing task titles

### By Position
- Pattern: "first task", "last task", "previous"
- Resolution: Context-aware positional reference

## Integration Pattern

```typescript
// Example usage in tool chain
async function mapUserInputToTool(userInput: string): Promise<ToolMapping> {
  // 1. Tokenize and analyze input
  const tokens = tokenize(userInput);

  // 2. Identify intent
  const intent = classifyIntent(tokens);

  // 3. Extract parameters
  const params = extractParameters(tokens, intent);

  // 4. Validate completeness
  const validation = validateParams(intent, params);

  // 5. Calculate confidence
  const confidence = calculateConfidence(intent, params, validation);

  return {
    intent,
    tool: getToolForIntent(intent),
    parameters: params,
    confidence,
    ...(validation.missing.length > 0 && {
      clarification_needed: generateClarificationPrompt(validation.missing)
    })
  };
}
```

## Best Practices

### 1. Always Validate User Context
Before executing any tool, ensure the user context is validated to prevent cross-user data access.

### 2. Prefer Task ID Over Title
When both are available, prefer task ID for higher accuracy and lower ambiguity.

### 3. Confirm Destructive Operations
For delete operations with medium or low confidence, always confirm with the user before execution.

### 4. Handle Batch Operations Carefully
When multiple tasks are referenced, process sequentially and report individual results.

### 5. Preserve Original Input
Store the original user input alongside the mapped output for debugging and audit purposes.

## Error Handling

### Invalid Tool Mapping
```
{
  "error": "INVALID_MAPPING",
  "message": "Could not map input to a valid tool",
  "original_input": "...",
  "suggestions": ["Did you mean to add a task?", "Try: 'Add task: <title>'"]
}
```

### Conflicting Parameters
```
{
  "error": "CONFLICTING_PARAMS",
  "message": "Parameters conflict with each other",
  "conflicts": [{"param1": "status=completed", "param2": "intent=add"}],
  "resolution": "Cannot add a task that is already completed"
}
```

## Testing Checklist

- [ ] All five intents correctly identified
- [ ] Task IDs extracted accurately
- [ ] Title extraction handles quoted strings
- [ ] Priority and date parsing works correctly
- [ ] Confidence levels assigned appropriately
- [ ] Edge cases return proper clarification requests
- [ ] Batch operations detected and flagged
- [ ] Integration with MCP tools validated
