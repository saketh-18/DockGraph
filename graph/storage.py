from neo4j import GraphDatabase
from typing import Dict, List


class GraphStorage:
    # start a connection
    def __init__(self, uri="neo4j://127.0.0.1:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        # self._ensure_indexes()

    # closing connection
    def close(self):
        self.driver.close()

    # Create index for fast lookup by id
    # def _ensure_indexes(self):
    #     with self.driver.session() as session:
    #         session.run(
    #             "CREATE CONSTRAINT IF NOT EXISTS "
    #             "ON (n) ASSERT n.id IS UNIQUE"
    #         )

    # ---------------- Nodes ----------------
    
    # update node | create if not there 
    def upsert_node(self, node: Dict):
        label = node["type"]
        props = node.get("properties", {}).copy()
        props["id"] = node["id"]
        props["name"] = node.get("name")

        with self.driver.session() as session:
            session.run(
                f"""
                MERGE (n:{label} {{id: $id}})
                SET n += $props
                """,
                id=node["id"],
                props=props,
            )

    # get node
    def get_node(self, node_id: str) -> Dict | None:
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

    # get node based on type
    def get_nodes_by_type(self, node_type: str) -> List[Dict]:
        with self.driver.session() as session:
            result = session.run(
                f"""
                MATCH (n:{node_type})
                RETURN properties(n) AS props
                """
            )

            return [
                {
                    "id": record["props"]["id"],
                    "type": node_type,
                    "properties": record["props"],
                }
                for record in result
            ]

    # delete node
    def delete_node(self, node_id: str):
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n {id: $id})
                DETACH DELETE n
                """,
                id=node_id,
            )

    # ---------------- Edges ----------------

    # update edge
    def upsert_edge(self, edge: Dict):
        rel_type = edge["type"].upper()

        with self.driver.session() as session:
            session.run(
                f"""
                MATCH (a {{id: $source}})
                MATCH (b {{id: $target}})
                MERGE (a)-[r:{rel_type} {{id: $id}}]->(b)
                """,
                id=edge["id"],
                source=edge["source"],
                target=edge["target"],
            )
