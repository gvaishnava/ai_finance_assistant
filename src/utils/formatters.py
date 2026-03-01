"""
Formatting utilities for financial data
"""

def format_currency(value: float, currency: str = "₹") -> str:
    """
    Format a number as currency
    
    Args:
        value: Numeric value
        currency: Currency symbol (default: ₹ for Indian Rupee)
        
    Returns:
        Formatted currency string
    """
    if value >= 10000000:  # 1 Crore
        return f"{currency}{value/10000000:.2f} Cr"
    elif value >= 100000:  # 1 Lakh
        return f"{currency}{value/100000:.2f} L"
    elif value >= 1000:
        return f"{currency}{value/1000:.2f}K"
    else:
        return f"{currency}{value:.2f}"

def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a number as percentage
    
    Args:
        value: Numeric value (e.g., 0.15 for 15%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string with + or - prefix
    """
    formatted = f"{value * 100:.{decimals}f}%"
    if value > 0:
        return f"+{formatted}"
    return formatted

def format_number(value: float, decimals: int = 2) -> str:
    """
    Format a number with thousands separators
    
    Args:
        value: Numeric value
        decimals: Number of decimal places
        
    Returns:
        Formatted number string
    """
    return f"{value:,.{decimals}f}"

def format_market_cap(value: float) -> str:
    """
    Format market capitalization
    
    Args:
        value: Market cap value
        
    Returns:
        Formatted market cap string
    """
    return format_currency(value, "₹")
