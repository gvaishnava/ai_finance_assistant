"""
Data package for AI Finance Assistant
"""

from .market_data import MarketDataClient, get_stock_quote, get_market_trends
from .portfolio import Portfolio, Holding
from .user_profile import UserProfile

__all__ = [
    'MarketDataClient',
    'get_stock_quote',
    'get_market_trends',
    'Portfolio',
    'Holding',
    'UserProfile',
]
