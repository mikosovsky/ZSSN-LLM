from mcp.server.fastmcp import FastMCP
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import io
import base64

mcp = FastMCP("Finance")

# work
@mcp.tool()
def get_stock_price(ticker: str) -> float:
    """
    Get the current stock price for a given ticker symbol.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        float: The current stock price.
    """
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")["Close"].iloc[-1]

# work
@mcp.tool()
def get_stock_info(ticker: str) -> dict:
    """
    Get detailed information about a stock.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        dict: A dictionary containing stock information.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        "symbol": info.get("symbol"),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice"),
        "previous_close": info.get("regularMarketPreviousClose"),
        "open": info.get("regularMarketOpen"),
        "high": info.get("dayHigh"),
        "low": info.get("dayLow")
    }

# work
@mcp.tool()
def get_stock_history(ticker: str, period: str = "1mo") -> dict:
    """
    Get historical stock prices for a given ticker symbol.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
        period (str): The period for which to retrieve historical data (default is '1mo').
    
    Returns:
        dict: A dictionary containing historical stock prices.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)
    return history.to_dict(orient="records")

# work
@mcp.tool()
def get_stock_dividends(ticker: str) -> dict:
    """
    Get dividend information for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        dict: A dictionary containing dividend information.
    """
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    return dividends.to_dict()
# work
@mcp.tool()
def get_stock_splits(ticker: str) -> dict:
    """
    Get stock split information for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        dict: A dictionary containing stock split information.
    """
    stock = yf.Ticker(ticker)
    splits = stock.splits
    return splits.to_dict()

# work
@mcp.tool()
def get_stock_recommendations(ticker: str) -> dict:
    """
    Get stock recommendations for a given ticker symbol.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        dict: A dictionary containing stock recommendations.
    """
    stock = yf.Ticker(ticker)
    recommendations = stock.recommendations
    return recommendations.to_dict(orient="records")

#work
@mcp.tool()
def get_stock_calendar(ticker: str) -> dict:
    """
    Get the earnings calendar for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        dict: A dictionary containing the earnings calendar.
    """
    stock = yf.Ticker(ticker)
    calendar = stock.calendar
    return calendar

@mcp.tool()
def get_stock_news(ticker: str) -> list:
    """
    Get the latest news articles for a given stock ticker.
    
    Args:
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
    
    Returns:
        list: A list of dictionaries containing news articles.
    """
    stock = yf.Ticker(ticker)
    news = stock.news
    return news

@mcp.tool()
def plot_stock_price(ticker: str, period: str, interval: str) -> str:
    """
    Plot the stock price for a given ticker symbol.

    Args:
        chart_num (int): The chart number to identify the plot.
        ticker (str): The stock ticker symbol (e.g., 'AAPL' for Apple Inc.).
        period (str): The period for which to retrieve historical data e.g. ['1d', '1wk', '1mo', '1y].
        interval (str): The interval for the historical data e.g. ['1m', '5m', '1h', '1d', '1wk', '1mo'].

    Returns:
        str: Ready string with encoded image of plot to add to the response.
    """
    stock = yf.Ticker(ticker)
    stock_history = stock.history(period=period, interval=interval)

    fig, ax = mpf.plot(
    stock_history,
    type='candle',
    style='yahoo',
    title=f'{ticker} Stock Price',
    ylabel='Price ($)',
    volume=True,
    returnfig=True
    )
    chart_name = f"app/static/chart_{ticker}_{period}_{interval}.png"
    plt.savefig(chart_name, format='png')
    str_plot = f'![{ticker} Stock Price]({chart_name})'
    return str_plot

if __name__ == "__main__":
    mcp.run(transport="stdio")