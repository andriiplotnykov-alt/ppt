

import json
import csv
import statistics
from models import (
    portfolio, transactions, userdata, Colors, normalize_ticker
)
from computations import (
    update_all_current_prices, recalculate_portfolio, get_portfolio_claim,
    percent_return, market_value, unrealized_pl, volatility, classify_risk,
    get_live_price, fmt_money
)
from visualization import (
    display_portfolio_table, display_transactions_table, display_navigation_menu,
    display_unrealised_pnl, display_best_and_worst, chart_allocation,
    chart_volatility, chart_pnl, chart_price_history
)

try:
    from passencrypt import save_state as save_encrypted_state, load_state as load_encrypted_state
except ImportError:
    print("⚠️  passencrypt module not found. Encryption features disabled.")
    save_encrypted_state = None
    load_encrypted_state = None

# Global state
creds = userdata[0]
preferences = userdata[1]
portfolio_metrics = {}


def save_state_encrypted():
    """Save encrypted state"""
    if save_encrypted_state is None:
        print("⚠️  Encryption module not available. Saving as JSON instead.")
        save_state()
        return
    
    data = {
        "portfolio": portfolio,
        "transactions": transactions,
        "userdata": userdata
    }
    try:
        save_encrypted_state(data)
        print("💾 Encrypted state saved (no password needed on next run).")
    except Exception as e:
        print(f"❌ Failed to save encrypted state: {e}")


def save_state(filename="userdata.json"):
    """Save state to JSON file"""
    data = {
        "portfolio": portfolio,
        "transactions": transactions,
        "userdata": userdata
    }
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 State saved to {filename}")
    except Exception as e:
        print(f"❌ Failed to save state: {e}")


def load_state(filename="userdata.json"):
    """Load state from JSON file"""
    global portfolio, transactions, userdata, creds, preferences, portfolio_metrics
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        portfolio[:] = data.get("portfolio", portfolio)
        transactions[:] = data.get("transactions", transactions)
        userdata[:] = data.get("userdata", userdata)
        creds = userdata[0]
        preferences = userdata[1]
        
        print("🔄 Previous session loaded.")
        refresh_portfolio_metrics()
    
    except FileNotFoundError:
        print("⚠️  No saved session found. Starting fresh.")


def refresh_portfolio_metrics():
    """Refresh portfolio metrics"""
    global portfolio_metrics
    portfolio_metrics = recalculate_portfolio(portfolio, preferences)


def print_header(text):
    """Print a fancy header with borders"""
    width = len(text) + 4
    print(f"\n{Colors.HEADER}{'═' * width}")
    print(f"║ {text} ║")
    print(f"{'═' * width}{Colors.RESET}\n")


