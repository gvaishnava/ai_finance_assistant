"""
Core constants for the application
"""

# Common words that are NOT tickers (Blacklist)
TICKER_BLACKLIST = {
    'ANALYSIS', 'AND', 'THE', 'FOR', 'WITH', 'NEWS', 'STOCK', 'PRICE', 'MARKET',
    'INDEX', 'NIFTY', 'SENSEX', 'BSE', 'NSE', 'INDIA', 'CURRENTLY', 'TODAY',
    'PERSPECTIVE', 'SUMMARY', 'REPORT', 'TRENDS', 'DETAILS', 'INFO', 'ABOUT',
    'ITC', 'PROVIDE', 'WITH' # Note: ITC is actually a ticker, but if it appears in a common word context, we might blacklist it if it causes issues. Actually ITC is a valid ticker, so I should keep it OUT of the blacklist. 
}

# Wait, ITC is a very popular Indian stock ticker (ITC.NS). I should NOT blacklist it.
# I'll stick to clear non-ticker words.

TICKER_BLACKLIST = {
    'ANALYSIS', 'AND', 'THE', 'FOR', 'WITH', 'NEWS', 'STOCK', 'PRICE', 'MARKET',
    'INDEX', 'NIFTY', 'SENSEX', 'BSE', 'NSE', 'INDIA', 'CURRENTLY', 'TODAY',
    'PERSPECTIVE', 'SUMMARY', 'REPORT', 'TRENDS', 'DETAILS', 'INFO', 'ABOUT',
    'PROVIDE', 'PLEASE', 'HOW', 'WHAT', 'WHICH', 'WHEN', 'WHERE', 'WHY',
    'IS', 'OF', 'IN', 'TO', 'A', 'AN', 'AM', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING',
    'HAVE', 'HAS', 'HAD', 'DO', 'DOES', 'DID', 'BUT', 'IF', 'OR', 'AS', 'BY', 'AT',
    'LIMITED', 'LTD', 'TRADING', 'SERVICES', 'HOLDINGS', 'INR', 'USD', 'RS', 'EQUITY',
    'PRIVATE', 'PVT', 'CORP', 'CORPORATION', 'GROUP', 'INDUSTRIES', 'FINANCIAL', 'INVESTMENT'
}
