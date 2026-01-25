from platform import node
from neo4j import GraphDatabase
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv();



class QueryEngine:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")
        auth = (user, password)
        # print(uri, auth)
        self.driver = GraphDatabase.driver(uri=uri, auth=auth)
        with self.driver.session(database="neo4j") as session:
            session.run("RETURN 1")

    def close(self):
        self.driver.close()

    # ---------------- Basic Queries ----------------

    
    def check_node_existence(self, node_id:str) -> bool:
        with self.driver.session() as session:
            result = session.run(
                """
                RETURN EXISTS { (n {id: $id}) } AS nodeExists
                """,
                id=node_id
            ).single()
            
            return result["nodeExists"] if result else False
        
        
    def get_node(self, node_id: str) -> Optional[Dict]:
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
        Find all transitive dependencies - what nodes this one depends on.
        This shows everything downstream that this node requires to function.
        
        Args:
            node_id (str): The unique identifier in format 'type:name'
                          Example: 'service:payment-service'
            filters (str): Optional filter by node type: 'service', 'database', 'cache'
                          or None to get all downstream dependencies
        
        Returns:
            list: A list of all downstream nodes (dependencies) with their properties
                  Returns empty list if no dependencies found
        """
        
        label_segment = f":{filters}" if filters else ""
        
        query =f"""
        MATCH (start {{id: $id}})-[*..10]->(n{label_segment})
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
        label_segment = f":{filters}" if filters else ""
            
        query = f"""
        MATCH (n{label_segment})-[*..10]->(target {{id: $id}})
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
        downstream_nodes = self.downstream(node_id, filters)
        upstream_nodes = self.upstream(node_id, filters)

        affected_nodes = {
            n["id"]: n for n in downstream_nodes + upstream_nodes
        }

        affected_nodes[node_id] = self.get_node(node_id)

        affected_teams = {}

        for node in affected_nodes.values():
            owner = self.get_owner(node.get("id"))
            if owner:
                affected_teams[owner["id"]] = owner

        return {
            "node": node_id,
            "downstream": downstream_nodes,
            "upstream": upstream_nodes,
            "teams": list(affected_teams.values()),
        }

def create_tools(engine: QueryEngine):
    

    @tool
    def check_node_existence(node_id: str) -> bool:
        """
        Check if a node exists in the database.
        
        Args:
            node_id (str): The unique identifier of the node in format 'type:name' 
                          (e.g., 'service:payment-service', 'database:users-db')
        
        Returns:
            bool: True if the node exists, False otherwise
        """
        return engine.check_node_existence(node_id)

    @tool
    def get_node(node_id: str) -> Optional[Dict]:
        """
        Retrieve a single node and all its properties by its unique identifier.
        
        Args:
            node_id (str): The unique identifier in format 'type:name'
                          (e.g., 'service:payment-service', 'database:users-db')
        
        Returns:
            dict: Node with id, type, and properties. None if node doesn't exist
        """
        return engine.get_node(node_id)

    @tool
    def get_nodes(type: str = "", filters: Dict = None) -> List[Dict]:
        """
        Retrieve all nodes of a specific type with optional filters.
        
        Args:
            type (str): Node type - one of: 'service', 'database', 'cache', 'team', 
                       or '' for all nodes
            filters (dict): Optional property filters (e.g., {'name': 'payment-service'})
        
        Returns:
            list: Nodes matching the criteria with id, type, and properties
        """
        return engine.get_nodes(type, filters)

    @tool
    def get_owner(node_id: str) -> Optional[Dict]:
        """
        Find the team that owns a service, database, or cache node.
        
        Args:
            node_id (str): Node identifier in format 'type:name'
                          (e.g., 'service:payment-service', 'database:payments-db')
        
        Returns:
            dict: The owning team with id, type, and properties. None if not found
        """
        return engine.get_owner(node_id)

    @tool
    def get_owned_by_team(node_id: str, filters: Optional[str] = None) -> Optional[Dict]:
        """
        Get all nodes owned by a team. Optionally filter by node type.
        
        Args:
            node_id (str): Team identifier in format 'type:name' 
                          (e.g., 'team:payments-team')
            filters (str): Optional type filter - 'service', 'database', 'cache'
        
        Returns:
            list: Nodes owned by the team with id, type, and properties
        """
        return engine.get_owned_by_team(node_id, filters)

    @tool
    def downstream(node_id: str, filters: Optional[str] = None) -> List[Dict]:
        """
        Find all transitive dependencies - what this node depends on.
        Shows everything downstream required for this node to function.
        
        Args:
            node_id (str): Node identifier in format 'type:name'
                          (e.g., 'service:payment-service')
            filters (str): Optional filter by 'service', 'database', or 'cache'
        
        Returns:
            list: All downstream dependency nodes with id, type, and properties
        """
        return engine.downstream(node_id, filters)

    @tool
    def upstream(node_id: str, filters: Optional[str] = None) -> List[Dict]:
        """
        Find all transitive dependents - what nodes depend on this one.
        Shows what would break or be affected if this node fails.
        
        Args:
            node_id (str): Node identifier in format 'type:name'
                          (e.g., 'database:payments-db')
            filters (str): Optional filter by 'service', 'database', or 'cache'
        
        Returns:
            list: All upstream dependent nodes with id, type, and properties
        """
        return engine.upstream(node_id, filters)

    @tool
    def path(from_id: str, to_id: str) -> List[str]:
        """
        Find the shortest path between two nodes in the dependency graph.
        
        Args:
            from_id (str): Starting node in format 'type:name'
                          (e.g., 'service:order-service')
            to_id (str): Ending node in format 'type:name'
                        (e.g., 'database:orders-db')
        
        Returns:
            list: Node IDs representing the path. Empty list if no path exists
        """
        return engine.path(from_id, to_id)

    @tool
    def blast_radius(node_id: str, filters: Optional[str] = None) -> Dict:
        """
        Perform comprehensive impact analysis - shows all effects of a node failure.
        Reveals the complete blast radius including dependencies, dependents, and teams.
        
        Args:
            node_id (str): Node identifier in format 'type:name'
                          (e.g., 'database:payments-db')
            filters (str): Optional filter by 'service', 'database', or 'cache'
        
        Returns:
            dict: Impact analysis with 'node', 'downstream', 'upstream', 'teams' keys
        """
        return engine.blast_radius(node_id, filters)

    return [
        check_node_existence,
        get_node,
        get_nodes,
        get_owner,
        get_owned_by_team,
        downstream,
        upstream,
        path,
        blast_radius,
    ]
    
    
        
        