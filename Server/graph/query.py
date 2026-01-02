from cProfile import label
from platform import node
from neo4j import GraphDatabase
from typing import List, Dict, Optional
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

class QueryEngine:
    def __init__(self, uri=uri, user=user, password=password):
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

    def get_nodes(self, type: str = "", filters: Dict = None) -> List[Dict]:
        """
        Retrieve nodes by type with optional property filters
        """
        filters = filters or {}

        where_clause = " AND ".join([f"n.{k} = ${k}" for k in filters])

        if type == "":
            query = f"""
            MATCH (n) 
            {"WHERE " + where_clause if where_clause else ""}
            RETURN properties(n) as props
            """
        else:
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
    
    def get_owned_by_team(self, node_id : str, filters: str = None) -> Optional[Dict]:
        # finding services, db, caches that are owned by a team with id
        label_segment = f":{filters}" if filters else ""

        query = f"""
            MATCH (n {{id: $id}})-[:OWNS]-(t{label_segment})
            RETURN properties(t) as props
            """
        with self.driver.session() as session:
            result = session.run(
                query,
                id=node_id,
            )

            if not result:
                return None;
            
            return [{
                "id" : record["props"]["id"],
                "type" : "team",
                "properties" : record["props"]
            } for record in result
            ] 
    # ---------------- Traversals ----------------

    def downstream(self, node_id: str, filters: str = None) -> List[Dict]:
        """
        All transitive dependencies (what this node depends on)
        """
        
        label_segment = f":{filters}" if filters else ""
        
        query =f"""
        MATCH (start {{id: $id}})-[]->(n{label_segment})
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

    def upstream(self, node_id: str, filters : str = None) -> List[Dict]:
        """
        All transitive dependents (what breaks if this node fails)
        """
        label_segment = f":{filters}" if filters else ""
            
        query = f"""
        MATCH (n{label_segment})-[]->(target {{id: $id}})
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

    def blast_radius(self, node_id: str, filters: str = None) -> Dict:
        """
        Full impact analysis: upstream, downstream, and owning teams
        """
        downstream_nodes = self.downstream(node_id, filters)
        upstream_nodes = self.upstream(node_id, filters)

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
