---
name: setup-logger
description: Configures a structured Pino logger with pino-pretty in development, redaction of sensitive paths (authorization headers, password, token, passwordHash), and the standard req/res/err serializers. Use when the user asks to set up logging, add Pino, or configure a logger.
---

# setup-logger

**Trigger**: "setup logging", "add pino", "configure logger"

**Template**:
```typescript
import pino from 'pino';
import { config } from '@/config';

export const logger = pino({
  level: config.log.level,
  ...(config.isProduction
    ? {}
    : {
        transport: {
          target: 'pino-pretty',
          options: { colorize: true, translateTime: 'HH:MM:ss', ignore: 'pid,hostname' },
        },
      }),
  redact: {
    paths: ['req.headers.authorization', 'body.password', 'body.token', '*.passwordHash'],
    censor: '[REDACTED]',
  },
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },
});
```
