from neo4j import GraphDatabase
from typing import List, Dict, Optional


class QueryEngine:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ---------------- Basic Queries ----------------

    def get_node(self, node_id: str) -> Optional[Dict]:
        """
        Retrieve a single node by ID
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n {id: $id})
                RETURN labels(n) AS labels, properties(n) AS props
                """,
                id=node_id,
            ).single()

            if not result:
                return None

            return {
                "id": result["props"]["id"],
                "type": result["labels"][0],
                "properties": result["props"],
            }

    def get_nodes(self, type: str, filters: Dict = None) -> List[Dict]:
        """
        Retrieve nodes by type with optional property filters
        """
        filters = filters or {}

        where_clause = " AND ".join([f"n.{k} = ${k}" for k in filters])

        query = f"""
        MATCH (n:{type})
        {"WHERE " + where_clause if where_clause else ""}
        RETURN properties(n) AS props
        """

        with self.driver.session() as session:
            result = session.run(query, **filters)

            return [
                {
                    "id": record["props"]["id"],
                    "type": type,
                    "properties": record["props"],
                }
                for record in result
            ]

    # ---------------- Ownership ----------------

    def get_owner(self, node_id: str) -> Optional[Dict]:
        """
        Find the team that owns a node
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (t:team)-[:OWNS]->(n {id: $id})
                RETURN properties(t) AS props
                """,
                id=node_id,
            ).single()

            if not result:
                return None

            return {
                "id": result["props"]["id"],
                "type": "team",
                "properties": result["props"],
            }

    # ---------------- Traversals ----------------

    def downstream(self, node_id: str, edge_types: List[str] = None) -> List[Dict]:
        """
        All transitive dependencies (what this node depends on)
        """
        rel_filter = (
            ":" + "|".join([e.upper() for e in edge_types])
            if edge_types else ""
        )

        query = f"""
        MATCH (start {{id: $id}})-[{rel_filter}*1..]->(n)
        RETURN DISTINCT properties(n) AS props, labels(n)[0] AS type
        """

        with self.driver.session() as session:
            result = session.run(query, id=node_id)

            return [
                {
                    "id": record["props"]["id"],
                    "type": record["type"],
                    "properties": record["props"],
                }
                for record in result
            ]

    def upstream(self, node_id: str, edge_types: List[str] = None) -> List[Dict]:
        """
        All transitive dependents (what breaks if this node fails)
        """
        rel_filter = (
            ":" + "|".join([e.upper() for e in edge_types])
            if edge_types else ""
        )

        query = f"""
        MATCH (n)-[{rel_filter}*1..]->(target {{id: $id}})
        RETURN DISTINCT properties(n) AS props, labels(n)[0] AS type
        """

        with self.driver.session() as session:
            result = session.run(query, id=node_id)

            return [
                {
                    "id": record["props"]["id"],
                    "type": record["type"],
                    "properties": record["props"],
                }
                for record in result
            ]

    # ---------------- Paths ----------------

    def path(self, from_id: str, to_id: str) -> List[str]:
        """
        Shortest path between two nodes (by ID)
        """
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (a {id: $startId}), (b {id: $endId})
                MATCH p = shortestPath((a)-[*]->(b))
                RETURN [n IN nodes(p) | n.id] AS path
                """,
                startId=from_id,
                endId=to_id,
            ).single()

            if not result:
                return []

            return result["path"]

    # ---------------- Impact Analysis ----------------

    def blast_radius(self, node_id: str) -> Dict:
        """
        Full impact analysis: upstream, downstream, and owning teams
        """
        downstream_nodes = self.downstream(node_id)
        upstream_nodes = self.upstream(node_id)

        affected_nodes = {
            n["id"]: n for n in downstream_nodes + upstream_nodes
        }

        affected_nodes[node_id] = self.get_node(node_id)

        affected_teams = {}

        for node in affected_nodes.values():
            owner = self.get_owner(node["id"])
            if owner:
                affected_teams[owner["id"]] = owner

        return {
            "node": node_id,
            "downstream": downstream_nodes,
            "upstream": upstream_nodes,
            "teams": list(affected_teams.values()),
        }
