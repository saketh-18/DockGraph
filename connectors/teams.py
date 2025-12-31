import yaml
from base import Connector


class TeamsConnector(Connector):
    def __init__(self, path="./data/teams.yaml"):
        self.path = path

    def parse(self):
        with open(self.path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        teams = doc.get("teams", [])
        nodes = []
        edges = []

        for t in teams:
            name = t.get("name")
            if not name:
                continue  # skip invalid entries

            safe_name = name.strip().lower().replace(" ", "-")

            node = {
                "id": f"team:{safe_name}",
                "type": "team",
                "name": name,  # human-readable
                "properties": {
                    "lead": t.get("lead"),
                    "slack": t.get("slack_channel"),
                    "pagerduty": t.get("pagerduty_schedule"),
                },
            }
            nodes.append(node)

            for owned in t.get("owns", []):
                owned_lc = owned.lower()

                if owned_lc.endswith("-db"):
                    target = f"database:{owned}"
                elif owned_lc.endswith("-cache") or "redis" in owned_lc:
                    target = f"cache:{owned}"
                else:
                    target = f"service:{owned}"

                edges.append({
                    "id": f"edge:{safe_name}-owns-{owned}",
                    "type": "owns",
                    "source": f"team:{safe_name}",
                    "target": target,
                    "properties": {},
                })

        return nodes, edges
