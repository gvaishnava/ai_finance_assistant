"""
Utilities to generate visualization data for the frontend (Recharts compatible)
"""

from typing import List, Dict, Any, Optional

def get_portfolio_allocation_chart(allocations: List[Dict]) -> Dict[str, Any]:
    """
    Generate data for a Pie chart of portfolio allocation
    """
    data = []
    for item in allocations:
        data.append({
            'name': item.get('name', item.get('symbol')),
            'value': round(item.get('allocation_percentage', 0), 2),
            'amount': round(item.get('value', 0), 2),
            'symbol': item.get('symbol')
        })
    
    return {
        'type': 'pie',
        'title': 'Portfolio Allocation',
        'data': data
    }

def get_sector_allocation_chart(sector_allocations: Dict[str, float]) -> Dict[str, Any]:
    """
    Generate data for a Bar or Pie chart of sector allocation
    """
    data = []
    for sector, percentage in sector_allocations.items():
        data.append({
            'name': sector,
            'value': round(percentage, 2)
        })
    
    # Sort by value descending
    data.sort(key=lambda x: x['value'], reverse=True)
    
    return {
        'type': 'bar',
        'title': 'Sector Allocation (%)',
        'data': data
    }

def get_market_history_chart(history_df: Any, symbol: str) -> Dict[str, Any]:
    """
    Generate data for a Line chart of stock history
    history_df is a pandas DataFrame from yfinance
    """
    if history_df is None or history_df.empty:
        return {}
        
    data = []
    # Take last 30 points if available
    points = history_df.tail(30)
    
    for date, row in points.iterrows():
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': round(row['Close'], 2)
        })
        
    return {
        'type': 'line',
        'title': f'{symbol} Price History',
        'data': data,
        'xAxis': 'date',
        'yAxis': 'price'
    }

def get_goal_projection_chart(goal: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data for a goal progress/projection chart
    """
    target = goal.get('target_amount', 0)
    current = goal.get('current_amount', 0)
    remaining = max(0, target - current)
    
    # Simple projection (Current vs Target)
    data = [
        {'name': 'Saved', 'value': current, 'fill': '#10b981'},
        {'name': 'Remaining', 'value': remaining, 'fill': '#e5e7eb'}
    ]
    
    return {
        'type': 'pie',
        'title': f"Progress for {goal.get('name', 'Goal')}",
        'data': data,
        'innerRadius': 60,
        'outerRadius': 80
    }

def get_market_indices_chart(indices: List[Dict]) -> Dict[str, Any]:
    """Generate a Bar chart for market indices status"""
    data = []
    for index in indices:
        data.append({
            'name': index.get('name', index['symbol']),
            'value': round(index.get('change_percent', 0), 2)
        })
    
    return {
        'type': 'bar',
        'title': 'Market Indices Change (%)',
        'data': data
    }

def get_news_impact_chart(sentiment_score: float) -> Dict[str, Any]:
    """Generate a gauge-like Pie chart for news sentiment/impact"""
    # sentiment_score from -1 to 1
    normalized = (sentiment_score + 1) / 2 * 100 # 0 to 100
    data = [
        {'name': 'Sentiment', 'value': round(normalized, 1), 'fill': '#3b82f6' if sentiment_score >= 0 else '#ef4444'},
        {'name': 'Level', 'value': 100 - normalized, 'fill': '#f3f4f6'}
    ]
    
    return {
        'type': 'pie',
        'title': 'Sentiment Impact Score',
        'data': data,
        'innerRadius': 60,
        'outerRadius': 80
    }

def get_goals_summary_chart(goals: List[Dict]) -> Dict[str, Any]:
    """Generate a Bar chart comparing multiple goals progress"""
    data = []
    for goal in goals:
        target = goal.get('target_amount', 0)
        current = goal.get('current_amount', 0)
        progress = (current / target * 100) if target > 0 else 0
        data.append({
            'name': goal.get('name', 'Goal'),
            'value': round(progress, 1)
        })
    
    return {
        'type': 'bar',
        'title': 'Progress Across All Goals (%)',
        'data': data
    }
