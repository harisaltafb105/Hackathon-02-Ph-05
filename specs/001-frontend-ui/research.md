# Research: Frontend-First Todo Web Application UI

**Feature**: 001-frontend-ui
**Date**: 2026-01-05
**Purpose**: Resolve technical unknowns and establish implementation patterns for production-quality frontend

## Research Areas

### 1. Next.js 16+ App Router Architecture

**Decision**: Use Next.js 16 App Router with TypeScript, client components for interactivity, server components where beneficial

**Rationale**:
- App Router (introduced in Next.js 13) is stable and recommended for new projects
- Client components (`'use client'`) required for interactive features (state, hooks, event handlers)
- Server components provide better initial load performance for static content
- TypeScript provides type safety eliminating entire classes of runtime errors

**Alternatives Considered**:
- **Pages Router**: Legacy approach, lacks server component support, not recommended for new projects
- **Create React App**: No longer maintained, lacks modern features like server components
- **Vite + React**: Good choice but lacks Next.js optimizations (image optimization, routing, etc.)

**Best Practices**:
- Use `app/` directory structure (not `pages/`)
- Mark interactive components with `'use client'` directive
- Keep server components default for better performance
- Use route groups `(app)` for organization without affecting URLs
- Leverage `loading.tsx` for automatic loading states
- Use `error.tsx` for error boundaries

### 2. shadcn/ui Component Selection and Customization

**Decision**: Use shadcn/ui as base component library with Tailwind CSS customization

**Rationale**:
- Not an NPM package - components copied to project for full control
- Built on Radix UI primitives (accessibility built-in)
- Fully customizable via Tailwind CSS
- TypeScript-first with excellent type definitions
- No runtime overhead - just React components
- Aligns with spec requirement for "no external UI kits other than shadcn/ui"

**Components to Use**:
- **Button**: Primary actions, secondary actions, danger actions
- **Card**: Task list items, containers
- **Dialog**: Add/Edit task modals, delete confirmation
- **Input**: Task title and description fields
- **Label**: Form field labels
- **Checkbox**: Task completion toggle
- **Tabs**: Filter controls (All/Active/Completed)
- **Separator**: Visual dividers
- **Skeleton**: Loading state placeholders

**Customization Strategy**:
- Define custom color palette in `tailwind.config.ts`
- Create design tokens for spacing (8px grid system)
- Override shadcn/ui default styles via CSS variables
- Create wrapper components for consistent prop patterns

**Best Practices**:
- Install only needed components (tree-shaking)
- Customize in `components/ui/` directory
- Extend base components in `components/` for feature-specific needs
- Use composition over prop drilling

### 3. State Management Strategy for Mocked Data

**Decision**: Use React Context API with useReducer for global task state

**Rationale**:
- No backend means no server state management needed (no React Query/SWR)
- Context + useReducer provides predictable state updates
- Simple enough for MVP, scales to backend integration
- Type-safe with TypeScript discriminated unions for actions
- Easy to swap for API calls later (same interface)

**Alternatives Considered**:
- **useState only**: Too fragmented across components, prop drilling
- **Zustand**: Overkill for frontend-only, adds dependency
- **Redux Toolkit**: Too complex for this scope, learning curve
- **Jotai/Recoil**: Atomic state nice but unnecessary complexity

**Implementation Pattern**:
```typescript
// State shape
type TaskState = {
  tasks: Task[]
  filter: 'all' | 'active' | 'completed'
  loading: boolean
  selectedTaskId: string | null
}

// Action types (discriminated union)
type TaskAction =
  | { type: 'ADD_TASK'; payload: Task }
  | { type: 'UPDATE_TASK'; payload: { id: string; updates: Partial<Task> } }
  | { type: 'DELETE_TASK'; payload: string }
  | { type: 'TOGGLE_COMPLETE'; payload: string }
  | { type: 'SET_FILTER'; payload: 'all' | 'active' | 'completed' }
  | { type: 'SET_LOADING'; payload: boolean }

// Provider wraps app
<TaskProvider initialTasks={mockedTasks}>
  <App />
</TaskProvider>
```

**Best Practices**:
- Single source of truth for tasks
- Immutable state updates
- Async simulation with setTimeout in actions
- Memoize filtered task lists with useMemo
- Separate concerns: state (context) + actions (reducer) + UI (components)

### 4. Framer Motion Animation Patterns

**Decision**: Use Framer Motion for declarative animations with performance best practices

**Rationale**:
- Declarative API integrates naturally with React
- Layout animations handled automatically
- Respects `prefers-reduced-motion`
- GPU-accelerated (transforms/opacity)
- Gesture support (drag, hover) built-in
- Spring physics for natural motion

**Alternatives Considered**:
- **CSS Transitions**: Limited control, requires manual state management
- **React Spring**: More complex API, steeper learning curve
- **GSAP**: Imperative API, less React-friendly, larger bundle
- **Pure CSS Animations**: No layout animation support, limited sequencing

