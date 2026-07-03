---
name: write-unit-test
description: Writes Vitest unit tests using strict Arrange-Act-Assert structure with vi.mock at service boundaries and vi.clearAllMocks in beforeEach. Use when the user asks to write a test, add tests, or write a unit test for a function or component.
---

# write-unit-test

**Trigger**: "write a test", "add tests", "unit test for"

**Pattern — Vitest**:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { userService } from './user.service';
import { userRepository } from '@/repositories/user.repository';
import { ConflictError } from '@/domain/errors';

vi.mock('@/repositories/user.repository');

describe('userService.create', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates a user and returns sanitized data', async () => {
    // Arrange
    vi.mocked(userRepository.findByEmail).mockResolvedValue(null);
    vi.mocked(userRepository.create).mockResolvedValue({
      id: 'user-1',
      email: 'alice@example.com',
      createdAt: new Date(),
    });

    // Act
    const result = await userService.create({
      email: 'alice@example.com',
      password: 'secureP@ss1',
    });

    // Assert
    expect(result.id).toBe('user-1');
    expect(result).not.toHaveProperty('passwordHash');
  });

  it('throws ConflictError when email already exists', async () => {
    // Arrange
    vi.mocked(userRepository.findByEmail).mockResolvedValue({ id: 'existing' } as any);

    // Act & Assert
    await expect(
      userService.create({ email: 'exists@example.com', password: 'pass' })
    ).rejects.toThrow(ConflictError);
  });
});
```
