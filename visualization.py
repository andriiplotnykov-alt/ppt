"""
visualization.py - Data visualization and display functions
"""

import yfinance as yf
import matplotlib.pyplot as plt
from tabulate import tabulate
from models import normalize_ticker
from computations import market_value, unrealized_pl, percent_return, fmt_money


def display_portfolio_table(portfolio_list, preferences=None):
    """Display portfolio as a formatted table"""
    headers = ["Ticker", "Qty", "Buy price", "Current price", "Market value", "Unreal. P&L", "Return %", "Risk", "Status"]
    rows = []
    
    for asset in portfolio_list:
        mv = market_value(asset)
        pl = unrealized_pl(asset)
        ret = percent_return(asset)
        rows.append([
            asset.get("ticker", ""),
            fmt_money(asset.get("quantity", 0)),
            fmt_money(asset.get("buy_price", 0)),
            fmt_money(asset.get("current_price", 0)),
            fmt_money(mv),
            fmt_money(pl),
            f"{ret:.2f}%",
            asset.get("risk", "N/A"),
            asset.get("status", "")
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="psql", stralign="right"))


def display_transactions_table(tx_list):
    """Display transactions as a formatted table"""
    headers = ["Date", "Ticker", "Type", "Qty", "Price"]
    rows = []
    
    for t in tx_list:
        rows.append([
            t.get("date", ""),
            t.get("ticker", ""),
            t.get("type", ""),
            fmt_money(t.get("quantity", 0)),
            fmt_money(t.get("price", 0))
        ])
    
    print(tabulate(rows, headers=headers, tablefmt="fancy_outline", stralign="right"))


def display_navigation_menu():
    """Display main navigation menu"""
    sections = ["Add", "View", "Charts", "Monthly", "Export", "Import", "Summary"]
    numbers = ["(1)", "(2)", "(3)", "(4)", "(5)", "(6)", "(7)"]
    print(tabulate([numbers], headers=sections, tablefmt="fancy_grid", stralign="center"))


def display_unrealised_pnl(unrealised_pnl_list):
    """Display unrealized P&L in table format"""
    headers = ["Ticker", "Unrealized P&L"]
    rows = []
    
    for ticker, pnl in unrealised_pnl_list:
        rows.append([ticker, fmt_money(pnl)])
    
    print(tabulate(rows, headers=headers, tablefmt="simple", stralign="right"))


def display_best_and_worst(best, worst):
    """Display best and worst performing assets"""
    print("\nYour best performers:")
    print(tabulate(best, headers=["Ticker", "Buy", "Current"], tablefmt="psql"))
    
    print("\nYour worst performer:")
    print(tabulate([worst], headers=["Ticker", "Buy", "Current"], tablefmt="psql"))


def chart_allocation(portfolio_list):
    """Display portfolio allocation as pie chart"""
    labels = [a["ticker"] for a in portfolio_list]
    values = [market_value(a) for a in portfolio_list]
    
    if not values or sum(values) == 0:
        print("⚠️  No allocation data to display.")
        return
    
    plt.figure(figsize=(7, 7))
    total = sum(values)
    use_legend = len(values) > 8 or any((v / total) < 0.05 for v in values)
    
    wedges, texts, autotexts = plt.pie(
        values,
        labels=None if use_legend else labels,
        autopct=(lambda pct: f"{pct:.1f}%") if not use_legend else None,
        pctdistance=0.75,
        startangle=140,
        wedgeprops=dict(width=0.5, edgecolor='w')
    )
    
    if use_legend:
        plt.legend(wedges, labels, title="Tickers", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    
    plt.title("Portfolio Allocation")
    plt.tight_layout()
    plt.show()


def chart_volatility(portfolio_list):
    """Display rolling volatility for portfolio assets"""
    plt.figure(figsize=(10, 5))
    plotted = 0
    
    for asset in portfolio_list[:12]:
        ticker = normalize_ticker(asset["ticker"])
        try:
            hist = yf.Ticker(ticker).history(period="6mo")
            if hist.empty:
                continue
            
            returns = hist["Close"].pct_change().dropna()
            if returns.empty:
                continue
            
            (returns.rolling(5).std() * (252 ** 0.5)).plot(label=asset["ticker"], alpha=0.8)
            plotted += 1
        except Exception as e:
            print(f"⚠️  Could not fetch data for {ticker}: {e}")
            continue
    
    if plotted == 0:
        print("⚠️  No volatility data available.")
        return
    
    plt.title("Rolling Volatility Comparison (5-day rolling)")
    plt.xlabel("Date")
    plt.ylabel("Annualized volatility")
    plt.legend(loc="upper left", bbox_to_anchor=(1.02, 1))
    plt.tight_layout()
    plt.show()


def chart_pnl(portfolio_list):
    """Display unrealized P&L bar chart"""
    tickers = [a["ticker"] for a in portfolio_list]
    pnls = [unrealized_pl(a) for a in portfolio_list]
    
    if not pnls:
        print("⚠️  No P&L data to display.")
        return
    
    plt.figure(figsize=(10, 5))
    colors = ['green' if p > 0 else 'red' for p in pnls]
    bars = plt.bar(tickers, pnls, color=colors, alpha=0.7)
    
    plt.title("Unrealized P&L per Asset")
    plt.ylabel("P&L ($)")
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    plt.xticks(rotation=45, ha="right")
    
    # Annotate bars
    for b in bars:
        h = b.get_height()
        plt.annotate(
            f"{h:,.0f}",
            xy=(b.get_x() + b.get_width() / 2, h),
            xytext=(0, 5 if h > 0 else -15),
            textcoords="offset points",
            ha='center',
            va='bottom' if h > 0 else 'top',
            fontsize=8
        )
    
    plt.tight_layout()
    plt.show()


def chart_price_history(portfolio_list):
    """Display price history for portfolio assets"""
    plt.figure(figsize=(10, 5))
    
    for asset in portfolio_list:
        ticker = normalize_ticker(asset["ticker"])
        try:
            hist = yf.Ticker(ticker).history(period="3mo")
            if hist.empty:
                continue
            
            plt.plot(hist.index, hist["Close"], label=asset["ticker"], linewidth=2)
        except Exception as e:
            print(f"⚠️  Could not fetch history for {ticker}: {e}")
            continue
    
    plt.title("Price History of Portfolio Assets (3 months)")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.legend()
    plt.tight_layout()
    plt.show()