**Animation Patterns to Implement**:

1. **Task List Animations** (AnimatePresence + layout):
```typescript
<AnimatePresence mode="popLayout">
  {filteredTasks.map(task => (
    <motion.div
      key={task.id}
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
    >
      <TaskCard task={task} />
    </motion.div>
  ))}
</AnimatePresence>
```

2. **Completion Toggle** (spring transition):
```typescript
<motion.div
  animate={{
    scale: isCompleted ? 0.95 : 1,
    opacity: isCompleted ? 0.6 : 1
  }}
  transition={{ type: 'spring', stiffness: 300, damping: 20 }}
>
```

3. **Modal Animations** (backdrop + content):
```typescript
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
>
  <motion.div
    initial={{ scale: 0.9, y: 20 }}
    animate={{ scale: 1, y: 0 }}
    exit={{ scale: 0.9, y: 20 }}
  >
```

**Performance Guidelines**:
- Animate only `transform` and `opacity` (GPU-accelerated)
- Use `layout` prop for automatic layout animations
- Keep duration under 300ms for micro-interactions
- Use `spring` physics for natural feel
- Limit concurrent animations (max 3-4 simultaneous)

### 5. Responsive Design Strategy

**Decision**: Mobile-first approach with Tailwind's responsive breakpoints

**Rationale**:
- Mobile-first ensures core functionality works on smallest screens
- Tailwind's breakpoints align with spec requirements
- Progressive enhancement adds complexity as screen grows
- Easier to add features than remove them

**Breakpoint Strategy**:
- **Default (mobile)**: 320px-640px - single column, vertical stack, large touch targets (min 44px)
- **sm (tablet)**: 640px-1024px - introduce subtle layout changes, 2-column possible
- **lg (desktop)**: 1024px+ - multi-column, hover states, denser information

**Responsive Patterns**:
```typescript
// Component spacing
<div className="p-4 sm:p-6 lg:p-8">

// Typography scaling
<h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">

// Layout changes
<div className="flex flex-col lg:flex-row gap-4">

// Conditional rendering (avoid if possible, prefer CSS)
{isMobile ? <MobileNav /> : <DesktopNav />}
```

**Best Practices**:
- Design mobile first, enhance for larger screens
- Use Tailwind breakpoint prefixes consistently
- Test on real devices (Chrome DevTools device emulation)
- Ensure touch targets minimum 44x44px on mobile
- Use `hidden lg:block` or `lg:hidden` sparingly

### 6. Accessibility Implementation (WCAG 2.1 AA)

**Decision**: Semantic HTML + ARIA labels + keyboard navigation + focus management

**Rationale**:
- WCAG 2.1 AA is standard for modern web applications
- Radix UI (shadcn/ui base) provides accessibility out of box
- Keyboard navigation required by spec (FR-016)
- Focus management critical for modals and dynamic content

**Implementation Checklist**:

1. **Semantic HTML**:
   - Use `<button>` not `<div onClick>`
   - Use `<form>` for task forms
   - Use `<main>`, `<nav>`, `<header>` landmarks

2. **Color Contrast** (WCAG AA):
   - Normal text: 4.5:1 minimum
   - Large text (18pt+): 3:1 minimum
   - Use Tailwind's slate scale for grays
   - Test with browser DevTools contrast checker

3. **Keyboard Navigation**:
   - Tab through all interactive elements
   - Enter/Space activate buttons
   - Escape closes modals
   - Arrow keys for lists (optional enhancement)

4. **Focus Management**:
   - Visible focus indicators (2-3px ring)
   - Trap focus in modals
   - Return focus to trigger on modal close
   - Skip links for screen readers

5. **ARIA Labels**:
   - `aria-label` for icon-only buttons
   - `aria-describedby` for form errors
   - `aria-live` for dynamic content announcements
   - `role="dialog"` with `aria-labelledby` for modals

**Testing Strategy**:
- Run Lighthouse accessibility audit (target ≥90)
- Test with keyboard only (unplug mouse)
- Test with screen reader (NVDA on Windows, VoiceOver on Mac)
- Verify contrast with DevTools or WebAIM contrast checker

### 7. Loading and Empty State Patterns

**Decision**: Skeleton screens for loading, illustration + CTA for empty states

**Rationale**:
- Skeleton screens indicate content structure, reduce perceived load time
- Empty states guide users to first action
- Maintains layout stability (no content shifts)

**Loading State Pattern**:
- Use shadcn/ui Skeleton component
- Match skeleton structure to actual content
- Minimum 500ms visibility (per spec FR-009)
- Simulate with setTimeout for mocked operations

**Empty State Pattern**:
- Lucide icon (e.g., CheckSquare, Clipboard)
- Encouraging message ("No tasks yet")
- Primary CTA ("Add your first task")
- Optional illustration or graphic

