**TL;DR** → Here’s a hands-on **Phase-1 exercise** using a *new* public API (Rick & Morty API). You’ll do a curl scavenger hunt, then fill in a **client skeleton** (requests + pydantic, timeouts, pagination, content-type aware errors). I included **expected output shapes** and a tiny **pytest** to self-check.

**Why** → You learn fastest by shipping. This mirrors everything from Phase 1—but on a different surface—so you cement headers, pagination, and error handling. It also gives your readers a clean exercise to add to the repo.

**Next steps**

1. Create a folder `phases/1b-exercise-rmapi/`.
2. Copy the **README** (below) and the **skeleton code** into that folder.
3. Run the curl labs, then complete the TODOs in the skeleton until the **pytest** passes.

---

# phases/1b-exercise-rmapi/README.md

# Phase 1 Exercise — Rick & Morty API (new surface, same skills)

> Goal: reproduce Phase-1 skills on a brand-new API: **discover → paginate → detail → error → code a small client** (requests + pydantic, timeouts, content-type aware parsing).

---

### ✅ Competencies Covered / In Progress

* 🧭 Surface mapping with curl (root discovery).
* 📑 Pagination (this API uses `?page=`).
* 🔎 Query filters (e.g., `?name=rick`).
* 🧱 Clean Python client with `requests.Session`, timeouts, `User-Agent`.
* 📦 Pydantic models for just-what-we-use validation.
* 🚦 Content-Type aware error handling (JSON vs text).
* 🧪 Self-check with pytest.

### 📚 Assumed Knowledge

* Terminal, Python, `pip install`.
* Phase 0/1 concepts (you did the PokéAPI work).

---

## 0) Quick setup

```bash
pip install requests pydantic pytest
```

---

## 1) Curl Scavenger Hunt

> API root: `https://rickandmortyapi.com/api/`

### 1.1 Root map

```bash
curl -sS https://rickandmortyapi.com/api/ | jq .
```

**Expected (shape):**

```json
{
  "characters": "https://rickandmortyapi.com/api/character",
  "locations": "https://rickandmortyapi.com/api/location",
  "episodes": "https://rickandmortyapi.com/api/episode"
}
```

### 1.2 List endpoint (pagination hint)

```bash
curl -sS https://rickandmortyapi.com/api/character | jq '{info, sample_names: [ .results[0:5][] | .name ]}'
```

**Expected (shape):**

```json
{
  "info": { "count": 826, "pages": 42, "next": "https://.../character?page=2", "prev": null },
  "sample_names": ["Rick Sanchez","Morty Smith","Summer Smith","Beth Smith","Jerry Smith"]
}
```

**Notice:** `info.next` reveals **`?page=`** pagination.

### 1.3 Follow the next page

```bash
curl -sS "https://rickandmortyapi.com/api/character?page=2" \
  | jq '{page2_first3: [ .results[0:3][] | .name ]}'
```

**Expected (shape):**

```json
{ "page2_first3": ["Aqua Morty", "Aqua Rick", "Arcade Alien"] }
```

### 1.4 Filter by query

```bash
curl -sS "https://rickandmortyapi.com/api/character?name=rick" \
  | jq '{count: .info.count, first5: [ .results[0:5][] | .name ]}'
```

**Expected (shape):**

```json
{ "count": 50, "first5": ["Rick Sanchez", "Aqua Rick", "Black & White Rick", " Cowboy Rick", "Colonial Rick"] }
```

### 1.5 Detail endpoint

```bash
curl -sS https://rickandmortyapi.com/api/character/1 \
  | jq '{id, name, status, species, origin: .origin.name}'
```

**Expected (shape):**

```json
{ "id": 1, "name": "Rick Sanchez", "status": "Alive", "species": "Human", "origin": "Earth (C-137)" }
```

### 1.6 Error behavior (don’t assume)

```bash
curl -sS -i https://rickandmortyapi.com/api/character/999999 \
  -w "\nHTTP_CODE:%{http_code}\nCONTENT_TYPE:%{content_type}\n"
```

**Expected (shape):**

