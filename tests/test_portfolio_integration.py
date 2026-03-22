import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.workflow.graph import arun_workflow
from src.agents.portfolio_agent import PortfolioAgent

@pytest.mark.asyncio
async def test_portfolio_routing_priority():
    """Test that portfolio agent is prioritized when source is portfolio"""
    query = "Analyze RELIANCE"
    metadata = {'stock_symbol': 'RELIANCE.NS'}
    
    # Mock supervisor to return 'portfolio' (as it should for this query)
    # But even if it returned 'finance_qa', the arun_workflow should now NOT force 'market'
    # if it's already a safe agent.
    
    with patch('src.workflow.graph.SupervisorAgent') as mock_supervisor_cls:
        mock_supervisor = mock_supervisor_cls.return_value
        mock_supervisor.route.return_value = 'portfolio'
        mock_supervisor.extract_symbols.return_value = ['RELIANCE.NS']
        
        # Mock PortfolioAgent.async_process
        with patch('src.workflow.graph.get_agent') as mock_get_agent:
            mock_portfolio_agent = AsyncMock()
            mock_portfolio_agent.async_process.return_value = {
                'response': 'Portfolio Analysis Result',
                'metadata': {}
            }
            mock_get_agent.return_value = mock_portfolio_agent
            
            result = await arun_workflow(
                query=query,
                metadata=metadata
            )
            
            assert result['selected_agent'] == 'portfolio'

@pytest.mark.asyncio
async def test_portfolio_agent_uses_profile():
    """Test that PortfolioAgent includes user profile in its prompt"""
    agent = PortfolioAgent()
    
    query = "Analyze my portfolio"
    user_profile = {
        'risk_tolerance': 'conservative',
        'knowledge_level': 'beginner'
    }
    portfolio_data = {'holdings': []}
    
    with patch.object(agent, 'async_generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Educated response"
        
        # We need to mock the retrieval and calculations to avoid errors
        with patch.object(agent, 'retrieve_context', return_value=[]):
            with patch('src.agents.portfolio_agent.Portfolio.from_dict') as mock_portfolio_cls:
                mock_portfolio = mock_portfolio_cls.return_value
                mock_portfolio.get_allocation.return_value = []
                mock_portfolio.get_sector_allocation.return_value = {}
                mock_portfolio.get_profit_loss.return_value = None
                
                await agent.async_process(
                    query=query,
                    context={'user_profile': user_profile, 'portfolio': portfolio_data}
                )
                
                # Check the prompt sent to LLM
                args, _ = mock_gen.call_args
                prompt = args[0]
                assert "conservative" in prompt
                assert "beginner" in prompt

@pytest.mark.asyncio
async def test_goal_agent_uses_profile():
    """Test that GoalPlanningAgent includes user profile in its prompt"""
    with patch('src.agents.base_agent.get_llm_client'):
        from src.agents.goal_planning_agent import GoalPlanningAgent
        agent = GoalPlanningAgent()
    
    query = "Help me plan for retirement"

    user_profile = {
        'risk_tolerance': 'aggressive',
        'knowledge_level': 'advanced'
    }
    
    with patch.object(agent, 'async_generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "Educated response"
        
        with patch.object(agent, 'retrieve_context', return_value=[]):
            with patch.object(agent, 'retriever') as mock_retriever:
                mock_retriever.get_citations.return_value = []
                await agent.async_process(
                    query=query,
                    context={'user_profile': user_profile}
                )

            
            args, _ = mock_gen.call_args
            prompt = args[0]
            assert "aggressive" in prompt
            assert "advanced" in prompt


if __name__ == "__main__":
    pytest.main([__file__])
