---
description: "Task list for Frontend-First Todo Web Application UI"
---

# Tasks: Frontend-First Todo Web Application UI

**Input**: Design documents from `/specs/001-frontend-ui/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/, research.md, quickstart.md

**Tests**: NOT requested - no test tasks included. Focus is on implementation and manual validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend-only project**: `frontend/` at repository root
- **App Router**: `frontend/app/` for pages and layouts
- **Components**: `frontend/components/` for all React components
- **Context/Hooks**: `frontend/context/` and `frontend/hooks/`
- **Types/Lib**: `frontend/types/` and `frontend/lib/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Navigate to project root and create Next.js 16 application in frontend/ directory with TypeScript, Tailwind CSS, and App Router
- [ ] T002 Install core dependencies: framer-motion, react-hook-form, @hookform/resolvers, zod, lucide-react
- [ ] T003 Install shadcn/ui dependencies: class-variance-authority, clsx, tailwind-merge, @radix-ui/react-dialog, @radix-ui/react-checkbox, @radix-ui/react-tabs
- [ ] T004 Initialize shadcn/ui configuration by running npx shadcn@latest init in frontend/ directory
- [ ] T005 [P] Install shadcn/ui button component in frontend/components/ui/button.tsx
- [ ] T006 [P] Install shadcn/ui card component in frontend/components/ui/card.tsx
- [ ] T007 [P] Install shadcn/ui dialog component in frontend/components/ui/dialog.tsx
- [ ] T008 [P] Install shadcn/ui input component in frontend/components/ui/input.tsx
- [ ] T009 [P] Install shadcn/ui label component in frontend/components/ui/label.tsx
- [ ] T010 [P] Install shadcn/ui checkbox component in frontend/components/ui/checkbox.tsx
- [ ] T011 [P] Install shadcn/ui tabs component in frontend/components/ui/tabs.tsx
- [ ] T012 [P] Install shadcn/ui separator component in frontend/components/ui/separator.tsx
- [ ] T013 [P] Install shadcn/ui skeleton component in frontend/components/ui/skeleton.tsx
- [ ] T014 Configure Tailwind theme in frontend/tailwind.config.ts with 8px grid system, slate color palette, and custom accent color
- [ ] T015 Configure TypeScript with strict mode in frontend/tsconfig.json
- [ ] T016 [P] Create directory structure: frontend/components/, frontend/context/, frontend/hooks/, frontend/lib/, frontend/types/
- [ ] T017 Verify dev server starts without errors by running npm run dev in frontend/ directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T018 [P] Create TypeScript type definitions in frontend/types/task.ts for Task, FilterType, UIState, AppState, TaskAction interfaces
- [ ] T019 [P] Create mocked task data in frontend/lib/mock-data.ts with 6 sample tasks (mix of completed and pending)
- [ ] T020 Create task context in frontend/context/task-context.tsx with reducer, TaskProvider, useTasks, and useTaskActions hooks
- [ ] T021 Implement ADD_TASK, UPDATE_TASK, DELETE_TASK, TOGGLE_COMPLETE actions in task reducer
- [ ] T022 Implement SET_FILTER, OPEN_MODAL, CLOSE_MODAL, SET_LOADING, SET_ERROR actions in task reducer
- [ ] T023 [P] Create useFilteredTasks hook in frontend/hooks/use-filtered-tasks.ts with memoized filtering logic
- [ ] T024 [P] Create useTaskCounts hook in frontend/hooks/use-task-counts.ts with memoized count calculation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View and Browse Tasks (Priority: P1) 🎯 MVP

**Goal**: Display task list with proper visual hierarchy, loading states, empty states, and responsive design

**Independent Test**: Load application with mocked data and verify tasks display correctly with animations, responsive layout, and visual distinction for completed tasks

### Implementation for User Story 1

