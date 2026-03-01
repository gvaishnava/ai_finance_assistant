"""
Portfolio management and analysis
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

from src.data.market_data import get_market_client
from src.utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Holding:
    """Represents a single holding in a portfolio"""
    symbol: str
    quantity: float
    average_price: Optional[float] = None
    purchase_date: Optional[datetime] = None

class Portfolio:
    """Represents a user's investment portfolio"""
    
    def __init__(self, holdings: List[Holding] = None):
        """
        Initialize portfolio
        
        Args:
            holdings: List of Holding objects
        """
        self.holdings = holdings or []
        self.market_client = get_market_client()
    
    def add_holding(self, holding: Holding):
        """Add a holding to the portfolio"""
        self.holdings.append(holding)
    
    def remove_holding(self, symbol: str):
        """Remove a holding by symbol"""
        self.holdings = [h for h in self.holdings if h.symbol != symbol]
    
    def get_current_value(self) -> Optional[float]:
        """
        Calculate current total portfolio value
        
        Returns:
            Total value or None if error
        """
        total = 0.0
        
        for holding in self.holdings:
            quote = self.market_client.get_quote(holding.symbol)
            if quote and quote.get('price'):
                total += quote['price'] * holding.quantity
            else:
                logger.warning(f"Could not fetch price for {holding.symbol}. Skipping in total calculation.")
        
        return total
    
    def get_investment_value(self) -> Optional[float]:
        """
        Calculate total invested amount
        
        Returns:
            Total invested or None if data incomplete
        """
        total = 0.0
        
        for holding in self.holdings:
            if holding.average_price is None:
                return None
            total += holding.average_price * holding.quantity
        
        return total
    
    def get_profit_loss(self) -> Optional[Dict]:
        """
        Calculate profit/loss
        
        Returns:
            Dictionary with absolute and percentage P&L
        """
        current_value = self.get_current_value()
        invested_value = self.get_investment_value()
        
        if current_value is None or invested_value is None:
            return None
        
        absolute_pl = current_value - invested_value
        percentage_pl = (absolute_pl / invested_value) * 100 if invested_value > 0 else 0
        
        return {
            'absolute': absolute_pl,
            'percentage': percentage_pl,
            'current_value': current_value,
            'invested_value': invested_value,
        }
    
    def get_allocation(self) -> List[Dict]:
        """
        Get portfolio allocation by holding
        
        Returns:
            List of holdings with their allocation percentages
        """
        current_value = self.get_current_value()
        
        if current_value is None or current_value == 0:
            return []
        
        allocations = []
        
        for holding in self.holdings:
            quote = self.market_client.get_quote(holding.symbol)
            if quote and quote.get('price'):
                value = quote['price'] * holding.quantity
                allocation_pct = (value / current_value) * 100
                
                allocations.append({
                    'symbol': holding.symbol,
                    'name': quote.get('name', holding.symbol),
                    'quantity': holding.quantity,
                    'current_price': quote['price'],
                    'value': value,
                    'allocation_percentage': allocation_pct,
                    'sector': quote.get('sector'),
                })
        
        # Sort by allocation percentage (descending)
        allocations.sort(key=lambda x: x['allocation_percentage'], reverse=True)
        
        return allocations
    
    def get_sector_allocation(self) -> Dict[str, float]:
        """
        Get portfolio allocation by sector
        
        Returns:
            Dictionary of sector to allocation percentage
        """
        current_value = self.get_current_value()
        
        if current_value is None or current_value == 0:
            return {}
        
        sector_values = {}
        
        for holding in self.holdings:
            quote = self.market_client.get_quote(holding.symbol)
            if quote and quote.get('price'):
                value = quote['price'] * holding.quantity
                sector = quote.get('sector', 'Unknown')
                
                if sector in sector_values:
                    sector_values[sector] += value
                else:
                    sector_values[sector] = value
        
        # Convert to percentages
        sector_allocations = {
            sector: (value / current_value) * 100
            for sector, value in sector_values.items()
        }
        
        return sector_allocations
    
    def to_dict(self) -> Dict:
        """Convert portfolio to dictionary"""
        return {
            'holdings': [
                {
                    'symbol': h.symbol,
                    'quantity': h.quantity,
                    'average_price': h.average_price,
                    'purchase_date': h.purchase_date.isoformat() if h.purchase_date else None,
                }
                for h in self.holdings
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Portfolio':
        """Create portfolio from dictionary"""
        holdings = [
            Holding(
                symbol=h['symbol'],
                quantity=h['quantity'],
                average_price=h.get('average_price'),
                purchase_date=datetime.fromisoformat(h['purchase_date']) if h.get('purchase_date') else None,
            )
            for h in data.get('holdings', [])
        ]
        
        return cls(holdings=holdings)
