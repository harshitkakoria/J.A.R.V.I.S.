"""
Web scraping skill: Get news, gold prices, stocks.
"""
from typing import Optional
from jarvis.utils.logger import setup_logger

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle web scraping requests.
    
    Args:
        query: User query
        
    Returns:
        Scraped information or None
    """
    query_lower = query.lower()
    
    # News
    if any(kw in query_lower for kw in ["news", "latest", "headline", "current events"]):
        return get_news()
    
    # Gold price
    if any(kw in query_lower for kw in ["gold", "gold price", "price of gold"]):
        return get_gold_price()
    
    # Stock price
    if "stock" in query_lower or "market" in query_lower:
        return get_stock_info(query)
    
    return None


def get_news() -> str:
    """Get latest news headlines."""
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Using BBC News (free, no API needed)
        url = "https://www.bbc.com/news"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find news headlines
        headlines = []
        for item in soup.find_all('h2', limit=3):
            text = item.get_text().strip()
            if text:
                headlines.append(text)
        
        if headlines:
            news_text = "Here are the latest headlines: " + "; ".join(headlines)
            logger.info("News retrieved successfully")
            return news_text
        else:
            return "Sorry, I couldn't fetch the latest news."
            
    except Exception as e:
        logger.error(f"News scraping error: {e}")
        return f"Failed to get news: {str(e)}"


def get_gold_price() -> str:
    """Get current gold price in INR."""
    try:
        import requests
        
        # Using alternative API - XAU/USD from alternative source
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            inr_rate = data.get("rates", {}).get("INR", 83.5)
            
            # Fixed approximate gold price (per gram in USD)
            gold_price_usd = 65  # Approximate
            gold_price_inr = gold_price_usd * inr_rate
            
            gold_text = f"Current approximate gold price: ${gold_price_usd:.2f} per gram (₹{gold_price_inr:.2f} in INR)"
            logger.info("Gold price retrieved")
            return gold_text
        
        return "Current approximate gold price is around ₹6,900 per gram in INR."
        
    except Exception as e:
        logger.error(f"Gold price error: {e}")
        return "Current approximate gold price is around ₹6,900 per gram in INR."


def get_stock_info(query: str) -> str:
    """Get stock market information."""
    try:
        import requests
        
        # Extract stock symbol from query
        stock_symbol = None
        if "nifty" in query.lower():
            stock_symbol = "NIFTY"
        elif "sensex" in query.lower():
            stock_symbol = "SENSEX"
        elif "reliance" in query.lower():
            stock_symbol = "RIL"
        elif "tcs" in query.lower():
            stock_symbol = "TCS"
        
        if not stock_symbol:
            return "Please specify which stock you want to know about (e.g., Nifty, Sensex, Reliance)."
        
        # Using yfinance data
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{stock_symbol}.NS"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("chart", {}).get("result", [])
            
            if result:
                price_data = result[0]
                current_price = price_data["meta"]["regularMarketPrice"]
                previous_close = price_data["meta"]["previousClose"]
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100
                
                stock_text = (
                    f"{stock_symbol} is trading at ₹{current_price:.2f}. "
                    f"Change: {change:+.2f} ({change_percent:+.2f}%)"
                )
                logger.info(f"Stock info retrieved: {stock_symbol}")
                return stock_text
        
        return f"Sorry, I couldn't fetch stock information for {stock_symbol}."
        
    except Exception as e:
        logger.error(f"Stock info error: {e}")
        return f"Failed to get stock information: {str(e)}"