```
HTTP/2 404
content-type: application/json; charset=utf-8
...
{"error":"There is nothing here"}
HTTP_CODE:404
CONTENT_TYPE:application/json; charset=utf-8
```

**Lesson:** Here, errors are JSON. Still **check Content-Type**—don’t assume.

### 1.7 Gentle burst (illustration)

```bash
seq 1 5 | xargs -I{} -n1 curl -s -o /dev/null -w "%{http_code}\n" \
  https://rickandmortyapi.com/api/character/1
```

**Likely output:** five `200`s. In real prod, expect `429` with `Retry-After`.

---

## 2) Your task: build a tiny RM client (skeleton provided)

Implement the TODOs in `rm_client_skeleton.py`:

* `RmClient` with `Session`, `User-Agent`, and `DEFAULT_TIMEOUT=5.0`.
* `list_characters(page=1, name=None)` → returns a typed `CharacterPage`.
* `get_character(id_or_name)`:

  * If numeric, fetch `/character/<id>`.
  * If string, call `/character?name=<str>` and return the first match’s summary.
* Content-Type aware error handling (like Phase 1).
* Minimal pydantic models: `CharacterListItem`, `Info`, `CharacterPage`.

Then: run the demo and the tests.

---

## 3) Expected outputs (shape)

**Demo run:**

```
== List page: page=2 ==
count: 826 pages: 42 has_next: True
first 5: ['Aqua Morty', 'Aqua Rick', 'Arcade Alien', 'Armagheadon', 'Armothy']

== Detail (id=1) ==
{'id': 1, 'name': 'Rick Sanchez', 'status': 'Alive', 'species': 'Human'}

== Search by name ('birdperson') ->
{'id': 47, 'name': 'Birdperson', 'status': 'Dead or Alive', 'species': 'Bird-Person'}

== Error probe ==
Caught APIError: HTTP 404 on https://rickandmortyapi.com/api/character/999999: {'error': 'There is nothing here'}
```

---

## 4) Self-check with pytest

```bash
pytest -q phases/1b-exercise-rmapi/test_rm_client.py
```

**All tests should pass** when you’re done.

---

## 5) Add to repo (optional)

* Put this folder under `phases/` and mention it at the end of Phase 1 as a bonus exercise for readers.

---

# phases/1b-exercise-rmapi/rm\_client\_skeleton.py

```python
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
```

---

# phases/1b-exercise-rmapi/test\_rm\_client.py

```python
import re
from phases._util_import import safe_import  # small helper below
from pathlib import Path

# Ensure import works whether repo root or exercise folder
RmClient = safe_import("phases/1b-exercise-rmapi/rm_client_skeleton.py", "RmClient")

def test_list_page_basic():
    c = RmClient()
    p = c.list_characters(page=1)
    assert p.info.count > 0
    assert len(p.results) > 0
    assert isinstance(p.results[0].name, str)

def test_detail_by_id():
    c = RmClient()
    d = c.get_character(1)
    assert d["id"] == 1
    assert "name" in d and isinstance(d["name"], str)

def test_search_by_name():
    c = RmClient()
    d = c.get_character("rick")
    assert "Rick" in d["name"]

def test_error_shape():
    c = RmClient()
    try:
        c.get_character(999999)
    except Exception as e:
        # should be our APIError with status and message
        s = str(e)
        assert "HTTP 404" in s and "There is nothing here" in s
    else:
        raise AssertionError("Expected an error for non-existent id")
```

---

# phases/\_util\_import.py  (helper so tests can import the exercise file)

```python
# Drop this in phases/_util_import.py so tests can import from a path easily.
import importlib.util
import sys
from pathlib import Path

def safe_import(relative_path: str, symbol: str):
    p = Path(relative_path)
    if not p.exists():
        # Try from repo root
        p = Path.cwd() / relative_path
    spec = importlib.util.spec_from_file_location("tmp_mod", p)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tmp_mod"] = mod
    spec.loader.exec_module(mod)  # type: ignore
    return getattr(mod, symbol)
```

---

## How to run

```bash
# Demo
python phases/1b-exercise-rmapi/rm_client_skeleton.py

# Tests
pytest -q phases/1b-exercise-rmapi/test_rm_client.py
```

---


