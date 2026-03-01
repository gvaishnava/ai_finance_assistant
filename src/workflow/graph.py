"""
LangGraph workflow definition for multi-agent orchestration
"""

import asyncio
from langgraph.graph import StateGraph, END
from typing import Dict

from src.workflow.state import ConversationState
from src.workflow.supervisor import SupervisorAgent
from src.agents import (
    FinanceQAAgent,
    PortfolioAgent,
    MarketAgent,
    GoalPlanningAgent,
    NewsSynthesizerAgent,
    TaxEducationAgent,
    TickerResolverAgent
)
from src.utils.logger import get_logger
from src.utils.tracing import traceable, atraceable

logger = get_logger(__name__)

# Initialize all agents (singleton pattern)
_agents_cache = {}

def get_agent(agent_name: str, config_path: str = "config.yaml"):
    """Get or create agent instance"""
    if agent_name not in _agents_cache:
        if agent_name == 'finance_qa':
            _agents_cache[agent_name] = FinanceQAAgent(config_path)
        elif agent_name == 'portfolio':
            _agents_cache[agent_name] = PortfolioAgent(config_path)
        elif agent_name == 'market':
            _agents_cache[agent_name] = MarketAgent(config_path)
        elif agent_name == 'goal_planning':
            _agents_cache[agent_name] = GoalPlanningAgent(config_path)
        elif agent_name == 'news':
            _agents_cache[agent_name] = NewsSynthesizerAgent(config_path)
        elif agent_name == 'tax':
            _agents_cache[agent_name] = TaxEducationAgent(config_path)
        elif agent_name == 'ticker_resolver':
            _agents_cache[agent_name] = TickerResolverAgent(config_path)
        else:
            raise ValueError(f"Unknown agent: {agent_name}")
    
    return _agents_cache[agent_name]

# Node functions for the graph

@traceable(name="workflow_route_node", tags=["workflow"])
def route_query_node(state: ConversationState) -> ConversationState:
    """Route the query to appropriate agent"""
    logger.info(f"Routing query: {state['query'][:50]}...")
    
    supervisor = SupervisorAgent()
    
    context = {
        'portfolio': state.get('portfolio'),
        'goals': state.get('goals'),
        'user_profile': state.get('user_profile'),
    }
    
    selected_agent = supervisor.route(state['query'], context)
    state['selected_agent'] = selected_agent
    
    logger.info(f"Selected agent: {selected_agent}")
    return state

@traceable(name="workflow_process_node", tags=["workflow"])
def process_with_agent_node(state: ConversationState) -> ConversationState:
    """Process query with the selected agent"""
    agent_name = state['selected_agent']
    logger.info(f"Processing with {agent_name}...")
    
    agent = get_agent(agent_name)
    
    # Prepare context
    context = {
        'user_profile': state.get('user_profile', {}),
        'portfolio': state.get('portfolio'),
        'goals': state.get('goals'),
        'session_id': state.get('session_id'),
    }
    
    # Process with agent
    result = agent.process(state['query'], context)
    
    # Update state
    state['response'] = result['response']
    state['agent_responses'] = [result]
    
    # Add message to history
    state['messages'] = [
        {'role': 'user', 'content': state['query']},
        {
            'role': 'assistant',
            'content': result['response'],
            'agent': agent_name,
            'metadata': result.get('metadata', {})
        }
    ]
    
    state['iteration_count'] = state.get('iteration_count', 0) + 1
    
    return state

def should_continue(state: ConversationState) -> str:
    """Determine if workflow should continue"""
    
    # For now, always end after one agent processes the query
    # In a more complex workflow, this could check for follow-up needs
    
    max_iterations = 10  # Safety limit
    
    if state.get('iteration_count', 0) >= max_iterations:
        logger.warning("Max iterations reached")
        return "end"
    
    if state.get('requires_followup', False):
        return "continue"
    
    return "end"

def create_workflow_graph(config_path: str = "config.yaml") -> StateGraph:
    """
    Create the LangGraph workflow
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Compiled StateGraph
    """
    # Create graph
    workflow = StateGraph(ConversationState)
    
    # Add nodes
    workflow.add_node("route", route_query_node)
    workflow.add_node("process", process_with_agent_node)
    
    # Define edges
    workflow.set_entry_point("route")
    workflow.add_edge("route", "process")
    
    # Conditional edge based on whether to continue
    workflow.add_conditional_edges(
        "process",
        should_continue,
        {
            "continue": "route",  # Loop back for follow-up
            "end": END
        }
    )
    
    # Compile and return
    return workflow.compile()

