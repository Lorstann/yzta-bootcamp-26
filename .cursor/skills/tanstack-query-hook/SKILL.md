---
name: tanstack-query-hook
description: Authors TanStack Query hooks using a hierarchical query-key factory, useQuery for reads with staleTime, and useMutation that updates the cache via setQueryData and invalidateQueries on success. Use when the user asks to fetch data in React, write a query hook, useQuery, or useMutation.
---

# tanstack-query-hook

**Trigger**: "fetch data in React", "query hook", "useMutation", "useQuery"

**Template**:
```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/shared/api/client';
import type { User } from '@/domain/entities/user';

// Query keys as constants — prevents typos, enables precise invalidation
export const userKeys = {
  all: ['users'] as const,
  lists: () => [...userKeys.all, 'list'] as const,
  detail: (id: string) => [...userKeys.all, 'detail', id] as const,
};

export function useUser(id: string) {
  return useQuery({
    queryKey: userKeys.detail(id),
    queryFn: () => api.get<User>(`/users/${id}`),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<User> }) =>
      api.patch<User>(`/users/${id}`, data),
    onSuccess: (updated) => {
      queryClient.setQueryData(userKeys.detail(updated.id), updated);
      queryClient.invalidateQueries({ queryKey: userKeys.lists() });
    },
  });
}
```
