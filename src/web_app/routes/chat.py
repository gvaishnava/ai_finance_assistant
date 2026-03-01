"""
Chat endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List

from src.web_app.models import (
    ChatRequest,
    ChatResponse,
    PortfolioRequest,
    GoalRequest,
    ConversationHistoryResponse,
    ConversationMessage,
    CitationModel
)
from src.workflow.graph import arun_workflow
from src.core.session import SessionManager
from src.data.portfolio import Portfolio, Holding
from src.utils.logger import get_logger, set_log_context, clear_log_context

logger = get_logger(__name__)

router = APIRouter()

# Initialize session manager
session_manager = SessionManager()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint
    
    Args:
        request: Chat request with message and optional session_id
        
    Returns:
        Chat response with agent's answer
    """
    try:
        logger.info(f"Chat request: {request.message[:50]}...")
        
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                session = session_manager.create_session(session_id=request.session_id)
        else:
            session = session_manager.create_session()
        
        # Get user profile, portfolio, and goals from session
        user_profile = session.user_profile
        portfolio = session.portfolio
        goals = session.goals

        # Set log context for this request
        set_log_context(session_id=session.session_id)

        # Run workflow asynchronously
        result = await arun_workflow(
            query=request.message,
            session_id=session.session_id,
            user_profile=user_profile,
            portfolio=portfolio,
            goals=goals,
            metadata=request.metadata  # Pass metadata
        )
        
        # Add to session history
        source = request.source or 'chat'
        session.add_message('user', request.message, source=source, metadata=request.metadata)
        session.add_message(
            'assistant',
            result['response'],
            agent=result.get('selected_agent'),
            metadata=result.get('agent_responses', [{}])[0].get('metadata'),
            source=source
        )
        
        # Save session
        session_manager.save_session(session)

        # Clear log context
        clear_log_context()

        # Build response
        agent_response = result.get('agent_responses', [{}])[0]
        
        citations = None
        if agent_response.get('citations'):
            citations = [
                CitationModel(**citation)
                for citation in agent_response['citations']
            ]
        
        return ChatResponse(
            response=result['response'],
            agent=result.get('selected_agent', 'unknown'),
            agent_display_name=agent_response.get('agent_display_name', 'AI Assistant'),
            session_id=session.session_id,
            citations=citations,
            metadata=agent_response.get('metadata')
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/portfolio", response_model=ChatResponse)
async def chat_portfolio(request: PortfolioRequest):
    """
    Chat with portfolio analysis
    
    Args:
        request: Portfolio request with holdings
        
    Returns:
        Chat response with portfolio analysis
    """
    try:
        logger.info(f"Portfolio chat request with {len(request.holdings)} holdings")
        
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                session = session_manager.create_session(session_id=request.session_id)
        else:
            session = session_manager.create_session()
        
        # Convert holdings to portfolio format
        holdings = [
            {
                'symbol': h.symbol,
                'quantity': h.quantity,
                'average_price': h.average_price
            }
            for h in request.holdings
        ]
        
        portfolio_data = {'holdings': holdings}
        
        # Save portfolio to session for persistence
        session.set_portfolio(portfolio_data)
        session_manager.save_session(session)

        # Set log context
        set_log_context(session_id=session.session_id)

        # Run workflow with portfolio context asynchronously
        result = await arun_workflow(
            query=request.message or "Analyze my portfolio",
            session_id=session.session_id,
            user_profile=session.user_profile,
            portfolio=portfolio_data
        )
        
        # Build response
        agent_response = result.get('agent_responses', [{}])[0]
        
        # Update session history
        session.add_message('user', request.message or "Analyze my portfolio", source='portfolio', metadata=request.metadata)
        session.add_message(
            'assistant', 
            result['response'], 
            agent=result.get('selected_agent'), 
            source='portfolio',
            metadata=agent_response.get('metadata')
        )
        session_manager.save_session(session)
        clear_log_context()

        # Build response
        agent_response = result.get('agent_responses', [{}])[0]
        
        return ChatResponse(
            response=result['response'],
            agent=result.get('selected_agent', 'portfolio'),
            agent_display_name=agent_response.get('agent_display_name', 'Portfolio Agent'),
            session_id=session.session_id,
            metadata=agent_response.get('metadata')
        )
        
    except Exception as e:
        logger.error(f"Error in portfolio chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/goal", response_model=ChatResponse)
async def chat_goal(request: GoalRequest):
    """
    Chat with goal planning
    
    Args:
        request: Goal request
        
    Returns:
        Chat response with goal planning advice
    """
    try:
        logger.info(f"Goal chat request: {request.name}")
        
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                session = session_manager.create_session(session_id=request.session_id)
        else:
            session = session_manager.create_session()
        
        # Create goal data
        goal_data = {
            'name': request.name,
            'goal_type': request.goal_type,
            'target_amount': request.target_amount,
            'target_date': request.target_date,
            'current_amount': request.current_amount
        }
        
        # Add or update goal
        session.add_goal(goal_data)
        
        # Save session before long-running workflow
        session_manager.save_session(session)

        # Set log context
        set_log_context(session_id=session.session_id)

        # Run workflow asynchronously
        result = await arun_workflow(
            query=request.message or f"Help me plan for {request.name}",
            session_id=session.session_id,
            user_profile=session.user_profile,
            goals=session.goals,
            metadata={'goal_name': request.name}  # Pass goal name
        )
        
        # Build response
        agent_response = result.get('agent_responses', [{}])[0]

        # Update session
        session.add_message('user', request.message or f"Help me with {request.name}", source='goal_planning', metadata=request.metadata)
        session.add_message(
            'assistant', 
            result['response'], 
            agent=result.get('selected_agent'), 
            source='goal_planning',
            metadata=agent_response.get('metadata')
        )
        session_manager.save_session(session)
        clear_log_context()
        
        return ChatResponse(
            response=result['response'],
            agent=result.get('selected_agent', 'goal_planning'),
            agent_display_name=agent_response.get('agent_display_name', 'Goal Planning Agent'),
            session_id=session.session_id,
            metadata=agent_response.get('metadata')
        )
        
    except Exception as e:
        logger.error(f"Error in goal chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{session_id}", response_model=ConversationHistoryResponse)
async def get_history(session_id: str, agent: str = None, source: str = None):
    """
    Get conversation history for a session
    
    Args:
        session_id: Session ID
        agent: Optional agent name to filter by
        source: Optional source tab to filter by
        
    Returns:
        Conversation history
    """
    try:
        session = session_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Use both filters if both provided, but source is preferred for tab-specific history
        messages = [
            ConversationMessage(
                role=msg['role'],
                content=msg['content'],
                agent=msg.get('agent'),
                source=msg.get('source'),
                metadata=msg.get('metadata'),
                timestamp=msg.get('timestamp', '')
            )
            for msg in session.get_conversation_history(agent_filter=agent, source_filter=source)
        ]
        
        return ConversationHistoryResponse(
            session_id=session_id,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=str(e))
