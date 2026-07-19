import math
import yfinance as yf


def _safe_number(value):
    """
    Convert a value to float safely.
    Returns None for missing, invalid, NaN or infinite values.
    """

    if value is None:
        return None

    try:
        value = float(value)

        if math.isnan(value) or math.isinf(value):
            return None

        return value

    except (TypeError, ValueError):
        return None


def _find_statement_value(statement, possible_names):
    """
    Search a financial statement for the first available
    row name and return the latest valid numeric value.
    """

    if statement is None or statement.empty:
        return None

    for name in possible_names:

        if name not in statement.index:
            continue

        row = statement.loc[name]

        # Normally yfinance returns a Series containing
        # several annual reporting periods.
        try:
            values = row.tolist()
        except AttributeError:
            values = [row]

        for value in values:

            number = _safe_number(value)

            if number is not None:
                return number

    return None


def calculate_roce_from_statements(financials, balance_sheet):
    """
    ROCE = EBIT / Capital Employed * 100

    Capital Employed =
    Total Assets - Current Liabilities
    """

    ebit = _find_statement_value(
        financials,
        [
            "EBIT",
            "Operating Income",
            "OperatingIncome",
        ],
    )

    total_assets = _find_statement_value(
        balance_sheet,
        [
            "Total Assets",
            "TotalAssets",
        ],
    )

    current_liabilities = _find_statement_value(
        balance_sheet,
        [
            "Current Liabilities",
            "Current Liabilities And Accrued Expenses",
            "CurrentLiabilities",
        ],
    )

    if ebit is None or total_assets is None:
        return None

    # Do not silently assume missing current liabilities = 0.
    if current_liabilities is None:
        return None

    capital_employed = (
        total_assets - current_liabilities
    )

    if capital_employed <= 0:
        return None

    roce = (
        ebit / capital_employed
    ) * 100

    return round(roce, 2)


def calculate_roce(symbol):
    """
    Backward-compatible ROCE function used by Stock Explorer.
    """

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:

        stock = yf.Ticker(symbol)

        financials = stock.financials
        balance_sheet = stock.balance_sheet

        return calculate_roce_from_statements(
            financials,
            balance_sheet,
        )

    except Exception:
        return None


def get_fundamental_metrics(symbol):
    """
    Fetch a broader fundamental dataset for one NSE stock.

    This becomes the base dataset for the future:
    Quality Engine
    Growth Engine
    Valuation Engine
    Alpha Score Engine
    """

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:

        stock = yf.Ticker(symbol)

        info = stock.info or {}

        financials = stock.financials
        balance_sheet = stock.balance_sheet

        roce = calculate_roce_from_statements(
            financials,
            balance_sheet,
        )

        return {

            # Profitability

            "roe": _safe_number(
                info.get("returnOnEquity")
            ),

            "roa": _safe_number(
                info.get("returnOnAssets")
            ),

            "roce": roce,

            "operating_margin": _safe_number(
                info.get("operatingMargins")
            ),

            "profit_margin": _safe_number(
                info.get("profitMargins")
            ),

            # Growth

            "revenue_growth": _safe_number(
                info.get("revenueGrowth")
            ),

            "earnings_growth": _safe_number(
                info.get("earningsGrowth")
            ),

            # Balance Sheet / Risk

            "debt_equity": _safe_number(
                info.get("debtToEquity")
            ),

            "current_ratio": _safe_number(
                info.get("currentRatio")
            ),

            "quick_ratio": _safe_number(
                info.get("quickRatio")
            ),

            # Valuation

            "pe": _safe_number(
                info.get("trailingPE")
            ),

            "forward_pe": _safe_number(
                info.get("forwardPE")
            ),

            "pb": _safe_number(
                info.get("priceToBook")
            ),

            "peg": _safe_number(
                info.get("pegRatio")
            ),

            # Cash / Earnings

            "free_cash_flow": _safe_number(
                info.get("freeCashflow")
            ),

            "operating_cash_flow": _safe_number(
                info.get("operatingCashflow")
            ),

            "total_cash": _safe_number(
                info.get("totalCash")
            ),

            "total_debt": _safe_number(
                info.get("totalDebt")
            ),
        }

    except Exception as error:

        return {
            "error": str(error)
        }