"""
models.py - Data structures, constants, and configuration
"""

# Ticker mapping for correct yfinance symbols (handles crypto and special cases)
TICKER_MAPPING = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "XRP": "XRP-USD",
    "LTC": "LTC-USD",
    "ADA": "ADA-USD",
    "SOL": "SOL-USD",
    "DOGE": "DOGE-USD",
    "SHIB": "SHIB-USD",
}

# Risk weights for portfolio analysis
RISK_WEIGHT = {
    "LOW": 1,
    "OPTIMAL": 2,
    "HIGH": 3
}

# Sample data structures
portfolio = [
    {"ticker": "AAPL", "quantity": 10, "buy_price": 150, "current_price": 170, "risk": "high"},
    {"ticker": "TSLA", "quantity": 3, "buy_price": 700, "current_price": 650, "risk": "high"},
    {"ticker": "BTC", "quantity": 0.02, "buy_price": 30000, "current_price": 45000, "risk": "high"}
]

transactions = [
    {"date": "2025-03-01", "ticker": "AAPL", "type": "buy", "quantity": 5, "price": 145},
    {"date": "2025-03-10", "ticker": "TSLA", "type": "buy", "quantity": 3, "price": 700},
]

userdata = [
    {"nick": "x", "password": "123", "Birthday": "14/09/2007", "country": "Minnesota"},
    {"layout": "1", "order": "HtoLrisk or LtoHrisk"}
]

# ANSI color codes for terminal formatting
class Colors:
    """ANSI color codes for terminal formatting"""
    # Basic colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    
    # Reset
    RESET = '\033[0m'
    
    # Combinations (pre-made for convenience)
    SUCCESS = '\033[1m\033[92m'  # Bold Green
    ERROR = '\033[1m\033[91m'    # Bold Red
    WARNING = '\033[1m\033[93m'  # Bold Yellow
    INFO = '\033[1m\033[96m'     # Bold Cyan
    HEADER = '\033[1m\033[95m'   # Bold Magenta


def normalize_ticker(ticker):
    """
    Normalize ticker symbol for yfinance.
    Maps common symbols to their correct yfinance equivalents.
    """
    ticker = ticker.upper().strip()
    return TICKER_MAPPING.get(ticker, ticker)
