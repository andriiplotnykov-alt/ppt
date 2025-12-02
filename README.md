# Python Portfolio Tracker

 
**What it is**
- A lightweight CLI tool to track holdings, transactions and unrealized P&L.
- Live price fetching (stocks & crypto), risk classification, portfolio metrics and multiple visualizations (allocation, volatility, P&L, price history).
- Modular architecture split into `models.py`, `computations.py`, `visualization.py` and `portt_main.py` for clarity and testability.

**Main features**
- **Live pricing**: Robust price fetching (yfinance) with ticker normalization for crypto (e.g. `BTC -> BTC-USD`).
- **Portfolio analytics**: Market value, percent returns, unrealized P&L, rolling volatility and risk classification.
- **Transaction support**: Add buy/sell transactions with proper portfolio updates and CSV import/export.
- **Visualizations**: Pie charts, volatility comparison, P&L bar charts and price history via `matplotlib`.
- **State persistence**: Save/load session state (JSON and optional encrypted storage).
- **Usability**: Simple menu-driven CLI with global commands and input validation.

**Why this is relevant to recruiters**
- **Practical data pipeline experience**: The project shows end-to-end handling of external market data, cleaning/normalizing symbols, aggregating time-series, and persisting application state.
- **Quantitative & analytics skills**: Implements financial metrics (returns, P&L, volatility) and produces visual summaries useful for portfolio monitoring or risk analysis.
- **Software engineering best practices**: Modular design, clear separation of concerns, input validation, and error handling—skills important for production-ready analytics tools.
- **Communication-ready outputs**: Tabulated summaries and charts suitable for inclusion in analyst reports or trading desk dashboards.

**Quick start**
1. Install dependencies:

```bash
pip install -r requirements.txt
# or
pip install yfinance matplotlib tabulate passencrypt
```

2. Run the app from the project folder:

```bash
python portt_main.py
```

3. Useful one-liners for testing modules:

```bash
python -c "from computations import get_live_price; print(get_live_price('BTC'))"
python -c "from visualization import display_portfolio_table; from models import portfolio; display_portfolio_table(portfolio)"
```

**Tech stack**
- Python 3.x, `yfinance`, `matplotlib`, `tabulate`.
- Simple flat-file persistence (JSON) with optional encryption (`passencrypt`).

**Professional applications**
- Rapid prototyping for portfolio analytics and reporting used by quant analysts, risk teams and PMs.
- Data ingestion & normalization patterns transferable to time-series model building and valuation pipelines.
- Visual and tabular outputs appropriate for investor decks, internal monitoring or backtesting dashboards.

**Notes & limitations**
- This is a compact demo, not a production trading system—no execution connectivity, order routing, or advanced risk limits.
- CSV import expects sensible headers; ticker normalization handles common crypto symbols (add mappings as needed).

**Files of interest**
- `portt_main.py` — application entry point (run this)
- `models.py` — shared data and config (ticker mapping)
- `computations.py` — financial calculations and live-price logic
- `visualization.py` — charting and tabular display
 
