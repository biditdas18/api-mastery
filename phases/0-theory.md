# Phase 0 — Theory (Cheat Sheet)
- Auth: API key, OAuth2 (client credentials, auth code), SigV4.
- Pagination: cursor vs page/limit; backpressure; consistency.
- Error Taxonomy: caller vs server vs transient; retryability matrix.
- Idempotency: keys, safe verbs, de-dup windows.
- Caching: in-proc LRU vs Redis TTL; cache stampede protection.
- Rate Limits: token bucket, leaky bucket; client- vs server-enforced.
- Resilience: retries (exp+jitter), circuit breaker, timeouts.
- Observability: structure logs; metrics (p95 latency, error rate); traces.
- Security: no public infra by default; least-privilege IAM; secret hygiene.
