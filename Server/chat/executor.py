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
        path_info = intent.get("path") or {}
        f_type = path_info.get("from_type") or None
        f_name = path_info.get("from_name") or None
        t_name = path_info.get("to_name") or None
        t_type = path_info.get("to_type") or None
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
            # Be defensive: if path parts are missing, try to derive from top-level entity
            if not (f_type and f_name):
                f_type = f_type or e_type
                f_name = f_name or e_name

            # If still missing required pieces, log and return empty path
            if not (f_type and f_name and t_type and t_name):
                print("[Executor] path intent missing fields:", intent)
                return []

            start_id = f"{f_type}:{f_name}"
            end_id = f"{t_type}:{t_name}"
            print(f"[Executor] path from {start_id} to {end_id}")
            return self.qe.path(start_id, end_id)