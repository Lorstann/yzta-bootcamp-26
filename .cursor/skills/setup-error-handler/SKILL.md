---
name: setup-error-handler
description: Sets up a global Express error-handling middleware that maps ZodError to 422, AppError to its statusCode, and unknown errors to 500, all wrapped in the standard { success false, error { code, message, details } } envelope. Use when the user asks for a global error handler, error middleware, or to set up errors.
---

# setup-error-handler

**Trigger**: "global error handler", "error middleware", "setup errors"

**Template**:
```typescript
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { AppError, ValidationError } from '@/domain/errors';
import { logger } from '@/utils/logger';

export const errorHandler = (
  err: unknown,
  req: Request,
  res: Response,
  _next: NextFunction
) => {
  // Zod validation errors
  if (err instanceof ZodError) {
    return res.status(422).json({
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid input',
        details: err.errors.map((e) => ({ field: e.path.join('.'), message: e.message })),
      },
    });
  }

  // Known application errors
  if (err instanceof AppError) {
    logger.warn({ err, path: req.path }, err.message);
    return res.status(err.statusCode).json({
      success: false,
      error: { code: err.code, message: err.message },
    });
  }

  // Unknown errors — don't leak internals
  logger.error({ err, path: req.path, method: req.method }, 'Unhandled error');
  res.status(500).json({
    success: false,
    error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' },
  });
};
```