**Implementation**:
```typescript
{isLoading ? (
  <TaskListSkeleton count={5} />
) : tasks.length === 0 ? (
  <EmptyState
    icon={<CheckSquare />}
    title="No tasks yet"
    description="Add your first task to get started"
    action={<Button onClick={handleAddTask}>Add Task</Button>}
  />
) : (
  <TaskList tasks={tasks} />
)}
```

### 8. Form Validation Strategy

**Decision**: Client-side validation with React Hook Form + inline error display

**Rationale**:
- React Hook Form provides performant validation without re-renders
- Inline errors provide immediate feedback (per spec FR-005)
- No backend validation needed (frontend-only phase)
- TypeScript integration ensures type-safe form data

**Alternatives Considered**:
- **Manual useState**: Too much boilerplate, error-prone
- **Formik**: Larger bundle, more complex API
- **Native HTML5 validation**: Limited customization, poor UX

**Validation Rules**:
- **Task title**: Required, 1-200 characters, trim whitespace
- **Task description**: Optional, 0-1000 characters

**Implementation Pattern**:
```typescript
const form = useForm<TaskFormData>({
  defaultValues: { title: '', description: '' },
  resolver: zodResolver(taskSchema)
})

// Zod schema
const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200).trim(),
  description: z.string().max(1000).optional()
})
```

### 9. Design Token System

**Decision**: Define design tokens in Tailwind config, use CSS variables for runtime theming

**Rationale**:
- Centralized design decisions
- Consistent spacing/colors across app
- Easy theme switching (dark mode future)
- IntelliSense support in VSCode

**Token Categories**:

1. **Colors**:
   - Neutral: slate-50 to slate-900
   - Accent: Choose one (blue-600, purple-600, or emerald-600)
   - Semantic: green (success), amber (warning), red (danger)

2. **Spacing** (8px grid):
   - 0.5 = 4px, 1 = 8px, 2 = 16px, 3 = 24px, 4 = 32px, etc.

3. **Typography**:
   - Font sizes: xs, sm, base, lg, xl, 2xl, 3xl
   - Font weights: normal (400), medium (500), semibold (600), bold (700)
   - Line heights: tight (1.25), normal (1.5), relaxed (1.75)

4. **Shadows**:
   - sm, md, lg, xl for depth hierarchy

5. **Border Radius**:
   - sm (4px), md (8px), lg (12px), xl (16px)

**Tailwind Configuration**:
```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary)',
        accent: 'var(--accent)',
      },
      spacing: {
        // 8px grid enforced
      }
    }
  }
}
```

### 10. Component Architecture Philosophy

**Decision**: Atomic design principles with container/presenter pattern

**Rationale**:
- Atomic design provides clear component hierarchy
- Container/presenter separates logic from presentation
- Reusable components reduce duplication
- Easier to test in isolation

**Component Layers**:

1. **Atoms** (`components/ui/`):
   - shadcn/ui components (Button, Input, Card, etc.)
   - Fully reusable, no business logic
   - Accept only props, no context

2. **Molecules** (`components/`):
   - TaskCard, TaskForm, FilterTabs
   - Combine atoms, minimal logic
   - Accept data + callbacks

3. **Organisms** (`components/`):
   - TaskList, AddTaskModal, DeleteConfirmDialog
   - Complex UI sections
   - May use context for state

4. **Templates** (`app/` layouts):
   - Page layouts
   - Compose organisms

5. **Pages** (`app/` routes):
   - Route-specific logic
   - Fetch data (or mock), pass to templates

**Container/Presenter Pattern**:
```typescript
// Container (logic)
function TaskListContainer() {
  const { tasks, filter } = useTasks()
  const filteredTasks = useMemo(() =>
    filterTasks(tasks, filter), [tasks, filter]
  )

  return <TaskListPresenter tasks={filteredTasks} />
}

// Presenter (UI)
function TaskListPresenter({ tasks }: { tasks: Task[] }) {
  return (
    <div>
      {tasks.map(task => <TaskCard key={task.id} task={task} />)}
    </div>
  )
}
```

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Framework | Next.js 16 App Router | Modern, optimized, server components |
| UI Library | shadcn/ui + Tailwind | Full control, accessible, customizable |
| State | Context + useReducer | Simple, predictable, swap-ready |
| Animations | Framer Motion | Declarative, performant, natural |
| Responsive | Mobile-first Tailwind | Progressive enhancement |
| Accessibility | Semantic HTML + ARIA | WCAG 2.1 AA compliant |
| Loading | Skeleton screens | Reduced perceived wait time |
| Validation | React Hook Form + Zod | Type-safe, inline errors |
| Design Tokens | Tailwind config | Centralized, consistent |
| Architecture | Atomic design | Reusable, testable, clear hierarchy |

## Implementation Readiness

All technical unknowns resolved. No NEEDS CLARIFICATION items remaining. Ready to proceed to Phase 1 (Data Model + Contracts).

## References

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Framer Motion Docs](https://www.framer.com/motion/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [React Hook Form](https://react-hook-form.com)
