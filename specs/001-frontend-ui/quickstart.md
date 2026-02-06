# Quickstart Guide: Frontend Todo Application

**Feature**: 001-frontend-ui
**Date**: 2026-01-05
**Purpose**: Step-by-step guide to set up, develop, and validate the frontend application

## Prerequisites

- **Node.js**: v20.x or later (LTS recommended)
- **Package Manager**: npm, yarn, or pnpm
- **Code Editor**: VS Code (recommended for TypeScript IntelliSense)
- **Browser**: Chrome, Firefox, Safari, or Edge (modern versions)

---

## Project Setup

### 1. Create Next.js Application

```bash
# Navigate to project root
cd D:\Hackathon-02\Todo-Fullstack

# Create Next.js 16 app with TypeScript, Tailwind CSS, App Router
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*"

# Navigate to frontend directory
cd frontend
```

**Configuration Selections**:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- `src/` directory: No (use `app/` at root)
- App Router: Yes
- Import alias: `@/*`

---

### 2. Install Dependencies

```bash
# Install shadcn/ui dependencies
npm install class-variance-authority clsx tailwind-merge
npm install @radix-ui/react-dialog @radix-ui/react-checkbox @radix-ui/react-tabs

# Install Framer Motion for animations
npm install framer-motion

# Install form handling and validation
npm install react-hook-form @hookform/resolvers zod

# Install icon library
npm install lucide-react

# Install dev dependencies
npm install -D @types/node @types/react @types/react-dom
```

---

### 3. Initialize shadcn/ui

```bash
# Initialize shadcn/ui configuration
npx shadcn@latest init

# Follow prompts:
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
```

This creates:
- `components/ui/` directory for shadcn components
- `lib/utils.ts` for utility functions
- Updates `tailwind.config.ts` with shadcn theme

---

### 4. Install shadcn/ui Components

```bash
# Install required components
npx shadcn@latest add button
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add checkbox
npx shadcn@latest add tabs
npx shadcn@latest add separator
npx shadcn@latest add skeleton
```

---

## Project Structure

After setup, your structure should look like:

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout (global providers)
│   ├── page.tsx                # Home page (main task view)
│   └── globals.css             # Global styles + Tailwind
├── components/
│   ├── ui/                     # shadcn/ui components (auto-generated)
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── label.tsx
│   │   ├── checkbox.tsx
│   │   ├── tabs.tsx
│   │   ├── separator.tsx
│   │   └── skeleton.tsx
│   ├── task-card.tsx           # Individual task display
│   ├── task-form.tsx           # Add/Edit task form
│   ├── task-list.tsx           # Animated task list
│   ├── filter-tabs.tsx         # All/Active/Completed tabs
│   ├── empty-state.tsx         # No tasks display
│   ├── task-list-skeleton.tsx  # Loading placeholder
│   ├── add-task-modal.tsx      # Add task dialog
│   ├── edit-task-modal.tsx     # Edit task dialog
│   └── delete-confirm-dialog.tsx # Delete confirmation
├── context/
│   └── task-context.tsx        # Global state provider
├── hooks/
│   ├── use-filtered-tasks.ts  # Compute filtered tasks
│   └── use-task-counts.ts     # Compute task counts
├── lib/
│   ├── utils.ts                # shadcn utility (auto-generated)
│   └── mock-data.ts            # Initial mocked tasks
├── types/
│   └── task.ts                 # TypeScript type definitions
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── next.config.js              # Next.js configuration
├── package.json                # Dependencies
└── .eslintrc.json              # ESLint configuration
```

---

## Configuration

### Tailwind CSS Customization

**File**: `tailwind.config.ts`

```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // shadcn/ui generates base colors
        // Customize accent color here
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
      },
      spacing: {
        // Enforce 8px grid system (already default in Tailwind)
      },
      borderRadius: {
        // Custom radius if needed
        lg: '0.75rem',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

**File**: `app/globals.css`

Add custom CSS variables:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light mode colors (shadcn auto-generates most) */
    --accent: 221 83% 53%; /* Example: blue-600 */
    --accent-foreground: 0 0% 100%;

    /* Add more custom tokens as needed */
  }

  .dark {
    /* Dark mode colors (optional) */
  }
}

/* Custom animation for reduced motion */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

### TypeScript Configuration

**File**: `tsconfig.json`

Ensure strict mode is enabled:

```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

---

## Development Workflow

### 1. Start Development Server

```bash
# From frontend directory
npm run dev

