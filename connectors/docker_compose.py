import yaml
import re
from base import Connector


class DockerComposeConnector(Connector):
    def __init__(self, path="./data/docker-compose.yml"):
        self.path = path

    # Extract service names referenced in env URLs
    def _parse_env_refs(self, env_list):
        refs = set()

        for e in env_list or []:
            if not isinstance(e, str):
                continue

            # http(s)://service-name
            m = re.search(r"https?://([a-zA-Z0-9\-]+)", e)
            if m:
                refs.add(m.group(1))

            # redis://service-name
            m = re.search(r"redis://([a-zA-Z0-9\-]+)", e)
            if m:
                refs.add(m.group(1))

            # postgres://user@service-name:5432/db
            m = re.search(r"@([a-zA-Z0-9\-]+):\d+", e)
            if m:
                refs.add(m.group(1))

        return refs

    # Infer node type from minimal, obvious signals
    def _infer_node_type(self, name, cfg):
        labels = cfg.get("labels", {}) or {}
        image = cfg.get("image", "") or ""

        if labels.get("type") == "database" or name.endswith("-db"):
            return "database"

        if labels.get("type") == "cache" or "redis" in image:
            return "cache"

        return "service"

    # Infer edge type based on target role
    def _infer_edge_type(self, target_type):
        if target_type == "database":
            return "reads_writes"
        if target_type == "cache":
            return "uses"
        return "calls"

    def parse(self):
        with open(self.path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f)

        services = doc.get("services", {})
        nodes = []
        edges = []

        # Build nodes first
        node_index = {}

        for name, cfg in services.items():
            ntype = self._infer_node_type(name, cfg)

            properties = {}

            # Extract exposed port (best-effort)
            ports = cfg.get("ports", [])
            if ports:
                p = ports[0]
                if isinstance(p, str) and ":" in p:
                    try:
                        properties["port"] = int(p.split(":")[0])
                    except Exception:
                        pass

            # Carry labels as metadata
            properties.update(cfg.get("labels", {}) or {})

            node = {
                "id": f"{ntype}:{name}",
                "type": ntype,
                "name": name,
                "properties": properties,
            }

            nodes.append(node)
            node_index[name] = node

        # Build edges only from real runtime references
        for name, cfg in services.items():
            source_id = f"service:{name}"

            env_refs = self._parse_env_refs(cfg.get("environment", []))

            for ref in env_refs:
                target_node = node_index.get(ref)
                if not target_node:
                    continue  # ignore unknown externals

                edge_type = self._infer_edge_type(target_node["type"])

                edge = {
                    "id": f"edge:{name}-{edge_type}-{ref}",
                    "type": edge_type,
                    "source": source_id,
                    "target": target_node["id"],
                    "properties": {},
                }

                edges.append(edge)

        return nodes, edges

