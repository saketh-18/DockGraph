# DockGraph — Engineering Knowledge Graph Prototype

## A. Setup & Usage

- **Start (Docker):** From the project root run:

```bash
docker-compose up --build
```

- **Start (local, Python backend + Next.js frontend):**

  - Backend (Windows / dev): create a venv, install `requirements.txt`, then run the CLI or API:

  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  pip install -r Server/requirements.txt
  # run CLI chat (graph built from data/):
  python -m chat.cli
  ```

  - Frontend (Next.js):

  ```bash
  cd frontend
  npm install
  npm run dev
  # open http://localhost:3000
  ```

- **Interacting with the chat interface:**

  - Web UI: open the frontend at `http://localhost:3000` and type natural-language questions into the chat input. The UI forwards queries to the backend query endpoint or runs the local intent mapping.
  - CLI: run `python -m chat.cli` for an interactive terminal chat that queries the graph.

- **Required environment variables:**
  - `OPENAI_API_KEY` — optional for LLM-assisted parsing or answer drafting.
  - `OPENAI_API_BASE` — optional if using a custom OpenAI-compatible endpoint.
  - Any other integrator-specific secrets (e.g., cloud credentials) are connector-specific and documented in the connector module that requires them.

## B. Architecture Overview

Diagram (data flow):

```
Config files (docker-compose.yml, teams.yaml, data/)
                   ↓
               Connectors
               (parse → nodes/edges)
                   ↓
                 Graph
           (storage + indices)
                   ↓
           Query Engine (upstream/downstream, path)
                   ↓
                Chat UI / CLI
         (natural language → mapped queries)
```

- **Key components:**
  - Connectors (`connectors/`): Parse YAML and other sources into canonical node/edge records.
  - Graph storage (`graph/`): In this prototype, a file-backed + in-memory graph (NetworkX/JSON). Stores nodes, edges, and metadata.
  - Query engine (`graph/query.py`): Implements `upstream()`, `downstream()`, path and ownership traversals with safeguards against cycles.
  - Chat (`chat/`, `Server/api/chat.py`, `frontend/`): Maps natural language to intents/queries, executes graph queries, and formats results for the UI.

## C. Design Questions (3–5 sentences each)

1. Connector pluggability: To add a new connector (for example, Terraform), implement the small `Connector` interface in `connectors/base.py` and create a new module `connectors/terraform.py` that parses Terraform state or HCL into the canonical node/edge shape. Register the connector in `connectors/__init__.py` or add it to the connector discovery routine so it is invoked during ingestion. Because connectors return plain node/edge records and the graph layer performs upserts, no core graph code changes are necessary. Tests and a small mapping example should accompany the connector so semantics are clear for other users.

2. Graph updates: The graph uses upsert semantics: connectors emit stable IDs and the graph storage upserts nodes and edges based on those IDs. To stay in sync with changing `docker-compose.yml` or other sources, run the ingestion on change (filesystem watcher, CI job, or periodic sync). Optionally compute a diff and perform garbage collection for nodes not emitted by any connector to remove stale resources. For higher confidence, apply transactional updates or version the graph snapshot so rollbacks are possible.

3. Cycle handling: Traversals (`upstream()`/`downstream()`) are implemented using breadth-first or depth-first search with a `visited` set; once a node is visited it is not enqueued again, which prevents infinite loops. Path-finding routines enforce maximum depth and optional hop limits as an extra safety. For analytics that must consider cycles (e.g., strongly-connected components), separate algorithms compute SCCs rather than naively traversing neighbors. Instrumentation logs traversal depth and early-terminates long-running queries to avoid runaway computation.

4. Query mapping: Natural language is mapped to graph queries in two stages: intent classification + slot extraction, then deterministic query construction. The prototype uses pattern matching and lightweight rules for common intents (ownership, blast radius, path) and an optional LLM step to translate complex phrasing into a structured query object. All LLM outputs are validated against the graph schema (allowed intents, node types, attributes) to ensure the system executes only safe, well-formed queries. This hybrid approach balances robustness (rules) with flexibility (LLM) while keeping the executed graph operations deterministic.

5. Failure handling: When the chat can't confidently answer, it returns a clarifying question or a provable partial answer rather than inventing facts — the system prefers admitting uncertainty. Answers are derived strictly from graph data and connector metadata; LLM-generated text is used only for formatting or paraphrasing and is anchored to returned graph facts. If a query requires external knowledge not present in the graph, the chat explains the missing data and suggests actions (e.g., run connector, add file, or grant permissions). Logging and user feedback loops capture failure modes so frequently missing facts can be automated into ingestion.

6. Scale considerations: With 10K nodes the in-memory file-backed graph and naive traversals would be the first bottlenecks — memory use and traversal latency would grow quickly. To scale, move storage to a graph database (Neo4j, JanusGraph, or Amazon Neptune), add indices for frequent lookup keys, and implement paged traversals and async query execution. Caching hot subgraphs and bounding traversal depth for UI queries will reduce load; also add background jobs for expensive analyses (e.g., full reachability) rather than doing them synchronously.

7. GraphDB choice: The prototype uses JSON + NetworkX for simplicity and fast iteration; for production you could pick Neo4j or an embedded graph store. If opting for something other than Neo4j (e.g., JanusGraph with Cassandra or Neptune), the reasons might include better horizontal scalability, cloud-managed operations, or tighter integration with existing datastore ecosystems. Each choice trades query language and tooling (Cypher vs Gremlin vs SPARQL), operational cost, and scaling characteristics — pick the one that aligns with your expected size, query patterns, and operational constraints.

## D. Tradeoffs & Limitations

- **Intentional simplifications:** The prototype favors simplicity over production readiness: connectors are synchronous, storage is file-backed/in-memory, and the UI is minimal. There is no RBAC, transactional ingestion, or persistent message queue for large-scale updates. LLM usage is limited and guarded — the system prioritizes graph-derived facts.
- **Weakest part:** The storage layer (file-backed + NetworkX) is the weakest link for scale and durability; it limits concurrency, query performance, and multi-user access. The natural-language-to-query mapping is intentionally simple and will need iterative refinement to handle diverse phrasing robustly.
- **With 20 more hours:** I would wire a pluggable connector test harness, add a filesystem watcher to auto-ingest on config change, and implement a lightweight Neo4j-backed option with a migration path from the prototype graph. I would also add end-to-end tests for common intents and a small instrumentation dashboard showing query latencies and graph size.

## E. AI Usage

- **Where AI helped most:** AI assisted with drafting natural-language paraphrases, suggested structure for README content, and helped design the intent-mapping approach. It was also used experimentally to prototype LLM-to-query translation snippets.
- **Where I corrected AI suggestions:** I constrained AI outputs to avoid hallucination, validated any proposed query against the schema, and rewrote portions that assumed production-grade features (transactions, scaling) that the prototype did not implement. I also corrected technical details to match the actual code layout and package names.
- **What I learned about AI-assisted development:** AI speeds up drafting and ideation, but human oversight is essential for correctness and safety — especially when the AI suggests code or architecture that doesn't match the implemented surface area. Keeping the AI-in-the-loop for formatting and suggestions while enforcing deterministic, validated execution paths gives the best balance.

---

If you want, I can: add a quick filesystem watcher to auto-reingest changed YAML files, or scaffold a Neo4j-backed storage adapter for scaled testing. Tell me which next step you'd prefer.
