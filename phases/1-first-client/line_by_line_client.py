"""
Phase 1 — Line-by-line API client using httpbin (local docker service)
Safe, local-only by default.
"""
from __future__ import annotations
import os
import time
from typing import Dict, Any, Optional, Tuple, List

import requests
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

load_dotenv()

HTTPBIN = os.getenv("HTTPBIN_URL", "http://localhost:8080")

class HeadersModel(BaseModel):
    # Minimal schema just to demonstrate validation
    Host: str = Field(..., description="Host header echoed by httpbin")

class HttpBinClient:
    def __init__(self, base_url: str, timeout_s: float = 5.0):
        # Use a session for connection pooling (perf)
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "api-mastery/phase1"})
        self.timeout_s = timeout_s

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def get_headers(self) -> HeadersModel:
        # Basic GET
        url = self._url("headers")
        resp = self.s.get(url, timeout=self.timeout_s)
        # Raise for non-2xx
        resp.raise_for_status()

        # httpbin returns {"headers": {...}}
        data = resp.json()
        try:
            model = HeadersModel(**data.get("headers", {}))
        except ValidationError as e:
            raise RuntimeError(f"Schema validation failed: {e}") from e
        return model

    def get_paginated_things(self, page: int = 1, per_page: int = 3) -> Dict[str, Any]:
        # Emulate pagination locally via httpbin's delay and params
        # (In real APIs, you would receive 'next' cursors or total counts)
        url = self._url("get")
        params = {"page": page, "per_page": per_page}
        resp = self.s.get(url, params=params, timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()

if __name__ == "__main__":
    client = HttpBinClient(HTTPBIN, timeout_s=5)
    print("Fetching headers...")
    headers = client.get_headers()
    print("Validated Host header:", headers.Host)

    print("Fetching a 'paginated' page...")
    page = client.get_paginated_things(page=2, per_page=5)
    print("Example payload:", page)
