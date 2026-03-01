import sys
import os
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.getcwd())

# Mock the google.genai and other LLM stuff BEFORE imports
import src.core.llm as llm
llm.GeminiClient = MagicMock()
llm.get_llm_client = MagicMock()

# Mock embeddings to avoid OpenAI key check
import src.rag.embeddings as embeddings
embeddings.get_embedding_client = MagicMock()

from src.utils.ticker_resolver import get_ticker_resolver
from src.agents.goal_planning_agent import GoalPlanningAgent

async def test_ticker_resolution():
    print("Testing Ticker Resolution...")
    resolver = get_ticker_resolver()
    
    # Test resolving "Infosys"
    ticker = resolver.resolve("Infosys")
    print(f"Resolved 'Infosys' to: {ticker}")
    
    # Test resolving "TCS"
    ticker = resolver.resolve("TCS")
    print(f"Resolved 'TCS' to: {ticker}")
    
    # Test resolving "ITC"
    ticker = resolver.resolve("ITC")
    print(f"Resolved 'ITC' to: {ticker}")

async def test_goal_logic():
    print("\nTesting Goal Logic ($0 balance)...")
    
    # Mock the LLM generation to avoid needing API keys/imports for this logic test
    with patch.object(GoalPlanningAgent, 'async_generate_response', new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = "This is a mock educational response for a $0 balance goal."
        
        agent = GoalPlanningAgent()
        
        goal = {
            'name': 'New Home',
            'target_amount': 1000000,
            'current_amount': 0,
            'goal_type': 'Savings',
            'target_date': '2030-01-01'
        }
        
        query = "Help me plan for my new home goal"
        response = await agent.async_process(query, goal_name='New Home', context={'goals': [goal]})
        
        print(f"Goal Analysis for $0 balance:")
        print(f"Metadata: {response['metadata']}")
        print(f"Analysis contains goals: {goal['name'] in response['response']}")

async def main():
    try:
        await test_ticker_resolution()
    except Exception as e:
        print(f"Ticker resolution test failed: {e}")
        
    try:
        await test_goal_logic()
    except Exception as e:
        print(f"Goal logic test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
