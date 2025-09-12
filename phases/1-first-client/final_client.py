"""
Phase 1 — Final client with small improvements:
- typed response models
- basic error handling wrapper
- timeouts + simple retry on connect timeouts (non-exponential for simplicity here)
"""
from __future__ import annotations
import os, time
from typing import Dict, Any, Optional
import requests
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()
HTTPBIN = os.getenv("HTTPBIN_URL", "http://localhost:8080")

class HeadersModel(BaseModel):
    Host: str = Field(...)

class APIError(Exception):
    pass

class HttpBinClient:
    def __init__(self, base_url: str, timeout_s: float = 5.0, max_retries:int = 2):
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "api-mastery/phase1-final"})
        self.timeout_s = timeout_s
        self.max_retries = max_retries

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        last_err = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.s.request(method, url, timeout=self.timeout_s, **kwargs)
                if resp.status_code >= 500:
                    # server error: bubble up (non-retry here for simplicity)
                    raise APIError(f"Server error {resp.status_code}: {resp.text[:200]}")
                resp.raise_for_status()
                return resp
            except (requests.ConnectionError, requests.Timeout) as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(0.2 * (attempt + 1))  # tiny backoff
                    continue
                raise APIError(f"Network error after retries: {e}") from e
            except requests.HTTPError as e:
                raise APIError(f"HTTP error: {e} | body={getattr(e.response,'text','')[:200]}") from e

        # Should not reach here
        raise APIError(f"Unreachable: {last_err}")

    def get_headers(self) -> HeadersModel:
        r = self._request("GET", "headers")
        data = r.json()
        return HeadersModel(**data.get("headers", {}))

if __name__ == "__main__":
    c = HttpBinClient(HTTPBIN)
    print("Host header:", c.get_headers().Host)