def run_workflow(
    query: str,
    session_id: str = None,
    user_profile: Dict = None,
    portfolio: Dict = None,
    goals: list = None,
    config_path: str = "config.yaml"
) -> Dict:
    """
    Run the workflow for a query
    
    Args:
        query: User query
        session_id: Session ID
        user_profile: User profile dictionary
        portfolio: Portfolio data
        goals: Financial goals
        config_path: Path to configuration
        
    Returns:
        Final state with response
    """
    from src.workflow.state import create_initial_state
    
    # Create initial state
    initial_state = create_initial_state(
        query=query,
        session_id=session_id,
        user_profile=user_profile,
        portfolio=portfolio,
        goals=goals
    )
    
    # Create and run workflow
    graph = create_workflow_graph(config_path)
    
    logger.info(f"Running workflow for query: {query[:50]}...")
    
    try:
        final_state = graph.invoke(initial_state)
        logger.info("Workflow completed successfully")
        return final_state
    except Exception as e:
        logger.error(f"Error in workflow: {e}")
        raise


@atraceable(name="financial_ai_workflow", tags=["workflow", "langgraph"])
async def arun_workflow(
    query: str,
    session_id: str = None,
    user_profile: Dict = None,
    portfolio: Dict = None,
    goals: list = None,
    config_path: str = "config.yaml",
    metadata: Dict = None,  # Added metadata
) -> Dict:
    """
    Async version of run_workflow.
    """
    from src.utils.logger import set_log_context
    from src.workflow.state import create_initial_state

    logger.info(f"Running async workflow for query: {query[:50]}...")

    # Set logging context
    set_log_context(session_id=session_id)

    # ── Step 1: Route ────────────────────────────────────────────────────────
    supervisor = SupervisorAgent(config_path)
    context = {
        'portfolio': portfolio,
        'goals': goals,
        'user_profile': user_profile or {},
    }
    selected_agent = await asyncio.get_event_loop().run_in_executor(
        None,
        lambda: supervisor.route(query, context),
    )
    
    # ── Step 2: Extract Symbols ──────────────────────────────────────────────
    # If we have a specific stock_symbol in metadata (from a UI action), use ONLY that.
    # This prevents extracting noise from generated prompts.
    if metadata and 'stock_symbol' in metadata:
        symbols = [metadata['stock_symbol']]
        # Force market agent if a specific stock is requested via metadata
        if selected_agent in ['portfolio', 'finance_qa']:
            selected_agent = 'market'
        logger.info(f"Using metadata stock symbol: {symbols}")
    else:
        # Otherwise extract from query (natural language)
        symbols = supervisor.extract_symbols(query)
        
        # ── Step 3: Use TickerResolverAgent if extracted symbols are weak ──
        # If we have no symbols or it looks like a company name might be missed, ask the agent
        if not symbols or (len(symbols) == 0 and len(query.split()) < 10):
            logger.info("No symbols extracted, triggering TickerResolverAgent...")
            ticker_agent = get_agent('ticker_resolver', config_path)
            # Use query as input to resolver
            resolver_result = await ticker_agent.async_process(query, context)
            symbols = resolver_result.get('metadata', {}).get('symbols', [])
            logger.info(f"TickerResolverAgent suggested: {symbols}")
    
    logger.info(f"Async workflow selected agent: {selected_agent}, symbols: {symbols}")

    # ── Step 2: Process with agent (async) ───────────────────────────────────
    agent = get_agent(selected_agent, config_path)
    
    # Merge symbols and metadata into kwargs
    agent_kwargs = {'symbols': symbols}
    if metadata:
        agent_kwargs.update(metadata)
        # Fix for Issue #2: If we have a goal_name in metadata, pass it explicitly as 'goal' if it matches
        if 'goal_name' in metadata and goals:
            goal_match = next((g for g in goals if g.get('name') == metadata['goal_name']), None)
            if goal_match:
                agent_kwargs['goal'] = goal_match

    try:
        result = await agent.async_process(
            query,
            context={
                'user_profile': user_profile or {},
                'portfolio': portfolio,
                'goals': goals,
                'session_id': session_id,
            },
            **agent_kwargs
        )
    except Exception as e:
        logger.error(f"Async agent processing failed: {e}")
        raise

    logger.info("Async workflow completed successfully")

    # ── Return same shape as run_workflow ────────────────────────────────────
    return {
        'query': query,
        'response': result['response'],
        'selected_agent': selected_agent,
        'agent_responses': [result],
        'session_id': session_id,
        'iteration_count': 1,
    }

