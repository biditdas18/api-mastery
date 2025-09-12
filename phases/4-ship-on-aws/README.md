# Phase 4 — Shipping on AWS (Safely)

**Principles**
- FastAPI app for business logic (optional demo).
- API Gateway used as **Private API** (no public endpoints); access via VPC Link / PrivateLink.
- S3 buckets are **private with BlockPublicAccess** fully enabled.
- IaC templates target LocalStack first; gating env var required to use real AWS.

**Getting started (LocalStack)**
```bash
# With compose running:
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
awslocal s3 mb s3://api-mastery-demo
awslocal s3 ls
```

**Enabling AWS mode (optional)**
- Set `USE_AWS=true` in `.env`.
- Provide credentials via your standard AWS profile/SSO (non-production accounts).
- Review templates before apply; confirm no public resources are created.
