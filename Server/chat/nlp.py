from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent
from graph.query import QueryEngine, create_tools
from .cache import Cache, get_cache_tools
import pprint
import json
from .output_schema import LLMOutput
from langchain_core.messages import AIMessage, HumanMessage


class NLP():
    def __init__(self):
        self.qe = QueryEngine()
        self.cache = Cache()
        self.history = [];
        MAX_TURNS = 6
        self.history = self.history[-MAX_TURNS*2:]
        
    def llm_agent(self, query : str):
        # takes input from user
        # create a chain which makes use of tools present in tool kit
        self.history.append(HumanMessage(content=query))
        system_prompt = """
You are a backend engineer executing graph queries based on user requests.

CRITICAL: Always pass node_id as a SIMPLE STRING, not an object or dict.

Node ID Format: <type>:<name>
Valid types: service, database, cache, team
Examples: 
- service:payment-service
- database:payments-db
- cache:redis-main
- team:payments-team

KEY RULES:
1. When calling tools, pass node_id as a plain string (e.g., "service:payment-service")
2. NEVER wrap parameters in curly braces or as JSON objects
3. Infer the correct node type from the user's request
4. Fix any typos in node names to match valid graph nodes
5. For filters parameter, pass only the type string: 'service', 'database', 'cache', or None

Tool-specific guidance:
- get_owner(node_id): Pass a service/database/cache node to find its owner team
- get_owned_by_team(node_id, filters): Pass a team node to find nodes it owns
- downstream(node_id, filters): Pass any node to find its dependencies
- upstream(node_id, filters): Pass any node to find what depends on it
- path(from_id, to_id): Pass two node IDs to find the shortest path
- blast_radius(node_id, filters): Pass any node for complete impact analysis
        """


        tools = create_tools(self.qe)
        cache_tools = get_cache_tools(self.cache)
        model = ChatGroq(model="openai/gpt-oss-120b")
        groq_agent = create_agent(
            model=model,
            tools=tools + cache_tools,
            system_prompt=system_prompt,
        )
        
        if query:
            result = groq_agent.invoke({
            "messages": self.history
            })
            
            final_ai = next(
            msg for msg in reversed(result["messages"])
            if isinstance(msg, AIMessage)
            )
            
            pp = pprint.PrettyPrinter(indent=4);
            # pp.pprint(result);
            # pp.pprint(final_ai.content);
            self.history.append(final_ai)
            
            # Structure the response using an LLM agent
            parser_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a response formatter. Convert the AI assistant's response into a structured JSON format.

RULES FOR DETERMINING 'type':

1. "list" - Use when:
   - Listing node/team names (ownership, dependencies, search results)
   - Response has 1+ extractable node/team names
   - Examples: "downstream dependencies", "who owns X", "nodes owned by team", "all services"

2. "path" - Use when:
   - Showing a route/path between two nodes
   - Response contains ordered sequence like "A -> B -> C"
   - Tool called: path()

3. "blast_radius" - Use when:
   - Complete impact analysis with upstream AND downstream
   - Response has separate sections for upstream/downstream/teams
   - Tool called: blast_radius()

4. "node_detail" - Use when:
   - Showing details/properties of a SINGLE node
   - Response describes one node's attributes/characteristics
   - Tool called: get_node() or asking "what is X" or "details about X"

5. "table" - Use when:
   - Showing properties/details of MULTIPLE nodes
   - Response lists several nodes with their attributes
   - Tool called: get_nodes()

6. "text" - Use when:
   - Yes/no answers, confirmations, existence checks
   - Explanations with NO extractable node names
   - General statements or acknowledgments

7. "error" - Use when:
   - Query failed or no results found
   - Error messages or unable to process

RULES FOR 'message':
- Provide clear, human-readable summary
- Include context (e.g., "Owner of payment-service", "Downstream dependencies of api-gateway")
- For errors: explain what went wrong

RULES FOR 'data':

FOR "list":
- Extract node/team names as array: ["payment-service", "users-db"]
- Remove prefixes (service:, database:, team:, cache:)
- Single item → still use array: ["payments-team"]

FOR "path":
- Ordered array of node names: ["api-gateway", "auth-service", "users-db"]
- Preserve order from start to end
- Remove prefixes

FOR "blast_radius":
- Dict with keys: "upstream", "downstream", "teams"
- Each value is array or null: {{"upstream": ["api-gateway"], "downstream": ["payments-db"], "teams": ["payments-team"]}}
- Remove prefixes from names

FOR "node_detail":
- Dict with node properties: {{"name": "payment-service", "type": "service", "description": "...", ...}}
- Include all relevant properties mentioned
- Clean format

FOR "table":
- Array of dicts, each with node properties: [{{"name": "svc1", "type": "service"}}, {{"name": "db1", "type": "database"}}]
- Consistent property keys across all items

FOR "text":
- Set data to null

FOR "error":
- Set data to null

EXAMPLES:
- "payments-team owns this" → type="list", data=["payments-team"]
- "Downstream: api-gateway, auth-service" → type="list", data=["api-gateway", "auth-service"]
- "Path: A->B->C" → type="path", data=["A", "B", "C"]
- "payment-service is a REST API..." → type="node_detail", data={{"name": "payment-service", "description": "REST API..."}}
- "Node exists: Yes" → type="text", data=null
- "Blast radius: upstream=[X], downstream=[Y], teams=[Z]" → type="blast_radius", data={{"upstream":["X"], "downstream":["Y"], "teams":["Z"]}}

ALWAYS remove type prefixes (service:, database:, team:, cache:) from node names."""),
                ("user", "Format this response into structured data:\n{content}")
            ])
            
            parser_llm = ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(LLMOutput)
            parser_chain = parser_prompt | parser_llm
            
            
            structured_result = parser_chain.invoke({
                "content": final_ai.content
            })
            
            
            print(structured_result)
            return structured_result
        return {
            "data" : "enter a valid query"
        }