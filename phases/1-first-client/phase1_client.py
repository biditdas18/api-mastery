#!/usr/bin/env python3
"""
Phase 1 — Clean Python client for PokéAPI (line-by-line friendly)

Save as:
  phases/1-first-client/phase1_client.py

Run:
  python phases/1-first-client/phase1_client.py
"""
from __future__ import annotations

import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# ---- Constants ----
BASE_URL = "https://pokeapi.co/api/v2"
DEFAULT_TIMEOUT = 5.0


# ---- Errors & helpers ----
class APIError(Exception):
    """Generic error type for our API client."""


def is_json_response(resp: requests.Response) -> bool:
    """Return True if response looks like JSON based on Content-Type."""
    ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    return ctype == "application/json"


# ---- Minimal models ----
class PokemonListItem(BaseModel):
    name: str
    url: str


class PokemonList(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[PokemonListItem]


# ---- Client ----
class PokeClient:
    def __init__(self, base_url: str = BASE_URL, timeout_s: float = DEFAULT_TIMEOUT):
        # Store base, init a Session for connection pooling, set a nice UA, keep a timeout.
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "api-mastery/phase1"})
        self.timeout_s = timeout_s

    def _url(self, path: str) -> str:
        # Join base with path safely (avoid accidental double slashes).
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        # Centralized place to call requests and handle errors consistently.
        url = self._url(path)
        try:
            resp = self.s.request(method, url, timeout=self.timeout_s, **kwargs)
        except requests.RequestException as e:
            raise APIError(f"network error: {e}") from e

        # Explicit status handling so we can craft good error messages.
        if resp.status_code >= 400:
            if is_json_response(resp):
                try:
                    data = resp.json()
                    msg = data if isinstance(data, dict) else {"error": str(data)}
                except ValueError:
                    msg = {"error": "<invalid-json-body>"}
            else:
                # Plain text error (e.g., PokéAPI 404 returns 'Not Found')
                msg = {"error": (resp.text or "").strip()[:200] or "<empty-body>"}
            raise APIError(f"HTTP {resp.status_code} on {url}: {msg}")

        return resp

    # Public methods

    def list_pokemon(self, limit: int = 20, offset: int = 0) -> PokemonList:
        """Return a page of pokemon using offset+limit pagination."""
        r = self._request("GET", "pokemon", params={"limit": limit, "offset": offset})
        data = r.json()
        return PokemonList(**data)

    def get_pokemon(self, name_or_id: str) -> Dict[str, Any]:
        """Return a compact dict summary for a pokemon by name or id."""
        r = self._request("GET", f"pokemon/{name_or_id}")
        data = r.json()
        return {
            "name": data.get("name"),
            "id": data.get("id"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "abilities": [a["ability"]["name"] for a in data.get("abilities", [])],
        }


# ---- Demo ----
if __name__ == "__main__":
    client = PokeClient()

    print("Listing 5 Pokémon starting at offset 10...")
    page = client.list_pokemon(limit=5, offset=10)
    print("count:", page.count)
    print("first 5 names:", [x.name for x in page.results])

    print("\nFetching 'ditto' details...")
    d = client.get_pokemon("ditto")
    print(d)

    print("\nProvoking an error (should be graceful):")
    try:
        client.get_pokemon("notapokemon")
    except APIError as e:
        print("Caught APIError as expected:", e)

