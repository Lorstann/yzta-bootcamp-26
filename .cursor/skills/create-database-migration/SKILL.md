---
name: create-database-migration
description: Authors Drizzle/Postgres migrations using snake_case identifiers, indexes on FKs and search columns, created_at/updated_at/deleted_at timestamps, and an explicit rollback. Use when the user asks to create a migration, add a table, or alter schema.
---

# create-database-migration

**Trigger**: "create a migration", "add a table", "alter schema"

**Rules**:
- ALWAYS include a `down` function (rollback).
- Include indexes for foreign keys and search columns.
- Use `snake_case` for all DB identifiers.
- Add `created_at`, `updated_at` to every table.
- Add `deleted_at` for any table holding user-generated content (soft delete).

**Template (Drizzle)**:
```typescript
import { pgTable, uuid, varchar, timestamp, index } from 'drizzle-orm/pg-core';

export const users = pgTable(
  'users',
  {
    id: uuid('id').defaultRandom().primaryKey(),
    email: varchar('email', { length: 255 }).notNull().unique(),
    passwordHash: varchar('password_hash', { length: 255 }).notNull(),
    role: varchar('role', { length: 50 }).notNull().default('user'),
    deletedAt: timestamp('deleted_at'),
    createdAt: timestamp('created_at').defaultNow().notNull(),
    updatedAt: timestamp('updated_at').defaultNow().notNull(),
  },
  (table) => ({
    emailIdx: index('users_email_idx').on(table.email),
  })
);
```
