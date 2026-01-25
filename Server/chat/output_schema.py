from typing import Union, Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field


class LLMOutput(BaseModel):
    """
    Structured output from the LLM agent.
    - type: The kind of response being returned
    - message: A human-readable summary or title
    - data: Optional structured data appropriate to the type
    """
    type: Literal["text", "list", "path", "blast_radius", "node_detail", "table", "error"] = Field(
        description="""Response type:
        - text: Simple text responses, confirmations, boolean results
        - list: List of node/team names (ownership, dependencies, search results)
        - path: Ordered sequence showing route between nodes
        - blast_radius: Impact analysis with upstream/downstream/teams
        - node_detail: Single node with detailed properties
        - table: Multiple nodes with their properties
        - error: Error messages"""
    )
    message: str = Field(
        description="A human-readable summary or explanation of the result"
    )
    data: Optional[Union[
        List[str], 
        Dict[str, Optional[List[str]]], 
        Dict[str, Any],
        List[Dict[str, Any]]
    ]] = Field(
        default=None,
        description="""Structured data based on type:
        - text: null
        - list: array of node/team names ["node1", "node2"]
        - path: ordered array of node names ["start", "middle", "end"]
        - blast_radius: dict with upstream/downstream/teams arrays
        - node_detail: dict with node properties {"name": "...", "type": "...", ...}
        - table: array of node property dicts [{"name": "...", "type": "..."}, ...]
        - error: null"""
    )
