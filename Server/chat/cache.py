import pprint
from langchain.tools import tool

class Cache():
    def __init__(self):
        self.cached = {}
        # for every intent : {
        #    entity_type : query_result 
        # }
    
    def get_cached_query(self, intent: str):
        # check cached if the intent is already present in the cached object
        if self.cached.get(intent.get("intent", ""), ""):
            intent = self.cached.get(intent.get("intent"));
            entity = f"{intent.get("entity_type")}:{intent.get("entity_name")}"
            if intent.get(entity):
                print("used cached value..")
                pp = pprint.PrettyPrinter(indent=4)
                pp.pprint(intent.get(entity));
                # ex : intent -> get owner, entity : payment-service => store [entity name]
                return intent.get(entity);
        else:
            print("no cache")
            return None

    def add_to_cache(self, intent: str, query_result: list[str]):
        action = intent.get("intent");
        entity = f"{intent.get("entity_type")}:{intent.get("entity_name")}"
        self.cached[action] = {}
        self.cached[action][entity] = query_result
        print("cached")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(query_result);


def get_cache_tools(cache: Cache):
    
    @tool
    def get_cached_query(intent: dict):
        """
        check cache before calling database
        valid intents : get_owner, get_owned, blast_radius, upstream, downstream, list_nodes
        Retrieve a cached query result for a given intent and entity.
        
        Args:
            intent (dict): Dictionary containing 'intent', 'entity_type', and 'entity_name' keys
                          Example: {'intent': 'get_owner', 'entity_type': 'service', 'entity_name': 'payment-service'}
        
        Returns:
            Query result if found in cache, None otherwise
        """
        print("fRom Cacheeeeee")
        return cache.get_cached_query(intent)
    
    @tool
    def add_to_cache(intent: dict, query_result: list):
        """
        after Every query add the query result to cache
        valid intents : get_owner, get_owned, blast_radius, upstream, downstream, list_nodes
        Add a query result to the cache for a given intent and entity.
        
        Args:
            intent (dict): Dictionary containing 'intent', 'entity_type', and 'entity_name' keys
                          Example: {'intent': 'get_owner', 'entity_type': 'service', 'entity_name': 'payment-service'}
            query_result (list): The query result to cache
        
        Returns:
            None. The result is stored in the internal cache and printed to console
        """
        return cache.add_to_cache(intent, query_result)
    
    return [
        get_cached_query,
        add_to_cache,
    ]