- [ ] T025 [P] [US1] Create TaskCard component in frontend/components/task-card.tsx with Card, Checkbox, and action buttons (Edit/Delete)
- [ ] T026 [P] [US1] Add Framer Motion completion animation to TaskCard (scale + opacity transition on toggle)
- [ ] T027 [P] [US1] Apply completion visual styles to TaskCard (strikethrough, muted colors, check icon for completed tasks)
- [ ] T028 [P] [US1] Add hover states to TaskCard showing Edit and Delete buttons with smooth fade-in animation
- [ ] T029 [P] [US1] Add Lucide icons to TaskCard (Check, Pencil, Trash2) with aria-labels for accessibility
- [ ] T030 [P] [US1] Create FilterTabs component in frontend/components/filter-tabs.tsx using shadcn/ui Tabs with All/Active/Completed options
- [ ] T031 [P] [US1] Display task counts in FilterTabs (e.g., "Active (5)") using useTaskCounts hook
- [ ] T032 [P] [US1] Create EmptyState component in frontend/components/empty-state.tsx with Lucide icon and contextual message based on filter
- [ ] T033 [P] [US1] Create TaskListSkeleton component in frontend/components/task-list-skeleton.tsx with 5 Skeleton components matching TaskCard layout
- [ ] T034 [US1] Create TaskList component in frontend/components/task-list.tsx with Framer Motion AnimatePresence for list animations
- [ ] T035 [US1] Add entry/exit animations to TaskList (fade + slide from below on add, fade + slide to left on delete)
- [ ] T036 [US1] Add layout animations to TaskList for smooth reordering when filter changes
- [ ] T037 [US1] Create HomePage in frontend/app/page.tsx with 'use client' directive, importing all US1 components
- [ ] T038 [US1] Add header layout to HomePage with title, FilterTabs, and Add Task button placeholder
- [ ] T039 [US1] Add conditional rendering logic to HomePage (loading → skeleton, empty → EmptyState, otherwise → TaskList)
- [ ] T040 [US1] Add responsive layout classes to HomePage (stack on mobile, optimize on desktop)
- [ ] T041 [US1] Create RootLayout in frontend/app/layout.tsx wrapping children with TaskProvider
- [ ] T042 [US1] Update frontend/app/globals.css with Tailwind directives, CSS custom properties for colors, and reduced motion media query
- [ ] T043 [US1] Test US1 by loading app and verifying mocked tasks display with proper styling, loading states work, empty state appears when no tasks, and layout is responsive

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Add New Tasks (Priority: P2)

**Goal**: Enable users to add new tasks via modal form with validation and smooth animations

**Independent Test**: Click "Add Task" button, fill form with valid data, submit, and verify new task appears in list with animation

### Implementation for User Story 2

- [ ] T044 [US2] Create TaskForm component in frontend/components/task-form.tsx using React Hook Form and Zod validation
- [ ] T045 [US2] Add form fields to TaskForm (title with Label + Input, description with Label + Input)
- [ ] T046 [US2] Implement Zod validation schema in TaskForm (title 1-200 chars required, description 0-1000 chars optional)
- [ ] T047 [US2] Add inline validation errors to TaskForm fields with aria-describedby for accessibility
- [ ] T048 [US2] Add character count display to TaskForm description field showing remaining characters
- [ ] T049 [US2] Add loading state to TaskForm that disables inputs and shows spinner on submit button
- [ ] T050 [US2] Add Submit (primary Button) and Cancel (outline Button) to TaskForm with keyboard support (Enter submits, Escape cancels)
- [ ] T051 [US2] Create AddTaskModal component in frontend/components/add-task-modal.tsx using shadcn/ui Dialog
- [ ] T052 [US2] Render TaskForm inside AddTaskModal content area
- [ ] T053 [US2] Connect AddTaskModal open state to context ui.activeModal === 'add-task'
- [ ] T054 [US2] Implement AddTaskModal onSubmit handler that dispatches ADD_TASK action with 500ms simulated async delay
- [ ] T055 [US2] Add focus management to AddTaskModal (focus title input on open, return focus to trigger button on close)
- [ ] T056 [US2] Add Framer Motion animations to AddTaskModal (backdrop fade, content scale + slide)
- [ ] T057 [US2] Connect "Add Task" button in HomePage to open AddTaskModal by dispatching OPEN_MODAL action
- [ ] T058 [US2] Test US2 by clicking Add Task, filling form with title "Test Task", submitting, and verifying task appears in list with smooth animation

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P3)

**Goal**: Enable users to toggle task completion status with satisfying visual feedback and animation

**Independent Test**: Click checkbox on a pending task, verify it animates to completed state, click again to toggle back

### Implementation for User Story 3

