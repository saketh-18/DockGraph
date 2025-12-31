from graph.storage import GraphStorage
from connectors.docker_compose import DockerComposeConnector
from connectors.teams import TeamsConnector


def load_graph():
    storage = GraphStorage(password="password")

    connectors = [
        DockerComposeConnector(path="./data/docker-compose.yml"),
        TeamsConnector(path="./data/teams.yaml"),
    ]

    for connector in connectors:
        nodes, edges = connector.parse()

        # Store nodes first
        for node in nodes:
            storage.upsert_node(node)

        # Then store edges
        for edge in edges:
            storage.upsert_edge(edge)

    storage.close()


if __name__ == "__main__":
    load_graph()
