#!/usr/bin/env python3
"""
Rick & Morty API client — Phase 1 exercise skeleton.

Complete the TODOs, then run:
  python phases/1b-exercise-rmapi/rm_client_skeleton.py
"""
#!/usr/bin/env python3
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import requests
from pydantic import BaseModel

BASE_URL = "https://rickandmortyapi.com/api"
DEFAULT_TIMEOUT = 5.0

class APIError(Exception): pass

def content_type_base(resp: requests.Response) -> str:
    raw = resp.headers.get("Content-Type", "")
    return raw.split(";", 1)[0].strip().lower()

def is_json_response(resp: requests.Response) -> bool:
    base = content_type_base(resp)
    return base.endswith("/json") or base.endswith("+json")

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

class RmClient:
    def __init__(self, base_url: str = BASE_URL, timeout_s: float = DEFAULT_TIMEOUT):
        # TODO: trim trailing '/', init Session, set User-Agent, store timeout
        raise NotImplementedError

    def _url(self, path: str) -> str:
        # TODO: join base + lstrip('/') path
        raise NotImplementedError

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        # TODO: request with timeout; on >=400 build JSON/text-aware msg and raise APIError
        raise NotImplementedError

    def list_characters(self, page: int = 1, name: Optional[str] = None) -> CharacterPage:
        # TODO: call /character with params; return CharacterPage(**r.json())
        raise NotImplementedError

    def get_character(self, id_or_name: Union[int, str]) -> Dict[str, Any]:
        # TODO: if numeric -> /character/<id>, else search by name and pick first
        # return {"id": ..., "name": ..., "status": ..., "species": ...}
        raise NotImplementedError

if __name__ == "__main__":
    c = RmClient()
    p2 = c.list_characters(page=2)
    print("count:", p2.info.count, "pages:", p2.info.pages, "has_next:", bool(p2.info.next))
    print("first 5:", [x.name for x in p2.results[:5]])
    print(c.get_character(1))
    print(c.get_character("birdperson"))

