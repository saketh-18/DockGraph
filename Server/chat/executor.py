from re import L
from typing import Dict
from graph.query import QueryEngine

class Executor:
    def __init__(self):
        self.qe = QueryEngine(password="password")
        
    def execute(self, intent: Dict):
        action = intent.get("intent")
        e_name = intent.get("entity_name")
        e_type = intent.get("entity_type")
        if intent.get("path"):
            f_type = intent.get("path", {}).get("from_type")
            f_name = intent.get("path", {}).get("from_name")
            t_name = intent.get("path", {}).get("to_name")
            t_type = intent.get("path", {}).get("to_type")
        filters = intent.get("filters")
        
        if action == "get_owner":
            return self.qe.get_owner(f"{e_type}:{e_name}")
        if action == "get_owned_by_team":
            return self.qe.get_owned_by_team(f"team:{e_name}", filters);
        if action == "list_nodes":
            return self.qe.get_nodes(e_type);
        if action == "downstream":
            return self.qe.downstream(f"{e_type}:{e_name}", filters)
        if action == "upstream":
            return self.qe.upstream(f"{e_type}:{e_name}", filters);
        if action == "blast_radius":
            return self.qe.blast_radius(f"{e_type}:{e_name}", filters);
        if action == "path":
            return self.qe.path(f"{f_type}:{f_name}", f"{t_type}:{t_name}")         