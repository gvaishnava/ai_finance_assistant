"""
Conversation state definition for LangGraph
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from dataclasses import dataclass, field
import operator

class ConversationState(TypedDict):
    """State schema for the conversation workflow"""
    
    # Current query and response
    query: str
    response: str
    
    # Agent routing
    selected_agent: Optional[str]
    agent_responses: Annotated[List[Dict], operator.add]  # Accumulate agent responses
    
    # Conversation history
    messages: Annotated[List[Dict], operator.add]  # Chat history
    
    # User context
    user_profile: Optional[Dict]
    session_id: Optional[str]
    
    # Additional context
    portfolio: Optional[Dict]
    goals: Optional[List[Dict]]
    
    # Workflow control
    requires_followup: bool
    iteration_count: int

def create_initial_state(
    query: str,
    session_id: str = None,
    user_profile: Dict = None,
    portfolio: Dict = None,
    goals: List[Dict] = None
) -> ConversationState:
    """
    Create initial conversation state
    
    Args:
        query: User query
        session_id: Session ID
        user_profile: User profile dictionary
        portfolio: Portfolio data
        goals: Financial goals
        
    Returns:
        Initial ConversationState
    """
    return ConversationState(
        query=query,
        response="",
        selected_agent=None,
        agent_responses=[],
        messages=[],
        user_profile=user_profile or {},
        session_id=session_id,
        portfolio=portfolio,
        goals=goals,
        requires_followup=False,
        iteration_count=0
    )
