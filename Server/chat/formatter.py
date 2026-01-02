def format_response(intent: dict, result):
    intent_type = intent["intent"]

    if intent_type == "blast_radius":
        return {
            "type": "blast_radius",
            "message": "Blast radius analysis",
            "data": {
                "Upstream": [n["properties"]["name"] for n in result.get("upstream", [])],
                "Downstream": [n["properties"]["name"] for n in result.get("downstream", [])],
                "Teams": [t["properties"]["name"] for t in result.get("teams", [])],
            },
        }
        
    if intent_type == "path":
        path_nodes = []

        for r in result:
            # Neo4j Path object
            if hasattr(r, "nodes"):
                for node in r.nodes:
                    name = node._properties.get("name")
                    if name:
                        path_nodes.append(name)

            # Dict-style path
            elif isinstance(r, dict) and "nodes" in r:
                for node in r["nodes"]:
                    name = node.get("properties", {}).get("name")
                    if name:
                        path_nodes.append(name)

        return path_nodes

    if intent_type == "get_owner":
        return {
            "type": "text",
            "message": (
                f"{result['properties']['name']} owns this."
                if result else "No owner found."
            ),
        }

    if intent_type == "path":
        # print("path result from formatter")
        # print(result)
        # result is expected to be a list of node ids (strings) from QueryEngine.path
        return {
            "type": "path",
            "message": "Shortest path",
            "data": result,
        }

    return {
        "type": "list",
        "message": "Results found",
        "data": [r["properties"]["name"] for r in result] if result else [],
    }
