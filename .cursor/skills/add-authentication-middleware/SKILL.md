---
name: add-authentication-middleware
description: Adds Express JWT authentication middleware with Bearer token parsing, role-based authorization via requireRole, and a typed Request.user property. Use when the user asks to protect a route, add auth, or require login.
---

# add-authentication-middleware

**Trigger**: "protect a route", "add auth", "require login"

**Template**:
```typescript
import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { UnauthorizedError } from '@/domain/errors';
import { config } from '@/config';
import { logger } from '@/utils/logger';

interface JwtPayload {
  sub: string;
  email: string;
  role: string;
}

declare global {
  namespace Express {
    interface Request {
      user?: JwtPayload;
    }
  }
}

export const authenticate = (req: Request, _res: Response, next: NextFunction) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return next(new UnauthorizedError('Missing token'));
  }

  const token = authHeader.slice(7);
  try {
    req.user = jwt.verify(token, config.jwt.accessSecret) as JwtPayload;
    next();
  } catch (err) {
    logger.warn({ err }, 'Invalid token');
    next(new UnauthorizedError('Invalid or expired token'));
  }
};

export const requireRole = (role: string) => (req: Request, _res: Response, next: NextFunction) => {
  if (req.user?.role !== role) {
    return next(new UnauthorizedError('Insufficient permissions'));
  }
  next();
};
```
