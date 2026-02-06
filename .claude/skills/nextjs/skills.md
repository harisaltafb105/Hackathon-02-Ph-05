# Next.js Development Skills

## Overview
Next.js is a React framework for building full-stack web applications. You use React Components to build user interfaces, and Next.js for additional features and optimizations.

## Core Competencies

### 1. App Router (Next.js 13+)
- **File-based routing**: Use the `app` directory for routing
- **Server Components**: Default to React Server Components for better performance
- **Client Components**: Use `'use client'` directive when you need interactivity, hooks, or browser APIs
- **Layouts**: Create shared UI across routes with `layout.tsx`
- **Loading States**: Use `loading.tsx` for automatic loading UI
- **Error Handling**: Implement `error.tsx` for error boundaries

### 2. Data Fetching Patterns
```typescript
// Server Component - fetch directly
async function getData() {
  const res = await fetch('https://api.example.com/data', {
    cache: 'no-store' // or 'force-cache' for static
  })
  return res.json()
}

export default async function Page() {
  const data = await getData()
  return <div>{/* render data */}</div>
}

// Client Component - use hooks
'use client'
import { useState, useEffect } from 'react'

export default function ClientPage() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .then(setData)
  }, [])

  return <div>{/* render data */}</div>
}
```

### 3. API Routes
```typescript
// app/api/route.ts
export async function GET(request: Request) {
  return Response.json({ message: 'Hello' })
}

export async function POST(request: Request) {
  const body = await request.json()
  // Process data
  return Response.json({ success: true })
}
```

### 4. Server Actions
```typescript
// app/actions.ts
'use server'

export async function createTodo(formData: FormData) {
  const title = formData.get('title')
  // Mutate database
  revalidatePath('/todos')
}

// In component
import { createTodo } from './actions'

export default function Form() {
  return (
    <form action={createTodo}>
      <input name="title" />
      <button type="submit">Create</button>
    </form>
  )
}
```

### 5. Middleware
```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Authentication, redirects, etc.
  return NextResponse.next()
}

export const config = {
  matcher: '/dashboard/:path*'
}
```

### 6. Environment Variables
- Use `.env.local` for local development secrets
- Prefix with `NEXT_PUBLIC_` for browser-accessible variables
- Access in Server Components: `process.env.SECRET_KEY`
- Access in Client Components: `process.env.NEXT_PUBLIC_API_URL`

### 7. Image Optimization
```typescript
import Image from 'next/image'

<Image
  src="/photo.jpg"
  width={500}
  height={300}
  alt="Description"
  priority // for LCP images
/>
```

### 8. Metadata and SEO
```typescript
// Static metadata
export const metadata = {
  title: 'Page Title',
  description: 'Page description'
}

// Dynamic metadata
export async function generateMetadata({ params }) {
  return {
    title: `Item ${params.id}`
  }
}
```

## Best Practices

### Performance
- Use Server Components by default
- Implement streaming with Suspense boundaries
- Optimize images with next/image
- Use dynamic imports for code splitting
- Implement proper caching strategies

### Type Safety
- Use TypeScript for type safety
- Define proper types for API responses
- Use typed route parameters and search params

### Code Organization
```
app/
  ├── (auth)/          # Route groups
  │   ├── login/
  │   └── register/
  ├── api/
  │   └── users/
  │       └── route.ts
  ├── dashboard/
  │   ├── layout.tsx
  │   ├── page.tsx
  │   └── loading.tsx
  └── layout.tsx       # Root layout
```

### Error Handling
- Implement error boundaries with `error.tsx`
- Use `not-found.tsx` for 404 pages
- Handle API errors gracefully
- Provide meaningful error messages

### Security
- Validate all user inputs
- Use environment variables for secrets
- Implement CSRF protection
- Sanitize data before rendering
- Use Server Actions for mutations

## Common Patterns

### Authentication Flow
1. Implement middleware for protected routes
2. Use Server Actions for login/logout
3. Store tokens securely (httpOnly cookies)
4. Validate on every request

### Form Handling
1. Use Server Actions for progressive enhancement
2. Implement client-side validation with react-hook-form
3. Show loading states during submission
4. Handle errors and display to users

### Data Mutations
1. Use Server Actions for database writes
2. Revalidate affected paths/tags
3. Implement optimistic updates on client
4. Handle race conditions

## Debugging Tips
- Use React DevTools
- Check Network tab for API calls
- Review build output for bundle sizes
- Use `console.log` in Server Components (shows in terminal)
- Use `console.log` in Client Components (shows in browser)

## Common Gotchas
- Server Components cannot use hooks or browser APIs
- Client Components increase bundle size
- `'use client'` only needed at boundary, not every component
- Cookies/headers only work in Server Components/Actions
- Dynamic rendering triggered by certain APIs (cookies, headers, searchParams)

## Resources
- Official Docs: https://nextjs.org/docs
- Learn Next.js: https://nextjs.org/learn
- Examples: https://github.com/vercel/next.js/tree/canary/examples
