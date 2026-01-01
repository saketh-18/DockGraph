from graph.storage import GraphStorage

store = GraphStorage(password="password")

# 1. Insert nodes
store.upsert_node({
    "id": "service:api-gateway",
    "type": "service",
    "name": "api-gateway",
    "properties": {"team": "platform-team", "port": 8080}
})

store.upsert_node({
    "id": "service:order-service",
    "type": "service",
    "name": "order-service",
    "properties": {"team": "orders-team"}
})

store.upsert_node({
    "id": "database:orders-db",
    "type": "database",
    "name": "orders-db",
    "properties": {"team": "orders-team"}
})

# 2. Insert edges
store.upsert_edge({
    "id": "edge:api-gateway-calls-order-service",
    "type": "calls",
    "source": "service:api-gateway",
    "target": "service:order-service",
    "properties": {}
})

store.upsert_edge({
    "id": "edge:order-service-reads-orders-db",
    "type": "reads_from",
    "source": "service:order-service",
    "target": "database:orders-db",
    "properties": {}
})

# 3. Read back
print("Fetch api-gateway:")
print(store.get_node("service:api-gateway"))

print("\nAll services:")
print(store.get_nodes_by_type("service"))

# 4. Delete node
store.delete_node("service:order-service")
print("\nDeleted order-service")

store.close()
