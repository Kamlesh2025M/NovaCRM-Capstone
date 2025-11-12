"""
State Definition for NovaCRM Assistant LangGraph

Defines the typed state structure used throughout the graph
"""

from typing import List, Optional, Literal
from typing_extensions import TypedDict

class AssistantState(TypedDict):
    """
    State for NovaCRM Assistant conversation flow
    
    Attributes:
        history: List of conversation summaries (rolling history)
        intent: Classified intent (FAQ, DataLookup, Escalation)
        query: Current user query
        answer: Final synthesized answer
        evidence: List of evidence items (doc IDs, file rows, tool payloads)
        errors: List of error messages encountered
        account_context: Account ID for scoping queries (optional)
    """
    history: List[str]
    intent: Optional[Literal["FAQ", "DataLookup", "Escalation"]]
    query: str
    answer: Optional[str]
    evidence: List[str]
    errors: List[str]
    account_context: Optional[str]

