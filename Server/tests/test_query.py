from graph.query import QueryEngine
import pprint

qe = QueryEngine()

pp = pprint.PrettyPrinter(indent=4);

# print(qe.get_node("service:api-gateway"))
# pp.pprint(qe.get_nodes("service"))
# pp.pprint(qe.downstream("service:api-gateway"));
# pp.pprint(qe.upstream("database:orders-db"))
# print(qe.path("service:api-gateway", "database:orders-db"))
# print(qe.blast_radius("database:orders-db"))
# pp.pprint(qe.get_owner("database:orders-db"));

# pp.pprint(qe.get_owned_by_team("team:orders-team"));

pp.pprint(qe.check_node_existence("service:payment-service"))
qe.close()
