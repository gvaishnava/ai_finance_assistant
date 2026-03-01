"""
Disclaimer management for regulatory compliance
"""

from typing import Dict
import yaml

def load_disclaimers(config_path: str = "config.yaml") -> Dict[str, str]:
    """
    Load disclaimers from configuration
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Dictionary of disclaimer types to text
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config.get('disclaimers', {})

def get_disclaimer(disclaimer_type: str = "general", config_path: str = "config.yaml") -> str:
    """
    Get a specific disclaimer
    
    Args:
        disclaimer_type: Type of disclaimer (general, tax, portfolio, etc.)
        config_path: Path to configuration file
        
    Returns:
        Disclaimer text
    """
    disclaimers = load_disclaimers(config_path)
    return disclaimers.get(disclaimer_type, disclaimers.get('general', ''))

def add_disclaimer_to_response(
    response: str,
    disclaimer_type: str = "general",
    config_path: str = "config.yaml"
) -> str:
    """
    Add disclaimer to a response
    
    Args:
        response: Original response text
        disclaimer_type: Type of disclaimer to add
        config_path: Path to configuration file
        
    Returns:
        Response with disclaimer appended
    """
    disclaimer = get_disclaimer(disclaimer_type, config_path)
    
    if disclaimer:
        return f"{response}\n\n---\n\n**Disclaimer:** {disclaimer}"
    
    return response

def format_citation(source: str, page: int = None) -> str:
    """
    Format a citation for knowledge base sources
    
    Args:
        source: Source document name
        page: Optional page number
        
    Returns:
        Formatted citation string
    """
    if page:
        return f"[Source: {source}, Page {page}]"
    return f"[Source: {source}]"
