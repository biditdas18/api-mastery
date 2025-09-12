

---

# Phase 1 — From curl to a Clean Python Client (PokéAPI)

> *This is my personal journey to master APIs for ML L5 readiness. In Phase 0 we “scavenger-hunted” an unknown API with curl. Here, we turn that discovery into a small, confident Python client—line by line, no magic.*

---

## ✅ Competencies Covered / In Progress

* 🔑 Headers & request setup (polite `User-Agent`, query params, timeouts).
* 🧱 HTTP client hygiene with `requests.Session` (connection pooling).
* 📦 Response handling that respects **Content-Type** (JSON vs text errors).
* 📑 Pagination via **limit + offset** (as observed in Phase 0).
* 🧪 Run-it-yourself examples with expected outputs.

## 📚 Assumed Knowledge

* You can run Python and `pip install` packages.
* You did (or skimmed) Phase 0’s curl exploration.
* No AWS required yet.

---

## 1) Quick setup

```bash
# From your repo root (venv optional)
pip install requests pydantic

# Sanity check: API reachable
curl -I https://pokeapi.co/api/v2/
```

---

## 2) Curl labs (hands-on, zero magic)

> We’ll rehearse the exact behaviors our Python client relies on—**with curl**. Every command is copy-pasteable, shows expected output (shape, not exact values), and explains what each flag/line does.

### 2.1 Base reachability & headers

```bash
# -sS = silent but show errors
# -D - = dump response headers to stdout
# -o /dev/null = discard the body (we only want headers here)
curl -sS -D - -o /dev/null https://pokeapi.co/api/v2/
```

**You’ll see (shape):**

```
HTTP/2 200
content-type: application/json; charset=utf-8
...
```

Why: Confirm protocol, status, and content type before parsing anything.

---

### 2.2 Root map (discover entry points)

```bash
# Pretty-print just the first few keys (omit `| jq ...` if you don’t have jq)
curl -sS https://pokeapi.co/api/v2/ | jq 'to_entries | map(.key) | .[0:6]'
```

**Expected (shape):**

```json
["ability","berry","pokemon", "..."]
```

Why: Let the API tell you its **top-level resources** (no docs needed).

---

### 2.3 List endpoint + pagination hint

```bash
curl -sS https://pokeapi.co/api/v2/pokemon \
  | jq '{count, next, previous, first_names: [ .results[0:5][] | .name ]}'
```

**Expected (shape):**

```json
{
  "count": 1281,
  "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
  "previous": null,
  "first_names": ["bulbasaur","ivysaur","venusaur","charmander","charmeleon"]
}
```

Why: The **`next`** link reveals the **pagination contract**: `offset` + `limit`.

---

### 2.4 Follow the API-suggested `next` page

```bash
curl -sS "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20" \
  | jq '{offset_20_limit_20_first: [ .results[0:5][] | .name ]}'
```

**Expected (shape):**

```json
{ "offset_20_limit_20_first": ["spearow","fearow","ekans","arbok","pikachu"] }
```

Why: Proves the server honors the suggested `next` pagination.

---

### 2.5 Experiment with your own page size & start

```bash
curl -sS "https://pokeapi.co/api/v2/pokemon?offset=10&limit=5" \
  | jq '{offset_10_limit_5_first: [ .results[0:5][] | .name ]}'
```

**Expected (shape):**

```json
{ "offset_10_limit_5_first": ["metapod","butterfree","weedle","kakuna","beedrill"] }
```

Lesson: You (the client) control these knobs; they’re not fixed.

---

### 2.6 Drill into an entity (detail endpoint)

```bash
curl -sS https://pokeapi.co/api/v2/pokemon/ditto \
  | jq '{name, id, height, weight, abilities: [ .abilities[].ability.name ]}'
```

**Expected (shape):**

```json
{
  "name": "ditto",
  "id": 132,
  "height": 3,
  "weight": 40,
  "abilities": ["limber","imposter"]
}
```

Why: This is the **resource detail** our Python client will fetch.

---

### 2.7 Error behavior (don’t assume JSON)

```bash
# -i = include headers
# -w prints code/content-type at end
curl -sS -i https://pokeapi.co/api/v2/pokemon/notapokemon \
  -w "\nHTTP_CODE:%{http_code}\nCONTENT_TYPE:%{content_type}\n"
```

