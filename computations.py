"""
computations.py - Computational functions for portfolio analysis
"""

import statistics
import yfinance as yf
from models import portfolio, RISK_WEIGHT, normalize_ticker


def percent_return(item):
    """Calculate percentage return on investment"""
    if item["buy_price"] == 0:
        return 0
    return (item["current_price"] - item["buy_price"]) / item["buy_price"] * 100


def market_value(item):
    """Calculate total market value of an asset"""
    return item["quantity"] * item["current_price"]


def unrealized_pl(item):
    """Calculate unrealized profit/loss"""
    return (item["current_price"] - item["buy_price"]) * item["quantity"]


def volatility(ticker, days=60):
    """
    Calculate annualized volatility for a ticker
    Returns None if insufficient data
    """
    ticker = normalize_ticker(ticker)
    try:
        data = yf.Ticker(ticker).history(period=f"{days}d")
        
        if len(data) < 2:
            return None
        
        returns = data["Close"].pct_change().dropna()
        vol = returns.std() * (252 ** 0.5)  # annualized volatility
        return vol
    except Exception as e:
        print(f"⚠️  Error calculating volatility for {ticker}: {e}")
        return None


def classify_risk(item):
    """
    Classify risk level based on volatility
    Returns: "HIGH", "OPTIMAL", or "LOW"
    """
    ticker = item["ticker"]
    vol = volatility(ticker)

    if vol is None:
        return "UNKNOWN"

    if vol > 0.45:        # extremely volatile (crypto, TSLA)
        return "HIGH"
    elif vol > 0.20:      # moderate stocks
        return "OPTIMAL"
    else:                 # stable stocks / ETFs
        return "LOW"


def risk_score(item):
    """Get numeric risk score for sorting"""
    level = classify_risk(item)
    return RISK_WEIGHT.get(level, 2)


def get_live_price(ticker):
    """
    Fetch current live price for a ticker.
    Handles crypto and stock tickers correctly.
    Returns float price or None on error.
    """
    ticker = normalize_ticker(ticker)
    try:
        data = yf.Ticker(ticker)
        hist = data.history(period="1d")
        
        if hist.empty:
            print(f"⚠️  No price data found for {ticker}")
            return None
        
        price = float(hist["Close"].iloc[-1])
        
        # Sanity check: validate price is reasonable
        if price <= 0:
            print(f"⚠️  Invalid price {price} for {ticker}")
            return None
        
        return price
    except Exception as e:
        print(f"❌ Error fetching price for {ticker}: {e}")
        return None


def update_all_current_prices(portfolio_list=None):
    """
    Update current prices for all assets in portfolio
    """
    if portfolio_list is None:
        portfolio_list = portfolio
    
    print("⏳ Updating live prices...")
    
    for asset in portfolio_list:
        ticker = asset["ticker"]
        new_price = get_live_price(ticker)
        
        if new_price is not None:
            asset["current_price"] = round(new_price, 2)
            print(f"✓ Updated {ticker} → ${new_price:.2f}")
        else:
            print(f"⚠️  Could not fetch price for {ticker}")
    
    print("🔄 Live prices updated!\n")


def recalculate_portfolio(portfolio_list=None, preferences=None):
    """
    Recalculate all portfolio metrics
    Returns dictionary with computed values
    """
    if portfolio_list is None:
        portfolio_list = portfolio
    
    if preferences is None:
        preferences = {"order": "HtoLrisk"}
    
    # Calculate totals
    total_value = sum([market_value(i) for i in portfolio_list])
    
    # Sort by various metrics
    sorted_by_return = sorted(portfolio_list, key=percent_return, reverse=True)
    sorted_by_pnl = sorted(portfolio_list, key=lambda x: unrealized_pl(x), reverse=True)
    
    # Sort by risk preference
    if preferences.get("order") == "HtoLrisk":
        sorted_by_risk = sorted(portfolio_list, key=risk_score, reverse=True)
    else:
        sorted_by_risk = sorted(portfolio_list, key=risk_score, reverse=False)
    
    # Get top 3 and worst
    top_3_best = sorted_by_return[0:3] if len(sorted_by_return) >= 3 else sorted_by_return
    
    best_ass = [
        [item["ticker"], f"{item['buy_price']:.2f}", f"{item['current_price']:.2f}"]
        for item in top_3_best
    ]
    
    worst = sorted_by_return[-1] if sorted_by_return else None
    worst_ass = [worst["ticker"], f"{worst['buy_price']:.2f}", f"{worst['current_price']:.2f}"] if worst else []
    
    # Unrealized P&L per asset
    unrealised_pnl = [(item["ticker"], unrealized_pl(item)) for item in sorted_by_pnl]
    
    # Add status to each asset
    for asset in portfolio_list:
        if percent_return(asset) > 0:
            asset["status"] = "profit"
        else:
            asset["status"] = "loss"
    
    return {
        "total_value": total_value,
        "sorted_by_return": sorted_by_return,
        "sorted_by_risk": sorted_by_risk,
        "sorted_by_pnl": sorted_by_pnl,
        "top_3_best": top_3_best,
        "best_ass": best_ass,
        "worst": worst,
        "worst_ass": worst_ass,
        "unrealised_pnl": unrealised_pnl
    }


def get_portfolio_claim(ventures, portfolio_list=None):
    """
    Determine portfolio investment claim based on risk allocation
    Returns: "daring", "conservative", or "balanced"
    """
    if portfolio_list is None:
        portfolio_list = portfolio
    
    high_count = 0
    low_count = 0
    
    for venture in ventures:
        for asset in portfolio_list:
            if asset["ticker"] == venture["ticker"]:
                if asset["risk"].upper() == "HIGH":
                    high_count += 1
                elif asset["risk"].upper() == "LOW":
                    low_count += 1
                break
    
    if high_count > low_count:
        return "daring"
    elif high_count < low_count:
        return "conservative"
    else:
        return "balanced"


def fmt_money(x):
    """Format number as money with 2 decimals and thousands separator"""
    try:
        return f"{x:,.2f}"
    except Exception:
        return str(x)