- [ ] T059 [US3] Connect TaskCard checkbox to useTaskActions toggleComplete handler
- [ ] T060 [US3] Add Framer Motion spring animation to TaskCard for completion toggle (scale 0.95, opacity 0.6 when completed)
- [ ] T061 [US3] Verify completed task visual styles from US1 work correctly with toggle (strikethrough, muted colors, check icon)
- [ ] T062 [US3] Add animation timing to completion toggle (200ms duration, spring physics with stiffness 300, damping 20)
- [ ] T063 [US3] Implement filter transition behavior: when task completed while "Active" filter active, task smoothly animates out of view
- [ ] T064 [US3] Test US3 by toggling multiple tasks between pending and completed states, verifying smooth animations and filter interactions

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Edit Existing Tasks (Priority: P4)

**Goal**: Enable users to modify existing task details via edit modal with pre-filled form

**Independent Test**: Hover over task, click Edit button, modify title or description, save, and verify updates appear

### Implementation for User Story 4

- [ ] T065 [US4] Create EditTaskModal component in frontend/components/edit-task-modal.tsx using shadcn/ui Dialog
- [ ] T066 [US4] Reuse TaskForm component inside EditTaskModal but pass mode='edit' and initialData props
- [ ] T067 [US4] Implement logic in EditTaskModal to find task by ui.selectedTaskId from context
- [ ] T068 [US4] Pre-fill TaskForm fields in EditTaskModal with current task title and description
- [ ] T069 [US4] Implement EditTaskModal onSubmit handler that dispatches UPDATE_TASK action with task id and updates
- [ ] T070 [US4] Add 500ms simulated async delay to EditTaskModal onSubmit to show loading state
- [ ] T071 [US4] Connect Edit button in TaskCard to open EditTaskModal by dispatching OPEN_MODAL with modal='edit-task' and taskId
- [ ] T072 [US4] Add focus management to EditTaskModal (focus title input on open, return focus to Edit button on close)
- [ ] T073 [US4] Ensure EditTaskModal closes after successful update and clears selectedTaskId
- [ ] T074 [US4] Test US4 by editing multiple tasks, verifying pre-filled data, saving changes, and confirming updates appear in TaskList

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P5)

**Goal**: Enable users to safely delete tasks with confirmation dialog to prevent accidental deletion

**Independent Test**: Hover over task, click Delete button, confirm in dialog, verify task animates out and is removed

### Implementation for User Story 5

- [ ] T075 [US5] Create DeleteConfirmDialog component in frontend/components/delete-confirm-dialog.tsx using shadcn/ui Dialog with role="alertdialog"
- [ ] T076 [US5] Display task title in DeleteConfirmDialog confirmation message (e.g., "Are you sure you want to delete 'Task Title'?")
- [ ] T077 [US5] Add Cancel button (outline variant) and Delete button (destructive variant) to DeleteConfirmDialog
- [ ] T078 [US5] Implement DeleteConfirmDialog onConfirm handler that dispatches DELETE_TASK action with task id
- [ ] T079 [US5] Add 500ms simulated async delay to DeleteConfirmDialog onConfirm with loading state on Delete button
- [ ] T080 [US5] Connect Delete button in TaskCard to open DeleteConfirmDialog by dispatching OPEN_MODAL with modal='delete-confirm' and taskId
- [ ] T081 [US5] Add focus management to DeleteConfirmDialog (focus Delete button by default as dangerous action)
- [ ] T082 [US5] Ensure DeleteConfirmDialog closes on Cancel or after successful deletion
- [ ] T083 [US5] Verify TaskList exit animation triggers when task is deleted (fade + slide to left)
- [ ] T084 [US5] Test US5 by deleting multiple tasks, confirming deletion dialog works, and verifying smooth removal animations

**Checkpoint**: At this point, User Stories 1, 2, 3, 4, AND 5 should all work independently

---

## Phase 8: User Story 6 - Filter Tasks by Status (Priority: P6)

**Goal**: Enable users to focus on specific task subsets by filtering All/Active/Completed tasks

**Independent Test**: Click each filter tab and verify only appropriate tasks display with smooth transitions

### Implementation for User Story 6

