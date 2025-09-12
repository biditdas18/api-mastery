
---

# 🗺 Phase 0 — The API Scavenger Hunt (Discovery in Action)

> *“This is my personal journey to master APIs as part of preparing for an ML L5 role at a MAANG-level company. Each phase builds both skill and intuition. By Phase 5, the goal is to meet the API expectations of an ML L5 engineer.”*

---

### ✅ Competencies Covered / In Progress

* 🧭 **Surface Mapping** — discovering undocumented endpoints from a base URL.
* 📦 **Resource Modeling** — learning how entities and sub-resources are exposed.
* 🚦 **Pagination, Rate Limits, Error Handling** — identifying how APIs constrain and communicate.
* 🛡 **Security & Cost Awareness** — safe probing practices, no public data misuse.
* 💡 **ML L5 Mindset** — approaching an API like a systems engineer, not just a consumer.

---

### 📚 Assumed Knowledge

* Terminal basics (`cd`, `curl`).
* Familiarity with JSON (key–value).
* No AWS experience required yet.

---

## 0.1 Dropped Into the Unknown

Imagine this: you’re given only this URL:

```
https://pokeapi.co/api/v2/
```

No docs, no instructions. An ML L5 engineer’s job is to **figure out what’s here**.

---

## 0.2 First Probe

```bash
curl -i https://pokeapi.co/api/v2/
```

Response (trimmed):

```json
{
  "ability": "https://pokeapi.co/api/v2/ability/",
  "berry": "https://pokeapi.co/api/v2/berry/",
  "pokemon": "https://pokeapi.co/api/v2/pokemon/"
}
```

👀 *Aha!* The API itself reveals a map of **root resources**.
We just learned:

* `/ability/` → abilities
* `/berry/` → berries
* `/pokemon/` → Pokémon

This is how you discover **entry points** in the absence of docs.

---

## 0.3 Resource Listing

```bash
curl -i https://pokeapi.co/api/v2/pokemon
```

Response:

```json
{
  "count": 1281,
  "next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20",
  "results": [
    { "name": "bulbasaur", "url": "https://pokeapi.co/api/v2/pokemon/1/" },
    { "name": "ivysaur", "url": "https://pokeapi.co/api/v2/pokemon/2/" },
    ...
  ]
}
```

Observations:

* We didn’t know `/pokemon` existed until the **root call told us**.
* The response includes **pagination hints** (`count`, `next`, `previous`).
* Each item links to its own **detail endpoint**.

---

## 0.4 Drilling Into an Entity

We follow one of the links:

```bash
curl https://pokeapi.co/api/v2/pokemon/ditto
```

Response (snippet):

```json
{
  "abilities": [
    { "ability": { "name": "limber", "url": "https://pokeapi.co/api/v2/ability/7/" } }
  ],
  "sprites": { "front_default": "https://..." },
  "moves": [...]
}
```

Now we see:

* **Entity detail schema** (abilities, moves, sprites).
* **Nested resources** (like `/ability/7/`).

This is how you organically **map the resource graph**.

---

## 0.5 Pagination — Discovering the Pattern

When we called `/pokemon` earlier, the JSON response included this field:

```json
"next": "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20"
```

👀 *Aha!* That tells us two things right away:

* This API uses **offset** and **limit** for pagination.
* The default page size is 20 (`limit=20`).

Now, an ML L5 engineer doesn’t stop there — they **test the pattern** to confirm it works as expected.

### Step 1 — Use the suggested `next` link

```bash
curl "https://pokeapi.co/api/v2/pokemon?offset=20&limit=20"
```

→ Returns the **second page**, 20 Pokémon starting from index 20.

### Step 2 — Experiment with custom values

```bash
curl "https://pokeapi.co/api/v2/pokemon?offset=10&limit=5"
```

→ Returns 5 Pokémon, starting at index 10.

📌 **Takeaway:**

* `offset` sets where the page starts.
* `limit` controls how many results per page.
* Both are **client-tunable knobs** — you’re not locked to the defaults.

This experiment is how you confirm the **pagination contract** and understand how much flexibility you have.

---

## 0.6 Error Handling

Let’s test how the API responds to something invalid:

```bash
curl -i https://pokeapi.co/api/v2/pokemon/notapokemon
```

Actual response:

```
HTTP/2 404 
content-type: text/plain; charset=utf-8
content-length: 9
...
Not Found
```

📌 **Observations:**

* The **status code** is `404`.
* The **Content-Type** is `text/plain` (not JSON).
* The body is just the string: `"Not Found"`.

⚠️ **ML L5 Lesson:**

* **Never assume error bodies are JSON.**
* Always inspect the `Content-Type` header.

  * If it’s `application/json`, you can safely parse and extract fields.
  * If it’s `text/plain`, treat it as opaque text and rely on the status code.
* Build clients that adapt to **different error contracts** gracefully.

This is what separates a robust service client from a brittle script.

---

## 0.7 Throttling & Bursts

PokéAPI doesn’t aggressively rate-limit, but real APIs do.
We can simulate burst calls:

```bash
seq 1 5 | xargs -I{} -n1 curl -s -o /dev/null -w "%{http_code}\n" \
  https://pokeapi.co/api/v2/pokemon/ditto
```

All return `200`.

📌 Lesson: *In production APIs, you’d expect `429 Too Many Requests` + `Retry-After` headers. Always design clients to handle that scenario.*

---

## 0.8 Reflection

From a single base URL, we now know:

* The **root map** of resources.
* Pagination style (`limit` + `offset`).
* Entity schema (`pokemon/ditto`).
* Error contract (plain-text 404s).
* The possibility of rate limiting.

This is the ML L5 mindset: **discover, document, and anticipate** — not just consume.

---

## 0.9 API Paradigms in Context

While PokéAPI is REST, let’s zoom out:

* **REST** → resources with predictable URIs. Great for CRUD.
* **GraphQL** → single endpoint, client defines query. Great when clients need flexible projections.
* **RPC (gRPC, JSON-RPC)** → procedure calls. Great for low-latency service-to-service comms.

📌 ML L5 skill: Choosing the right paradigm isn’t about hype — it’s about *matching access patterns with system evolution costs*.

---

## 0.10 Roadmap

* **Phase 0 (this doc)** → Discovery + mindset.
* **Phase 1** → Recreate this exploration in Python (typed client, schema validation, pagination).
* **Phase 2** → Production-grade client (retries, idempotency, structured errors).
* **Phase 3** → Resilience (caching, rate limiting, circuit breakers).
* **Phase 4** → AWS integration (SigV4 auth, API Gateway Private, Lambda/FastAPI).
* **Phase 5** → Shipping (IaC, observability, cost awareness, L5 readiness).

---

## 0.11 Thanks

🙏 Huge thanks to [PokéAPI](https://pokeapi.co/) for providing a free, public dataset that makes this journey hands-on and fun.

---

⚡ Next: In **Phase 1**, we’ll turn these curls into a **line-by-line Python client** with schema validation and pagination handling.

---
