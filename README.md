# Engineering Knowledge Graph (EKG) Prototype

Mini prototype that ingests YAML configs (docker-compose, teams, optional k8s), builds a graph, and provides a CLI chat interface to query ownership, dependencies, blast radius and paths.

See `docker-compose.yml` for single-command startup. Use `python -m chat.cli` for a local run.

Requirements: Python 3.10+

Quick start (local, without Docker):

1. python -m venv .venv
2. .venv\Scripts\activate (Windows) or source .venv/bin/activate
3. pip install -r requirements.txt
4. python -m chat.cli

Project layout:

- data/: provided input YAMLs
- connectors/: connectors that parse files into nodes/edges
- graph/: storage + query engine
- chat/: CLI natural-language interface

Design notes and README answers are included in this file bottom section.

---

## Design answers (brief)

1. Connector pluggability: connectors implement a small `Connector` interface in `connectors/base.py` and return lists of nodes/edges. To add a connector, add a file under `connectors/` and register it in `connectors/__init__.py` (no core changes required).

2. Graph updates: graph storage supports upsert behavior. On re-run, connectors upsert nodes/edges by `id`. To keep in sync, run connectors periodically or on file change; implement diff/GC to remove resources no longer present.

3. Cycle handling: traversals use BFS/DFS with a `visited` set to avoid revisiting nodes, preventing infinite loops.

4. Query mapping: the CLI implements a simple pattern matcher to map intents to graph queries. An LLM wrapper can be added for more flexible parsing, but rules ensure deterministic behavior.

5. Failure handling: on ambiguous or unanswerable queries the chat asks clarifying questions instead of guessing. It avoids hallucination by only using graph-derived facts.

6. Scale considerations: current file-backed storage and in-memory NetworkX graph will struggle beyond ~10k nodes. We would switch to a production graph DB (Neo4j) and add indexing, pagination, and async loading.

7. GraphDB choice: This prototype uses JSON + NetworkX for simplicity. For production, Neo4j is recommended for performance, Cypher queries, and visualization.

---

See `data/` for input YAMLs and `chat/` for usage examples.
