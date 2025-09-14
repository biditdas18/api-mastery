#!/usr/bin/env python3
"""
Rick & Morty API client — Phase 1 exercise skeleton.

Complete the TODOs, then run:
  python phases/1b-exercise-rmapi/rm_client_skeleton.py
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import requests
from pydantic import BaseModel

BASE_URL = "https://rickandmortyapi.com/api"
DEFAULT_TIMEOUT = 5.0


# ---------- Errors & helpers ----------

class APIError(Exception):
    """Single error type for this client."""


def content_type_base(resp: requests.Response) -> str:
    raw = resp.headers.get("Content-Type", "")
    return raw.split(";", 1)[0].strip().lower()


def is_json_response(resp: requests.Response) -> bool:
    base = content_type_base(resp)
    # Treat application/json AND +json vendor types as JSON
    return base.endswith("/json") or base.endswith("+json")


# ---------- Models (just what we use) ----------

class CharacterListItem(BaseModel):
    id: int
    name: str
    status: Optional[str] = None
    species: Optional[str] = None


class Info(BaseModel):
    count: int
    pages: int
    next: Optional[str]
    prev: Optional[str]


class CharacterPage(BaseModel):
    info: Info
    results: List[CharacterListItem]


# ---------- Client ----------

class RmClient:
    def __init__(self, base_url: str = BASE_URL, timeout_s: float = DEFAULT_TIMEOUT):
        # TODO: store base_url without trailing '/', init Session, set User-Agent, store timeout
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "api-mastery/rm-exercise"})
        self.timeout_s = timeout_s

    def _url(self, path: str) -> str:
        # TODO: join base + lstrip('/') path
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = self._url(path)
        try:
            resp = self.s.request(method, url, timeout=self.timeout_s, **kwargs)
        except requests.RequestException as e:
            raise APIError(f"network error: {e}") from e

        if resp.status_code >= 400:
            # Respect Content-Type before parsing
            if is_json_response(resp):
                try:
                    data = resp.json()
                    msg = data if isinstance(data, dict) else {"error": str(data)}
                except ValueError:
                    msg = {"error": "<invalid-json-body>"}
            else:
                msg = {"error": (resp.text or "").strip()[:200] or "<empty-body>"}
            raise APIError(f"HTTP {resp.status_code} on {url}: {msg}")

        return resp

    # ---- Public API ----

    def list_characters(self, page: int = 1, name: Optional[str] = None) -> CharacterPage:
        """Return a page of characters. If 'name' provided, filter by name."""
        params: Dict[str, Any] = {"page": page}
        if name:
            params["name"] = name
        r = self._request("GET", "character", params=params)
        data = r.json()
        # TODO: return a CharacterPage model from 'data'
        return CharacterPage(**data)

    def get_character(self, id_or_name: Union[int, str]) -> Dict[str, Any]:
        """If int: fetch by id. If str: search by name (first match). Return a compact summary."""
        if isinstance(id_or_name, int) or (isinstance(id_or_name, str) and id_or_name.isdigit()):
            # by id
            r = self._request("GET", f"character/{int(id_or_name)}")
            data = r.json()
        else:
            # by name → use the list endpoint with ?name=
            page = self.list_characters(page=1, name=str(id_or_name))
            if not page.results:
                raise APIError(f"No character found for name={id_or_name!r}")
            # take the first match
            data = page.results[0].model_dump()

        # compact summary
        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "status": data.get("status"),
            "species": data.get("species"),
        }


# ---------- Demo ----------

if __name__ == "__main__":
    c = RmClient()

    print("== List page: page=2 ==")
    p2 = c.list_characters(page=2)
    print("count:", p2.info.count, "pages:", p2.info.pages, "has_next:", bool(p2.info.next))
    print("first 5:", [x.name for x in p2.results[:5]])

    print("\n== Detail (id=1) ==")
    print(c.get_character(1))

    print("\n== Search by name ('birdperson') ->")
    print(c.get_character("birdperson"))

    print("\n== Error probe ==")
    try:
        c.get_character(999999)
    except APIError as e:
        print("Caught APIError:", e)