def print_section(title):
    """Print a section divider"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}▸ {title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * (len(title) + 2)}{Colors.RESET}")


def ouinput(prompt="> "):
    """
    Enhanced input with global command support
    Global commands: /home, /menu, /exit, /info
    Returns None if global command was used (caller should handle)
    """
    text = input(prompt).strip()
    
    # GLOBAL COMMANDS
    if text == "/home":
        home_page()
        return None
    elif text == "/menu":
        main_menu()
        return None
    elif text == "/exit":
        print("👋 Goodbye!")
        save_state_encrypted()
        exit()
    elif text == "/info" or text == "/help":
        print("Available commands: /home, /menu, /exit, /info, /help")
        return ouinput(prompt)
    else:
        return text


def get_float(prompt):
    """Get float input with validation"""
    while True:
        val = ouinput(prompt)
        if val is None:  # Global command was used
            return None
        try:
            return float(val)
        except ValueError:
            print("❌ Numbers only, try again.")


def check_password(password):
    """
    Check if password is strong enough
    Returns: True if strong, False if weak
    """
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False
    special_chars = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
    
    if len(password) < 8:
        print(" Password needs at least 8 characters")
        return False
    
    for char in password:
        if char.isupper():
            has_upper = True
        elif char.islower():
            has_lower = True
        elif char.isdigit():
            has_digit = True
        elif char in special_chars:
            has_special = True
    
    # Check for repetitive characters
    has_repetition = False
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            print(f"Such repetition is forbidden '{password[i:i+3]}'")
            has_repetition = True
            break
    
    # Check for common weak patterns
    weak_patterns = ["123", "abc", "password", "qwerty", "admin"]
    has_weak = False
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            print(f"⚠️  Warning: Contains weak pattern '{pattern}'")
            has_weak = True
            break
    
    # Report results
    checks_passed = 0
    
    if has_upper:
        print("✓ Has uppercase letters")
        checks_passed += 1
    else:
        print("❌ Missing uppercase letters (A-Z)")
    
    if has_lower:
        print("✓ Has lowercase letters")
        checks_passed += 1
    else:
        print("❌ Missing lowercase letters (a-z)")
    
    if has_digit:
        print("✓ Has numbers")
        checks_passed += 1
    else:
        print("❌ Missing numbers (0-9)")
    
    if has_special:
        print("✓ Has special characters")
        checks_passed += 1
    else:
        print("❌ Missing special characters (!@#$...)")
    
    if checks_passed >= 3 and not has_repetition and not has_weak:
        print("\n✅ Password is STRONG!")
        return True
    elif checks_passed >= 2:
        print(f"\n⚠️  Password is WEAK - passed only {checks_passed}/4 checks")
        return False
    else:
        print(f"\n❌ Password is TOO WEAK - passed only {checks_passed}/4 checks")
        return False


def home_page():
    """Setup home page with user credentials"""
    print("\n" + "="*60)
    print(" Welcome to the Ultimate Portfolio Tracking Tool!")
    print("="*60)
    
    username = ouinput("Input your nickname: ")
    if username is None:
        return
    
    if len(username) >= 8:
        print("⚠️  Make it shorter (max 7 characters)")
        return home_page()
    else:
        userdata[0]["nick"] = username
        print(f"Hello, {username}! 👋")
    
    while True:
        password = ouinput("\nSecure your account with a strong password: ")
        if password is None:
            return
        
        print("\n--- Checking password strength ---")
        
        if check_password(password):
            userdata[0]["password"] = password
            print("\n✅ Account secured!")
            break
        else:
            retry = ouinput("\nTry again? (yes/no): ")
            if retry is None:
                return
            if retry.lower() != "yes":
                print("⚠️  Continuing with weak password (not recommended)")
                userdata[0]["password"] = password
                break
    
    print("\n🚀 Setup complete! Redirecting to main menu...\n")
    ouinput("Press Enter to continue...")


def make_transaction():
    """Add a new transaction"""
    print_header("NEW TRANSACTION")
    
    # Get transaction details
    date = ouinput(f"{Colors.BOLD}Enter date (YYYY-MM-DD): {Colors.RESET}")
    if date is None:
        return False
    
    ticker = ouinput(f"{Colors.BOLD}Enter ticker symbol: {Colors.RESET}")
    if ticker is None:
        return False
    ticker = ticker.upper()
    
    trans_type = ouinput(f"{Colors.BOLD}Enter type (buy/sell): {Colors.RESET}")
    if trans_type is None:
        return False
    trans_type = trans_type.lower()
    
    quantity = get_float(f"{Colors.BOLD}Enter quantity: {Colors.RESET}")
    if quantity is None:
        return False
    
    price = get_float(f"{Colors.BOLD}Enter price: {Colors.RESET}")
    if price is None:
        return False
    
    # Show transaction details
    print_section("Transaction Summary")
    print(f"  Date:     {Colors.CYAN}{date}{Colors.RESET}")
    print(f"  Ticker:   {Colors.CYAN}{ticker}{Colors.RESET}")
    print(f"  Type:     {Colors.CYAN}{trans_type}{Colors.RESET}")
    print(f"  Quantity: {Colors.CYAN}{quantity}{Colors.RESET}")
    print(f"  Price:    {Colors.CYAN}${price:.2f}{Colors.RESET}")
    
    # Confirm transaction
    confirm = ouinput(f"\n{Colors.WARNING}Do you confirm? (yes/no): {Colors.RESET}")
    if confirm is None:
        return False
    
    if confirm.lower() != "yes":
        print(f"{Colors.ERROR}✗ Transaction declined{Colors.RESET}")
        return False
    
    # Create new transaction
    new_trans = {
        "date": date,
        "ticker": ticker,
        "type": trans_type,
        "quantity": quantity,
        "price": price
    }
    transactions.append(new_trans)
    
    # Update portfolio
    existing_asset = None
    for asset in portfolio:
        if asset["ticker"] == ticker:
            existing_asset = asset
            break
    
    if existing_asset:
        # Update existing asset
        if trans_type == "buy":
            total_qty = existing_asset["quantity"] + quantity
            total_cost = (existing_asset["quantity"] * existing_asset["buy_price"]) + (quantity * price)
            existing_asset["buy_price"] = total_cost / total_qty
            existing_asset["quantity"] = total_qty
        elif trans_type == "sell":
            existing_asset["quantity"] -= quantity
            if existing_asset["quantity"] <= 0:
                portfolio.remove(existing_asset)
    else:
        # Add new asset
        portfolio.append({
            "ticker": ticker,
            "quantity": quantity,
            "buy_price": price,
            "current_price": price,
            "risk": "OPTIMAL"
        })
    
    refresh_portfolio_metrics()
    print(f"{Colors.SUCCESS}✓ Transaction confirmed and added!{Colors.RESET}")
    return True


def port_perf():
    """Display portfolio performance"""
    update_all_current_prices(portfolio)
    refresh_portfolio_metrics()
    
    perf_rep = ouinput("To see the current performance report type X: ")
    if perf_rep is None:
        return
    
    if perf_rep == "X":
        total_value = portfolio_metrics.get("total_value", 0)
        best_ass = portfolio_metrics.get("best_ass", [])
        worst_ass = portfolio_metrics.get("worst_ass", [])
        unrealised_pnl = portfolio_metrics.get("unrealised_pnl", [])
        
        print(f"Your portfolio is estimated at ${total_value:,.2f}")
        print(f"\nYou've invested in {len(portfolio)} stocks")
        display_best_and_worst(best_ass, worst_ass)
        print("\n--- Unrealized P&L ---")
        display_unrealised_pnl(unrealised_pnl)
        ouinput("\nPress Enter to return to menu...")
    else:
        print("❌ Invalid input.")


def monthly_recap():
    """Display monthly summary"""
    # Get transactions from latest month
    if not transactions:
        print("⚠️  No transactions yet.")
        return
    
    buy_transactions = [t for t in transactions if t["type"] == "buy"]
    if not buy_transactions:
        print("⚠️  No buy transactions yet.")
        return
    
    latest_date = max(t["date"] for t in buy_transactions)
    latest_month = latest_date[0:7]
    ventures = [t for t in buy_transactions if t["date"][0:7] == latest_month]
    
    print(f" ---- Monthly summary ({latest_month}) ----")
    print(f"Amount of ventures: {len(ventures)}")
    
    total_growth = sum(unrealized_pl(asset) for asset in portfolio)
    print(f"Your networth has grown by ${total_growth:,.2f}")
    
    avg_return = statistics.mean(percent_return(asset) for asset in portfolio) if portfolio else 0
    print(f"Growth anticipated next month: {avg_return:.2f}%")
    
    claim = get_portfolio_claim(ventures, portfolio)
    print(f"You were: {claim}")
    ouinput("\nPress Enter to return to menu...")


def export_portfolio_csv(filename="portfolio_export.csv"):
    """Export portfolio to CSV"""
    keys = ["ticker", "quantity", "buy_price", "current_price", "risk", "status"]
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(portfolio)
        print(f"📁 Portfolio exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting portfolio: {e}")


def export_transactions_csv(filename="transactions_export.csv"):
    """Export transactions to CSV"""
    keys = ["date", "ticker", "type", "quantity", "price"]
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(transactions)
        print(f"📁 Transactions exported to {filename}")
    except Exception as e:
        print(f"❌ Error exporting transactions: {e}")


def import_portfolio_csv(filename="portfolio_import.csv"):
    """Import portfolio from CSV"""
    global portfolio
    
    try:
        new_portfolio = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print(f"❌ '{filename}' has no header row.")
                return
            
            def parse_float(row, candidates, default=0.0):
                for key in candidates:
                    if key in row and row[key] != "":
                        try:
                            return float(row[key])
                        except ValueError:
                            try:
                                cleaned = row[key].replace(",", "").replace("$", "").strip()
                                return float(cleaned)
                            except Exception:
                                continue
                return default
            
            for row in reader:
                qty = parse_float(row, ["quantity", "qty", "shares", "amount", "units"])
                buy = parse_float(row, ["buy_price", "buyprice", "buy", "price", "cost"])
                cur = parse_float(row, ["current_price", "currentprice", "current", "close", "last"])
                ticker = (row.get("ticker") or row.get("symbol") or "").strip().upper()
                
                if ticker == "":
                    print(f"⚠️  Skipping row without ticker: {row}")
                    continue
                
                new_portfolio.append({
                    "ticker": ticker,
                    "quantity": qty,
                    "buy_price": buy,
                    "current_price": cur,
                    "risk": row.get("risk", "OPTIMAL"),
                    "status": row.get("status", "")
                })
        
        if not new_portfolio:
            print(f"⚠️  No valid portfolio rows found in '{filename}'.")
            return
        
        portfolio[:] = new_portfolio
        refresh_portfolio_metrics()
        print(f"📥 Portfolio imported from {filename}")
    
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found.")
        print("👉 Make sure the file is in the same folder as your script.")


def import_transactions_csv(filename="transactions_import.csv"):
    """Import transactions from CSV"""
    global transactions
    
    try:
        new_tx = []
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row["quantity"] = float(row["quantity"])
                row["price"] = float(row["price"])
                new_tx.append(row)
        
        transactions[:] = new_tx
        print(f"📥 Transactions imported from {filename}")
    
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found.")
        print("👉 Make sure the file is in the same folder as your script.")


def charts():
    """Display chart menu"""
    print_header("DATA VISUALIZATION")
    print("(1) Portfolio Volatility Graph")
    print("(2) Asset Allocation Pie Chart")
    print("(3) P&L Bar Chart")
    print("(4) Price History")
    
    uchar = get_float("Select the chart that you want to view: ")
    
    if uchar is None:
        return
    
    try:
        uchar = int(uchar)
    except Exception:
        print("❌ Invalid input.")
        return
    
    if uchar == 1:
        chart_volatility(portfolio)
    elif uchar == 2:
        chart_allocation(portfolio)
    elif uchar == 3:
        chart_pnl(portfolio)
    elif uchar == 4:
        chart_price_history(portfolio)
    elif uchar == 0:
        return
    else:
        print("❌ Invalid option.")
        return
    
    ouinput("\nPress Enter to continue...")


def summary_view():
    """Display portfolio summary"""
    print_header("PORTFOLIO SUMMARY")
    print("\n--- All Transactions ---")
    display_transactions_table(transactions)
    
    sorted_by_risk = portfolio_metrics.get("sorted_by_risk", portfolio)
    print("\n--- Portfolio assets (sorted by risk) ---")
    display_portfolio_table(sorted_by_risk)
    
    ouinput("\nPress Enter to return to menu...")


def main_menu():
    """Main navigation menu"""
    while True:
        print("-" * 6 + "<" * 15 + "  NAVIGATE FREELY  " + ">" * 15 + "-" * 6)
        display_navigation_menu()
        
        nav1 = get_float("Enter a number to access the section: ")
        if nav1 is None:
            continue
        
        try:
            choice = int(nav1)
        except Exception:
            print("❌ Invalid option. Please enter a number.")
            continue
        
        if choice == 1:
            make_transaction()
        elif choice == 2:
            port_perf()
        elif choice == 3:
            charts()
        elif choice == 4:
            monthly_recap()
        elif choice == 5:
            export_portfolio_csv()
            export_transactions_csv()
        elif choice == 6:
            fname = ouinput("Enter portfolio CSV filename (default portfolio_import.csv): ")
            if fname is None:
                continue
            fname = fname.strip() or "portfolio_import.csv"
            import_portfolio_csv(fname)
            
            fname_tx = ouinput("Enter transactions CSV filename (default transactions_import.csv): ")
            if fname_tx is None:
                continue
            fname_tx = fname_tx.strip() or "transactions_import.csv"
            import_transactions_csv(fname_tx)
        elif choice == 7:
            summary_view()
        elif choice == 0:
            print("👋 Goodbye!")
            save_state_encrypted()
            exit()
        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    # Initialize portfolio with live prices
    print("⏳ Loading initial data...\n")
    try:
        # Try encrypted state first
        if load_encrypted_state is not None:
            try:
                loaded = load_encrypted_state()
                if loaded:
                    portfolio[:] = loaded.get("portfolio", portfolio)
                    transactions[:] = loaded.get("transactions", transactions)
                    userdata[:] = loaded.get("userdata", userdata)
                    creds = userdata[0]
                    preferences = userdata[1]
                    print("🔄 Encrypted session loaded.")
                    refresh_portfolio_metrics()
                else:
                    load_state()
            except Exception as e:
                print(f"⚠️  Encrypted load failed: {e}")
                load_state()
        else:
            load_state()
    except Exception as e:
        print(f"⚠️  Error during load: {e}")
    
    # Fetch live prices on startup
    print("\n⏳ Fetching live prices...")
    update_all_current_prices(portfolio)
    refresh_portfolio_metrics()
    
    # Start app
    home_page()
    main_menu()
    save_state_encrypted()
