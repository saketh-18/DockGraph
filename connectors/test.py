import docker_compose
import pprint
import teams

pp = pprint.PrettyPrinter(indent=4)

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