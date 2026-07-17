import yfinance as yf


def get_stock_data(symbol):
    """
    Fetch stock data from Yahoo Finance.
    """

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        return {
            "name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "price": info.get("currentPrice", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe": info.get("trailingPE", "N/A"),
            "pb": info.get("priceToBook", "N/A"),
            "roe": info.get("returnOnEquity", "N/A"),
            "debt_equity": info.get("debtToEquity", "N/A"),
        }

    except Exception as e:
        return {"error": str(e)}