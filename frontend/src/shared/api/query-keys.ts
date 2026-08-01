export const queryKeys = {
  checkin: {
    current: () => ['checkin', 'current'] as const,
    history: () => ['checkin', 'history'] as const,
  },
  tasks: {
    all: () => ['tasks', 'all'] as const,
  },
  profile: {
    me: () => ['profile', 'me'] as const,
    stats: () => ['profile', 'stats'] as const,
  },
  institution: {
    students: () => ['institution', 'students'] as const,
    roi: () => ['institution', 'roi'] as const,
  },
}
