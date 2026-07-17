import yfinance as yf


def calculate_roce(symbol):
    """
    Calculate ROCE using:
    ROCE = EBIT / Capital Employed × 100
    """

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:
        stock = yf.Ticker(symbol)

        financials = stock.financials
        balance_sheet = stock.balance_sheet

        # -------- EBIT --------
        ebit = None

        for key in [
            "EBIT",
            "Operating Income",
            "OperatingIncome"
        ]:
            if key in financials.index:
                ebit = financials.loc[key].iloc[0]
                break

        # -------- Assets --------
        total_assets = None

        for key in [
            "Total Assets",
            "TotalAssets"
        ]:
            if key in balance_sheet.index:
                total_assets = balance_sheet.loc[key].iloc[0]
                break

        # -------- Current Liabilities --------
        current_liabilities = 0

        for key in [
            "Current Liabilities",
            "CurrentLiabilities"
        ]:
            if key in balance_sheet.index:
                current_liabilities = balance_sheet.loc[key].iloc[0]
                break

        if (
            ebit is None
            or total_assets is None
        ):
            return None

        capital_employed = total_assets - current_liabilities

        roce = (ebit / capital_employed) * 100

        return round(float(roce), 2)

    except Exception:
        return None