# Server starts at http://localhost:3000
```

### 2. Implement Components

**Order of Implementation** (recommended):

1. **Types** (`types/task.ts`)
   - Define Task, FilterType, AppState, TaskAction interfaces
   - Export all types for use across app

2. **Mock Data** (`lib/mock-data.ts`)
   - Create 5-10 sample tasks for initial state

3. **Context** (`context/task-context.tsx`)
   - Implement reducer logic
   - Create TaskProvider component
   - Export useTasks and useTaskActions hooks

4. **Hooks** (`hooks/`)
   - Implement useFilteredTasks
   - Implement useTaskCounts

5. **Atomic Components** (use shadcn/ui as-is)
   - Button, Card, Dialog, Input, etc.

6. **Molecule Components** (`components/`)
   - TaskCard (display single task)
   - TaskForm (add/edit form)
   - FilterTabs (All/Active/Completed)
   - EmptyState (no tasks message)
   - TaskListSkeleton (loading state)

7. **Organism Components** (`components/`)
   - TaskList (animated list)
   - AddTaskModal (dialog wrapper)
   - EditTaskModal (dialog wrapper)
   - DeleteConfirmDialog (confirmation)

8. **Page** (`app/page.tsx`)
   - Compose all organisms
   - Wire up context hooks
   - Implement layout

9. **Layout** (`app/layout.tsx`)
   - Wrap app in TaskProvider
   - Add global styles and metadata

### 3. Test in Browser

**Manual Testing Checklist**:

- [ ] **View Tasks**: Open app, see mocked tasks displayed
- [ ] **Add Task**: Click "Add Task", fill form, submit, see new task appear
- [ ] **Edit Task**: Hover task, click "Edit", modify, save, see updates
- [ ] **Delete Task**: Hover task, click "Delete", confirm, see task removed
- [ ] **Toggle Complete**: Click checkbox, see task animate to completed state
- [ ] **Filter All**: Click "All" tab, see all tasks
- [ ] **Filter Active**: Click "Active", see only pending tasks
- [ ] **Filter Completed**: Click "Completed", see only done tasks
- [ ] **Empty State**: Delete all tasks, see empty state message
- [ ] **Loading State**: Trigger simulated async operation, see skeleton

**Responsive Testing**:

- [ ] **Mobile (375px)**: Layout stacks vertically, touch targets large
- [ ] **Tablet (768px)**: Smooth transition, readable
- [ ] **Desktop (1440px)**: Optimal layout, hover states visible

**Accessibility Testing**:

- [ ] **Keyboard Navigation**: Tab through all elements, Enter/Space activates
- [ ] **Focus Indicators**: Clear visible focus rings on all interactive elements
- [ ] **Screen Reader**: Use NVDA/VoiceOver, verify task announcements
- [ ] **Color Contrast**: Check with DevTools (4.5:1 for text, 3:1 for large)

**Animation Testing**:

- [ ] **Task Add**: Smooth fade-in + slide from below
- [ ] **Task Complete**: Scale + opacity transition
- [ ] **Task Delete**: Fade-out + slide to left
- [ ] **Filter Change**: Smooth list transition
- [ ] **Modal Open/Close**: Backdrop fade + content scale

---

## Quality Validation

### Run Lighthouse Audit

```bash
# Open Chrome DevTools (F12)
# Navigate to Lighthouse tab
# Select "Desktop" or "Mobile"
# Check "Accessibility" category
# Run audit

# Target: Accessibility score >= 90
```

### Check Bundle Size

```bash
# Build for production
npm run build

# Check output for bundle sizes
# Ensure main bundle < 200KB gzipped
```

### Verify TypeScript

```bash
# Check for type errors
npm run type-check

# Or use built-in Next.js check
npm run build
```

---

## Troubleshooting

### Issue: Tailwind styles not applying

**Solution**:
1. Check `tailwind.config.ts` content paths include all component directories
2. Verify `@tailwind` directives present in `app/globals.css`
3. Restart dev server (`Ctrl+C`, then `npm run dev`)

### Issue: shadcn/ui components not found

**Solution**:
1. Verify components installed: `ls components/ui/`
2. Re-run: `npx shadcn@latest add <component-name>`
3. Check import paths use `@/components/ui/...`

### Issue: Framer Motion animations not working

**Solution**:
1. Verify `framer-motion` installed: `npm list framer-motion`
2. Check `'use client'` directive at top of animated components
3. Wrap animated lists in `<AnimatePresence>`

### Issue: Context not providing values

**Solution**:
1. Verify `TaskProvider` wraps app in `app/layout.tsx`
2. Check hooks called inside component (not top-level)
3. Ensure context default value matches AppState interface

---

## Next Steps After Implementation

1. **Visual Polish Checklist**:
   - [ ] Consistent spacing (8px grid)
   - [ ] Smooth animations (60fps)
   - [ ] Clear visual hierarchy
   - [ ] Elegant color palette
   - [ ] Proper typography scale

2. **Run Full Test Suite** (manual):
   - [ ] All user stories tested (P1-P6)
   - [ ] All functional requirements verified (FR-001 to FR-020)
   - [ ] Success criteria measured (SC-001 to SC-015)

3. **Prepare for Backend Integration** (future phase):
   - State management architecture supports API calls
   - Task interface matches backend schema
   - Async patterns ready for real HTTP requests

---

## Useful Commands

```bash
# Development
npm run dev            # Start dev server
npm run build          # Production build
npm run start          # Start production server
npm run lint           # Run ESLint

# Component generation (shadcn)
npx shadcn@latest add [component]  # Add new shadcn component

# Type checking
npx tsc --noEmit      # Check TypeScript without building
```

---

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Components](https://ui.shadcn.com)
- [Tailwind CSS](https://tailwindcss.com)
- [Framer Motion](https://www.framer.com/motion/)
- [React Hook Form](https://react-hook-form.com)
- [Zod Validation](https://zod.dev)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)

---

## Support

For issues or questions during implementation:
1. Check this quickstart guide
2. Review feature specification (`specs/001-frontend-ui/spec.md`)
3. Consult research document (`specs/001-frontend-ui/research.md`)
4. Review component contracts (`specs/001-frontend-ui/contracts/`)
5. Check data model (`specs/001-frontend-ui/data-model.md`)