- [ ] T085 [US6] Connect FilterTabs onClick handlers to dispatch SET_FILTER action with selected filter type
- [ ] T086 [US6] Verify useFilteredTasks hook correctly filters tasks based on context filter state
- [ ] T087 [US6] Ensure TaskList uses filtered tasks from useFilteredTasks hook instead of raw tasks array
- [ ] T088 [US6] Verify FilterTabs highlights active tab correctly based on context filter state
- [ ] T089 [US6] Test filter transitions by clicking Active → Completed → All and verifying smooth AnimatePresence transitions
- [ ] T090 [US6] Test filter behavior when adding new task (appears only if matches active filter)
- [ ] T091 [US6] Test filter behavior when completing task in Active view (task animates out smoothly)
- [ ] T092 [US6] Test US6 by cycling through all filter states and verifying correct task subsets display with animations

**Checkpoint**: All user stories should now be independently functional

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Visual quality, animation consistency, responsive design, and accessibility improvements

### Visual Polish

- [ ] T093 [P] Audit and finalize color palette in frontend/app/globals.css (neutral slate base, single accent color, semantic colors)
- [ ] T094 [P] Verify typography hierarchy across all components (2xl for headings, base for body, sm for metadata)
- [ ] T095 [P] Audit all components for consistent 8px grid spacing (padding, margins, gaps)
- [ ] T096 [P] Apply consistent shadow depths to cards and modals (sm, md, lg)
- [ ] T097 [P] Ensure consistent border radius across all components (md = 8px)
- [ ] T098 [P] Verify hover states on all interactive elements (150-200ms transitions, clear feedback)
- [ ] T099 [P] Add visible focus indicators to all interactive elements (2-3px ring, high contrast color)
- [ ] T100 Verify overall visual quality meets "hackathon-ready" standard (no tutorial look, premium feel)

### Animation Consistency

- [ ] T101 [P] Audit all animations for consistent timing (100-200ms micro, 200-300ms transitions, 300-500ms complex)
- [ ] T102 [P] Verify all animations use GPU-accelerated properties (transform, opacity only)
- [ ] T103 [P] Test animations in Chrome DevTools Performance tab to confirm 60fps
- [ ] T104 [P] Verify reduced motion media query works (animations disable when prefers-reduced-motion: reduce)
- [ ] T105 [P] Ensure no more than 3-4 concurrent animations at any time

### Responsive Design

- [ ] T106 Test mobile layout (320px-640px) for single column, stacked elements, and 44px minimum touch targets
- [ ] T107 Test tablet layout (640px-1024px) for smooth transitions and appropriate spacing
- [ ] T108 Test desktop layout (1024px+) for centered container, hover states, and optimal information density
- [ ] T109 Verify no horizontal scroll on any viewport size (320px to 1920px+)
- [ ] T110 Test modals on mobile (full-screen on small devices, centered on larger)

### Accessibility

- [ ] T111 [P] Verify all interactive elements use semantic HTML (<button>, <form>, not <div onClick>)
- [ ] T112 [P] Add ARIA labels to icon-only buttons (Edit, Delete, Add Task)
- [ ] T113 [P] Connect form errors to inputs via aria-describedby
- [ ] T114 [P] Ensure modals have role="dialog" and aria-labelledby pointing to title
- [ ] T115 [P] Add aria-busy and aria-live for loading state announcements
- [ ] T116 Test keyboard navigation (Tab through all elements, Enter/Space activates, Escape closes modals)
- [ ] T117 Test focus management (focus trapped in modals, returns to trigger on close)
- [ ] T118 Run WebAIM contrast checker on all text/background combinations (4.5:1 for normal text, 3:1 for large text)
- [ ] T119 Run Lighthouse accessibility audit and achieve score >= 90
- [ ] T120 Test with screen reader (NVDA or VoiceOver) to verify task announcements and navigation

### Final Validation

- [ ] T121 Test complete user flow: Add task → Mark complete → Edit → Delete → Filter, verifying all interactions work smoothly
- [ ] T122 Verify all 6 user stories (P1-P6) are independently testable and functional
- [ ] T123 Verify all 20 functional requirements (FR-001 to FR-020) from spec are met
- [ ] T124 Measure and verify key success criteria (add task <10s, mark complete <2s, initial render <1s, 60fps animations)
- [ ] T125 Test on multiple browsers (Chrome, Firefox, Safari, Edge) for cross-browser compatibility
- [ ] T126 Run npm run build in frontend/ directory and verify no TypeScript errors
- [ ] T127 Verify bundle size is reasonable (<500KB total)
- [ ] T128 Run quickstart.md validation checklist to ensure all setup and testing steps work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if staffed)
  - OR sequentially in priority order (P1 → P2 → P3 → P4 → P5 → P6)
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - REQUIRED FOR MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but builds on US1's display components
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses TaskCard from US1
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Reuses TaskForm from US2
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Independent deletion flow
- **User Story 6 (P6)**: Can start after Foundational (Phase 2) - Enhances US1's FilterTabs component

