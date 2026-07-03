---
name: setup-rate-limiting
description: Configures express-rate-limit backed by a Redis store with a global limiter and a stricter auth limiter that skips successful requests, plus structured logging on limit breaches. Use when the user asks to add rate limiting, throttling, or DDoS protection.
---

# setup-rate-limiting

**Trigger**: "rate limit", "throttle", "DDoS protection"

**Template**:
```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redisClient } from '@/infrastructure/cache/redis';
import { logger } from '@/utils/logger';

export const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
  handler: (req, res) => {
    logger.warn({ ip: req.ip }, 'Rate limit exceeded');
    res.status(429).json({
      success: false,
      error: { code: 'RATE_LIMIT', message: 'Too many requests, please try again later.' },
    });
  },
});

export const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  store: new RedisStore({ sendCommand: (...args) => redisClient.sendCommand(args) }),
});
```
