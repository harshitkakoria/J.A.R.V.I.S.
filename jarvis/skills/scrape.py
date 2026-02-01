"""Web scraping - news, stocks."""
import requests
import yfinance as yf
from bs4 import BeautifulSoup

def handle(query: str) -> str:
    """Handle scraping."""
    q = query.lower()
    
    if any(kw in q for kw in ["news", "headline", "latest"]):
        return get_news()
    
    if "gold" in q:
        return get_stock("GC=F", "Gold")
    
    if "stock" in q or "price" in q:
        # Try to extract a ticker like "AAPL" or "TSLA"
        words = q.split()
        for word in words:
            if word.isupper() and len(word) <= 5 and word.isalpha():
                return get_stock(word)
                
        # Common usage mapping
        if "apple" in q: return get_stock("AAPL", "Apple")
        if "google" in q: return get_stock("GOOGL", "Google")
        if "microsoft" in q: return get_stock("MSFT", "Microsoft")
        if "tesla" in q: return get_stock("TSLA", "Tesla")
        if "amazon" in q: return get_stock("AMZN", "Amazon")
        if "bitcoin" in q: return get_stock("BTC-USD", "Bitcoin")
        
        return "Please say the stock ticker (e.g., 'AAPL stock') or common name."
    
    return None


def get_news() -> str:
    """Get news headlines."""
    try:
        url = "https://www.bbc.com/news"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.content, 'html.parser')
        
        headlines = []
        for h2 in soup.find_all('h2', limit=3):
            text = h2.get_text().strip()
            if text:
                headlines.append(text)
        
        if headlines:
            return "Headlines: " + "; ".join(headlines)
    except:
        pass
    
    return "Couldn't fetch news"


def get_stock(symbol: str, name: str = None) -> str:
    """Get real-time stock price."""
    try:
        ticker = yf.Ticker(symbol)
        # fast_info is efficient
        price = ticker.fast_info.last_price
        
        if not name:
            name = symbol.upper()
            
        if price:
            return f"{name} ({symbol.upper()}): ${price:.2f}"
    except Exception as e:
        return f"Couldn't check stock for {symbol}"
        
    return f"Could not find price for {symbol}"