**Actual behavior (shape):**

```
HTTP/2 404
content-type: text/plain; charset=utf-8
...
Not Found
HTTP_CODE:404
CONTENT_TYPE:text/plain; charset=utf-8
```

Lesson: `Content-Type` is **text/plain** here. Don’t `resp.json()` blindly.

---

### 2.8 Gentle burst (illustration only)

```bash
# Fire 5 quick requests; print only statuses
seq 1 5 | xargs -I{} -n1 curl -s -o /dev/null -w "%{http_code}\n" \
  https://pokeapi.co/api/v2/pokemon/ditto
```

**Likely output:**

```
200
200
200
200
200
```

Why: Real production APIs often return **429** with `Retry-After`. We’ll design for that in later phases.

---

## 3) Build the client (conversational + line-by-line)

> Create `phases/1-first-client/phase1_client.py`. The snippets below explain the “why”. (Full file linked at the end.)

### 3.1 Imports & constants

```python
import requests
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

BASE_URL = "https://pokeapi.co/api/v2"
DEFAULT_TIMEOUT = 5.0
```

* `requests` = HTTP workhorse.
* `pydantic` = light schema validation so our code fails early if shape changes.
* `DEFAULT_TIMEOUT` keeps us from hanging forever.

### 3.2 Error type and a tiny helper

```python
class APIError(Exception):
    """Our single error type for clarity."""

def is_json_response(resp: requests.Response) -> bool:
    ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
    return ctype == "application/json"
```

* One app-level exception keeps error handling focused.
* **Key habit**: check `Content-Type` before calling `resp.json()`.

### 3.3 Minimal models we actually use

```python
class PokemonListItem(BaseModel):
    name: str
    url: str

class PokemonList(BaseModel):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[PokemonListItem]
```

* Model only what you need for the current task; add more later.

### 3.4 Client skeleton with a polite session

```python
class PokeClient:
    def __init__(self, base_url: str = BASE_URL, timeout_s: float = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "api-mastery/phase1"})
        self.timeout_s = timeout_s

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"
```

* `Session` → connection pooling, fewer TCP handshakes.
* `User-Agent` → be a good citizen; helps API owners debug/identify load.

### 3.5 Central request wrapper (where robustness lives)

```python
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
```

* We **don’t** call `raise_for_status()`—we craft clearer errors with URL + status + best-effort body.
* If not JSON (like PokéAPI 404), we return the text (e.g., `"Not Found"`).

### 3.6 Public methods (list + detail)

```python
    def list_pokemon(self, limit: int = 20, offset: int = 0) -> PokemonList:
        r = self._request("GET", "pokemon", params={"limit": limit, "offset": offset})
        return PokemonList(**r.json())

    def get_pokemon(self, name_or_id: str) -> Dict[str, Any]:
        r = self._request("GET", f"pokemon/{name_or_id}")
        data = r.json()
        return {
            "name": data.get("name"),
            "id": data.get("id"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "abilities": [a["ability"]["name"] for a in data.get("abilities", [])],
        }
```

* Mirrors what we did with curl: list a page; fetch an entity by id/name.
* Return a compact dict for readability now; we can model it richer later.

### 3.7 A tiny main to prove it works

```python
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
```

---

## 4) Run it

```bash
python phases/1-first-client/phase1_client.py
```

### Expected output (shape should match)

```
Listing 5 Pokémon starting at offset 10...
count: 1281
first 5 names: ['metapod', 'butterfree', 'weedle', 'kakuna', 'beedrill']

Fetching 'ditto' details...
{'name': 'ditto', 'id': 132, 'height': 3, 'weight': 40, 'abilities': ['limber', 'imposter']}

Provoking an error (should be graceful):
Caught APIError as expected: HTTP 404 on https://pokeapi.co/api/v2/pokemon/notapokemon: {'error': 'Not Found'}
```

(Names in that first page can differ based on `offset`; the pattern is what matters.)

---

## 5) Why this is ML-L5-grade

* You **encoded the observed contract** (pagination style, error bodies) into the client.
* You respected **Content-Type** and didn’t assume JSON for errors.
* You built a **clear error surface** with status + URL + helpful message.
* You kept the code **boringly simple**—the right starting point for production hardening.

**Next (Phase 2):** retries with jitter, idempotency, structured errors, and basic observability—turning a clean client into a production-grade one.

---

