---
name: create-api-endpoint
description: Scaffolds a REST API endpoint with a thin route, controller, service, repository, shared Zod schema, and tests. Use when the user asks to create an API endpoint, add a route, or build a new REST endpoint.
---

# create-api-endpoint

**Trigger**: "create an API endpoint", "add a route", "new REST endpoint"

**Pattern to follow**:
1. Route file (`/api/routes/<resource>.routes.ts`) — thin, only wires middleware + controller.
2. Controller (`/api/controllers/<resource>.controller.ts`) — parse/validate request, call service, format response.
3. Service (`/services/<resource>.service.ts`) — all business logic, no Express knowledge.
4. Repository (`/repositories/<resource>.repository.ts`) — DB access only, returns domain entities.
5. Zod schema (`/domain/schemas/<resource>.schema.ts`) — shared between frontend and backend via monorepo or copy.
6. Tests: `<resource>.service.test.ts` (unit) + `<resource>.routes.test.ts` (integration with Supertest).

**Template — Controller**:
```typescript
import { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { createUserSchema } from '@/domain/schemas/user.schema';
import { userService } from '@/services/user.service';
import { logger } from '@/utils/logger';

export const createUser = async (
  req: Request,
  res: Response,
  next: NextFunction
): Promise<void> => {
  try {
    const body = createUserSchema.parse(req.body);
    const user = await userService.create(body);
    logger.info({ userId: user.id, action: 'user.created' }, 'User created');
    res.status(201).json({ success: true, data: user });
  } catch (err) {
    next(err);
  }
};
```

**Template — Service**:
```typescript
import { CreateUserDto } from '@/domain/schemas/user.schema';
import { userRepository } from '@/repositories/user.repository';
import { ConflictError } from '@/domain/errors';
import { hashPassword } from '@/utils/crypto';

export const userService = {
  async create(dto: CreateUserDto) {
    const existing = await userRepository.findByEmail(dto.email);
    if (existing) throw new ConflictError('Email already in use');

    const passwordHash = await hashPassword(dto.password);
    return userRepository.create({ ...dto, passwordHash });
  },
};
```
