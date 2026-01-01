def format_response(intent: dict, result):
    if intent["intent"] == "get_owner":
        if not result:
            return "I couldn't find an owning team."
        return f"{result['properties']['name']} owns this."

    if intent["intent"] == "list_nodes":
        if not result:
            return "No results found."
        names = [r["properties"]["name"] for r in result]
        return "Found:\n- " + "\n- ".join(names)

    if intent["intent"] in ["downstream", "upstream"]:
        if not result:
            return "No dependencies found."
        names = [r["properties"]["name"] for r in result]
        return "Affected components:\n- " + "\n- ".join(names)

    if intent["intent"] == "blast_radius":
        return (
            "Blast radius:\n"
            f"Upstream: {[n['properties']['name'] for n in result['upstream']]}\n"
            f"Downstream: {[n['properties']['name'] for n in result['downstream']]}\n"
            f"Teams: {[t['properties']['name'] for t in result['teams']]}"
        )
    if intent["intent"] == "path":
        if not result:
            return f"No path found between {intent["path"]["from_name"]} and {intent["path"]["to_name"]}";
        path = [f"{r} -> " for r in result]
        return " ".join(path);
    
    if intent["intent"] == "get_owned_by_team":
        if not result:
            return "No nodes found"
        names = [r["properties"]["name"] for r in result]
        return "Found:\n- " + "\n- ".join(names)

    return "I'm not sure how to answer that."
