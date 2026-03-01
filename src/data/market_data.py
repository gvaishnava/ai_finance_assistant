"""
Market data client using yfinance
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import yaml

from src.utils.logger import get_logger
from src.utils.ticker_resolver import get_ticker_resolver
from src.core.constants import TICKER_BLACKLIST

logger = get_logger(__name__)

class MarketDataClient:
    """Client for fetching market data using yfinance"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize market data client
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.config = config['market_data']
        self.cache: Dict[str, tuple] = {}  # symbol -> (data, timestamp)
        self.cache_duration = self.config['cache_duration']
        
        logger.info("Initialized MarketDataClient")
    
    def get_quote(self, symbol: str, depth: int = 0) -> Optional[Dict]:
        """
        Get current quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS' for NSE)
            depth: Recursion depth to prevent infinite loops
            
        Returns:
            Dictionary with quote data or None if not found
        """
        if not symbol or symbol.upper() in TICKER_BLACKLIST:
            return None
            
        try:
            # Check cache
            if symbol in self.cache:
                data, timestamp = self.cache[symbol]
                if (datetime.now() - timestamp).total_seconds() < self.cache_duration:
                    logger.debug(f"Returning cached data for {symbol}")
                    return data
            
            # Try common Indian suffixes first, then original symbol
            symbols_to_try = []
            base_symbol = symbol.split('.')[0].upper()
            if not symbol.startswith('^'):
                 # Exhaustive check for Indian stocks: try both suffixes regardless of input suffix
                 symbols_to_try.extend([f"{base_symbol}.NS", f"{base_symbol}.BO"])
            if symbol.upper() not in symbols_to_try:
                symbols_to_try.append(symbol.upper())
            
            for sym in symbols_to_try:
                try:
                    ticker = yf.Ticker(sym)
                    info = ticker.info
                    
                    # Validate we got price data (essential)
                    price = info.get('currentPrice') or info.get('regularMarketPrice')
                    if not price:
                        logger.debug(f"No price found for {sym} in yfinance info: {list(info.keys())[:20]}")

                    if price:
                        # Found valid data
                        quote = {
                            'symbol': sym,
                            'name': info.get('longName', sym),
                            'price': price,
                            'change': info.get('regularMarketChange'),
                            'change_percent': info.get('regularMarketChangePercent'),
                            'volume': info.get('volume'),
                            'market_cap': info.get('marketCap'),
                            'pe_ratio': info.get('trailingPE'),
                            'day_high': info.get('dayHigh'),
                            'day_low': info.get('dayLow'),
                            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                            'sector': info.get('sector'),
                            'industry': info.get('industry'),
                            'currency': info.get('currency', 'INR'),
                        }
                        
                        # Cache the result for the requested symbol
                        self.cache[symbol] = (quote, datetime.now())
                        # Also cache for the actual found symbol if different
                        if sym != symbol:
                             self.cache[sym] = (quote, datetime.now())
                        
                        return quote
                except Exception:
                    continue
            
            if depth >= 1:
                logger.warning(f"Max resolution depth reached for {symbol}. Stopping.")
                return None
                
            # If we get here, no symbol worked. Try resolving via TickerResolver
            resolver = get_ticker_resolver()
            resolved_ticker = resolver.resolve(symbol)
            
            if resolved_ticker and resolved_ticker.upper() != symbol.upper():
                logger.info(f"Retrying get_quote with resolved ticker: {resolved_ticker} (depth {depth + 1})")
                return self.get_quote(resolved_ticker, depth=depth + 1)
            
            logger.warning(f"Could not find valid data for {symbol} or suffixes")
            return None
        
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_historical_data(
        self,
        symbol: str,
        period: str = None,
        interval: str = None
    ) -> Optional[pd.DataFrame]:
        """
        Get historical data for a symbol
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with historical data or None if error
        """
        try:
            period = period or self.config['default_period']
            interval = interval or self.config['default_interval']
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            return hist
        
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_market_indices(self) -> List[Dict]:
        """
        Get major market indices
        
        Returns:
            List of index quotes
        """
        indices = [
            '^NSEI',      # NIFTY 50
            '^NSEBANK',   # NIFTY BANK
            '^BSESN',     # BSE SENSEX
        ]
        
        results = []
        for index in indices:
            quote = self.get_quote(index)
            if quote:
                results.append(quote)
        
        return results
    
    def search_symbol(self, query: str) -> List[Dict]:
        """
        Search for stock symbols
        
        Args:
            query: Search query
            
        Returns:
            List of matching stocks
        """
        # For Indian stocks, add .NS for NSE and .BO for BSE
        symbols_to_try = [
            query.upper(),
            f"{query.upper()}.NS",
            f"{query.upper()}.BO",
        ]
        
        results = []
        for symbol in symbols_to_try:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if info.get('symbol'):
                    results.append({
                        'symbol': symbol,
                        'name': info.get('longName', symbol),
                        'exchange': info.get('exchange'),
                    })
            except:
                continue
        
        return results

# Global client instance
_market_client: Optional[MarketDataClient] = None

def get_market_client(config_path: str = "config.yaml") -> MarketDataClient:
    """
    Get or create market data client singleton
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        MarketDataClient instance
    """
    global _market_client
    
    if _market_client is None:
        _market_client = MarketDataClient(config_path)
    
    return _market_client

def get_stock_quote(symbol: str, config_path: str = "config.yaml") -> Optional[Dict]:
    """
    Convenience function to get a stock quote
    
    Args:
        symbol: Stock symbol
        config_path: Path to configuration file
        
    Returns:
        Quote dictionary or None
    """
    client = get_market_client(config_path)
    return client.get_quote(symbol)

def get_market_trends(config_path: str = "config.yaml") -> List[Dict]:
    """
    Convenience function to get market indices
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        List of index quotes
    """
    client = get_market_client(config_path)
    return client.get_market_indices()
