from graph.query import QueryEngine

qe = QueryEngine(password="password")

print(qe.get_node("service:api-gateway"))
print(qe.get_nodes("database"))
print(qe.downstream("service:api-gateway"))
print(qe.upstream("database:orders-db"))
print(qe.path("service:api-gateway", "database:orders-db"))
print(qe.blast_radius("database:orders-db"))

qe.close()
