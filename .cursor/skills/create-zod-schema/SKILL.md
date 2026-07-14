---
name: create-zod-schema
description: Authors shared Zod schemas in /domain/schemas/ using .strict() objects, user-readable error messages in English, and an exported inferred TypeScript DTO. Use when the user asks to create a schema, validate input, or add validation.
---

# create-zod-schema

**Trigger**: "create a schema", "validate input", "add validation"

**Rules**:
- Define once in `/domain/schemas/` — reuse on frontend and backend.
- Export both the schema and the inferred TypeScript type.
- Use `.strict()` on object schemas to reject unknown fields.
- Custom error messages in English, user-readable.

**Template**:
```typescript
import { z } from 'zod';

export const createUserSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
    .regex(/[0-9]/, 'Must contain at least one number'),
  name: z.string().min(2, 'Name must be at least 2 characters').max(100),
}).strict();

export type CreateUserDto = z.infer<typeof createUserSchema>;
```
