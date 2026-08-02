# Equa AWS demo infrastructure (CDK)

Cost-conscious **demo** deploy for Equa in `us-east-1` (or your `CDK_DEFAULT_REGION`).

## Architecture

| Stack | Resources |
|-------|-----------|
| `EquaNetwork` | VPC, 1 NAT, public + private subnets |
| `EquaData` | Aurora PostgreSQL Serverless v2, S3 uploads, Secrets |
| `EquaApi` | ECS Fargate (0.5 vCPU / 1 GB) + ALB |
| `EquaFrontend` | S3 + CloudFront (SPA; `/api/*` → ALB) |

CloudFront is the public URL so the PWA and API share HTTPS origin (no custom domain required).

## Prerequisites

1. AWS CLI configured (`aws sts get-caller-identity` works)
2. Node.js 20+, Docker (for API image build during `cdk deploy`)
3. CDK bootstrap once per account/region:

```bash
cd infra
npx cdk bootstrap aws://ACCOUNT/us-east-1
```

## Deploy

```bash
cd infra
npm ci
npx cdk deploy --all --require-approval never
```

After deploy, set the LLM key (from `EquaData` outputs `LlmApiKeySecretArn`):

```bash
aws secretsmanager put-secret-value \
  --secret-id <LlmApiKeySecretArn> \
  --secret-string 'YOUR_GEMINI_OR_OPENAI_KEY'

# Force new task to pick up (optional if secret was REPLACE_ME at first boot)
aws ecs update-service --cluster <cluster> --service <service> --force-new-deployment
```

Open the `CloudFrontUrl` output from `EquaFrontend`.

## Enable pgvector (once)

Connect to Aurora (bastion / ECS exec / Query Editor) and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Alembic migrations also assume pgvector when curriculum/RAG tables are used.

## Tear down

```bash
cd infra
npx cdk destroy --all
```

Stops most demo charges (NAT + Aurora + ALB are the big line items).

## Notes

- Demo defaults: destroyable data, single NAT, no custom domain / ACM.
- Frontend build sets `VITE_API_BASE_URL=` (relative) and `VITE_USE_MOCK=false`.
- ALB idle timeout is 300s for chat streaming; CloudFront origin read timeout is 60s (raise if needed for long SSE).
