# Security & Compliance Guardrails

**Goal:** Realistic demos that are *safe by default* for personal and corporate laptops.

## Defaults
- All labs run locally via Docker: **LocalStack**, **Redis**, **httpbin**.
- **No public resources** are created by default.
- **No real credentials** required for local mode.

## Optional AWS Mode (off by default)
- S3 buckets created with `BlockPublicAcls`, `BlockPublicPolicy`, `RestrictPublicBuckets` all **true**.
- API Gateway endpoints are **Private** (access via VPC Links only).
- IAM is least-privilege; never commit keys. Use environment variables via `.env`.
- CloudWatch logs redact sensitive values.

## Source Control
- `.env` and secrets are ignored by `.gitignore`.
- Use pre-commit hooks (`detect-secrets`) if you choose.
- Do **not** publish internal screenshots, tickets, or customer data.

## Responsible Use
- This is a personal educational project; examples are generic.
- Review templates before enabling AWS mode.
