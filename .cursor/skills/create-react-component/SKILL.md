---
name: create-react-component
description: Builds a typed React functional component with co-located React Testing Library tests, react-hook-form + Zod validation, and explicit loading, error, and empty states. Use when the user asks to create a component, add a page, or build a form.
---

# create-react-component

**Trigger**: "create a component", "add a page", "build a form"

**Pattern**:
1. Functional component with typed props interface.
2. Co-located `*.test.tsx` using React Testing Library.
3. Custom hook if stateful logic > 10 lines.
4. Error boundary wrapper for page-level components.
5. Loading + Error + Empty states always handled.

**Template**:
```tsx
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/shared/api/client';
import { Button } from '@/shared/components/ui/Button';
import { Input } from '@/shared/components/ui/Input';
import { FormError } from '@/shared/components/ui/FormError';

const schema = z.object({
  email: z.string().email('Invalid email'),
  password: z.string().min(8, 'Min 8 characters'),
});

type FormData = z.infer<typeof schema>;

interface LoginFormProps {
  onSuccess: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const mutation = useMutation({
    mutationFn: (data: FormData) => api.post('/auth/login', data),
    onSuccess,
    onError: (err) => {
      setError('root', { message: err.message ?? 'Login failed' });
    },
  });

  return (
    <form onSubmit={handleSubmit((data) => mutation.mutate(data))}>
      <Input {...register('email')} type="email" label="Email" error={errors.email?.message} />
      <Input {...register('password')} type="password" label="Password" error={errors.password?.message} />
      {errors.root && <FormError message={errors.root.message!} />}
      <Button type="submit" loading={mutation.isPending}>
        Sign in
      </Button>
    </form>
  );
}
```
