"""
Supervisor agent for routing queries to appropriate specialist agents
"""

from typing import Dict
import yaml
import re

from src.core.llm import get_llm_client
from src.utils.logger import get_logger
from src.core.constants import TICKER_BLACKLIST

logger = get_logger(__name__)

class SupervisorAgent:
    """Supervisor agent that routes queries to appropriate specialist agents"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize supervisor
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config
        self.llm_client = get_llm_client(config_path)
        
        # Load agent descriptions
        self.agents = {
            'finance_qa': config['agents']['finance_qa']['description'],
            'portfolio': config['agents']['portfolio']['description'],
            'market': config['agents']['market']['description'],
            'goal_planning': config['agents']['goal_planning']['description'],
            'news': config['agents']['news']['description'],
            'tax': config['agents']['tax']['description'],
        }
        
        logger.info("Initialized SupervisorAgent")
    
    def route(self, query: str, context: Dict = None) -> str:
        """
        Route a query to the appropriate agent
        
        Args:
            query: User query
            context: Optional context (portfolio, goals, etc.)
            
        Returns:
            Agent name to handle the query
        """
        # Use keyword-based routing first (fast)
        keyword_agent = self._keyword_based_routing(query, context)
        
        if keyword_agent:
            logger.info(f"Keyword routing: {keyword_agent}")
            return keyword_agent
        
        # Fall back to LLM-based routing for complex queries
        return self._llm_based_routing(query)
    
    def _keyword_based_routing(self, query: str, context: Dict = None) -> str:
        """Fast keyword-based routing"""
        
        query_lower = query.lower()
        
        # Portfolio-related keywords
        if any(word in query_lower for word in ['portfolio', 'holdings', 'my stocks', 'my investments']):
            return 'portfolio'
        
        # Market-related keywords
        if any(word in query_lower for word in ['market', 'stock price', 'stock', 'price', 'nifty', 'sensex', 'index', 'ticker']):
            return 'market'
        
        # Goal planning keywords
        if any(word in query_lower for word in ['goal', 'planning', 'retirement', 'save for', 'target']):
            return 'goal_planning'
        
        # Tax keywords
        if any(word in query_lower for word in ['tax', 'taxation', 'ltcg', 'stcg', '80c', 'deduction']):
            return 'tax'
        
        # News keywords
        if any(word in query_lower for word in ['news', 'announcement', 'event', 'happening']):
            return 'news'
        
        # Context-based routing (only if explicitly relevant)
        if context and not query_lower.strip(): # If it's an empty query but has context, maybe?
            if context.get('portfolio'):
                return 'portfolio'
            if context.get('news_article'):
                return 'news'
        
        # Default to LLM decision for everything else not caught by keywords
        return None  # Let LLM decide
    
    def _llm_based_routing(self, query: str) -> str:
        """LLM-based routing for complex queries"""
        
        agent_list = "\n".join([f"- {name}: {desc}" for name, desc in self.agents.items()])
        
        prompt = f"""You are a routing supervisor for a financial education chatbot with specialized agents.
 
Available agents:
{agent_list}
 
User query: "{query}"
 
Which single agent is MOST appropriate to handle this query? Respond with ONLY the agent name from the list above, nothing else.
 
If the query is a general financial question or concept explanation, choose: finance_qa"""
        
        try:
            response = self.llm_client.generate(
                prompt,
                system_prompt="You are a query router. Respond with only the agent name.",
                temperature=0.1
            )
            
            # Extract agent name from response
            agent_name = response.strip().lower()
            
            # Validate
            if agent_name in self.agents:
                logger.info(f"LLM routing: {agent_name}")
                return agent_name
            
            # If LLM returned invalid agent, try to find it in response
            for agent in self.agents:
                if agent in response.lower():
                    logger.info(f"LLM routing (extracted): {agent}")
                    return agent
            
        except Exception as e:
            logger.error(f"Error in LLM routing: {e}")
        
        # Default fallback
        logger.info("Routing fallback: finance_qa")
        return 'finance_qa'
 
    def extract_symbols(self, query: str) -> list:
        """Extract stock symbols from query"""
        # Look for potential tickers:
        # 1. Words with .NS or .BO suffix (case insensitive, then upper)
        # 2. Text in parentheses (e.g., (INFY))
        # 3. Uppercase words of length 2-6 (common ticker length)
        
        symbols = set()
        
        # 1. Suffix-based (e.g., RELIANCE.NS) - extract the whole thing
        suffix_matches = re.findall(r'\b([A-Za-z0-9]+\.(?:NS|BO))\b', query)
        for m in suffix_matches:
            symbols.add(m.upper())
            
        # 2. Parentheses (e.g., (INFY)) - usually very reliable
        paren_matches = re.findall(r'\(?([A-Z]{2,10})\)?', query)
        for m in paren_matches:
            # Check if this isn't just part of a suffix match already found
            if not any(m in s for s in symbols):
                symbols.add(m)
            
        # 3. Uppercase only words (2-6 chars)
        upper_matches = re.findall(r'\b([A-Z]{2,6})\b', query)
        for m in upper_matches:
            # Skip if it's already part of a longer symbol (like INFY in INFY.NS)
            if any(m in s for s in symbols):
                continue
            symbols.add(m)
            
        # Filter and unique
        unique_symbols = []
        for s in symbols:
            # Skip noise
            if s.isdigit() or len(s) < 2:
                continue
            if s.upper() in TICKER_BLACKLIST:
                continue
            unique_symbols.append(s)
            
        return unique_symbols

def route_query(query: str, context: Dict = None, config_path: str = "config.yaml") -> str:
    """
    Convenience function to route a query
    
    Args:
        query: User query
        context: Optional context
        config_path: Path to configuration
        
    Returns:
        Agent name
    """
    supervisor = SupervisorAgent(config_path)
    return supervisor.route(query, context)
