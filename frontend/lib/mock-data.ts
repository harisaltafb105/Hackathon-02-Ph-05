import type { Task } from '@/types/task'

// Initial mocked tasks for development
export const mockedTasks: Task[] = [
  {
    id: '1',
    title: 'Complete project documentation',
    description: 'Write comprehensive README with setup instructions, API documentation, and usage examples.',
    completed: false,
    createdAt: new Date('2026-01-03T09:00:00Z'),
    updatedAt: new Date('2026-01-04T14:30:00Z'),
  },
  {
    id: '2',
    title: 'Review pull requests',
    description: 'Check and approve pending PRs from the team. Focus on code quality and test coverage.',
    completed: true,
    createdAt: new Date('2026-01-02T10:15:00Z'),
  },
  {
    id: '3',
    title: 'Buy groceries',
    description: '',
    completed: false,
    createdAt: new Date('2026-01-05T08:30:00Z'),
  },
  {
    id: '4',
    title: 'Schedule team meeting',
    description: 'Coordinate with all team members for quarterly planning session. Book conference room.',
    completed: true,
    createdAt: new Date('2026-01-01T11:00:00Z'),
  },
  {
    id: '5',
    title: 'Update dependencies',
    description: 'Run npm audit and update all outdated packages. Test for breaking changes.',
    completed: false,
    createdAt: new Date('2026-01-04T15:45:00Z'),
  },
  {
    id: '6',
    title: 'Fix production bug',
    description: 'Investigate and resolve the authentication timeout issue reported by users.',
    completed: false,
    createdAt: new Date('2026-01-05T10:00:00Z'),
  },
]
