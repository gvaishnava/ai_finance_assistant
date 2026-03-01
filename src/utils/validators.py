"""
Input validation utilities
"""

import re
from typing import Optional

def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # Basic validation: alphanumeric, 1-10 characters, may include dots
    pattern = r'^[A-Z0-9.]{1,10}$'
    
    # Convert to uppercase for validation
    return bool(re.match(pattern, symbol.upper()))

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Trim whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t')
    
    return text

def validate_portfolio_data(portfolio: dict) -> tuple[bool, Optional[str]]:
    """
    Validate portfolio data structure
    
    Args:
        portfolio: Portfolio dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(portfolio, dict):
        return False, "Portfolio must be a dictionary"
    
    if 'holdings' not in portfolio:
        return False, "Portfolio must contain 'holdings' key"
    
    if not isinstance(portfolio['holdings'], list):
        return False, "Holdings must be a list"
    
    for holding in portfolio['holdings']:
        if not isinstance(holding, dict):
            return False, "Each holding must be a dictionary"
        
        required_keys = ['symbol', 'quantity']
        for key in required_keys:
            if key not in holding:
                return False, f"Holding missing required key: {key}"
        
        if not validate_stock_symbol(holding['symbol']):
            return False, f"Invalid stock symbol: {holding['symbol']}"
        
        try:
            quantity = float(holding['quantity'])
            if quantity <= 0:
                return False, f"Quantity must be positive: {holding['symbol']}"
        except (ValueError, TypeError):
            return False, f"Invalid quantity for {holding['symbol']}"
    
    return True, None
