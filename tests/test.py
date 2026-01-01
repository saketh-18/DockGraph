# import docker_compose
import connectors.docker_compose as docker_compose
import pprint
# import teams
import connectors.teams as teams

pp = pprint.PrettyPrinter(indent=4)

import yaml

# obj = teams.TeamsConnector();
# (nodes, edges) = obj.parse();
# pp.pprint(nodes)
# print("edges -> ")
# pp.pprint(edges)

obj = docker_compose.DockerComposeConnector();
(nodes, edges) = obj.parse();
pp.pprint(nodes);
print("edges -> ")
pp.pprint(edges);

# with open("./data/teams.yaml", "r") as f:
#     data = yaml.safe_load(f);
    
# entities = [];
# for key in data.get("teams", {}):
#     entities.append(key.get("name"));

# pp.pprint(entities);