### Within Each Phase

**Setup Phase**:
- Tasks T001-T004 must be sequential (create app, install deps, init shadcn)
- Tasks T005-T013 can run in parallel (install shadcn components)
- Tasks T014-T016 can run in parallel (configure project)
- Task T017 validates setup (run after all above)

**Foundational Phase**:
- Tasks T018-T019 can run in parallel (types and mock data independent)
- Task T020 depends on T018 (context needs types)
- Tasks T021-T022 are sequential within T020 (reducer actions)
- Tasks T023-T024 can run in parallel after T020 (custom hooks)

**User Story Phases**:
- Component creation tasks marked [P] can run in parallel
- Integration tasks depend on component tasks completing
- Testing task should run after all implementation tasks

**Polish Phase**:
- Visual polish tasks (T093-T100) can run in parallel
- Animation tasks (T101-T105) can run in parallel
- Responsive tests (T106-T110) should run sequentially (same device)
- Accessibility tasks (T111-T120) can run mostly in parallel
- Final validation tasks (T121-T128) should run sequentially

---

## Parallel Example: User Story 1

```bash
# Launch component creation tasks in parallel:
- T025: TaskCard component
- T030: FilterTabs component
- T032: EmptyState component
- T033: TaskListSkeleton component

# After components complete, integrate:
- T034-T036: TaskList with animations (depends on TaskCard)
- T037-T040: HomePage assembly (depends on all US1 components)
- T041-T042: RootLayout and global styles (depends on context from Phase 2)
- T043: Test US1 (depends on all above)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T017)
2. Complete Phase 2: Foundational (T018-T024) - CRITICAL
3. Complete Phase 3: User Story 1 (T025-T043)
4. **STOP and VALIDATE**: Test US1 independently
5. Polish visual quality (selected tasks from Phase 9)
6. Deploy/demo if ready

**MVP Scope**: Tasks T001-T043 + selective polish tasks = ~43 core tasks for minimum viable product

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (Tasks T001-T024)
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!) (Tasks T025-T043)
3. Add User Story 2 → Test independently → Deploy/Demo (Tasks T044-T058)
4. Add User Story 3 → Test independently → Deploy/Demo (Tasks T059-T064)
5. Add User Story 4 → Test independently → Deploy/Demo (Tasks T065-T074)
6. Add User Story 5 → Test independently → Deploy/Demo (Tasks T075-T084)
7. Add User Story 6 → Test independently → Deploy/Demo (Tasks T085-T092)
8. Polish all aspects → Final QA → Production ready (Tasks T093-T128)

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Tasks T001-T024)
2. Once Foundational is done, split work:
   - Developer A: User Story 1 (T025-T043)
   - Developer B: User Story 2 (T044-T058) - can start in parallel
   - Developer C: User Story 3 (T059-T064) - can start in parallel
3. Stories complete and integrate independently
4. Team reconvenes for Polish phase (Tasks T093-T128)

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Tests are NOT included** - focus is on implementation and manual validation
- Visual quality is highest priority - polish tasks (Phase 9) are critical
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Task Count Summary

- **Total Tasks**: 128
- **Setup (Phase 1)**: 17 tasks
- **Foundational (Phase 2)**: 7 tasks (BLOCKING)
- **User Story 1 (P1)**: 19 tasks (MVP CORE)
- **User Story 2 (P2)**: 15 tasks
- **User Story 3 (P3)**: 6 tasks
- **User Story 4 (P4)**: 10 tasks
- **User Story 5 (P5)**: 10 tasks
- **User Story 6 (P6)**: 8 tasks
- **Polish (Phase 9)**: 36 tasks

**MVP Scope**: 43 tasks (Setup + Foundational + US1 + selective polish)
**Full Implementation**: 128 tasks (all user stories + complete polish)
**Parallel Opportunities**: 50+ tasks marked [P] can run concurrently
