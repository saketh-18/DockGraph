

# DockGraph — Engineering Knowledge Graph

DockGraph is an engineering knowledge graph prototype that turns infrastructure and config files into a graph you can query using natural language. The goal is simple: understand system ownership, dependencies, and blast radius without digging through YAMLs and repos manually.

---

## A. Setup & Usage

### Running the project

**Using Docker (recommended):**

```bash
docker-compose up --build
```

This starts the backend API, graph ingestion, and required services.

**Running locally (without Docker):**

Backend:

```bash
cd Server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m chat.cli
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:3000`.

---

### Deployed Version

* **Frontend:** [https://dock-graph.vercel.app/](https://dock-graph.vercel.app/)
* **Backend API:** [https://dockgraph.onrender.com](https://dockgraph.onrender.com)
* **Graph Database:** Neo4j Aura (cloud-hosted)

---

### How to use the chat interface

* Open the frontend and type natural language questions like:

  * “What services depend on redis?”
  * “Who owns the auth service?”
  * “What breaks if postgres goes down?”
* The chat maps your question to a graph query and returns results strictly from graph data.
* A CLI-based chat (`python -m chat.cli`) is also available for quick testing.

---

### Required Environment Variables

```env
GROQ_API_KEY=your_key_here  (used for intent parsing)
NEO4J_URI=neo4j+s://<aura-instance>
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

Connector-specific credentials (if any) are scoped to that connector only.

---

## B. Architecture Overview

### Data Flow

```
Config Files
(docker-compose.yml, yaml)
        ↓
     Connectors
(parse → nodes & edges)
        ↓
      Graph
 (Neo4j / local graph)
        ↓
   Query Engine
 (upstream, downstream,
  blast radius)
        ↓
      Chat Layer
 (NL → intent → query)
```

---

### Key Components

* **Connectors:** Parse config files and emit canonical nodes and edges.
* **Graph Layer:** Stores relationships in Neo4j (Aura) or local graph during development.
* **Query Engine:** Traverses the graph safely (blast radius, ownership, paths).
* **Chat Layer:** Converts natural language into structured graph queries and formats results.

---

## C. Design Questions

### 1. Connector pluggability

Adding a new connector (for example, Terraform) only requires implementing the base connector interface and emitting nodes/edges in the expected format. No core graph or query logic needs to change. Once registered, the ingestion pipeline automatically includes it. This keeps connectors isolated and easy to extend.

---

### 2. Graph updates

Graph updates use upsert semantics with stable IDs. When a config file changes, re-running ingestion updates existing nodes and relationships instead of duplicating them. Stale nodes can be cleaned up using diff-based or full re-ingestion strategies. This makes the graph eventually consistent with the source configs.

---

### 3. Cycle handling

All traversals maintain a `visited` set to prevent revisiting nodes. Traversals also enforce depth limits to avoid runaway queries. This ensures `upstream()` and `downstream()` never fall into infinite loops even with cyclic dependencies.

---

### 4. Query mapping

Natural language is first mapped to a high-level intent (ownership, dependency, blast radius). That intent is then translated into a deterministic graph query. AI is used only to help with intent extraction — not query execution. Every generated query is schema-validated before running.

---

### 5. Failure handling

If the system can’t confidently answer, it says so instead of guessing. Responses are always grounded in graph data, and missing information is explicitly called out. The chat may ask for clarification or suggest adding a connector. This avoids hallucination by design.

---

### 6. Scale considerations

The first thing to break at ~10K nodes would be traversal latency and memory pressure during complex queries. To scale, I’d rely more heavily on indexed graph queries, pagination, caching hot paths, and async execution. Heavy analytics would move to background jobs instead of live chat queries.

---

## D. Tradeoffs & Limitations

* **What I skipped:** RBAC, multi-tenant isolation, and real-time ingestion triggers were intentionally skipped to keep the scope focused.
* **Weakest part:** Natural-language intent mapping is still shallow and rule-heavy; it needs more real usage data to mature.
* **With 20 more hours:** I’d add automated file watchers for live graph updates, deeper intent confidence scoring, and performance instrumentation for large traversals.

---

## E. AI Usage

* **Where AI helped most:** Frontend UI generation and initial scaffolding.
* **Where I overrode AI:** The query layer. AI-generated traversal logic was often overcomplicated and sometimes incorrect, so I replaced it with deterministic, validated graph queries.
* **What I learned:** AI is powerful when used as an assistant, not a decision-maker. Over-relying on it creates more problems later. Human supervision at every step is non-negotiable if you care about correctness and maintainability.

---